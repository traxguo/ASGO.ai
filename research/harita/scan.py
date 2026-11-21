"""
Nasdaq 5m "edge map": measure which situations are followed by a one-sided move, before writing any rule.
Procedure, cells and the elimination bar are pre-registered in results/2026-11-21_nasdaq_harita/README.md.

    python research/harita/scan.py [--data DIR] [--out DIR]

Look-ahead discipline: every event and condition at bar k uses only bars <= k (daily values from completed days);
outcomes use bars k+1 .. k+H. Validation numbers are computed only for cells that survive the development scan.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "aslan_5dk"))
import run  # noqa: E402

efb = run.efb
OUT = run.ROOT / "results" / "2026-11-21_nasdaq_harita"
MIN = run.MIN
HORIZONS = (12, 48)             # 1 hour, 4 hours of 5m bars
T_MIN = 3.7                     # ~Bonferroni for 400 two-sided tests at 5%
MIN_DAYS = 200
MIN_EDGE = 0.02                 # in daily ATR units (~7 points at 24000 with ATR ~1.5%)
FVG_AGE = 24
TOUCH = 0.15
P40, P150 = 0.0017, 0.0062
SESSIONS = ("asia", "london", "nyam", "nypm")


# ------------------------------------------------------------------ context

def context(x: efb.Inst, lv: run.Levels) -> dict:
    n = len(x.c)
    tday = lv.tday
    d = pd.DataFrame({"d": tday, "h": x.h, "l": x.lo, "c": x.c}).groupby("d").agg(
        h=("h", "max"), l=("l", "min"), c=("c", "last"))
    prev_c = d.c.shift(1)
    tr = np.maximum(d.h - d.l, np.maximum((d.h - prev_c).abs(), (d.l - prev_c).abs()))
    atr = tr.rolling(14).mean().shift(1)                     # completed days only
    sma = d.c.rolling(20).mean().shift(1)
    trend = np.sign(d.c.shift(1) - sma)
    hi_vol = (atr > atr.rolling(100, min_periods=60).median()).astype(float).where(atr.notna())
    pos = np.searchsorted(d.index.to_numpy(), tday)
    ny = pd.DatetimeIndex(x.start).tz_localize("UTC").tz_convert(run.NY)
    m = (ny.hour * 60 + ny.minute).to_numpy()
    sess = np.where((m >= 18 * 60) | (m < 3 * 60), 0, np.where(m < 9 * 60 + 30, 1, np.where(m < 12 * 60, 2, 3)))
    slot = m // 30
    return {"atr": atr.to_numpy()[pos], "trend": trend.to_numpy()[pos], "hivol": hi_vol.to_numpy()[pos],
            "sess": sess, "slot": slot, "tday": tday, "year": ny.year.to_numpy(), "n": n}


# ------------------------------------------------------------------ events: (k array, side array)

def ev_band(x: efb.Inst, nmin: int, nmax: int) -> tuple[np.ndarray, np.ndarray]:
    h, lo, c = x.h, x.lo, x.c
    n = len(c)
    hi_t, lo_t = run.sparse(h, np.maximum), run.sparse(lo, np.minimum)
    ks, ss = [], []
    last = {1: -10**9, -1: -10**9}
    for B in range(nmax + 2, n):
        for N in range(nmax, nmin - 1, -1):
            top, bot = run.rq(hi_t, B - N, B - 1, max), run.rq(lo_t, B - N, B - 1, min)
            w, p = top - bot, c[B - 1]
            if not (P40 * p <= w <= P150 * p):
                continue
            side = 1 if c[B] > top else (-1 if c[B] < bot else 0)
            if side == 0:
                continue
            seg = slice(B - N, B)
            ti = np.flatnonzero(h[seg] >= top - TOUCH * w)
            bi = np.flatnonzero(lo[seg] <= bot + TOUCH * w)
            if len(ti) < 2 or len(bi) < 2 or ti[-1] - ti[0] < 3 or bi[-1] - bi[0] < 3:
                continue
            if B - last[side] >= 12:
                ks.append(B)
                ss.append(side)
                last[side] = B
            break
    return np.array(ks, np.int64), np.array(ss, np.int64)


def first_today(mask: np.ndarray, group: np.ndarray) -> np.ndarray:
    """True only on the first True bar of each group (groups are contiguous runs)."""
    s = pd.Series(mask)
    prior = s.astype(int).groupby(group).cumsum() - s.astype(int)
    return mask & (prior.to_numpy() == 0)


def ev_level(x: efb.Inst, hi_lv: np.ndarray, lo_lv: np.ndarray, group: np.ndarray, kind: str):
    h, lo, c = x.h, x.lo, x.c
    ok_h, ok_l = np.isfinite(hi_lv), np.isfinite(lo_lv)
    if kind == "fade":
        up = ok_h & first_today(ok_h & (h > hi_lv), group) & (c < hi_lv)
        dn = ok_l & first_today(ok_l & (lo < lo_lv), group) & (c > lo_lv)
        k = np.r_[np.flatnonzero(up), np.flatnonzero(dn)]
        s = np.r_[-np.ones(up.sum(), np.int64), np.ones(dn.sum(), np.int64)]
    else:
        up = first_today(ok_h & (c > hi_lv), group)
        dn = first_today(ok_l & (c < lo_lv), group)
        k = np.r_[np.flatnonzero(up), np.flatnonzero(dn)]
        s = np.r_[np.ones(up.sum(), np.int64), -np.ones(dn.sum(), np.int64)]
    o = np.argsort(k, kind="stable")
    return k[o], s[o]


def session_levels(x: efb.Inst, lv: run.Levels):
    """Latest ended Asia or London session high/low (within 24h) and a group id per (session instance)."""
    n = len(x.c)
    end = x.start + 5 * MIN
    best_end = np.full(n, -1, np.int64)
    hi = np.full(n, np.nan)
    lo = np.full(n, np.nan)
    gid = np.full(n, -1, np.int64)
    for si, name in enumerate(("asia", "london")):
        keys, hs, ls, lasts, ends = lv.sess[name]
        p = np.searchsorted(ends, end, side="right") - 1
        ok = (p >= 0)
        pe = np.where(ok, ends[np.clip(p, 0, None)], -1)
        ok &= (end - pe) < 24 * 60 * MIN
        newer = ok & (pe > best_end)
        best_end = np.where(newer, pe, best_end)
        hi = np.where(newer, hs[np.clip(p, 0, None)], hi)
        lo = np.where(newer, ls[np.clip(p, 0, None)], lo)
        gid = np.where(newer, p * 2 + si, gid)
    return hi, lo, gid


def ev_fvg(x: efb.Inst, kind: str):
    h, lo, c = x.h, x.lo, x.c
    n = len(c)
    bull = np.zeros(n, bool)
    bear = np.zeros(n, bool)
    bull[2:] = lo[2:] > h[:-2]
    bear[2:] = h[2:] < lo[:-2]
    ks, ss = [], []
    used = set()
    for i in np.flatnonzero(bull | bear):
        s = 1 if bull[i] else -1
        bot, top = (h[i - 2], lo[i]) if s > 0 else (h[i], lo[i - 2])
        for k in range(i + 1, min(i + FVG_AGE + 1, n)):
            if kind == "respect":
                touched = lo[k] <= top if s > 0 else h[k] >= bot
                if touched:
                    held = c[k] > top if s > 0 else c[k] < bot
                    if held and (k, s) not in used:
                        ks.append(k)
                        ss.append(s)
                        used.add((k, s))
                    break
            else:
                broke = c[k] < bot if s > 0 else c[k] > top
                if broke:
                    if (k, -s) not in used:
                        ks.append(k)
                        ss.append(-s)
                        used.add((k, -s))
                    break
    k = np.array(ks, np.int64)
    s = np.array(ss, np.int64)
    o = np.argsort(k, kind="stable")
    return k[o], s[o]


# ------------------------------------------------------------------ scan

def outcomes(x: efb.Inst, ctx: dict, H: int) -> np.ndarray:
    n = len(x.c)
    r = np.full(n, np.nan)
    j = np.arange(n) + H
    ok = j < n
    jj = np.clip(j, 0, n - 1)
    ok &= (x.start[jj] - x.start) <= int(H * 5 * MIN * 1.5)
    r[ok] = (x.c[jj[ok]] - x.c[ok]) / ctx["atr"][ok]          # move in daily-ATR units (both in points)
    return r


def cell_stats(edge: np.ndarray, tday: np.ndarray, year: np.ndarray) -> dict:
    df = pd.DataFrame({"e": edge, "d": tday, "y": year}).dropna()
    if df.empty:
        return {"n_events": 0, "n_days": 0, "mean": np.nan, "t": np.nan, "years_same_sign": 0}
    # one event per day: the first one (known without looking ahead). A per-day MEAN would be biased because the
    # number of later events in a day depends on the path inside the earlier events' outcome windows.
    per_day = df.groupby("d", sort=False).first()
    m, sd, nd = per_day.e.mean(), per_day.e.std(ddof=1), len(per_day)
    t = m / (sd / np.sqrt(nd)) if nd > 1 and sd > 0 else np.nan
    ym = per_day.groupby("y").e.mean()
    return {"n_events": len(df), "n_days": nd, "mean": m, "t": t,
            "years_same_sign": int((np.sign(ym) == np.sign(m)).sum()), "n_years": int(len(ym))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=efb.DATA)
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    x = efb.load("NAS100", a.data)
    assert x.start.max() < efb.HOLDOUT.value, "holdout data must not be loaded"
    lv = run.Levels(x)
    ctx = context(x, lv)
    per = efb.period_of(x.start + 5 * MIN)
    print(f"NAS100 5m bars {len(x.c)}", flush=True)

    shi, slo, sgid = session_levels(x, lv)
    pd_group = lv.tday
    events = {
        "band_1_4h": ev_band(x, 12, 48),
        "band_4_8h": ev_band(x, 49, 96),
        "pd_fade": ev_level(x, lv.pdh, lv.pdl, pd_group, "fade"),
        "pd_break": ev_level(x, lv.pdh, lv.pdl, pd_group, "break"),
        "sess_fade": ev_level(x, shi, slo, sgid, "fade"),
        "sess_break": ev_level(x, shi, slo, sgid, "break"),
        "fvg_respect": ev_fvg(x, "respect"),
        "ifvg": ev_fvg(x, "inverse"),
    }
    for e, (k, s) in events.items():
        print(e, len(k), flush=True)

    rows = []
    survivors = []
    for H in HORIZONS:
        r = outcomes(x, ctx, H)
        dev_bar = (per == "dev") & np.isfinite(r)
        slot_mean = pd.Series(r[dev_bar]).groupby(ctx["slot"][dev_bar]).mean()
        base = slot_mean.reindex(range(48)).fillna(0.0).to_numpy()[ctx["slot"]]
        for e, (k, s) in events.items():
            keep = np.isfinite(ctx["atr"][k]) & np.isfinite(ctx["trend"][k]) & np.isfinite(ctx["hivol"][k])
            k, s = k[keep], s[keep]
            edge = s * (r[k] - base[k])
            raw = s * r[k]
            cost = 1e-4 * x.c[k] / ctx["atr"][k]            # round-trip cost in daily-ATR units
            sess = ctx["sess"][k]
            withtr = (s * ctx["trend"][k]) > 0
            hiv = ctx["hivol"][k] > 0.5
            dev = per[k] == "dev"
            cells = [("all", np.ones(len(k), bool))]
            cells += [(f"sess={SESSIONS[q]}", sess == q) for q in range(4)]
            cells += [("trend=with", withtr), ("trend=against", ~withtr)]
            cells += [("vol=high", hiv), ("vol=low", ~hiv)]
            for q in range(4):
                for tw in (True, False):
                    for hv in (True, False):
                        cells.append((f"sess={SESSIONS[q]}|trend={'with' if tw else 'against'}|"
                                      f"vol={'high' if hv else 'low'}", (sess == q) & (withtr == tw) & (hiv == hv)))
            for name, mk in cells:
                md = mk & dev
                st = cell_stats(edge[md], ctx["tday"][k[md]], ctx["year"][k[md]])
                row = {"event": e, "horizon_bars": H, "cell": name, **{f"dev_{q}": v for q, v in st.items()},
                       "dev_raw_mean": float(np.nanmean(raw[md])) if md.any() else np.nan,
                       "dev_cost_mean": float(np.nanmean(cost[md])) if md.any() else np.nan}
                ok = (st["n_days"] >= MIN_DAYS and np.isfinite(st["t"]) and abs(st["t"]) >= T_MIN
                      and st["years_same_sign"] >= 4 and abs(st["mean"]) >= MIN_EDGE)
                row["dev_survives"] = bool(ok)
                if ok:
                    direction = int(np.sign(st["mean"]))
                    mv = mk & (per[k] == "val")
                    sv = cell_stats(direction * edge[mv], ctx["tday"][k[mv]], ctx["year"][k[mv]])
                    net2 = direction * raw[mv] - 2 * cost[mv]
                    row.update({"direction": direction, **{f"val_{q}": v for q, v in sv.items()},
                                "val_net2x_mean": float(np.nanmean(net2)) if mv.any() else np.nan})
                    row["val_pass"] = bool(sv["n_days"] >= 30 and np.isfinite(sv["t"]) and sv["t"] >= 2.0
                                           and row["val_net2x_mean"] > 0)
                    survivors.append(row)
                rows.append(row)
    cells_df = pd.DataFrame(rows)
    cells_df.round(5).to_csv(a.out / "cells.csv", index=False)
    pd.DataFrame(survivors).round(5).to_csv(a.out / "survivors.csv", index=False)
    print(f"cells tested: {len(cells_df)}, dev survivors: {len(survivors)}, "
          f"val pass: {sum(r.get('val_pass', False) for r in survivors)}")
    top = cells_df.reindex(cells_df.dev_t.abs().sort_values(ascending=False).index).head(25)
    print(top[["event", "horizon_bars", "cell", "dev_n_days", "dev_mean", "dev_t", "dev_years_same_sign",
               "dev_survives"]].round(3).to_string())
    if survivors:
        print(pd.DataFrame(survivors)[["event", "horizon_bars", "cell", "direction", "dev_mean", "dev_t",
                                       "val_n_days", "val_mean", "val_t", "val_net2x_mean", "val_pass"]]
              .round(3).to_string())


if __name__ == "__main__":
    main()
