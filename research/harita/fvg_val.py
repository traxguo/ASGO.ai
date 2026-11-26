"""
Single declared follow-up of the FVG grid (results/2026-11-26_nasdaq_fvg_grid/README.md, addendum): the strongest
development cell (1h FVG, all sizes, mid-touch respect, age up to 24 1h bars, no trend filter, 1h horizon) is scored
once on validation (2025-01 .. 2026-03). Not part of the original pre-registration; a pass makes it a candidate only.

    python research/harita/fvg_val.py [--data DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fvg_grid as g  # noqa: E402

scan, run, efb = g.scan, g.run, g.efb


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=efb.DATA)
    ap.add_argument("--out", type=Path, default=g.OUT)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    x = efb.load("NAS100", a.data)
    assert x.start.max() < efb.HOLDOUT.value, "holdout data must not be loaded"
    lv = run.Levels(x)
    ctx = scan.context(x, lv)
    per = efb.period_of(x.start + 5 * g.MIN)
    H = 12
    r = scan.outcomes(x, ctx, H)
    dev_bar = (per == "dev") & np.isfinite(r)
    sm = pd.Series(r[dev_bar]).groupby(ctx["slot"][dev_bar]).mean()
    base = sm.reindex(range(48)).fillna(0.0).to_numpy()[ctx["slot"]]
    k, s = g.events(x, ctx["atr"], g.TFS["1h"], g.SIZES["all"], "mid", g.AGES["old"], ctx["tday"])
    keep = np.isfinite(ctx["atr"][k]) & np.isfinite(ctx["trend"][k])
    k, s = k[keep], s[keep]
    edge = s * (r[k] - base[k])
    cost = 1e-4 * x.c[k] / ctx["atr"][k]
    rows = []
    for p in ("dev", "val"):
        m = per[k] == p
        st = scan.cell_stats(edge[m], ctx["tday"][k[m]], ctx["year"][k[m]])
        # tradable view: first event per day, raw signed move minus 2x cost
        df = pd.DataFrame({"d": ctx["tday"][k[m]], "net2": s[m] * r[k[m]] - 2 * cost[m]}).dropna()
        first = df.groupby("d", sort=False).first()
        rows.append({"period": p, **st, "net2x_mean": first.net2.mean(),
                     "net2x_t": first.net2.mean() / (first.net2.std(ddof=1) / np.sqrt(len(first)))})
    res = pd.DataFrame(rows)
    v = res[res.period == "val"].iloc[0]
    res["val_pass"] = bool(v.n_days >= 30 and v.t >= 2.0 and v.net2x_mean > 0)
    res.round(5).to_csv(a.out / "followup_1h_mid.csv", index=False)
    print(res.round(4).to_string())


if __name__ == "__main__":
    main()
