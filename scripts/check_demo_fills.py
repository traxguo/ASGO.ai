"""
Checks every closed Bitget DEMO trade of Fitil Avcisi / Derin Fitil against the REAL market (Binance USDⓈ-M
1m candles from data.binance.vision). The Bitget demo account runs its own order book, and its prices can
differ from the real market; a demo fill at a price the real market never traded is not evidence.

For each closed demo trade (forward/bitget_fitil/state.json):
- real_fill: did a real 1m low between 15 minutes before the demo fill and the fill minute reach the fill price?
- real_exit: the real open price of the minute the demo bot sold (market order)
- real_ret_pct: what the trade would have made at real prices with the same fees (0 when it would not fill)
Days whose Binance file is not published yet (today) are left as "pending".

    python scripts/check_demo_fills.py   # writes dashboard/canli/demo_gercek_kontrol.csv
"""

import csv
import io
import json
import math
import sys
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "forward" / "bitget_fitil" / "state.json"
OUT = REPO / "dashboard" / "canli" / "demo_gercek_kontrol.csv"
CACHE = Path.home() / ".cache" / "asgo_1m"
URL = "https://data.binance.vision/data/futures/um/daily/klines/{s}/1m/{s}-1m-{d}.zip"
SPOT_URL = "https://data.binance.vision/data/spot/daily/klines/{s}/1m/{s}-1m-{d}.zip"  # when a futures day is missing
FIELDS = ["key", "pair", "mode", "fill_time", "fill_price", "exit_time", "demo_exit", "demo_ret_pct",
          "real_low", "real_fill", "real_exit", "real_ret_pct", "status", "note"]


def day_rows(sym: str, day: str) -> dict[int, list[float]] | None:
    """{open_time_ms: [open, high, low, close]} for one UTC day, None when Binance has not published it."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{sym}-1m-{day}.zip"
    if not path.is_file():
        for url in (URL, SPOT_URL):  # Binance skipped some futures days (2026-10-28); spot is within ~0.1%
            try:
                with urllib.request.urlopen(url.format(s=sym, d=day), timeout=60) as r:
                    path.write_bytes(r.read())
                break
            except Exception as e:  # 404 for a day that is not out yet
                print(f"{sym} {day}: not available at {url.split('/data/')[1].split('/')[0]} ({e})")
        else:
            return None
    with zipfile.ZipFile(path) as z:
        text = z.read(z.namelist()[0]).decode()
    out = {}
    for row in csv.reader(io.StringIO(text)):
        if not row or not row[0].isdigit():
            continue
        ts = int(row[0])
        out[ts // 1000 if ts > 10**14 else ts] = [float(x) for x in row[1:5]]  # spot files use microseconds
    return out


def candles(sym: str, start: datetime, end: datetime):
    rows = {}
    d = start.date()
    while d <= end.date():
        got = day_rows(sym, d.isoformat())
        if got is None:
            return None
        rows.update(got)
        d += timedelta(days=1)
    a, b = int(start.timestamp() * 1000), int(end.timestamp() * 1000)
    return {k: v for k, v in rows.items() if a <= k <= b}


def minute(t: datetime) -> datetime:
    return t.replace(second=0, microsecond=0)


def check(key: str, t: dict) -> dict:
    sym = t["pair"].split("/")[0] + "USDT"
    fill_t = datetime.fromisoformat(t["fill_time"])
    exit_t = datetime.fromisoformat(t["exit_time"])
    fill = float(t["fill_price"])
    demo_exit = t.get("exit_price")
    demo_ok = demo_exit is not None and not (isinstance(demo_exit, float) and math.isnan(demo_exit))
    notional = fill * float(t["amount"])
    fee_pct = float(t.get("fees_usdt") or 0) / notional * 100
    if not demo_ok:
        fee_pct *= 2  # only the entry fee is known; assume the same again for the exit
    row = {"key": key, "pair": t["pair"], "mode": t.get("mode", ""), "fill_time": t["fill_time"],
           "fill_price": fill, "exit_time": t["exit_time"], "demo_exit": demo_exit if demo_ok else "",
           "demo_ret_pct": t.get("ret_pct") if demo_ok else ""}
    around = candles(sym, minute(fill_t) - timedelta(minutes=15), minute(fill_t))
    at_exit = candles(sym, minute(exit_t), minute(exit_t))
    if around is None or at_exit is None:
        return {**row, "status": "pending", "note": "Binance 1m data for this day is not published yet"}
    low = min(v[2] for v in around.values())
    real_exit = next(iter(at_exit.values()))[0]
    filled = low <= fill
    ret = (real_exit / fill - 1) * 100 - fee_pct if filled else 0.0
    note = ("real market traded the demo fill price" if filled else
            f"real market never traded {fill:g} (lowest {low:g}); on real prices this trade would not exist")
    return {**row, "real_low": low, "real_fill": "yes" if filled else "no", "real_exit": real_exit,
            "real_ret_pct": round(ret, 3), "status": "checked", "note": note}


def main() -> None:
    trades = json.loads(STATE.read_text(encoding="utf-8"))["trades"]
    rows = [check(k, t) for k, t in sorted(trades.items(), key=lambda kv: kv[1].get("fill_time") or "")
            if t.get("status") == "closed"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r["pair"], r["fill_time"][:16], r.get("real_fill", "-"), r.get("demo_ret_pct"), r.get("real_ret_pct", "-"), r["status"])


if __name__ == "__main__":
    sys.exit(main())
