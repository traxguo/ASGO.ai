"""
Data diagnostics for the index/forex batch: compact per-day summaries of the 5m HistData bars (dev + val only),
committed by the workflow so the data can be inspected from the research container.

    python research/endeks_forex/diag.py
Writes results/2026-11-09_endeks_forex_batch/diag/daily_<NAME>.csv: UTC day, first/last bar time, bar count,
open/high/low/close, and the largest single 5m close-to-close move of the day.
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "user_data" / "efb5m"
OUT = ROOT / "results" / "2026-11-09_endeks_forex_batch" / "diag"
HOLDOUT = pd.Timestamp("2026-04-01", tz="UTC")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("NAS100", "SPX500", "GER40", "XAUUSD", "EURUSD"):
        path = DATA / f"{name}_5m.feather"
        if not path.exists():
            continue
        d = pd.read_feather(path)
        t = pd.DatetimeIndex(d["date"])
        t = t.tz_localize("UTC") if t.tz is None else t.tz_convert("UTC")
        d.index = t
        d = d[d.index < HOLDOUT]
        d["ret"] = np.log(d.close).diff().abs()
        d["tm"] = d.index.strftime("%H:%M")
        g = d.groupby(d.index.date)
        out = pd.DataFrame({
            "first": g.tm.first(), "last": g.tm.last(), "bars": g.close.size(),
            "open": g.open.first(), "high": g.high.max(), "low": g.low.min(), "close": g.close.last(),
            "max_5m_move_pct": g.ret.max() * 100,
        })
        out.index.name = "day"
        out.round(5).to_csv(OUT / f"daily_{name}.csv")
        print(name, len(out), "days", flush=True)


if __name__ == "__main__":
    main()
