"""
Learning-model test on Nasdaq 5m: can a gradient-boosted tree model combine many situations (FVG, iFVG, bands,
levels, session, trend, volatility, recent moves) into a 1-hour direction call that survives costs out of sample?
Procedure, features, fixed model settings and the pass bar are pre-registered in
results/2026-11-26_nasdaq_ogrenen/README.md.

    python research/ogrenen/ml.py [--data DIR] [--out DIR]

Walk-forward: the model never sees the year it is tested on. Validation (2025-01 .. 2026-03) is scored once, only
for a side that passes the development walk-forward.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harita"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "aslan_5dk"))
import run  # noqa: E402
import scan  # noqa: E402

efb = run.efb
OUT = run.ROOT / "results" / "2026-11-26_nasdaq_ogrenen"
MIN = run.MIN
H = 12                         # 1 hour
STEP = 3                       # a sample every 15 minutes
TEST_YEARS = (2022, 2023, 2024)
Q = 0.10                       # trade the top / bottom 10% of predicted probabilities
MODEL = dict(max_depth=3, learning_rate=0.05, max_iter=200, l2_regularization=1.0, min_samples_leaf=200,
             random_state=20261126)


def recent_event(n: int, k: np.ndarray, s: np.ndarray, within: int) -> np.ndarray:
    """Side (+1/-1) of the latest event within the last `within` bars (0 if none), known at each bar."""
    last_side = np.zeros(n)
    last_k = np.full(n, -10**9)
    last_side[k] = s
    last_k[k] = k
    idx = np.maximum.accumulate(np.where(last_k > -10**9, np.arange(n), -1))
    out = np.where(idx >= 0, last_side[np.clip(idx, 0, None)], 0.0)
    age = np.arange(n) - idx
    return np.where((idx >= 0) & (age < within), out, 0.0)


def features(x: efb.Inst) -> tuple[pd.DataFrame, dict]:
    lv = run.Levels(x)
    ctx = scan.context(x, lv)
    n = len(x.c)
    c, h, lo = x.c, x.h, x.lo
    atr = ctx["atr"]
    f = {}
    for m in (1, 3, 6, 12, 24, 48, 96):
        prev = np.r_[np.full(m, np.nan), c[:-m]]
        f[f"ret_{m}"] = (c - prev) / atr
    for m in (24, 48):
        hh = pd.Series(h).rolling(m).max().to_numpy()
        ll = pd.Series(lo).rolling(m).min().to_numpy()
        f[f"pos_{m}"] = (c - ll) / np.where(hh - ll > 0, hh - ll, np.nan)
        f[f"width_{m}"] = (hh - ll) / atr
    day = pd.Series(lv.tday)
    dh = pd.Series(h).groupby(day).cummax().to_numpy()
    dl = pd.Series(lo).groupby(day).cummin().to_numpy()
    f["dist_dayhigh"] = (dh - c) / atr
    f["dist_daylow"] = (c - dl) / atr
    f["dist_pdh"] = (lv.pdh - c) / atr
    f["dist_pdl"] = (c - lv.pdl) / atr
    shi, slo, _ = scan.session_levels(x, lv)
    f["dist_sess_hi"] = (shi - c) / atr
    f["dist_sess_lo"] = (c - slo) / atr
    r1 = np.r_[np.nan, np.diff(np.log(c))]
    v12 = pd.Series(r1).rolling(12).std().to_numpy()
    v96 = pd.Series(r1).rolling(96).std().to_numpy()
    f["vol_ratio"] = v12 / v96
    f["atr_pct"] = atr / c
    f["trend"] = ctx["trend"]
    f["hivol"] = ctx["hivol"]
    f["sess"] = ctx["sess"].astype(float)
    f["slot"] = ctx["slot"].astype(float)
    f["weekday"] = pd.DatetimeIndex(x.start).tz_localize("UTC").tz_convert(run.NY).weekday.to_numpy().astype(float)
    pd_group = lv.tday
    ev = {
        "band": scan.ev_band(x, 12, 48),
        "pd_fade": scan.ev_level(x, lv.pdh, lv.pdl, pd_group, "fade"),
        "pd_break": scan.ev_level(x, lv.pdh, lv.pdl, pd_group, "break"),
        "sess_fade": scan.ev_level(x, shi, slo, _sess_gid(x, lv), "fade"),
        "sess_break": scan.ev_level(x, shi, slo, _sess_gid(x, lv), "break"),
        "fvg_respect": scan.ev_fvg(x, "respect"),
        "ifvg": scan.ev_fvg(x, "inverse"),
    }
    for name, (k, s) in ev.items():
        f[f"ev_{name}_3"] = recent_event(n, k, s, 3)
        f[f"ev_{name}_12"] = recent_event(n, k, s, 12)
    return pd.DataFrame(f), ctx


def level_features(x: efb.Inst, idx: np.ndarray, atr: np.ndarray) -> pd.DataFrame:
    """Per-sample "identity" of nearby FVGs and levels: which one might matter (distance, size, age, untaken)."""
    lv, htf = run.Levels(x), run.HTF(x)
    c, h, lo = x.c, x.h, x.lo
    n = len(c)
    bull5 = np.zeros(n, bool)
    bear5 = np.zeros(n, bool)
    bull5[2:] = lo[2:] > h[:-2]
    bear5[2:] = h[2:] < lo[:-2]
    last_bull = np.maximum.accumulate(np.where(bull5, np.arange(n), -1))
    last_bear = np.maximum.accumulate(np.where(bear5, np.arange(n), -1))
    out = np.full((len(idx), 16), np.nan)
    for row, k in enumerate(idx.tolist()):
        e, a = c[k], atr[k]
        for col, s_ in ((0, 1), (4, -1)):            # +1: bullish HTF FVGs (support), -1: bearish (resistance)
            bot, top, formed, t = htf.fvg[s_]
            q0 = np.searchsorted(t, x.start[k] - run.HTF_FVG_AGE)
            best = None
            cnt = 0
            for q in range(q0, len(t)):
                if t[q] > x.start[k]:
                    break
                f = int(formed[q])
                if f >= k:
                    continue
                if s_ > 0 and run.rq(htf.cmin, f + 1, k, min) < bot[q]:
                    continue                       # support broken by a close
                if s_ < 0 and run.rq(htf.cmax, f + 1, k, max) > top[q]:
                    continue
                cnt += 1
                d = (e - top[q]) if s_ > 0 else (bot[q] - e)
                if best is None or abs(d) < abs(best[0]):
                    best = (d, top[q] - bot[q], (x.start[k] - t[q]) / (60 * MIN))
            out[row, col] = cnt
            if best:
                out[row, col + 1] = best[0] / a
                out[row, col + 2] = best[1] / a
                out[row, col + 3] = best[2]
        up, dn = lv.candidates(int(k), True), lv.candidates(int(k), False)
        out[row, 8] = len(up)
        out[row, 9] = (min(up) - e) / a if up else np.nan
        out[row, 10] = len(dn)
        out[row, 11] = (e - max(dn)) / a if dn else np.nan
        for col, lastf, s_ in ((12, last_bull, 1), (14, last_bear, -1)):
            i = lastf[k]
            if i >= 2:
                size = (lo[i] - h[i - 2]) if s_ > 0 else (lo[i - 2] - h[i])
                out[row, col] = size / a
                out[row, col + 1] = k - i
    cols = ["htf_sup_n", "htf_sup_dist", "htf_sup_size", "htf_sup_age_h",
            "htf_res_n", "htf_res_dist", "htf_res_size", "htf_res_age_h",
            "liq_up_n", "liq_up_dist", "liq_dn_n", "liq_dn_dist",
            "fvg5_bull_size", "fvg5_bull_age", "fvg5_bear_size", "fvg5_bear_age"]
    return pd.DataFrame(out, columns=cols)


def _sess_gid(x, lv):
    return scan.session_levels(x, lv)[2]


def run_test(x: efb.Inst, out: Path) -> None:
    X, ctx = features(x)
    n = len(x.c)
    end = x.start + 5 * MIN
    mins = (end // MIN) % 1440
    r = scan.outcomes(x, ctx, H)                      # 1h move in daily-ATR units
    cost = 1e-4 * x.c / ctx["atr"]
    year = pd.DatetimeIndex(end).tz_localize("UTC").year.to_numpy()
    per = efb.period_of(end)
    ok = (np.arange(n) % STEP == 0) & (mins >= 6 * 60) & (mins <= 19 * 60) & np.isfinite(r) & np.isfinite(ctx["atr"])
    idx = np.flatnonzero(ok)
    y = (r[idx] > 0).astype(int)
    L = level_features(x, idx, ctx["atr"])
    Xs = np.hstack([X.iloc[idx].to_numpy(float), L.to_numpy(float)])
    yr, pr = year[idx], per[idx]
    print(f"samples {len(idx)}, features {Xs.shape[1]}", flush=True)

    def trades(test_mask, model, thr):
        p = model.predict_proba(Xs[test_mask])[:, 1]
        side = np.where(p >= thr[1], 1, np.where(p <= thr[0], -1, 0))
        ii = idx[test_mask]
        # non-overlapping: at most one open trade, each lasts H bars
        rows, free = [], -1
        for q in np.flatnonzero(side != 0):
            k = ii[q]
            if k <= free:
                continue
            free = k + H
            rows.append((k, side[q], side[q] * r[k] - cost[k], side[q] * r[k] - 2 * cost[k], year[k]))
        return pd.DataFrame(rows, columns=["k", "side", "net1", "net2", "year"])

    def fit(train_mask):
        m = HistGradientBoostingClassifier(**MODEL)
        m.fit(Xs[train_mask], y[train_mask])
        p_tr = m.predict_proba(Xs[train_mask])[:, 1]
        return m, (np.quantile(p_tr, Q), np.quantile(p_tr, 1 - Q))

    wf = []
    for ty in TEST_YEARS:
        m, thr = fit((yr < ty) & (pr == "dev"))
        t = trades((yr == ty) & (pr == "dev"), m, thr)
        t["test_year"] = ty
        wf.append(t)
        print(ty, len(t), t.groupby("side").net1.mean().round(4).to_dict(), flush=True)
    wf = pd.concat(wf, ignore_index=True)
    wf.to_csv(out / "walkforward_trades.csv", index=False)

    rows = []
    for side, name in ((1, "long"), (-1, "short")):
        g = wf[wf.side == side]
        yearly = g.groupby("test_year").net2.mean()
        t_stat = g.net2.mean() / (g.net2.std(ddof=1) / np.sqrt(len(g))) if len(g) > 1 else np.nan
        passed = bool(len(g) >= 100 and g.net2.mean() > 0 and t_stat >= 2.5 and (yearly > 0).sum() >= 2)
        row = {"unit": name, "dev_trades": len(g), "dev_net1_mean_atr": g.net1.mean(), "dev_net2_mean_atr": g.net2.mean(),
               "dev_t_net2": t_stat, "dev_win_pct": (g.net1 > 0).mean() * 100,
               **{f"net2_{yy}": yearly.get(yy, np.nan) for yy in TEST_YEARS}, "dev_pass": passed}
        if passed:
            m, thr = fit(pr == "dev")
            v = trades(pr == "val", m, thr)
            v = v[v.side == side]
            tv = v.net2.mean() / (v.net2.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else np.nan
            row.update({"val_trades": len(v), "val_net2_mean_atr": v.net2.mean(), "val_t_net2": tv,
                        "val_pass": bool(len(v) >= 30 and v.net2.mean() > 0 and tv >= 2.0)})
        rows.append(row)
    res = pd.DataFrame(rows)
    res.round(4).to_csv(out / "result.csv", index=False)
    print(res.round(4).to_string())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=efb.DATA)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    x = efb.load("NAS100", a.data)
    assert x.start.max() < efb.HOLDOUT.value, "holdout data must not be loaded"
    print(f"NAS100 5m bars {len(x.c)}", flush=True)
    run_test(x, a.out)


if __name__ == "__main__":
    main()
