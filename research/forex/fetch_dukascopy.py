"""
Download Dukascopy 1-minute BID and ASK candles and save 5-minute bid/ask bars per symbol.
Used only on a GitHub runner (the research container cannot reach Dukascopy); the data is
cached by actions/cache and never committed (2026-10-28, owner's forex question).

    python research/forex/fetch_dukascopy.py EURUSD XAUUSD USATECHIDXUSD --start 2020-01-01 --end 2026-10-01

Output: user_data/forex/<SYMBOL>_5m.feather with columns
date, bid_open, bid_high, bid_low, bid_close, ask_open, ask_high, ask_low, ask_close.
"""

import argparse
import lzma
import struct
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parents[2] / "user_data" / "forex"
POINT = {"EURUSD": 1e5, "XAUUSD": 1e3, "USATECHIDXUSD": 1e3}
URL = "https://datafeed.dukascopy.com/datafeed/{sym}/{y}/{m:02d}/{d:02d}/{side}_candles_min_1.bi5"


def fetch_day(sym: str, day: date, side: str) -> list[tuple]:
    url = URL.format(sym=sym, y=day.year, m=day.month - 1, d=day.day, side=side)  # month is 0-based
    for attempt in range(5):
        try:
            raw = urllib.request.urlopen(url, timeout=30).read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:  # no file for that day
                return []
            time.sleep(1 + attempt * 2)
        except Exception:  # noqa: BLE001 - retry network hiccups
            time.sleep(1 + attempt * 2)
    else:
        return []
    if not raw:
        return []
    data = lzma.decompress(raw)
    base = pd.Timestamp(day, tz="UTC")
    rows = []
    for off in range(0, len(data) - 23, 24):
        t, o, c, lo, hi, vol = struct.unpack(">5if", data[off:off + 24])
        if vol <= 0:
            continue
        p = POINT[sym]
        rows.append((base + pd.Timedelta(seconds=t), o / p, hi / p, lo / p, c / p))
    return rows


def bars(sym: str, days: list[date], side: str) -> pd.DataFrame:
    with ThreadPoolExecutor(16) as ex:
        parts = list(ex.map(lambda d: fetch_day(sym, d, side), days))
    df = pd.DataFrame([r for p in parts for r in p], columns=["date", "open", "high", "low", "close"]).set_index("date")
    return df.resample("5min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("symbols", nargs="+")
    ap.add_argument("--start", default="2020-01-01")
    ap.add_argument("--end", default="2026-10-01")
    a = ap.parse_args()
    d0, d1 = date.fromisoformat(a.start), date.fromisoformat(a.end)
    days = [d0 + timedelta(n) for n in range((d1 - d0).days) if (d0 + timedelta(n)).weekday() != 5]
    OUT.mkdir(parents=True, exist_ok=True)
    for sym in a.symbols:
        path = OUT / f"{sym}_5m.feather"
        if path.exists():
            print(f"{sym}: cached")
            continue
        bid, ask = bars(sym, days, "BID"), bars(sym, days, "ASK")
        df = bid.add_prefix("bid_").join(ask.add_prefix("ask_"), how="inner").reset_index()
        df.to_feather(path)
        spread = (df.ask_close - df.bid_close) / df.bid_close * 100
        print(f"{sym}: {len(df)} bars {df.date.iloc[0]} -> {df.date.iloc[-1]}, last bid {df.bid_close.iloc[-1]}, "
              f"median spread {spread.median():.4f}%")


if __name__ == "__main__":
    main()
