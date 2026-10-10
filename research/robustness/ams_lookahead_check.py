#!/usr/bin/env python3
"""
Lookahead check for ams_liquidity_mss: signals computed with data up to random cut
points must equal the values computed on the full history.

Usage: python research/robustness/ams_lookahead_check.py BTC [cuts]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from strategies.candidates import ams_liquidity_mss as ams  # noqa: E402

DATA = Path("user_data/data/binance/futures")
COLS = ["long_trigger", "short_trigger", "long_edge", "short_edge", "long_struct_stop", "short_struct_stop"]


def main():
    coin = sys.argv[1]
    cuts = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    rd = lambda t: pd.read_feather(DATA / f"{coin}_USDT_USDT-{t}-futures.feather")  # noqa: E731
    df, d1 = rd("15m"), rd("1d")
    df = df[df["date"] >= df["date"].iloc[-1] - pd.Timedelta(days=500)].reset_index(drop=True)
    full = ams.find_signals(df, ams.liquidity_levels(df, d1))
    n_sig = int((full.long_trigger != "").sum() + (full.short_trigger != "").sum())
    bad = 0
    for k in sorted(np.random.default_rng(1).integers(len(df) // 4, len(df) - 1, cuts)):
        end = df["date"].iloc[k] + ams.TF
        part_df = df.iloc[: k + 1]
        part_d1 = d1[d1["date"] + pd.Timedelta(days=1) <= end]
        part = ams.find_signals(part_df, ams.liquidity_levels(part_df, part_d1))
        a = full.iloc[: k + 1][COLS].reset_index(drop=True)
        b = part[COLS].reset_index(drop=True)
        same = (a == b) | (a.isna() & b.isna())
        if not same.all().all():
            bad += 1
            print("MISMATCH at", df["date"].iloc[k], same.all().to_dict())
    print(f"{coin}: {cuts} cut points, {bad} mismatches, {n_sig} signals")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
