#!/usr/bin/env python3
"""
Lookahead check for fvg_ob: setup columns computed with 3m data up to random cut
points must equal the values computed on the full history (both entry modes).

Usage: python research/robustness/fvg_ob_lookahead_check.py BTC [cuts] [days]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from strategies.retired import fvg_ob  # noqa: E402

DATA = Path("user_data/data/binance/futures")


def main():
    coin = sys.argv[1]
    cuts = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    df = pd.read_feather(DATA / f"{coin}_USDT_USDT-3m-futures.feather")
    start = pd.Timestamp("2023-01-01", tz="UTC")
    df = df[(df["date"] >= start - pd.Timedelta(days=5)) & (df["date"] < start + pd.Timedelta(days=days))].reset_index(drop=True)
    bad, n_sig = 0, 0
    for mode in ("mid", "edge"):
        full = fvg_ob.find_setups(df, mode)
        n_sig += int(full["long_rr_ok"].sum() + full["short_rr_ok"].sum())
        for k in sorted(np.random.default_rng(1).integers(len(df) // 4, len(df) - 1, cuts)):
            part = fvg_ob.find_setups(df.iloc[: k + 1].reset_index(drop=True), mode)
            a = full.iloc[: k + 1].reset_index(drop=True)
            same = (a == part) | (a.isna() & part.isna())
            if not same.all().all():
                bad += 1
                print("MISMATCH", mode, df["date"].iloc[k], [c for c, ok in same.all().items() if not ok])
    print(f"{coin}: {cuts} cut points x 2 modes, {bad} mismatches, {n_sig} signals")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
