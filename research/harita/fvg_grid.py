"""
FVG grid on Nasdaq: all FVG variants tested at once with a multiple-testing bar (no criteria changed after results).
Timeframes 5m/15m/1h/4h x size x entry type x age x trend filter x horizon = 288 cells.
Pre-registered in results/2026-11-26_nasdaq_fvg_grid/README.md.

    python research/harita/fvg_grid.py [--data DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scan  # noqa: E402

run, efb = scan.run, scan.efb
OUT = run.ROOT / "results" / "2026-11-26_nasdaq_fvg_grid"
MIN = run.MIN
TFS = {"5m": 1, "15m": 3, "1h": 12, "4h": 48}          # TF bar = this many 5m bars
SIZES = {"all": 0.0, "mid": 0.10, "big": 0.25}          # gap size in daily ATR
ENTRIES = ("respect", "mid", "inverse")
AGES = {"fresh": 6, "old": 24}                          # max age in TF bars
TRENDS = ("none", "with")
HORIZONS = (12, 48)
T_MIN, MIN_DAYS, MIN_EDGE = 3.7, 200, 0.02


def tf_bars(x: efb.Inst, mult: int, ny_day: np.ndarray):
    """TF bars built from 5m bars: blocks of `mult` 5m bars in clock time (4h blocks start 17:00 New York)."""
    if mult == 1:
        return x.h, x.lo, np.arange(len(x.c))
    if mult == 48:
        ny = pd.DatetimeIndex(x.start).tz_localize("UTC").tz_convert(run.NY).tz_localize(None) + pd.Timedelta(hours=7)
        key = ny.asi8 // (4 * 60 * MIN)
    else:
        key = x.start // (mult * 5 * MIN)
    g = pd.DataFrame({"k": key, "h": x.h, "l": x.lo, "i": np.arange(len(x.c))}).groupby("k", sort=True).agg(
        h=("h", "max"), l=("l", "min"), last=("i", "max"))
    return g.h.to_numpy(), g.l.to_numpy(), g["last"].to_numpy()


def events(x: efb.Inst, atr: np.ndarray, mult: int, min_size: float, entry: str, age: int, ny_day):
    H_, L_, last = tf_bars(x, mult, ny_day)
    h, lo, c = x.h, x.lo, x.c
    n = len(c)
    ks, ss = [], []
    j = np.arange(2, len(H_))
    for s, sel in ((1, j[L_[j] > H_[j - 2]]), (-1, j[H_[j] < L_[j - 2]])):
        for q in sel:
            bot, top = (H_[q - 2], L_[q]) if s > 0 else (H_[q], L_[q - 2])
            f = int(last[q])                       # 5m index at which the gap is known
            a = atr[f]
            if not np.isfinite(a) or (top - bot) < min_size * a:
                continue
            mid = (bot + top) / 2
            stop_at = min(f + age * mult, n - 1)
            for k in range(f + 1, stop_at + 1):
                if entry == "inverse":
                    if (s > 0 and c[k] < bot) or (s < 0 and c[k] > top):
                        ks.append(k)
                        ss.append(-s)
                        break
                    continue
                lvl = top if (s > 0 and entry == "respect") else bot if entry == "respect" else mid
                touched = lo[k] <= lvl if s > 0 else h[k] >= lvl
                if touched:
                    held = c[k] > lvl if s > 0 else c[k] < lvl
                    if held:
                        ks.append(k)
                        ss.append(s)
                    break                          # first touch only
    k = np.array(ks, np.int64)
    s = np.array(ss, np.int64)
    o = np.argsort(k, kind="stable")
    return k[o], s[o]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=efb.DATA)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    x = efb.load("NAS100", a.data)
    assert x.start.max() < efb.HOLDOUT.value, "holdout data must not be loaded"
    lv = run.Levels(x)
    ctx = scan.context(x, lv)
    per = efb.period_of(x.start + 5 * MIN)
    print(f"NAS100 5m bars {len(x.c)}", flush=True)
    outs, bases = {}, {}
    for H in HORIZONS:
        r = scan.outcomes(x, ctx, H)
        dev_bar = (per == "dev") & np.isfinite(r)
        sm = pd.Series(r[dev_bar]).groupby(ctx["slot"][dev_bar]).mean()
        outs[H], bases[H] = r, sm.reindex(range(48)).fillna(0.0).to_numpy()[ctx["slot"]]
    rows, survivors = [], []
    for tf, size, entry, age in itertools.product(TFS, SIZES, ENTRIES, AGES):
        k, s = events(x, ctx["atr"], TFS[tf], SIZES[size], entry, AGES[age], ctx["tday"])
        keep = np.isfinite(ctx["atr"][k]) & np.isfinite(ctx["trend"][k])
        k, s = k[keep], s[keep]
        print(tf, size, entry, age, len(k), flush=True)
        for trend in TRENDS:
            m0 = np.ones(len(k), bool) if trend == "none" else (s * ctx["trend"][k]) > 0
            for H in HORIZONS:
                r, base = outs[H], bases[H]
                edge = s * (r[k] - base[k])
                raw = s * r[k]
                cost = 1e-4 * x.c[k] / ctx["atr"][k]
                md = m0 & (per[k] == "dev")
                st = scan.cell_stats(edge[md], ctx["tday"][k[md]], ctx["year"][k[md]])
                row = {"tf": tf, "size": size, "entry": entry, "age": age, "trend": trend, "horizon_bars": H,
                       **{f"dev_{q}": v for q, v in st.items()}}
                ok = (st["n_days"] >= MIN_DAYS and np.isfinite(st["t"]) and abs(st["t"]) >= T_MIN
                      and st["years_same_sign"] >= 4 and abs(st["mean"]) >= MIN_EDGE)
                row["dev_survives"] = bool(ok)
                if ok:
                    d = int(np.sign(st["mean"]))
                    mv = m0 & (per[k] == "val")
                    sv = scan.cell_stats(d * edge[mv], ctx["tday"][k[mv]], ctx["year"][k[mv]])
                    net2 = d * raw[mv] - 2 * cost[mv]
                    row.update({"direction": d, **{f"val_{q}": v for q, v in sv.items()},
                                "val_net2x_mean": float(np.nanmean(net2)) if mv.any() else np.nan})
                    row["val_pass"] = bool(sv["n_days"] >= 30 and np.isfinite(sv["t"]) and sv["t"] >= 2.0
                                           and row["val_net2x_mean"] > 0)
                    survivors.append(row)
                rows.append(row)
    cells = pd.DataFrame(rows)
    cells.round(5).to_csv(a.out / "cells.csv", index=False)
    pd.DataFrame(survivors).round(5).to_csv(a.out / "survivors.csv", index=False)
    print(f"cells tested: {len(cells)}, dev survivors: {len(survivors)}, "
          f"val pass: {sum(r.get('val_pass', False) for r in survivors)}")
    print(f"t sd {cells.dev_t.std():.3f}, |t|>2: {(cells.dev_t.abs() > 2).sum()}, |t|>3: {(cells.dev_t.abs() > 3).sum()}")
    top = cells.reindex(cells.dev_t.abs().sort_values(ascending=False).index).head(20)
    print(top[["tf", "size", "entry", "age", "trend", "horizon_bars", "dev_n_days", "dev_mean", "dev_t",
               "dev_years_same_sign", "dev_survives"]].round(3).to_string())
    if survivors:
        print(pd.DataFrame(survivors).round(3).to_string())


if __name__ == "__main__":
    main()
