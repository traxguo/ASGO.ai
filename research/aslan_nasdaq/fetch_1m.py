"""
Download HistData.com 1-minute bars (free, bid prices) for NAS100, EURUSD and XAUUSD and keep
them as 1-minute bars (Aslan v7 needs 1m). Same source and time handling as
research/forex/fetch_histdata.py: HistData times are EST without daylight saving (UTC-5),
converted to UTC there. Runs on a GitHub runner only (the research container cannot reach
the site); cached by actions/cache, never committed. Holdout months (2026-04+) are not fetched.

    python research/aslan_nasdaq/fetch_1m.py
Output: user_data/forex1m/<SYMBOL>_1m.feather with columns date (UTC), open, high, low, close.
"""

import os
import sys
from pathlib import Path

import pandas as pd
from histdata import download_hist_data as dl
from histdata.api import Platform as P, TimeFrame as TF

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "forex"))
from fetch_histdata import MONTHS_2026, SYMBOLS, YEARS, read_zip  # noqa: E402

OUT = ROOT / "user_data" / "forex1m"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "zips"
    tmp.mkdir(exist_ok=True)
    for sym, code in SYMBOLS.items():
        path = OUT / f"{sym}_1m.feather"
        if path.exists():
            print(f"{sym}: cached", flush=True)
            continue
        parts = []
        jobs = [(str(y), None) for y in YEARS] + [("2026", str(m)) for m in MONTHS_2026]
        for year, month in jobs:
            os.chdir(tmp)  # the package writes the zip into the working directory
            z = dl(year=year, month=month, pair=code, platform=P.GENERIC_ASCII, time_frame=TF.ONE_MINUTE)
            parts.append(read_zip(tmp / Path(z).name))
            print(f"  {sym} {year}{'-' + month if month else ''}: {len(parts[-1])} minutes", flush=True)
        m = pd.concat(parts).sort_index()
        m = m[~m.index.duplicated()]
        m.reset_index(names="date").to_feather(path)
        print(f"{sym}: {len(m)} bars {m.index[0]} -> {m.index[-1]}, last close {m.close.iloc[-1]}", flush=True)
        for f in tmp.glob("*.zip"):
            f.unlink()


if __name__ == "__main__":
    main()
