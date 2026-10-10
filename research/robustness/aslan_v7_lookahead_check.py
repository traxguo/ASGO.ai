#!/usr/bin/env python3
"""
Lookahead check for aslan_liquidity v7 (5m MSS -> 1m FVG/iFVG): 1m signals and
stops computed with data up to random cut points must equal the full-history values.

Usage: python research/robustness/aslan_v7_lookahead_check.py BTC [cuts]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from strategies.candidates import aslan_liquidity_v3 as v3  # noqa: E402
from strategies.candidates import aslan_liquidity_v7 as v7  # noqa: E402

DATA = Path("user_data/data/binance/futures")
COLS = ["long_trigger", "short_trigger", "long_struct_stop", "short_struct_stop"]


def compute(m1, m5, h1, h4, d1):
    return v7.find_entries_1m(m1, v7.mss_events(m5, v3.all_levels(h1, h4, d1), 144), 60)


def main():
    coin = sys.argv[1]
    cuts = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    rd = lambda t: pd.read_feather(DATA / f"{coin}_USDT_USDT-{t}-futures.feather")  # noqa: E731
    m1, m5, h1, h4, d1 = rd("1m"), rd("5m"), rd("1h"), rd("4h"), rd("1d")
    start = m1["date"].iloc[-1] - pd.Timedelta(days=120)  # keep it fast
    m1 = m1[m1["date"] >= start].reset_index(drop=True)
    m5 = m5[m5["date"] >= start - pd.Timedelta(days=5)].reset_index(drop=True)
    full = compute(m1, m5, h1, h4, d1)
    bad = 0
    for k in sorted(np.random.default_rng(0).integers(len(m1) // 4, len(m1) - 1, cuts)):
        end = m1["date"].iloc[k] + pd.Timedelta(minutes=1)
        cut = lambda x, m: x[x["date"] + pd.Timedelta(minutes=m) <= end]  # noqa: E731
        part = compute(m1.iloc[: k + 1], cut(m5, 5), cut(h1, 60), cut(h4, 240), cut(d1, 1440))
        a = full.iloc[: k + 1][COLS].reset_index(drop=True)
        b = part[COLS].reset_index(drop=True)
        same = (a == b) | (a.isna() & b.isna())
        if not same.all().all():
            bad += 1
            print("MISMATCH at", m1["date"].iloc[k], same.all().to_dict())
    print(f"{coin} v7: {cuts} cut points, {bad} mismatches, {int((full.long_trigger != '').sum() + (full.short_trigger != '').sum())} signals")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
