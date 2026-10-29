"""
Download HistData.com 1-minute bars (free, bid prices) and save 5-minute bars per symbol.
Runs on a GitHub runner (the research container cannot reach the site); cached, never committed.
Dukascopy was tried first but throttles the runner (25-35 s per request, then HTTP 429).

    python research/forex/fetch_histdata.py

HistData times are EST without daylight saving (UTC-5). Bars are bid only, so scan.py adds a
fixed round-trip cost per instrument instead of a recorded spread.
Output: user_data/forex/<SYMBOL>_5m.feather with columns date (UTC), open, high, low, close.
"""

import io
import os
import zipfile
from pathlib import Path

import pandas as pd
from histdata import download_hist_data as dl
from histdata.api import Platform as P, TimeFrame as TF

OUT = Path(__file__).resolve().parents[2] / "user_data" / "forex"
SYMBOLS = {"EURUSD": "eurusd", "XAUUSD": "xauusd", "NAS100": "nsxusd"}
YEARS = range(2020, 2026)
MONTHS_2026 = range(1, 4)  # validation ends 2026-03; the holdout months are not downloaded


def read_zip(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        name = [n for n in z.namelist() if n.endswith(".csv")][0]
        raw = z.read(name).decode()
    df = pd.read_csv(io.StringIO(raw), sep=";", header=None, names=["t", "open", "high", "low", "close", "vol"])
    df["date"] = pd.to_datetime(df.t, format="%Y%m%d %H%M%S") + pd.Timedelta(hours=5)
    return df.set_index(pd.DatetimeIndex(df.date).tz_localize("UTC"))[["open", "high", "low", "close"]]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "zips"
    tmp.mkdir(exist_ok=True)
    for sym, code in SYMBOLS.items():
        path = OUT / f"{sym}_5m.feather"
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
        b = m.resample("5min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        b.reset_index(names="date").to_feather(path)
        print(f"{sym}: {len(b)} bars {b.index[0]} -> {b.index[-1]}, last close {b.close.iloc[-1]}", flush=True)


if __name__ == "__main__":
    main()
