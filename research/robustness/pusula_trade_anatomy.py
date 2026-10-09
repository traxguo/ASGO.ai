"""
Trade anatomy for a pusula backtest (development data only):
- bootstrap: 95% range of the average R and of the max drawdown when trade order / sample changes
- concentration: share of total R from the best 5 / 10 trades
- giveback: best open profit (MFE, in R) vs the realised R for trend-exit trades

  python research/robustness/pusula_trade_anatomy.py <backtest zip> <strategy>
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from freqtrade.data.btanalysis import load_backtest_stats  # noqa: E402

from make_report import trade_r  # noqa: E402

STOP_RE = re.compile(r"stop=([0-9.eE+-]+)")


def max_dd_pct(rs: np.ndarray, risk: float = 0.01) -> float:
    eq = np.cumprod(1 + risk * rs)
    return float(((np.maximum.accumulate(eq) - eq) / np.maximum.accumulate(eq)).max())


def main() -> None:
    zip_path, strat = sys.argv[1], sys.argv[2]
    trades = load_backtest_stats(zip_path)["strategy"][strat]["trades"]
    rows = []
    for t in trades:
        r = trade_r(t)
        entry = next(o for o in t["orders"] if o["ft_is_entry"])["safe_price"]
        stop = float(STOP_RE.search(t["enter_tag"]).group(1))
        risk = abs(entry - stop)
        best = (t["max_rate"] - entry) if not t["is_short"] else (entry - t["min_rate"])
        rows.append({**r, "mfe_r": best / risk, "exit": t["exit_reason"], "pair": t["pair"]})
    df = pd.DataFrame(rows)
    rs = df["r"].to_numpy()
    rng = np.random.default_rng(7)
    means, dds = [], []
    for _ in range(5000):
        sample = rng.choice(rs, size=len(rs), replace=True)
        means.append(sample.mean())
        dds.append(max_dd_pct(sample))
    srt = np.sort(rs)[::-1]
    print(f"{strat}: {len(rs)} trades, mean {rs.mean():+.3f}R, total {rs.sum():+.1f}R")
    print(f"bootstrap mean R 2.5-97.5%: {np.percentile(means, 2.5):+.3f} .. {np.percentile(means, 97.5):+.3f}; "
          f"P(mean<=0) = {np.mean(np.array(means) <= 0):.3f}")
    print(f"bootstrap max DD (1% risk) median {np.median(dds)*100:.1f}%, 95th pct {np.percentile(dds, 95)*100:.1f}%")
    print(f"best 5 trades = {srt[:5].sum():+.1f}R, best 10 = {srt[:10].sum():+.1f}R of {rs.sum():+.1f}R; "
          f"total without best 10: {srt[10:].sum():+.1f}R")
    ex = df[df["exit"] == "exit_signal"]
    if len(ex):
        print(f"trend exits: {len(ex)}, avg best open profit {ex.mfe_r.mean():.2f}R, avg realised {ex.r.mean():.2f}R, "
              f"avg given back {(ex.mfe_r - ex.r).mean():.2f}R")
    print(df.groupby("exit")["r"].agg(["count", "mean", "sum"]).round(2).to_string())
    print("losers that were >= 1R in profit first:", int(((df.r < 0) & (df.mfe_r >= 1)).sum()),
          "| >= 2R:", int(((df.r < 0) & (df.mfe_r >= 2)).sum()))


if __name__ == "__main__":
    main()
