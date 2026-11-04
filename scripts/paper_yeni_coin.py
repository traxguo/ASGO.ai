"""
Paper tracking of Yeni Coin Short, 14-day version (cards/yeni_coin_short.md), with live Bitget public prices.
No keys, no orders, no demo account (supervisor decision 2026-11-04: the 7-day rule failed the holdout; the
pre-fixed 14-day rule is only followed forward on paper). Rules are frozen until the 2026-11-30 review.

Tested rule (research/shortside/a_new_listing.py, K1 H14 S40):
- signal: a USDT perpetual gets its first daily candle on Binance USDⓈ-M (listing day D)
- entry: short at the open of day D+1 (00:00 UTC) -> here: the Bitget daily open of D+1 for the same coin
- stop 40% above the entry, checked on closed daily candles (a gap above the stop exits at that day's open),
  0.3% extra slippage on stop exits
- exit at the close of the 14th day (D+1 .. D+14) if the stop was not hit
- 1% risk per trade (notional = equity x 1% / 40%), at most 10 open, 0.20% round-trip cost, Bitget funding included

Binance listings are read from the public data.binance.vision archive (the Binance API is blocked on GitHub
runners): a symbol that was not in the archive at the previous run is new; its listing day is the date of its
first daily kline file. Coins not listed on Bitget by the entry day are logged as skipped.

    python scripts/paper_yeni_coin.py           # update state and trades
    python scripts/paper_yeni_coin.py --check   # print what would happen, save nothing
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

OUT_DIR = REPO / "forward" / "paper_yeni_coin"
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix={p}&delimiter=/&marker={m}"
SYM_PREFIX = "data/futures/um/daily/klines/"
STOP = 0.40
HOLD_DAYS = 14
RISK = 0.01
MAX_OPEN = 10
COST = 0.002
STOP_SLIP = 0.003
START_EQUITY = 10_000.0
DAY_MS = 86_400_000
FIELDS = ["symbol", "pair", "listed", "entry_day", "entry", "stop", "exit_day", "exit", "why",
          "funding_pct", "ret_pct", "pnl_usdt", "note"]


# ---------- Binance listings (public archive) ----------

def _get(url: str) -> str:
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "asgo-research"})
            return urllib.request.urlopen(req, timeout=40).read().decode()
        except Exception:  # noqa: BLE001 - retried, then empty
            time.sleep(1 + 2 * i)
    return ""


def _listing(prefix: str) -> list[str]:
    out, marker = [], ""
    while True:
        x = _get(S3.format(p=prefix, m=marker))
        if not x:
            raise RuntimeError(f"archive listing failed: {prefix}")
        out += re.findall(r"<Prefix>([^<]+)</Prefix>", x)[1:] + re.findall(r"<Key>([^<]+)</Key>", x)
        nm = re.search(r"<NextMarker>([^<]+)</NextMarker>", x)
        if "<IsTruncated>true" not in x or not nm:
            return out
        marker = nm.group(1)


def binance_symbols() -> set[str]:
    names = [p.rstrip("/").split("/")[-1] for p in _listing(SYM_PREFIX)]
    return {s for s in names if s.endswith("USDT") and "_" not in s}


def binance_first_day(symbol: str) -> date | None:
    keys = _listing(f"{SYM_PREFIX}{symbol}/1d/")
    days = sorted(re.findall(rf"{symbol}-1d-(\d{{4}}-\d{{2}}-\d{{2}})\.zip$", "\n".join(keys), re.M))
    return date.fromisoformat(days[0]) if days else None


# ---------- Bitget ----------

def bitget_pair(markets: dict, symbol: str) -> str | None:
    """Binance 'XYZUSDT' -> Bitget 'XYZ/USDT:USDT' (also tries without/with a 1000-style prefix)."""
    base = symbol[:-4]
    cands = [base, re.sub(r"^(1000000|10000|1000|1M)", "", base)]
    cands += ["1000" + cands[1]]
    for b in cands:
        p = f"{b}/USDT:USDT"
        if p in markets:
            return p
    return None


def daily(pub, pair: str, start: date, count: int) -> list[list[float]]:
    since = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp() * 1000)
    rows = pub.fetch_ohlcv(pair, "1d", since=since, limit=count)
    return [r for r in rows if r[0] >= since][:count]


def funding_sum(pub, pair: str, start_ms: int, end_ms: int) -> float:
    """Sum of funding rates in [start, end); positive = longs paid shorts. 0 if unavailable."""
    try:
        rows = pub.fetch_funding_rate_history(pair, since=start_ms, limit=100)
    except Exception as e:  # noqa: BLE001
        print(f"{pair}: no funding history ({e})")
        return 0.0
    return sum(float(r.get("fundingRate") or 0) for r in rows if start_ms <= int(r["timestamp"]) < end_ms)


# ---------- rules ----------

def manage(t: dict, candles: list[list[float]], today: date) -> None:
    """Applies stop / 14-day exit on closed daily candles starting at the entry day. Mutates t when closed."""
    stop = t["stop"]
    entry_day = date.fromisoformat(t["entry_day"])
    for k, (ts, o, h, _l, c, *_rest) in enumerate(candles[:HOLD_DAYS]):
        d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date()
        if d >= today:  # not closed yet
            return
        if o >= stop and k > 0:
            t.update(exit_day=d.isoformat(), exit=o * (1 + STOP_SLIP), why="stop_gap")
            return
        if h >= stop:
            t.update(exit_day=d.isoformat(), exit=stop * (1 + STOP_SLIP), why="stop")
            return
        if k == HOLD_DAYS - 1 or d >= entry_day + timedelta(days=HOLD_DAYS - 1):
            t.update(exit_day=d.isoformat(), exit=c, why="time")
            return


def close_out(t: dict, fund: float, equity: float) -> float:
    gross = 1 - t["exit"] / t["entry"]
    net = gross - COST + fund
    t["funding_pct"] = round(fund * 100, 3)
    t["ret_pct"] = round(net * 100, 3)
    t["pnl_usdt"] = round(t["notional"] * net, 2)
    return equity + t["pnl_usdt"]


def run_once(pub, state: dict, now: datetime, archive: set[str], first_day=binance_first_day) -> list[str]:
    msgs: list[str] = []
    today = now.date()
    trades = state.setdefault("trades", [])
    equity = state.setdefault("equity", START_EQUITY)
    known = set(state.get("known", []))
    pending = state.setdefault("pending", [])
    if not known:  # first run: everything already listed is history, track only what appears from now on
        state["known"] = sorted(archive)
        return msgs
    for s in sorted(archive - known):
        d = first_day(s)
        if d is None:
            continue
        pending.append({"symbol": s, "listed": d.isoformat()})
        known.add(s)
    state["known"] = sorted(known)

    still = []
    for p in pending:
        entry_day = date.fromisoformat(p["listed"]) + timedelta(days=1)
        if entry_day > today:
            still.append(p)
            continue
        if entry_day < today - timedelta(days=3):  # found too late (archive delay): skip, do not backfill
            trades.append({**p, "entry_day": entry_day.isoformat(), "why": "skipped", "note": "found too late"})
            continue
        pair = bitget_pair(pub.markets, p["symbol"])
        base = {**p, "pair": pair, "entry_day": entry_day.isoformat()}
        if pair is None:
            trades.append({**base, "why": "skipped", "note": "not on Bitget"})
            msgs.append(f"KÂĞIT atlandı: {p['symbol'][:-4]} (Bitget'te yok)")
            continue
        rows = daily(pub, pair, entry_day, 1)
        if not rows or datetime.fromtimestamp(rows[0][0] / 1000, tz=timezone.utc).date() != entry_day:
            trades.append({**base, "why": "skipped", "note": "no Bitget candle on entry day"})
            msgs.append(f"KÂĞIT atlandı: {p['symbol'][:-4]} (giriş gününde Bitget'te işlem yok)")
            continue
        n_open = sum(1 for t in trades if t.get("why") == "open")
        if n_open >= MAX_OPEN:
            trades.append({**base, "why": "skipped", "note": "max open"})
            continue
        entry = rows[0][1]
        t = {**base, "entry": entry, "stop": entry * (1 + STOP), "notional": round(equity * RISK / STOP, 2),
             "why": "open", "exit_day": None, "exit": None}
        trades.append(t)
        msgs.append(f"KÂĞIT short: {p['symbol'][:-4]} @ {entry:.6g} (Binance'te {p['listed']} listelendi; "
                    f"stop {t['stop']:.6g}, en geç 14 gün)")
    state["pending"] = still

    for t in trades:
        if t.get("why") != "open":
            continue
        entry_day = date.fromisoformat(t["entry_day"])
        manage(t, daily(pub, t["pair"], entry_day, HOLD_DAYS), today)
        if t.get("exit") is None:
            continue
        start = int(datetime(entry_day.year, entry_day.month, entry_day.day, tzinfo=timezone.utc).timestamp() * 1000)
        ed = date.fromisoformat(t["exit_day"])
        end = int(datetime(ed.year, ed.month, ed.day, tzinfo=timezone.utc).timestamp() * 1000) + DAY_MS
        equity = close_out(t, funding_sum(pub, t["pair"], start, end), equity)
        why = {"time": "14 gün doldu", "stop": "stop", "stop_gap": "stop (boşlukla)"}[t["why"]]
        msgs.append(f"KÂĞIT kapanış: {t['symbol'][:-4]} @ {t['exit']:.6g} ({why}), net {t['ret_pct']:+.2f}%")
    state["equity"] = round(equity, 2)
    state["last_run"] = now.isoformat()
    return msgs


def save(state: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "state.json").write_text(json.dumps(state, indent=1), encoding="utf-8")
    with (OUT_DIR / "trades.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(state.get("trades", []))


def notify(lines: list[str]) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not lines or not token:
        return
    from signals.dispatcher.telegram_client import TelegramClient, parse_chat_id

    text = "Yeni Coin Short (14 gün) — gerçek emir yok, kâğıt takip\n" + "\n".join(lines)
    targets = [parse_chat_id(os.environ.get("TELEGRAM_CHAT_ID"))]
    group = os.environ.get("TELEGRAM_GROUP_ID", "").strip()
    if group.lstrip("-").isdigit() and int(group) < 0:  # the one group the owner chose (rule 7)
        targets.append(int(group))
    for chat in targets:
        try:
            TelegramClient(token, chat, timeout=20).send_message(text)
        except Exception as e:  # noqa: BLE001 - a message problem must not stop the tracker
            print(f"telegram message not sent: {e}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="run against live data but save and send nothing")
    a = ap.parse_args()
    import bitget_demo as bd

    now = datetime.now(timezone.utc)
    pub = bd.public_exchange()
    pub.load_markets()
    archive = binance_symbols()
    path = OUT_DIR / "state.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"started": now.isoformat()}
    msgs = run_once(pub, state, now, archive)
    opened = [t for t in state.get("trades", []) if t.get("why") == "open"]
    closed = [t for t in state.get("trades", []) if t.get("ret_pct") is not None]
    print(f"paper yeni coin: archive {len(archive)} symbols, pending {len(state.get('pending', []))}, "
          f"open {len(opened)}, closed {len(closed)}, equity {state.get('equity')}")
    for m in msgs:
        print(m)
    if a.check:
        return
    save(state)
    notify(msgs)


if __name__ == "__main__":
    main()
