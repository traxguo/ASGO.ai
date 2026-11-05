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

Second variant, tracked separately (forward/paper_yeni_coin_hedge/, cards/yeni_coin_short_btc_hedge.md,
supervisor decision 2026-11-04, no holdout run because this family already saw the holdout):
BTC-hedged new-coin short from research/neutral/newlist_portfolio.py (card rule N7 M30 S30):
- entry at the open of day D+8 (= close of day D+7, a week after listing): short the coin with 5% of equity
  (isolated 1x, the coin leg can lose at most its margin) and long BTC with another 5% of equity
- only if the coin is among the 100 most traded: research used Binance 30-day volume rank on day D+7; live we
  use Bitget instead (coin's average daily quote volume over its closed days D+1..D+7 vs the 100th largest
  24h quote volume of Bitget USDT perps), because the full Binance volume table is not available on the runner
- stop: coin trades 30% above the entry (first 1h candle whose high reaches it; fill max(hour open, stop) +0.2%)
- otherwise exit at the close of the 30th day (D+8 .. D+37); a coin that stops trading exits at its last close
- both legs leave on the same day; BTC leg exits at that day's close; at most 20 open; 0.20% round trip per leg;
  Bitget funding on both legs
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


# ---------- BTC-hedged variant (N7 M30 S30) ----------

H_OUT_DIR = REPO / "forward" / "paper_yeni_coin_hedge"
H_WAIT = 8          # entry day = listing day + 8 (open) = close of listing day + 7
H_HOLD = 30
H_STOP = 0.30
H_SLOT = 0.05
H_MAX_OPEN = 20
H_SLIP = 0.002
H_TOP = 100
BTC = "BTC/USDT:USDT"
H_FIELDS = ["symbol", "pair", "listed", "entry_day", "entry", "stop", "btc_entry", "notional", "exit_day", "exit",
            "btc_exit", "why", "coin_ret_pct", "btc_ret_pct", "ret_pct", "pnl_usdt", "note"]


def _day(ts: int) -> date:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date()


def _ms(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)


def top_volume_cut(pub) -> float:
    """24h quote volume of the H_TOP-th most traded Bitget USDT perpetual (0 if unknown -> no filter)."""
    try:
        tk = pub.fetch_tickers()
    except Exception as e:  # noqa: BLE001
        print(f"tickers unavailable ({e}); volume filter skipped")
        return 0.0
    vols = sorted((float(t.get("quoteVolume") or 0) for k, t in tk.items() if k.endswith("/USDT:USDT")), reverse=True)
    return vols[H_TOP - 1] if len(vols) >= H_TOP else 0.0


def hedge_manage(pub, t: dict, today: date) -> None:
    """Stop / 30-day / delisting exit on closed days. Mutates t when closed."""
    entry_day = date.fromisoformat(t["entry_day"])
    rows = [r for r in daily(pub, t["pair"], entry_day, H_HOLD) if _day(r[0]) < today]
    last = None
    for k, r in enumerate(rows):
        d = _day(r[0])
        if d != entry_day + timedelta(days=k):  # a missing day: the coin stopped trading
            break
        last = r
        if r[2] >= t["stop"]:
            hours = [h for h in pub.fetch_ohlcv(t["pair"], "1h", since=r[0], limit=24) if h[0] < r[0] + DAY_MS]
            hit = next((h for h in hours if h[2] >= t["stop"]), None)
            fill = max(hit[1], t["stop"]) if hit else max(r[1], t["stop"])
            t.update(exit_day=d.isoformat(), exit=fill * (1 + H_SLIP), why="stop")
            return
        if k == H_HOLD - 1:
            t.update(exit_day=d.isoformat(), exit=r[4], why="time")
            return
    gone = last is not None and _day(last[0]) < today - timedelta(days=2) and len(rows) < H_HOLD
    if gone or (last is None and today > entry_day + timedelta(days=2)):
        d = _day(last[0]) if last else entry_day
        t.update(exit_day=d.isoformat(), exit=last[4] if last else t["entry"], why="delist")


def hedge_close(pub, t: dict, equity: float) -> float:
    ed = date.fromisoformat(t["exit_day"])
    btc = daily(pub, BTC, ed, 1)
    t["btc_exit"] = btc[0][4] if btc and _day(btc[0][0]) == ed else t["btc_entry"]
    start, end = _ms(date.fromisoformat(t["entry_day"])), _ms(ed) + DAY_MS
    coin = max(1 - t["exit"] / t["entry"] + funding_sum(pub, t["pair"], start, end), -1.0)  # isolated 1x
    hedge = t["btc_exit"] / t["btc_entry"] - 1 - funding_sum(pub, BTC, start, end)
    pnl = t["notional"] * (coin + hedge - 2 * COST)
    t.update(coin_ret_pct=round(coin * 100, 3), btc_ret_pct=round(hedge * 100, 3),
             ret_pct=round(pnl / (2 * t["notional"]) * 100, 3), pnl_usdt=round(pnl, 2))
    return equity + pnl


def run_hedge(pub, state: dict, now: datetime, archive: set[str], first_day=binance_first_day,
              vol_cut=top_volume_cut) -> list[str]:
    msgs: list[str] = []
    today = now.date()
    trades = state.setdefault("trades", [])
    equity = state.setdefault("equity", START_EQUITY)
    known = set(state.get("known", []))
    pending = state.setdefault("pending", [])
    if not known:
        state["known"] = sorted(archive)
        return msgs
    for s in sorted(archive - known):
        d = first_day(s)
        if d is not None:
            pending.append({"symbol": s, "listed": d.isoformat()})
        known.add(s)
    state["known"] = sorted(known)

    still, cut = [], None
    for p in pending:
        entry_day = date.fromisoformat(p["listed"]) + timedelta(days=H_WAIT)
        if entry_day > today:
            still.append(p)
            continue
        if entry_day < today - timedelta(days=3):
            trades.append({**p, "entry_day": entry_day.isoformat(), "why": "skipped", "note": "found too late"})
            continue
        pair = bitget_pair(pub.markets, p["symbol"])
        base = {**p, "pair": pair, "entry_day": entry_day.isoformat()}
        if pair is None:
            trades.append({**base, "why": "skipped", "note": "not on Bitget"})
            continue
        rows = daily(pub, pair, date.fromisoformat(p["listed"]) + timedelta(days=1), H_WAIT)
        if not rows or _day(rows[-1][0]) != entry_day:
            trades.append({**base, "why": "skipped", "note": "no Bitget candle on entry day"})
            continue
        hist = [r[5] * r[4] for r in rows[:-1]]
        cut = vol_cut(pub) if cut is None else cut
        if len(hist) < 5 or sum(hist) / len(hist) < cut:
            trades.append({**base, "why": "skipped", "note": "not in top 100 by volume"})
            continue
        if sum(1 for t in trades if t.get("why") == "open") >= H_MAX_OPEN:
            trades.append({**base, "why": "skipped", "note": "max open"})
            continue
        btc = daily(pub, BTC, entry_day, 1)
        if not btc or _day(btc[0][0]) != entry_day:
            still.append(p)
            continue
        entry = rows[-1][1]
        t = {**base, "entry": entry, "stop": entry * (1 + H_STOP), "btc_entry": btc[0][1],
             "notional": round(equity * H_SLOT, 2), "why": "open", "exit_day": None, "exit": None}
        trades.append(t)
        msgs.append(f"KÂĞIT short {p['symbol'][:-4]} @ {entry:.6g} + long BTC @ {btc[0][1]:.6g} "
                    f"({p['listed']} listelendi; stop {t['stop']:.6g}, en geç 30 gün)")
    state["pending"] = still

    for t in trades:
        if t.get("why") != "open":
            continue
        hedge_manage(pub, t, today)
        if t.get("exit") is None:
            continue
        equity = hedge_close(pub, t, equity)
        why = {"time": "30 gün doldu", "stop": "stop", "delist": "coin listeden çıktı"}[t["why"]]
        msgs.append(f"KÂĞIT kapanış: {t['symbol'][:-4]} @ {t['exit']:.6g} ({why}), çift net {t['ret_pct']:+.2f}%")
    state["equity"] = round(equity, 2)
    state["last_run"] = now.isoformat()
    return msgs


def save(state: dict, out_dir: Path = OUT_DIR, fields: list[str] = FIELDS) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "state.json").write_text(json.dumps(state, indent=1), encoding="utf-8")
    with (out_dir / "trades.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(state.get("trades", []))


def notify(lines: list[str], title: str = "Yeni Coin Short (14 gün) — gerçek emir yok, kâğıt takip") -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not lines or not token:
        return
    from signals.dispatcher.telegram_client import TelegramClient, parse_chat_id

    text = title + "\n" + "\n".join(lines)
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
    if not a.check:
        save(state)
        notify(msgs)

    # second variant: BTC-hedged, separate state; a failure here must not undo the 14-day log above
    try:
        hpath = H_OUT_DIR / "state.json"
        hstate = json.loads(hpath.read_text(encoding="utf-8")) if hpath.exists() else {"started": now.isoformat()}
        hmsgs = run_hedge(pub, hstate, now, archive)
        hop = sum(1 for t in hstate.get("trades", []) if t.get("why") == "open")
        print(f"paper yeni coin hedge: pending {len(hstate.get('pending', []))}, open {hop}, equity {hstate.get('equity')}")
        for m in hmsgs:
            print(m)
        if not a.check:
            save(hstate, H_OUT_DIR, H_FIELDS)
            notify(hmsgs, "Yeni Coin Short + BTC long (30 gün) — gerçek emir yok, kâğıt takip")
    except Exception as e:  # noqa: BLE001
        print(f"hedge variant failed: {e}")
        if a.check:
            raise


if __name__ == "__main__":
    main()
