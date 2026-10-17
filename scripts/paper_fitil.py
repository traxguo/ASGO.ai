"""
Paper tracking of Fitil Avcisi + Derin Fitil on 81 coins (config/pairs_wide81.json), with live Bitget prices.
No keys, no orders: the Bitget demo account lists only 15 coins, so this follows the exact tested rules on the
whole universe to count how many trades they really give per day (plan "çukurdan çıkış", 2026-10-17).

Same rules and the same fill test as the research scans (research/scans/wick_catcher*.py):
- each closed hour: coins in a daily uptrend get a buy limit at hour open x 0.95, downtrend coins at x 0.92
  (scripts/bitget_fitil.py depth_for, last closed daily candle before the hour)
- filled only if a 15m low in that hour trades 0.1% under the limit; entry = min(limit, that 15m open)
- skipped if BTC fell 3% from its hour open up to the fill candle (guard)
- at most 5 open, each equity / 5; exit at the close of the 12th 15m candle after the fill candle (3h)
- costs: 0.02% maker in, 0.06% taker out + 0.05% slippage
Hours are judged only after they closed, so nothing is decided with data the live bot could not have had.

    python scripts/paper_fitil.py
"""

import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bitget_demo as bd  # noqa: E402
import bitget_fitil as bf  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PAIRS_FILE = REPO / "config" / "pairs_wide81.json"
OUT_DIR = REPO / "forward" / "paper_fitil"
FILLPAD = 0.001
COST = 0.0002 + 0.0011
START_EQUITY = 10_000.0
MAX_BACKFILL_HOURS = 6
Q = timedelta(minutes=15)
FIELDS = ["pair", "mode", "hour", "limit_price", "fill_time", "entry", "exit_time", "exit", "ret_pct", "pnl_usdt"]


def candles_15m(pub, pair: str, start: datetime, count: int) -> list[list[float]]:
    rows = pub.fetch_ohlcv(pair, "15m", since=int(start.timestamp() * 1000), limit=count)
    first = int(start.timestamp() * 1000)
    return [r for r in rows if r[0] >= first][:count]


def judge_hour(pub, pairs: list[str], hour: datetime, daily_cache: dict) -> list[dict]:
    """Fills that the tested rule would have had in this closed hour (before the max-open cap)."""
    btc = candles_15m(pub, bf.BTC, hour, 4)
    btc_open = btc[0][1] if btc else None
    fills = []
    for pair in pairs:
        key = (pair, hour.date())
        if key not in daily_cache:
            try:
                daily_cache[key] = bf.depth_for(bd.fetch_candles(pub, pair, "1d", 120, hour))
            except Exception as e:  # noqa: BLE001 - one coin with no data must not stop the others
                print(f"{pair}: no daily data ({e})")
                daily_cache[key] = (None, float("nan"), "")
        depth, _, mode = daily_cache[key]
        if depth is None:
            continue
        rows = candles_15m(pub, pair, hour, 4)
        if len(rows) < 4:
            continue
        limit = rows[0][1] * (1 - depth)
        for j, r in enumerate(rows):
            if r[3] <= limit * (1 - FILLPAD):
                if btc_open and min(b[3] for b in btc[: j + 1]) <= btc_open * (1 - bf.BTC_GUARD):
                    break
                fill_open = datetime.fromtimestamp(r[0] / 1000, tz=timezone.utc)
                fills.append({"pair": pair, "mode": mode, "hour": hour.isoformat(), "limit_price": limit,
                              "fill_time": fill_open.isoformat(), "entry": min(limit, r[1])})
                break
    return sorted(fills, key=lambda f: f["fill_time"])


def exit_time(t: dict) -> datetime:
    return datetime.fromisoformat(t["fill_time"]) + 13 * Q  # close of the 12th 15m candle after the fill candle


def run_once(pub, state: dict, now: datetime, pairs: list[str]) -> list[str]:
    msgs = []
    trades = state.setdefault("trades", [])
    equity = state.setdefault("equity", START_EQUITY)
    this_hour = now.replace(minute=0, second=0, microsecond=0)
    done = datetime.fromisoformat(state["done_until"]) if state.get("done_until") else this_hour - timedelta(hours=1)
    hour = max(done, this_hour - timedelta(hours=MAX_BACKFILL_HOURS))
    cache: dict = {}
    while hour + timedelta(hours=1) <= now:
        for f in judge_hour(pub, pairs, hour, cache):
            ft = datetime.fromisoformat(f["fill_time"])
            open_now = [t for t in trades if t.get("exit_time") is None or datetime.fromisoformat(t["exit_time"]) > ft]
            if len(open_now) >= bf.MAX_OPEN or any(t["pair"] == f["pair"] and t.get("exit") is None for t in trades):
                continue
            f.update({"exit_time": None, "exit": None, "ret_pct": None, "pnl_usdt": None, "size": equity / bf.MAX_OPEN})
            trades.append(f)
            msgs.append(f"KÂĞIT alış: {f['pair'].split('/')[0]} @ {f['entry']:.6g} "
                        f"({'düşen coin, %8 altı' if f['mode'] == 'derin' else 'yükselen coin, %5 altı'})")
        hour += timedelta(hours=1)
        state["done_until"] = hour.isoformat()
    for t in trades:
        if t.get("exit") is not None or exit_time(t) > now:
            continue
        rows = candles_15m(pub, t["pair"], exit_time(t) - Q, 1)
        if not rows:
            continue
        t["exit"] = rows[0][4]
        t["exit_time"] = exit_time(t).isoformat()
        ret = t["exit"] / t["entry"] - 1 - COST
        t["ret_pct"] = round(ret * 100, 3)
        t["pnl_usdt"] = round(t["size"] * ret, 2)
        equity += t["pnl_usdt"]
        msgs.append(f"KÂĞIT satış: {t['pair'].split('/')[0]} @ {t['exit']:.6g}, net {t['ret_pct']:+.2f}%")
    state["equity"] = round(equity, 2)
    return msgs


def save(state: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "state.json").write_text(json.dumps(state, indent=1), encoding="utf-8")
    with (OUT_DIR / "trades.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(state.get("trades", []))


def main() -> None:
    now = datetime.now(timezone.utc)
    pairs_all = json.loads(PAIRS_FILE.read_text(encoding="utf-8"))["exchange"]["pair_whitelist"]
    pub = bd.public_exchange()
    pub.load_markets()
    pairs = [p for p in pairs_all if p in pub.markets]
    path = OUT_DIR / "state.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"started": now.isoformat()}
    msgs = run_once(pub, state, now, pairs)
    save(state)
    closed = [t for t in state["trades"] if t.get("exit") is not None]
    print(f"paper: {len(pairs)} coins, {len(state['trades'])} trades ({len(closed)} closed), equity {state['equity']}")
    if msgs and os.environ.get("TELEGRAM_BOT_TOKEN", "").strip():
        bf.notify(["(Gerçek emir yok, 81 coinde kâğıt takip)"] + msgs)


if __name__ == "__main__":
    main()
