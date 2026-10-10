#!/usr/bin/env python3
"""
Lookahead check for aslan_liquidity (Freqtrade's lookahead-analysis cannot
replay its 1d/4h level logic). For random cut points, signals computed with
data only up to the cut must equal the signals computed on the full history.

Usage: python research/robustness/aslan_lookahead_check.py BTC 1h 12 [cuts]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from strategies.candidates import aslan_liquidity as al  # noqa: E402

DATA = Path("user_data/data/binance/futures")
COLS = ["long_trigger", "short_trigger", "long_struct_stop", "short_struct_stop", "bias"]


def compute(df, h4, d1, win):
    lv = pd.concat([al.htf_levels(d1, 1440, True), al.htf_levels(h4, 240)]).sort_values("avail", kind="stable")
    sig = al.find_signals(df, lv, win)
    tf = df["date"].iloc[1] - df["date"].iloc[0]
    b = al.daily_bias(d1)
    m = pd.merge_asof(pd.DataFrame({"avail": (df["date"] + tf).astype("datetime64[ns, UTC]")}), b, on="avail")
    sig["bias"] = m["bias"].fillna(0).to_numpy()
    return sig


def main():
    coin, tf, win = sys.argv[1], sys.argv[2], int(sys.argv[3])
    cuts = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    rd = lambda t: pd.read_feather(DATA / f"{coin}_USDT_USDT-{t}-futures.feather")  # noqa: E731
    df, h4, d1 = rd(tf), rd("4h"), rd("1d")
    full = compute(df, h4, d1, win)
    rng = np.random.default_rng(0)
    bad = 0
    for k in sorted(rng.integers(len(df) // 4, len(df) - 1, cuts)):
        cut = df["date"].iloc[k]
        end = cut + (df["date"].iloc[1] - df["date"].iloc[0])  # close of candle k
        part = compute(df.iloc[: k + 1], h4[h4["date"] + pd.Timedelta("4h") <= end], d1[d1["date"] + pd.Timedelta("1D") <= end], win)
        a = full.iloc[: k + 1][COLS].reset_index(drop=True)
        b = part[COLS].reset_index(drop=True)
        same = (a == b) | (a.isna() & b.isna())
        if not same.all().all():
            bad += 1
            print("MISMATCH at", cut, same.all().to_dict())
    print(f"{coin} {tf}: {cuts} cut points, {bad} mismatches")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
