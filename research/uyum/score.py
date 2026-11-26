"""
Confluence ("uyum puanı") test on Nasdaq 5m: trade only when many criteria point the same way.
Criteria, thresholds, stop/target and the pass bar are pre-registered in results/2026-11-26_nasdaq_uyum/README.md.

    python research/uyum/score.py [--data DIR] [--out DIR] [--sets 2000]

Look-ahead discipline: every criterion at bar k uses bars <= k only (daily values from completed days, swings only
after confirmation, higher-timeframe FVGs only after their bar closed); entry is the close of k.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harita"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "aslan_5dk"))
import run  # noqa: E402
import scan  # noqa: E402

efb = run.efb
OUT = run.ROOT / "results" / "2026-11-26_nasdaq_uyum"
MIN = run.MIN
RECENT = 12                  # "recent" = within the last hour
STOP_ATR, TP_ATR = 0.30, 0.60
NEAR_ATR = 0.30              # higher-timeframe FVG support/resistance this close (daily ATR)
SWING_TOL = 0.05             # swing level "tested" when the wick came within 0.05 ATR
THRESHOLDS = {"main": 4, "score3": 3, "score5": 5, "score6": 6}
CRITERIA = ["trend_d", "trend_4h", "htf_fvg", "sweep", "swing_held", "fvg_respect", "band_break"]


def recent(n: int, k: np.ndarray, s: np.ndarray, side: int, within: int) -> np.ndarray:
    """True at bar b if an event of `side` happened in (b - within, b]."""
    m = np.zeros(n, bool)
    kk = k[s == side]
    if len(kk) == 0:
        return m
    last = np.full(n, -10**9)
    last[kk] = kk
    last = np.maximum.accumulate(last)
    return (np.arange(n) - last) < within


def htf_fvg_near(x, htf, k: int, side: int, atr: float) -> bool:
    """An unbroken 1h/4h FVG on the trade's side (support below for long) within NEAR_ATR of price, or price in it."""
    bot, top, formed, t = htf.fvg[side]
    e = x.c[k]
    q0 = np.searchsorted(t, x.start[k] - run.HTF_FVG_AGE)
    for q in range(q0, len(t)):
        if t[q] > x.start[k]:
            break
        f = int(formed[q])
        if f >= k:
            continue
        if side > 0:
            if run.rq(htf.cmin, f + 1, k, min) < bot[q]:
                continue
            if bot[q] <= e and e - top[q] <= NEAR_ATR * atr:
                return True
        else:
            if run.rq(htf.cmax, f + 1, k, max) > top[q]:
                continue
            if top[q] >= e and bot[q] - e <= NEAR_ATR * atr:
                return True
    return False


def swing_held(x, lv, k: int, side: int, atr: float) -> bool:
    """Latest confirmed 1h swing low (long) was tested in the last hour and price closes back above it."""
    vals, lasts, confs, tstart = lv.h1_lo if side > 0 else lv.h1_hi
    p = np.searchsorted(confs, k, side="right") - 1          # confs are increasing with time
    if p < 0:
        return False
    v = vals[p]
    a = max(k - RECENT + 1, 0)
    if side > 0:
        return bool(x.lo[a:k + 1].min() <= v + SWING_TOL * atr and x.c[k] > v)
    return bool(x.h[a:k + 1].max() >= v - SWING_TOL * atr and x.c[k] < v)


def build(x: efb.Inst) -> pd.DataFrame:
    lv, htf = run.Levels(x), run.HTF(x)
    ctx = scan.context(x, lv)
    n = len(x.c)
    atr = ctx["atr"]
    shi, slo, sgid = scan.session_levels(x, lv)
    ev = {
        "sweep": [scan.ev_level(x, lv.pdh, lv.pdl, lv.tday, "fade"), scan.ev_level(x, shi, slo, sgid, "fade")],
        "fvg_respect": [scan.ev_fvg(x, "respect")],
        "band_break": [scan.ev_band(x, 12, 48)],
    }
    rec = {}
    fresh = {1: np.zeros(n, bool), -1: np.zeros(n, bool)}
    for name, lst in ev.items():
        for side in (1, -1):
            m = np.zeros(n, bool)
            for k, s in lst:
                m |= recent(n, k, s, side, RECENT if name != "fvg_respect" else 3)
                fresh[side][k[s == side]] = True
            rec[(name, side)] = m
    sma4h = pd.Series(x.c).rolling(20 * 48, min_periods=10 * 48).mean().to_numpy()
    rows = []
    for side in (1, -1):
        for k in np.flatnonzero(fresh[side]).tolist():
            a = atr[k]
            if not np.isfinite(a) or not np.isfinite(ctx["trend"][k]) or not np.isfinite(sma4h[k]):
                continue
            sc = {
                "trend_d": ctx["trend"][k] == side,
                "trend_4h": (x.c[k] - sma4h[k]) * side > 0,
                "htf_fvg": htf_fvg_near(x, htf, k, side, a),
                "sweep": rec[("sweep", side)][k],
                "swing_held": swing_held(x, lv, k, side, a),
                "fvg_respect": rec[("fvg_respect", side)][k],
                "band_break": rec[("band_break", side)][k],
            }
            rows.append({"k": k, "side": side, "atr": a, **{c: bool(v) for c, v in sc.items()},
                         "score": int(sum(sc.values()))})
    df = pd.DataFrame(rows).sort_values(["k", "side"], kind="stable").reset_index(drop=True)
    # a bar where both sides qualify is ambiguous: dropped
    both = df.groupby("k").side.transform("nunique") > 1
    return df[~both].reset_index(drop=True), lv


def run_threshold(x, lv, cand: pd.DataFrame, name: str, primary: bool, thr: int, funnel: dict) -> pd.DataFrame:
    end = x.start + 5 * MIN
    mins = (end // MIN) % 1440
    ny = pd.DatetimeIndex(end).tz_localize("UTC").tz_convert(run.NY)
    ny_min = (ny.hour * 60 + ny.minute).to_numpy()
    f = {"candidates": 0, "score": 0, "window": 0, "ny_open": 0, "busy": 0, "risk": 0, "trades": 0}
    out, free_after = [], -1
    for row in cand.itertuples(index=False):
        k, side = int(row.k), int(row.side)
        f["candidates"] += 1
        if row.score < thr:
            f["score"] += 1
            continue
        if not (6 * 60 <= mins[k] <= 19 * 60):
            f["window"] += 1
            continue
        if 9 * 60 + 30 <= ny_min[k] <= 9 * 60 + 45:
            f["ny_open"] += 1
            continue
        if k <= free_after:
            f["busy"] += 1
            continue
        e = x.c[k]
        stop = e - side * STOP_ATR * row.atr
        tp = e + side * TP_ATR * row.atr
        risk = abs(stop - e) / e
        if risk < run.RISK_MIN:                  # stop is ATR-based, so no upper cap
            f["risk"] += 1
            continue
        j, px, why = run.simulate(x.start, x.o, x.h, x.lo, x.c, k, side, float(stop), float(tp), run.MAX_HOLD)
        free_after = j
        f["trades"] += 1
        out.append({"cell": name, "primary": primary, "side": side, "k": k, "j": j, "t_in": int(end[k]),
                    "t_out": int(x.start[j] + 5 * MIN), "entry": e, "stop": stop, "tp": tp, "exit": px,
                    "why": ("stop", "hedef", "süre")[why], "risk": risk, "tp_d": abs(tp / e - 1),
                    "gross": side * (px / e - 1), "score": row.score})
    funnel[name] = f
    tr = pd.DataFrame(out)
    if tr.empty:
        return tr
    nights = efb.nights(tr.t_in.to_numpy(), tr.t_out.to_numpy())
    tr["swap"] = [run.SWAP[int(s)] * nn / 365 for s, nn in zip(tr.side, nights)]
    for m in (1, 2):
        tr[f"r{m}"] = (tr.gross - m * (run.COST + tr.swap)) / tr.risk
    tr["period"] = efb.period_of(tr.t_in.to_numpy())
    return tr


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=efb.DATA)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--sets", type=int, default=2000)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    x = efb.load("NAS100", a.data)
    assert x.start.max() < efb.HOLDOUT.value, "holdout data must not be loaded"
    print(f"NAS100 5m bars {len(x.c)}", flush=True)
    cand, lv = build(x)
    per_c = efb.period_of(x.start[cand.k.to_numpy()])
    print("candidates", len(cand), "score counts (dev):",
          cand[per_c == "dev"].score.value_counts().sort_index().to_dict(), flush=True)
    # how often each criterion is true, development only (information)
    cand[per_c == "dev"][CRITERIA].mean().round(3).to_csv(a.out / "criteria_share.csv")
    funnel, parts = {}, []
    for name, thr in THRESHOLDS.items():
        parts.append(run_threshold(x, lv, cand, name, name == "main", thr, funnel))
        print(name, funnel[name], flush=True)
    tr = pd.concat([p for p in parts if not p.empty], ignore_index=True)
    pd.DataFrame(funnel).T.to_csv(a.out / "funnel.csv")
    summ = run.summarise(tr)
    summ.round(4).to_csv(a.out / "summary.csv", index=False)

    rng = np.random.default_rng(20261127)
    end = x.start + 5 * MIN
    mins = (end // MIN) % 1440
    main_tr = tr[tr.primary]
    pool = np.flatnonzero((mins >= 6 * 60) & (mins <= 19 * 60) & (efb.period_of(end) == "dev"))
    pool = pool[pool < len(x.c) - 300]
    rows = []
    for unit, s in (("long", 1), ("short", -1)):
        g = main_tr[(main_tr.side == s) & (main_tr.period == "dev")]
        real = g.r1.mean() if len(g) else np.nan
        means = np.full(a.sets, np.nan)
        if len(g):
            for q in range(a.sets):
                idx = rng.choice(pool, size=len(g)).astype(np.int64)
                means[q] = run.control_mean(x.start, x.o, x.h, x.lo, x.c, idx, np.full(len(g), s, np.int64),
                                            g.risk.to_numpy(float), g.tp_d.to_numpy(float), run.MAX_HOLD, 1,
                                            run.COST, run.SWAP[1], run.SWAP[-1])
        p = (1 + np.sum(means >= real)) / (a.sets + 1) if len(g) else np.nan
        sel = summ[(summ.cell == "main") & (summ.unit == unit)]
        ok, fails = run.verdict(sel.iloc[0], p) if len(sel) else (False, "işlem yok")
        rows.append({"unit": unit, "p_dev": round(float(p), 4), "real_dev_r": round(float(real), 4),
                     "ctrl_mean_r": round(float(np.nanmean(means)), 4) if len(g) else np.nan,
                     "pass": ok, "failed": fails})
        print(f"{unit}: real dev {real:.4f}R, p {p:.4f} -> {'PASS' if ok else 'FAIL: ' + fails}")
    pd.DataFrame(rows).to_csv(a.out / "pass.csv", index=False)
    yearly = main_tr.assign(year=pd.to_datetime(main_tr.t_in, utc=True).dt.year).groupby(["year", "side"]).r1.agg(
        ["count", "mean", "sum"]).round(3)
    yearly.to_csv(a.out / "yearly.csv")
    print(summ.round(3).to_string())


if __name__ == "__main__":
    main()
