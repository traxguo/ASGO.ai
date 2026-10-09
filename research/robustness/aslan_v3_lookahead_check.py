#!/usr/bin/env python3
"""
Lookahead check for aslan_liquidity v3 (see aslan_lookahead_check.py): signals,
stops and trend computed with data up to random cut points must equal the
values computed on the full history.

Usage: python research/robustness/aslan_v3_lookahead_check.py BTC 15m 48 [cuts]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from strategies.candidates import aslan_liquidity_v3 as v3  # noqa: E402

DATA = Path("user_data/data/binance/futures")
COLS = ["long_trigger", "short_trigger", "long_kind", "short_kind", "long_struct_stop", "short_struct_stop", "trend_4h", "trend_1h"]


def compute(df, h1, h4, d1, win):
    sig = v3.find_signals_v3(df, v3.all_levels(h1, h4, d1), win)
    tf = df["date"].iloc[1] - df["date"].iloc[0]
    base = pd.DataFrame({"avail": (df["date"] + tf).astype("datetime64[ns, UTC]")})
    for name, src, mins in (("trend_4h", h4, 240), ("trend_1h", h1, 60)):
        sig[name] = pd.merge_asof(base, v3.structure_trend(src, mins), on="avail")["trend"].fillna(0).to_numpy()
    return sig


def main():
    coin, tf, win = sys.argv[1], sys.argv[2], int(sys.argv[3])
    cuts = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    rd = lambda t: pd.read_feather(DATA / f"{coin}_USDT_USDT-{t}-futures.feather")  # noqa: E731
    df, h1, h4, d1 = rd(tf), rd("1h"), rd("4h"), rd("1d")
    # keep it fast: last ~2 years
    start = df["date"].iloc[-1] - pd.Timedelta(days=700)
    df = df[df["date"] >= start].reset_index(drop=True)
    full = compute(df, h1, h4, d1, win)
    step = df["date"].iloc[1] - df["date"].iloc[0]
    bad = 0
    for k in sorted(np.random.default_rng(0).integers(len(df) // 4, len(df) - 1, cuts)):
        end = df["date"].iloc[k] + step
        cut = lambda x, m: x[x["date"] + pd.Timedelta(minutes=m) <= end]  # noqa: E731
        part = compute(df.iloc[: k + 1], cut(h1, 60), cut(h4, 240), cut(d1, 1440), win)
        a = full.iloc[: k + 1][COLS].reset_index(drop=True)
        b = part[COLS].reset_index(drop=True)
        same = (a == b) | (a.isna() & b.isna())
        if not same.all().all():
            bad += 1
            print("MISMATCH at", df["date"].iloc[k], same.all().to_dict())
    print(f"{coin} {tf}: {cuts} cut points, {bad} mismatches")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
