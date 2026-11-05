"""
Download HistData.com 1-minute bars (free, bid) for stock indices, 2020-01 .. 2026-09, for the frozen
Nasdaq rules test on other indices (research/aslan_nasdaq/indices.py). Same source and EST -> UTC
handling as research/forex/fetch_histdata.py. Runs on a GitHub runner; cached, never committed.

    python research/aslan_nasdaq/fetch_indices.py
Output: user_data/indices1m/<NAME>_1m.feather with columns date (UTC), open, high, low, close.
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

OUT = ROOT / "user_data" / "indices1m"
SYMBOLS = {"NAS100": "nsxusd", "SPX500": "spxusd", "GER40": "grxeur", "UK100": "ukxgbp", "JPN225": "jpxjpy"}
YEARS = range(2020, 2026)
MONTHS_2026 = range(1, 10)  # through the 2026-04..09 window; nothing later


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "zips"
    tmp.mkdir(exist_ok=True)
    for name, code in SYMBOLS.items():
        path = OUT / f"{name}_1m.feather"
        if path.exists():
            print(f"{name}: cached", flush=True)
            continue
        parts = []
        jobs = [(str(y), None) for y in YEARS] + [("2026", str(m)) for m in MONTHS_2026]
        try:
            for year, month in jobs:
                os.chdir(tmp)
                z = dl(year=year, month=month, pair=code, platform=P.GENERIC_ASCII, time_frame=TF.ONE_MINUTE)
                parts.append(read_zip(tmp / Path(z).name))
        except Exception as e:  # noqa: BLE001 - a missing symbol is reported and skipped
            print(f"{name} ({code}): download failed at {year}{'-' + month if month else ''}: {e}", flush=True)
            continue
        m = pd.concat(parts).sort_index()
        m = m[~m.index.duplicated()]
        m.reset_index(names="date").to_feather(path)
        print(f"{name}: {len(m)} bars {m.index[0]} -> {m.index[-1]}, last close {m.close.iloc[-1]}", flush=True)
        for f in tmp.glob("*.zip"):
            f.unlink()


if __name__ == "__main__":
    main()
