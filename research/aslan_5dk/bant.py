"""
Aslan's band breakout on Nasdaq 5m (5th and last idea slot, owner approved 2026-11-19).
Rules, costs, control and pass bar are pre-registered in results/2026-11-19_aslan_bant/README.md (section 1).
Differs from sikisma.py: the MSP is the band edge itself; entry is the close of the bar that closes through it;
stop under the nearest FVG of the breakout leg; target the nearest level 40-80 points away (else 60 points).

    python research/aslan_5dk/bant.py [--data DIR] [--out DIR] [--sets 2000]

Look-ahead discipline: the band comes from bars before the breakout bar B; FVGs and swings are used only after the
bars that form / confirm them have closed (all <= B); the entry is the close of B.
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
OUT = run.ROOT / "results" / "2026-11-19_aslan_bant"
TOUCH = 0.15            # a touch = wick within 15% of the band width from the band edge
PAD = 0.0002            # stop ~5 points beyond the FVG / swing
P40, P60, P80, P100 = 0.0017, 0.0025, 0.0033, 0.0042   # 40/60/80/100 Nasdaq points at ~24000
REARM = 12              # no new trigger on the same side within 12 bars of the last one

# name: (primary, min bars, min width, max width, stop mode, target mode, htf rule 8c)
SETUPS = {
    "main": (True, 12, P40, 0.0062, "fvg", "level", True),
    "no_htf": (False, 12, P40, 0.0062, "fvg", "level", False),
    "fix60": (False, 12, P40, 0.0062, "fvg", "fix", True),
    "min24": (False, 24, P40, 0.0062, "fvg", "level", True),
    "w_max0.30": (False, 12, P40, 0.0030, "fvg", "level", True),
    "stop_band": (False, 12, P40, 0.0062, "band", "level", True),
}


def triggers(x: efb.Inst, min_n: int, wmin: float, wmax: float, stop_mode: str) -> tuple[pd.DataFrame, dict]:
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
    st = {"breakouts": 0, "no_stop": 0}
    last = {1: -10**9, -1: -10**9}
    for B in range(60, n - 1):
        best = None
        for N in range(48, min_n - 1, -1):
            top, bot = run.rq(hi_t, B - N, B - 1, max), run.rq(lo_t, B - N, B - 1, min)
            w = top - bot
            p = c[B - 1]
            if not (wmin * p <= w <= wmax * p):
                continue
            side = 1 if c[B] > top else (-1 if c[B] < bot else 0)
            if side == 0:
                continue
            seg = slice(B - N, B)
            ti = np.flatnonzero(h[seg] >= top - TOUCH * w)
            bi = np.flatnonzero(lo[seg] <= bot + TOUCH * w)
            if len(ti) < 2 or len(bi) < 2 or ti[-1] - ti[0] < 3 or bi[-1] - bi[0] < 3:
                continue
            best = (N, top, bot, side, ti + B - N, bi + B - N)
            break
        if best is None:
            continue
        N, top, bot, side, ti, bi = best
        if B - last[side] < REARM:
            continue
        last[side] = B
        st["breakouts"] += 1
        e = c[B]
        # breakout leg starts at the last touch of the opposite band edge
        leg = int(bi[-1] if side > 0 else ti[-1])
        stop = np.nan
        if stop_mode == "fvg":
            same = bull5 if side > 0 else bear5
            fv = [i for i in range(leg + 2, B + 1) if same[i]]
            edges = [h[i - 2] for i in fv if h[i - 2] < e] if side > 0 else [lo[i - 2] for i in fv if lo[i - 2] > e]
            if edges:
                stop = (max(edges) * (1 - PAD)) if side > 0 else (min(edges) * (1 + PAD))
            else:
                sw = sl if side > 0 else sh
                sws = [i for i in range(B - N, B - 1) if sw[i] and i + 2 <= B]
                if sws:
                    stop = lo[sws[-1]] * (1 - PAD) if side > 0 else h[sws[-1]] * (1 + PAD)
        else:
            stop = bot * (1 - PAD) if side > 0 else top * (1 + PAD)
        if not np.isfinite(stop) or (side > 0 and stop >= e) or (side < 0 and stop <= e):
            st["no_stop"] += 1
            continue
        rows.append((B, side, stop, leg))
    return pd.DataFrame(rows, columns=["k", "side", "stop", "ext"]), st


def run_setup(x: efb.Inst, lv: run.Levels, htf: run.HTF, trig: pd.DataFrame, name: str, primary: bool,
              tmode: str, use_htf: bool, funnel: dict) -> pd.DataFrame:
    end = x.start + 5 * run.MIN
    mins = (end // run.MIN) % 1440
    ny = pd.DatetimeIndex(end).tz_localize("UTC").tz_convert(run.NY)
    ny_min = (ny.hour * 60 + ny.minute).to_numpy()
    f = {"triggers": 0, "window": 0, "ny_open": 0, "busy": 0, "risk": 0, "near": 0, "level_tp": 0, "fixed_tp": 0,
         "htf_no_confirm": 0, "trades": 0}
    out = []
    free_after = -1
    for k, side, stop, ext in trig.itertuples(index=False):
        f["triggers"] += 1
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
        risk = abs(stop - e) / e
        if not (run.RISK_MIN <= risk <= P100):
            f["risk"] += 1
            continue
        opp = lv.candidates(k, above=(side < 0))
        if any(abs(v / e - 1) <= run.NEAR for v in opp):
            f["near"] += 1
            continue
        tp = e * (1 + side * P60)
        if tmode == "level":
            cand = [v for v in lv.candidates(k, above=(side > 0)) if P40 <= side * (v / e - 1) <= P80]
            if cand:
                tp = (min(cand) * (1 - run.TP_PAD)) if side > 0 else (max(cand) * (1 + run.TP_PAD))
                f["level_tp"] += 1
            else:
                f["fixed_tp"] += 1
        if use_htf and htf.obstacle(int(k), int(side), e) and not htf.confirmed(int(k), int(side), int(ext)):
            f["htf_no_confirm"] += 1
            continue
        j, px, why = run.simulate(x.start, x.o, x.h, x.lo, x.c, int(k), int(side), float(stop), float(tp),
                                  run.MAX_HOLD)
        free_after = j
        f["trades"] += 1
        out.append({"cell": name, "primary": primary, "side": side, "k": k, "j": j,
                    "t_in": int(end[k]), "t_out": int(x.start[j] + 5 * run.MIN), "entry": e, "stop": stop, "tp": tp,
                    "exit": px, "why": ("stop", "hedef", "süre")[why], "risk": risk,
                    "tp_d": abs(tp / e - 1), "gross": side * (px / e - 1)})
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
    print(f"NAS100 5m bars {len(x.start)}")
    lv, htf = run.Levels(x), run.HTF(x)
    funnel, parts, trig_stats = {}, [], {}
    for name, (primary, min_n, wmin, wmax, smode, tmode, use_htf) in SETUPS.items():
        trig, st = triggers(x, min_n, wmin, wmax, smode)
        trig_stats[name] = st
        parts.append(run_setup(x, lv, htf, trig, name, primary, tmode, use_htf, funnel))
        print(name, st, funnel[name])
    tr = pd.concat(parts, ignore_index=True)
    pd.DataFrame(trig_stats).T.join(pd.DataFrame(funnel).T).to_csv(a.out / "funnel.csv")
    summ = run.summarise(tr)
    summ.round(4).to_csv(a.out / "summary.csv", index=False)

    rng = np.random.default_rng(20261121)
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
