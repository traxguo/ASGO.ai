"""
Aslan's consolidation breakout on Nasdaq 5m (the 4th and last idea slot).
Rules, costs, control and pass bar are pre-registered in results/2026-11-19_aslan_sikisma/README.md (section 1).
Reuses the exits, levels, filters and report of research/aslan_5dk/run.py.

    python research/aslan_5dk/sikisma.py [--data DIR] [--out DIR] [--sets 2000]

Look-ahead discipline: the range is built from bars before the breakout bar B; FVGs and swings are used only
after the bars that form / confirm them have closed; the entry is the close of bar k.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run  # noqa: E402

efb = run.efb
OUT = run.ROOT / "results" / "2026-11-19_aslan_sikisma"
WAIT = 24          # bars after the breakout in which the entry must come
TOUCH = 0.15       # a touch = wick within 15% of the band width from the band edge
MIN15 = 15 * run.MIN

# name: (primary, min bars, max width, iFVG required, target mode)
SETUPS = {
    "main": (True, 12, 0.0022, True, "level"),
    "no_ifvg": (False, 12, 0.0022, False, "level"),
    "min24": (False, 24, 0.0022, True, "level"),
    "w0.15": (False, 12, 0.0015, True, "level"),
    "w0.30": (False, 12, 0.0030, True, "level"),
    "fix2R": (False, 12, 0.0022, True, 2.0),
}


def fvg15(x: efb.Inst) -> tuple:
    """15m FVGs from closed 15m blocks: (bull bot, bull top, bear bot, bear top) each with (first idx, formed idx)."""
    key = x.start // MIN15
    n = len(x.c)
    g = pd.DataFrame({"k": key, "h": x.h, "l": x.lo, "i": np.arange(n)}).groupby("k").agg(
        h=("h", "max"), l=("l", "min"), last=("i", "max"), first=("i", "min"))
    H, L, last, first = g.h.to_numpy(), g.l.to_numpy(), g["last"].to_numpy(), g["first"].to_numpy()
    j = np.arange(2, len(H))
    bull = j[L[j] > H[j - 2]]
    bear = j[H[j] < L[j - 2]]
    return {1: (H[bull - 2], L[bull], first[bull - 2], last[bull]),       # zone bot, top, first idx, formed idx
            -1: (H[bear], L[bear - 2], first[bear - 2], last[bear])}


def setups(x: efb.Inst, min_n: int, width: float, need_ifvg: bool, f15: dict) -> pd.DataFrame:
    h, lo, c = x.h, x.lo, x.c
    n = len(c)
    hi_t, lo_t = run.sparse(h, np.maximum), run.sparse(lo, np.minimum)
    sh = np.zeros(n, bool)
    sl = np.zeros(n, bool)
    sh[2:-2] = (h[2:-2] > h[:-4]) & (h[2:-2] > h[1:-3]) & (h[2:-2] > h[3:-1]) & (h[2:-2] > h[4:])
    sl[2:-2] = (lo[2:-2] < lo[:-4]) & (lo[2:-2] < lo[1:-3]) & (lo[2:-2] < lo[3:-1]) & (lo[2:-2] < lo[4:])
    bull5 = np.zeros(n, bool)
    bear5 = np.zeros(n, bool)
    bull5[2:] = lo[2:] > h[:-2]
    bear5[2:] = h[2:] < lo[:-2]
    rows = []
    stats = {"breakouts": 0, "invalid": 0, "expired": 0, "entries": 0}
    for B in range(60, n - WAIT - 1):
        top12, bot12 = run.rq(hi_t, B - min_n, B - 1, max), run.rq(lo_t, B - min_n, B - 1, min)
        side = 1 if c[B] > top12 else (-1 if c[B] < bot12 else 0)
        if side == 0 or top12 - bot12 > width * c[B - 1]:
            continue
        best = None
        for N in range(48, min_n - 1, -1):
            top, bot = run.rq(hi_t, B - N, B - 1, max), run.rq(lo_t, B - N, B - 1, min)
            if top - bot > width * c[B - 1]:
                continue
            if (side > 0 and c[B] <= top) or (side < 0 and c[B] >= bot):
                continue
            best = (N, top, bot)
            break
        if best is None:
            continue
        N, top, bot = best
        w = top - bot
        seg = slice(B - N, B)
        ti = np.flatnonzero(h[seg] >= top - TOUCH * w)
        bi = np.flatnonzero(lo[seg] <= bot + TOUCH * w)
        if len(ti) < 2 or len(bi) < 2 or ti[-1] - ti[0] < 3 or bi[-1] - bi[0] < 3:
            continue
        stats["breakouts"] += 1
        # pullback: opposing FVGs formed after B, inverted by a close; then a close through the last swing after B
        opp5 = bear5 if side > 0 else bull5
        sw = sh if side > 0 else sl
        o15 = f15[-side]
        ifvg = not need_ifvg
        zones = []
        done = False
        for k in range(B + 1, B + WAIT + 1):
            if (side > 0 and c[k] < bot) or (side < 0 and c[k] > top):
                stats["invalid"] += 1
                done = True
                break
            if not ifvg:
                # 5m FVG formed at bar i (bars i-2..i all strictly after B) becomes known at the close of i
                if k >= B + 4 and opp5[k - 1]:
                    i = k - 1
                    zones.append(lo[i - 2] if side > 0 else h[i - 2])   # far edge to close through
                q = np.flatnonzero((o15[3] == k - 1) & (o15[2] > B))
                for qq in q:
                    zones.append(o15[1][qq] if side > 0 else o15[0][qq])
                if any((c[k] > z) if side > 0 else (c[k] < z) for z in zones):
                    ifvg = True
            if not ifvg:
                continue
            swings = [i for i in range(B + 1, k - 1) if sw[i] and i + 2 <= k]
            if not swings:
                continue
            msp = h[swings[-1]] if side > 0 else lo[swings[-1]]
            if (side > 0 and c[k] > msp) or (side < 0 and c[k] < msp):
                ext = B + int(np.argmin(lo[B:k + 1]) if side > 0 else np.argmax(h[B:k + 1]))
                stop = lo[ext] if side > 0 else h[ext]
                rows.append((k, side, stop, ext))
                stats["entries"] += 1
                done = True
                break
        if not done:
            stats["expired"] += 1
    df = pd.DataFrame(rows, columns=["k", "side", "stop", "ext"]).sort_values("k", kind="stable").reset_index(drop=True)
    return df, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=efb.DATA)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--sets", type=int, default=2000)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    x = efb.load("NAS100", a.data)
    assert x.start.max() < efb.HOLDOUT.value, "holdout data must not be loaded"
    print(f"NAS100 5m bars {len(x.start)}")
    lv, htf, f15 = run.Levels(x), run.HTF(x), fvg15(x)
    funnel, parts, setup_stats = {}, [], {}
    for name, (primary, min_n, width, need_ifvg, mode) in SETUPS.items():
        trig, st = setups(x, min_n, width, need_ifvg, f15)
        setup_stats[name] = st
        run.CELLS[name] = (primary, mode, True, (6 * 60, 19 * 60), True)
        parts.append(run.run_cell(x, lv, htf, trig, name, funnel))
        print(name, st, funnel[name])
    tr = pd.concat(parts, ignore_index=True)
    pd.DataFrame(setup_stats).T.join(pd.DataFrame(funnel).T, rsuffix="_f").to_csv(a.out / "funnel.csv")
    summ = run.summarise(tr)
    summ.round(4).to_csv(a.out / "summary.csv", index=False)

    rng = np.random.default_rng(20261120)
    end = x.start + 5 * run.MIN
    mins = (end // run.MIN) % 1440
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
        r = summ[(summ.cell == "main") & (summ.unit == unit)].iloc[0]
        ok, fails = run.verdict(r, p)
        rows.append({"unit": unit, "p_dev": round(float(p), 4), "ctrl_mean_r": round(float(np.nanmean(means)), 4)
                     if len(g) else np.nan, "real_dev_r": round(float(real), 4), "pass": ok, "failed": fails})
        print(f"{unit}: real dev {real:.4f}R, p {p:.4f} -> {'PASS' if ok else 'FAIL: ' + fails}")
    pd.DataFrame(rows).to_csv(a.out / "pass.csv", index=False)
    yearly = main_tr.assign(year=pd.to_datetime(main_tr.t_in, utc=True).dt.year).groupby(["year", "side"]).r1.agg(
        ["count", "mean", "sum"]).round(3)
    yearly.to_csv(a.out / "yearly.csv")
    keep = ["cell", "side", "t_in", "t_out", "entry", "stop", "tp", "exit", "why", "risk", "r1", "r2", "period"]
    t = main_tr[keep].copy()
    for col in ("t_in", "t_out"):
        t[col] = pd.to_datetime(t[col], utc=True).dt.tz_convert("Europe/Istanbul").dt.strftime("%Y-%m-%d %H:%M")
    t.round(5).to_csv(a.out / "trades_main.csv", index=False)
    print(summ[summ.cell == "main"].round(3).to_string())


if __name__ == "__main__":
    main()
