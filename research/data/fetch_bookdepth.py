"""
Download Binance USD-M daily bookDepth archives (data.binance.vision) and keep only
5-minute features, so raw zips never touch the disk.

bookDepth = cumulative resting size within +-1..5% of mid, snapshot every ~30-60 s.
Feature per 5 min (mean of snapshots inside the bucket, labelled by bucket START):
  imb1 = (bid1 - ask1) / (bid1 + ask1)   (+-1% band, notional)
  imb5 = same for +-5% band
  liq1 = bid1 + ask1 notional (USDT)
A bucket labelled T is fully known at T+5min; consumers must shift accordingly.

Usage: python research/data/fetch_bookdepth.py BTC ETH SOL --start 2023-01-01 --end 2026-10-01
Output: user_data/data/bookdepth/<COIN>-5m.feather
"""
import argparse, io, os, time, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

URL = "https://data.binance.vision/data/futures/um/daily/bookDepth/{s}/{s}-bookDepth-{d}.zip"
OUT = "user_data/data/bookdepth"


def one_day(sym: str, day: str):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(URL.format(s=sym, d=day), timeout=60) as r:
                raw = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    else:
        return None
    z = zipfile.ZipFile(io.BytesIO(raw))
    df = pd.read_csv(z.open(z.namelist()[0]))
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    p = df.pivot_table(index="timestamp", columns="percentage", values="notional", aggfunc="last")
    f = pd.DataFrame(index=p.index)
    f["imb1"] = (p[-1] - p[1]) / (p[-1] + p[1])
    f["imb5"] = (p[-5] - p[5]) / (p[-5] + p[5])
    f["liq1"] = p[-1] + p[1]
    return f.resample("5min").mean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("coins", nargs="+")
    ap.add_argument("--start", default="2023-01-01")
    ap.add_argument("--end", default="2026-10-01")
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    days = [d.strftime("%Y-%m-%d") for d in pd.date_range(a.start, a.end, freq="D", inclusive="left")]
    for coin in a.coins:
        sym = f"{coin}USDT"
        with ThreadPoolExecutor(a.workers) as ex:
            parts = [x for x in ex.map(lambda d: one_day(sym, d), days) if x is not None]
        out = pd.concat(parts).sort_index()
        out = out[~out.index.duplicated()]
        out.reset_index(names="date").to_feather(f"{OUT}/{coin}-5m.feather")
        print(coin, len(parts), "days", out.index.min(), out.index.max(), flush=True)


if __name__ == "__main__":
    main()
