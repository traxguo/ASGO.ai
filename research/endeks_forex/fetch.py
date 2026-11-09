"""
Download HistData.com 1-minute bars (free, bid) for the index/forex batch (results/2026-11-09_endeks_forex_batch)
and save 5-minute bars. Same source and EST -> UTC handling as research/forex/fetch_histdata.py.
Runs on a GitHub runner (the research container cannot reach the site); cached, never committed.

Only 2020-01 .. 2026-03 is downloaded: the holdout window (2026-04 .. 2026-09) is never fetched.

    python research/endeks_forex/fetch.py
Output: user_data/efb5m/<NAME>_5m.feather with columns date (UTC bar start), open, high, low, close.
"""

import os
import sys
from pathlib import Path

import pandas as pd
from histdata import download_hist_data as dl
from histdata.api import Platform as P, TimeFrame as TF

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "forex"))
from fetch_histdata import read_zip  # noqa: E402

OUT = ROOT / "user_data" / "efb5m"
SYMBOLS = {
    "NAS100": "nsxusd", "SPX500": "spxusd", "GER40": "grxeur",
    "EURUSD": "eurusd", "GBPUSD": "gbpusd", "XAUUSD": "xauusd",
    "USDJPY": "usdjpy", "USDCAD": "usdcad", "USDSEK": "usdsek", "USDCHF": "usdchf",
}
YEARS = range(2020, 2026)
MONTHS_2026 = range(1, 4)  # validation ends 2026-03; holdout months are not downloaded


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "zips"
    tmp.mkdir(exist_ok=True)
    failed = []
    for name, code in SYMBOLS.items():
        path = OUT / f"{name}_5m.feather"
        if path.exists():
            print(f"{name}: cached", flush=True)
            continue
        parts = []
        jobs = [(str(y), None) for y in YEARS] + [("2026", str(m)) for m in MONTHS_2026]
        try:
            for year, month in jobs:
                os.chdir(tmp)  # the package writes the zip into the working directory
                z = dl(year=year, month=month, pair=code, platform=P.GENERIC_ASCII, time_frame=TF.ONE_MINUTE)
                parts.append(read_zip(tmp / Path(z).name))
        except Exception as e:  # noqa: BLE001 - a missing symbol is reported, the rest continues
            print(f"{name} ({code}): download failed at {year}{'-' + month if month else ''}: {e}", flush=True)
            failed.append(name)
            continue
        m = pd.concat(parts).sort_index()
        m = m[~m.index.duplicated()]
        m = m[m.index < pd.Timestamp("2026-04-01", tz="UTC")]
        b = m.resample("5min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        b.reset_index(names="date").to_feather(path)
        print(f"{name}: {len(b)} 5m bars {b.index[0]} -> {b.index[-1]}, last close {b.close.iloc[-1]}", flush=True)
        for f in tmp.glob("*.zip"):
            f.unlink()
    if failed:
        print(f"FAILED: {failed}", flush=True)


if __name__ == "__main__":
    main()
