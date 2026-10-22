"""
Queue item 13 (diagnostic, no rule change): split PusulaV2NoBe trades by the age
of the coin's daily long regime at entry.

Trend age = number of consecutive CLOSED daily candles, ending with the last
daily candle that closed at or before the trade's entry time, whose regime score
(same `regime_score` as the strategy) is >= +1. No lookahead: a daily candle
dated D counts only if D + 1 day <= entry time.

  python research/robustness/pusula_trend_age.py <backtest zip> [<backtest zip> ...]
      [--strategy PusulaV2NoBe] [--datadir user_data/data/binance/futures] [--csv out.csv]
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from freqtrade.data.btanalysis import load_backtest_stats  # noqa: E402

from make_report import trade_r  # noqa: E402
from strategies.candidates.pusula import regime_score  # noqa: E402

BUCKETS = [(0, 10, "0-10"), (11, 30, "11-30"), (31, 90, "31-90"), (91, 10**6, "90+")]


def daily_age(pair: str, datadir: Path) -> pd.DataFrame:
    """Per daily candle: close time and run length of score >= +1 ending at that candle."""
    f = datadir / f"{pair.replace('/', '_').replace(':', '_')}-1d-futures.feather"
    d = pd.read_feather(f).sort_values("date").reset_index(drop=True)
    up = (regime_score(d) >= 1).to_numpy()
    age = np.zeros(len(up), dtype=int)
    run = 0
    for i, u in enumerate(up):
        run = run + 1 if u else 0
        age[i] = run
    return pd.DataFrame({"close_time": d["date"] + pd.Timedelta(days=1), "age": age,
                         "first_date": d["date"].iloc[0]})


def bucket(age: int) -> str:
    for lo, hi, name in BUCKETS:
        if lo <= age <= hi:
            return name
    return "?"


def trades_with_age(zip_path: str, strategy: str, datadir: Path) -> pd.DataFrame:
    trades = load_backtest_stats(zip_path)["strategy"][strategy]["trades"]
    cache, rows = {}, []
    for t in trades:
        pair = t["pair"]
        if pair not in cache:
            cache[pair] = daily_age(pair, datadir)
        d = cache[pair]
        entry = pd.Timestamp(t["open_date"])
        known = d[d["close_time"] <= entry]
        age = int(known["age"].iloc[-1]) if len(known) else 0
        rows.append({"pair": pair, "open_date": entry, "age": age, "bucket": bucket(age),
                     "r": trade_r(t)["r"], "profit_abs": t["profit_abs"]})
    return pd.DataFrame(rows)


def summary(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for _, _, name in BUCKETS + [(0, 0, "all")]:
        g = df if name == "all" else df[df["bucket"] == name]
        if g.empty:
            out.append({"bucket": name, "trades": 0})
            continue
        r = g["r"].sort_values(ascending=False)
        out.append({"bucket": name, "trades": len(g), "win_rate_%": round(100 * (r > 0).mean(), 1),
                    "avg_R": round(r.mean(), 2), "median_R": round(r.median(), 2), "total_R": round(r.sum(), 2),
                    "avg_R_ex_best": round(r.iloc[1:].mean(), 2) if len(r) > 1 else np.nan,
                    "best_R": round(r.iloc[0], 2)})
    return pd.DataFrame(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("zips", nargs="+")
    ap.add_argument("--strategy", default="PusulaV2NoBe")
    ap.add_argument("--datadir", default=str(ROOT / "user_data/data/binance/futures"))
    ap.add_argument("--csv")
    a = ap.parse_args()
    allrows = []
    for z in a.zips:
        df = trades_with_age(z, a.strategy, Path(a.datadir))
        df.insert(0, "source", Path(z).name)
        allrows.append(df)
        print(f"\n{Path(z).name} / {a.strategy}: {len(df)} trades, total {df['r'].sum():.2f}R")
        print(summary(df).to_string(index=False))
    if a.csv:
        pd.concat(allrows).to_csv(a.csv, index=False)


if __name__ == "__main__":
    main()
