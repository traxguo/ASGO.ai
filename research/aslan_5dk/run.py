"""
Aslan's 5-minute structure-break rule on Nasdaq (the plan's last idea slot).
Rules, costs, control and pass bar are pre-registered in results/2026-11-19_aslan_5dk/README.md (section 1).
Data: HistData NAS100 5m bars from research/endeks_forex/fetch.py (dev + validation only, holdout never loaded).

    python research/aslan_5dk/run.py [--data DIR] [--out DIR] [--sets 2000]

Look-ahead discipline: everything used when bar k closes is known at that close.
  * a 5m swing at bar i is confirmed at the close of bar i+2 (2 left / 2 right, strict)
  * a 1h swing at hour j is confirmed at the close of hour j+2; it is a target candidate only after that
  * Asia (TR 02:00-09:00) and London (TR 10:00-15:00) levels exist only once the session has ended
  * the previous trading day (New York 17:00 -> 17:00) is complete by definition
  * "untaken" = no wick touched the level from its formation through bar k (inclusive)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "endeks_forex"))
import batch as efb  # noqa: E402  (data loading and cleaning, rollover count, period split)

OUT = ROOT / "results" / "2026-11-19_aslan_5dk"
MIN = efb.MIN
HOUR = 60 * MIN
NY = "America/New_York"
COST = 1e-4                      # round trip
SWAP = {1: 0.05, -1: 0.025}      # yearly financing per side (pessimistic, same as the index batch)
MIN_TGT = 0.00075                # target level at least ~20 points away
TP_PAD = 0.0002                  # take profit ~5 points before the level
NEAR = 0.0011                    # untaken opposite level within ~30 points: skip
RISK_MIN, RISK_MAX = 0.0004, 0.006
MAX_HOLD = 24 * HOUR
H1_LOOKBACK = 5 * 24 * HOUR      # 1h swings of the last 5 days
HTF_FVG_AGE = 10 * 24 * HOUR     # 1h / 4h FVGs of the last 10 days
IFVG_BACK = 20                   # 5m bars before the stop bar searched for an inversed FVG


# ------------------------------------------------------------------ range queries

def sparse(a: np.ndarray, fn) -> list[np.ndarray]:
    t = [a]
    j = 1
    while (1 << j) <= len(a):
        p = t[-1]
        t.append(fn(p[:-(1 << (j - 1))], p[(1 << (j - 1)):]))
        j += 1
    return t


def rq(t: list[np.ndarray], i: int, j: int, fn):
    """fn over a[i..j] inclusive (i <= j)."""
    k = (j - i + 1).bit_length() - 1
    return fn(t[k][i], t[k][j - (1 << k) + 1])


# ------------------------------------------------------------------ exits

@njit(cache=True)
def simulate(start, o, h, lo, c, k, side, stop, tp, max_hold):
    """Enter at the close of bar k. Returns (exit index, exit price, reason 0 stop / 1 target / 2 time)."""
    t_end = start[k] + 5 * 60_000_000_000
    n = len(c)
    for j in range(k + 1, n):
        if side < 0:
            if o[j] >= stop:
                return j, o[j], 0
            if h[j] >= stop:
                return j, stop, 0
            if lo[j] <= tp:
                return j, tp, 1
        else:
            if o[j] <= stop:
                return j, o[j], 0
            if lo[j] <= stop:
                return j, stop, 0
            if h[j] >= tp:
                return j, tp, 1
        if start[j] + 5 * 60_000_000_000 - t_end >= max_hold:
            return j, c[j], 2
    return n - 1, c[n - 1], 2


@njit(cache=True)
def control_mean(start, o, h, lo, c, idx, side, stop_d, tp_d, max_hold, mult, cost, swap_l, swap_s):
    """Mean net R of random entries at bars idx with the given side and stop / target distances (fractions)."""
    tot = 0.0
    for q in range(len(idx)):
        k = idx[q]
        e = c[k]
        s = side[q]
        stop = e * (1.0 + stop_d[q]) if s < 0 else e * (1.0 - stop_d[q])
        tp = e * (1.0 - tp_d[q]) if s < 0 else e * (1.0 + tp_d[q])
        j, px, _ = simulate(start, o, h, lo, c, k, s, stop, tp, max_hold)
        gross = s * (px / e - 1.0)
        # overnight count approximated by elapsed days (control only; the real trades use exact NY rollovers)
        nights = (start[j] - start[k]) // (24 * 3600 * 1_000_000_000)
        sw = (swap_l if s > 0 else swap_s) * nights / 365.0
        tot += (gross - mult * (cost + sw)) / stop_d[q]
    return tot / len(idx)


# ------------------------------------------------------------------ levels

class Levels:
    """Candidate liquidity levels with their formation bar index (5m), queried for 'untaken at k'."""

    def __init__(self, x: efb.Inst):
        self.x = x
        n = len(x.start)
        end = x.start + 5 * MIN
        self.lo_t, self.hi_t = sparse(x.lo, np.minimum), sparse(x.h, np.maximum)
        utc = pd.DatetimeIndex(x.start).tz_localize("UTC")
        # trading day (New York 17:00 -> 17:00)
        ny = utc.tz_convert(NY).tz_localize(None) + pd.Timedelta(hours=7)
        tday = ny.normalize().asi8 // (1440 * MIN)
        self.tday = tday
        df = pd.DataFrame({"d": tday, "h": x.h, "l": x.lo, "i": np.arange(n)})
        g = df.groupby("d").agg(h=("h", "max"), l=("l", "min"), last=("i", "max"))
        days = g.index.to_numpy()
        # previous trading day for each bar: the latest complete day before the bar's day
        pos = np.searchsorted(days, tday) - 1
        ok = pos >= 0
        self.pdh = np.where(ok, g.h.to_numpy()[np.clip(pos, 0, None)], np.nan)
        self.pdl = np.where(ok, g.l.to_numpy()[np.clip(pos, 0, None)], np.nan)
        self.pd_end = np.where(ok, g["last"].to_numpy()[np.clip(pos, 0, None)], -1)
        # Asia TR 02:00-09:00 = UTC 23:00 (previous day) - 06:00; London TR 10:00-15:00 = UTC 07:00-12:00
        self.sess = {}
        for name, a, b in (("asia", -1 * HOUR, 6 * HOUR), ("london", 7 * HOUR, 12 * HOUR)):
            # shift so the session lies inside one shifted day: Asia starts at 23:00 UTC of the previous date
            sh = x.start - a if a < 0 else x.start
            uday = sh // (1440 * MIN)
            off = sh - uday * 1440 * MIN
            lo_off, hi_off = (0, b - a) if a < 0 else (a, b)
            inwin = (off >= lo_off) & (off < hi_off)
            key = np.where(inwin, uday, -1)
            dd = pd.DataFrame({"k": key, "h": x.h, "l": x.lo, "i": np.arange(n)})
            dd = dd[dd.k >= 0].groupby("k").agg(h=("h", "max"), l=("l", "min"), last=("i", "max"))
            self.sess[name] = (dd.index.to_numpy(), dd.h.to_numpy(), dd.l.to_numpy(), dd["last"].to_numpy(),
                               dd.index.to_numpy() * 1440 * MIN + b)
        # 1h bars from 5m (UTC hours) and their 2/2 swings
        hr = x.start // HOUR
        hh = pd.DataFrame({"hr": hr, "h": x.h, "l": x.lo, "i": np.arange(n)}).groupby("hr").agg(
            h=("h", "max"), l=("l", "min"), last=("i", "max"))
        H, L, last = hh.h.to_numpy(), hh.l.to_numpy(), hh["last"].to_numpy()
        hs = np.zeros(len(H), bool)
        ls = np.zeros(len(H), bool)
        hs[2:-2] = (H[2:-2] > H[:-4]) & (H[2:-2] > H[1:-3]) & (H[2:-2] > H[3:-1]) & (H[2:-2] > H[4:])
        ls[2:-2] = (L[2:-2] < L[:-4]) & (L[2:-2] < L[1:-3]) & (L[2:-2] < L[3:-1]) & (L[2:-2] < L[4:])
        conf = np.r_[last[2:], np.full(2, n + 10)]      # 5m index at which hour j+2 is complete
        self.h1_hi = (H[hs], last[hs], conf[hs], hh.index.to_numpy()[hs] * HOUR)
        self.h1_lo = (L[ls], last[ls], conf[ls], hh.index.to_numpy()[ls] * HOUR)
        self.end = end

    def untaken(self, level: float, formed: int, k: int, above: bool) -> bool:
        if formed >= k:
            return False
        if above:
            return rq(self.hi_t, formed + 1, k, max) < level
        return rq(self.lo_t, formed + 1, k, min) > level

    def candidates(self, k: int, above: bool) -> list[float]:
        """Untaken levels above (highs) or below (lows) as known at the close of bar k."""
        out = []
        t_close = self.end[k]
        if self.pd_end[k] >= 0:
            lv = self.pdh[k] if above else self.pdl[k]
            if np.isfinite(lv) and self.untaken(lv, int(self.pd_end[k]), k, above):
                out.append(lv)
        for name in ("asia", "london"):
            keys, hs, ls, lasts, ends = self.sess[name]
            p = np.searchsorted(ends, t_close, side="right") - 1   # latest session that has ended
            if p >= 0 and t_close - ends[p] < 24 * HOUR:
                lv = hs[p] if above else ls[p]
                if self.untaken(lv, int(lasts[p]), k, above):
                    out.append(lv)
        vals, lasts, confs, tstart = self.h1_hi if above else self.h1_lo
        a = np.searchsorted(tstart, self.x.start[k] - H1_LOOKBACK)
        b = np.searchsorted(tstart, self.x.start[k])
        for q in range(a, b):
            if confs[q] <= k and self.untaken(vals[q], int(lasts[q]), k, above):
                out.append(vals[q])
        return out


# ------------------------------------------------------------------ higher-timeframe obstacles (addendum 8c)

def htf_bars(x: efb.Inst, key: np.ndarray) -> tuple:
    n = len(x.c)
    g = pd.DataFrame({"k": key, "h": x.h, "l": x.lo, "i": np.arange(n)}).groupby("k").agg(
        h=("h", "max"), l=("l", "min"), last=("i", "max"), first=("i", "min"))
    return g.h.to_numpy(), g.l.to_numpy(), g["last"].to_numpy(), x.start[g["first"].to_numpy()]


class HTF:
    """1h / 4h FVGs and 4h swings, and the 5m FVG / iFVG confirmation."""

    def __init__(self, x: efb.Inst):
        self.x = x
        n = len(x.c)
        self.cmax, self.cmin = sparse(x.c, np.maximum), sparse(x.c, np.minimum)
        self.hmax, self.lmin = sparse(x.h, np.maximum), sparse(x.lo, np.minimum)
        ny = pd.DatetimeIndex(x.start).tz_localize("UTC").tz_convert(NY).tz_localize(None) + pd.Timedelta(hours=7)
        k1 = x.start // HOUR
        k4 = ny.asi8 // (4 * HOUR)               # 4h blocks starting 17:00 New York
        self.fvg = {1: [], -1: []}               # +1 bullish (support), -1 bearish (resistance)
        for key in (k1, k4):
            H, L, last, t0 = htf_bars(x, key)
            j = np.arange(2, len(H))
            bull = j[L[j] > H[j - 2]]
            bear = j[H[j] < L[j - 2]]
            self.fvg[1].append(pd.DataFrame({"bot": H[bull - 2], "top": L[bull], "formed": last[bull], "t": t0[bull]}))
            self.fvg[-1].append(pd.DataFrame({"bot": H[bear], "top": L[bear - 2], "formed": last[bear], "t": t0[bear]}))
            if key is k4:
                sw_h = np.zeros(len(H), bool)
                sw_l = np.zeros(len(H), bool)
                sw_h[2:-2] = (H[2:-2] > H[:-4]) & (H[2:-2] > H[1:-3]) & (H[2:-2] > H[3:-1]) & (H[2:-2] > H[4:])
                sw_l[2:-2] = (L[2:-2] < L[:-4]) & (L[2:-2] < L[1:-3]) & (L[2:-2] < L[3:-1]) & (L[2:-2] < L[4:])
                conf = np.r_[last[2:], np.full(2, n + 10)]
                self.sw4 = {1: (H[sw_h], last[sw_h], conf[sw_h]), -1: (L[sw_l], last[sw_l], conf[sw_l])}
        for s_ in (1, -1):
            f = pd.concat(self.fvg[s_], ignore_index=True).sort_values("t").reset_index(drop=True)
            self.fvg[s_] = (f.bot.to_numpy(), f.top.to_numpy(), f.formed.to_numpy(), f.t.to_numpy())
        h, lo = x.h, x.lo
        self.bull5 = np.zeros(n, bool)
        self.bear5 = np.zeros(n, bool)
        self.bull5[2:] = lo[2:] > h[:-2]
        self.bear5[2:] = h[2:] < lo[:-2]

    def obstacle(self, k: int, side: int, e: float) -> bool:
        """An opposing 1h/4h FVG or an untaken 4h swing level at or just ahead of the entry."""
        x = self.x
        bot, top, formed, t = self.fvg[-side]       # long meets bearish FVGs above, short bullish below
        a = np.searchsorted(t, x.start[k] - HTF_FVG_AGE)
        for q in range(a, len(t)):
            if formed[q] >= k:
                if t[q] > x.start[k]:
                    break
                continue
            f = int(formed[q])
            if side > 0:
                if rq(self.cmax, f + 1, k, max) > top[q]:
                    continue                          # mitigated
                if bot[q] <= e <= top[q] or (bot[q] > e and bot[q] - e <= NEAR * e):
                    return True
            else:
                if rq(self.cmin, f + 1, k, min) < bot[q]:
                    continue
                if bot[q] <= e <= top[q] or (top[q] < e and e - top[q] <= NEAR * e):
                    return True
        vals, formed4, conf4 = self.sw4[side]          # long: 4h highs above, short: 4h lows below
        for v, f, cf in zip(vals, formed4, conf4):
            if cf > k or f >= k:
                continue
            if side > 0:
                if v >= e and v - e <= NEAR * e and rq(self.hmax, int(f) + 1, k, max) < v:
                    return True
            else:
                if v <= e and e - v <= NEAR * e and rq(self.lmin, int(f) + 1, k, min) > v:
                    return True
        return False

    def confirmed(self, k: int, side: int, ext: int) -> bool:
        """5m FVG in the trade direction inside the reversal move, or a close through an opposing 5m FVG (iFVG)."""
        x = self.x
        same, opp = (self.bull5, self.bear5) if side > 0 else (self.bear5, self.bull5)
        if ext + 2 <= k and same[ext + 2:k + 1].any():
            return True
        for i in np.flatnonzero(opp[max(ext - IFVG_BACK, 2):k + 1]) + max(ext - IFVG_BACK, 2):
            if i >= k:
                continue
            if side > 0 and rq(self.cmax, int(i) + 1, k, max) > x.lo[i - 2]:
                return True
            if side < 0 and rq(self.cmin, int(i) + 1, k, min) < x.h[i - 2]:
                return True
        return False


# ------------------------------------------------------------------ the rule

CELLS = {  # name: (primary, target mode, near filter, window UTC minutes [a, b], higher-timeframe rule 8c)
    "main": (True, "level", True, (6 * 60, 19 * 60), True),
    "fix1R": (False, 1.0, True, (6 * 60, 19 * 60), True),
    "fix1.5R": (False, 1.5, True, (6 * 60, 19 * 60), True),
    "fix2R": (False, 2.0, True, (6 * 60, 19 * 60), True),
    "no_near": (False, "level", False, (6 * 60, 19 * 60), True),
    "no_htf": (False, "level", True, (6 * 60, 19 * 60), False),
    "ny_only": (False, "level", True, (13 * 60 + 30, 19 * 60), True),
}


def triggers(x: efb.Inst) -> pd.DataFrame:
    """Every structure-break trigger (both sides) with its stop, independent of position state."""
    h, lo, c = x.h, x.lo, x.c
    n = len(c)
    sh = np.zeros(n, bool)
    sl = np.zeros(n, bool)
    sh[2:-2] = (h[2:-2] > h[:-4]) & (h[2:-2] > h[1:-3]) & (h[2:-2] > h[3:-1]) & (h[2:-2] > h[4:])
    sl[2:-2] = (lo[2:-2] < lo[:-4]) & (lo[2:-2] < lo[1:-3]) & (lo[2:-2] < lo[3:-1]) & (lo[2:-2] < lo[4:])
    H = []  # confirmed swing highs (index)
    L = []
    rows = []
    for k in range(4, n):
        i = k - 2                       # the swing at i is confirmed when bar k closes
        if sh[i]:
            H.append(i)
        if sl[i]:
            L.append(i)
        if len(H) < 2 or len(L) < 2:
            continue
        t1, t2, d1, d2 = H[-2], H[-1], L[-2], L[-1]
        up = h[t2] > h[t1] and lo[d2] > lo[d1]
        down = h[t2] < h[t1] and lo[d2] < lo[d1]
        short = up and c[k] < lo[d2] and c[k - 1] >= lo[d2]
        long_ = down and c[k] > h[t2] and c[k - 1] <= h[t2]
        if short and long_:
            continue
        if short:
            ext = t2 + int(np.argmax(h[t2:k + 1]))
            rows.append((k, -1, h[ext], ext))
        elif long_:
            ext = d2 + int(np.argmin(lo[d2:k + 1]))
            rows.append((k, 1, lo[ext], ext))
    return pd.DataFrame(rows, columns=["k", "side", "stop", "ext"])


def run_cell(x: efb.Inst, lv: Levels, htf: HTF, trig: pd.DataFrame, cell: str, funnel: dict) -> pd.DataFrame:
    primary, mode, near, (wa, wb), use_htf = CELLS[cell]
    end = x.start + 5 * MIN
    mins = (end // MIN) % 1440
    ny = pd.DatetimeIndex(end).tz_localize("UTC").tz_convert(NY)
    ny_min = (ny.hour * 60 + ny.minute).to_numpy()
    f = {"triggers": 0, "window": 0, "ny_open": 0, "risk": 0, "near": 0, "no_target": 0, "htf_no_confirm": 0, "busy": 0,
         "trades": 0, "htf_confirmed": 0}
    out = []
    free_after = -1
    for k, side, stop, ext in trig.itertuples(index=False):
        f["triggers"] += 1
        if not (wa <= mins[k] <= wb):
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
        if not (RISK_MIN <= risk <= RISK_MAX):
            f["risk"] += 1
            continue
        if near:
            opp = lv.candidates(k, above=(side < 0))
            if any(abs(v / e - 1) <= NEAR for v in opp):
                f["near"] += 1
                continue
        if mode == "level":
            cand = lv.candidates(k, above=(side > 0))
            if side < 0:
                cand = [v for v in cand if v <= e * (1 - MIN_TGT)]
                if not cand:
                    f["no_target"] += 1
                    continue
                tp = max(cand) * (1 + TP_PAD)
            else:
                cand = [v for v in cand if v >= e * (1 + MIN_TGT)]
                if not cand:
                    f["no_target"] += 1
                    continue
                tp = min(cand) * (1 - TP_PAD)
        else:
            tp = e + side * mode * abs(stop - e)
        if use_htf and htf.obstacle(int(k), int(side), e):
            if not htf.confirmed(int(k), int(side), int(ext)):
                f["htf_no_confirm"] += 1
                continue
            f["htf_confirmed"] += 1
        j, px, why = simulate(x.start, x.o, x.h, x.lo, x.c, int(k), int(side), float(stop), float(tp), MAX_HOLD)
        free_after = j
        f["trades"] += 1
        out.append({"cell": cell, "primary": primary, "side": side, "k": k, "j": j,
                    "t_in": int(end[k]), "t_out": int(x.start[j] + 5 * MIN), "entry": e, "stop": stop, "tp": tp,
                    "exit": px, "why": ("stop", "hedef", "süre")[why], "risk": risk,
                    "tp_d": abs(tp / e - 1), "gross": side * (px / e - 1)})
    funnel[cell] = f
    tr = pd.DataFrame(out)
    if tr.empty:
        return tr
    nights = efb.nights(tr.t_in.to_numpy(), tr.t_out.to_numpy())
    tr["swap"] = [SWAP[int(s)] * nn / 365 for s, nn in zip(tr.side, nights)]
    for m in (1, 2):
        tr[f"r{m}"] = (tr.gross - m * (COST + tr.swap)) / tr.risk
    tr["period"] = efb.period_of(tr.t_in.to_numpy())
    return tr


# ------------------------------------------------------------------ report

def max_dd_r(r: np.ndarray, risk: float = 0.01) -> float:
    eq = np.r_[1.0, np.cumprod(1 + risk * r)]
    peak = np.maximum.accumulate(eq)
    return float(((peak - eq) / peak).max() * 100)


def summarise(tr: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cell, g in tr.groupby("cell", sort=False):
        for unit, gu in (("long", g[g.side > 0]), ("short", g[g.side < 0]), ("both", g)):
            row = {"cell": cell, "primary": bool(g.primary.iloc[0]), "unit": unit}
            for p in ("dev", "val"):
                gp = gu[gu.period == p].sort_values("t_out")
                r, r2 = gp.r1.to_numpy(), gp.r2.to_numpy()
                pos, neg = r[r > 0].sum(), -r[r < 0].sum()
                row.update({f"{p}_n": len(r), f"{p}_avg_r": r.mean() if len(r) else np.nan,
                            f"{p}_pf": pos / neg if neg > 0 else np.nan,
                            f"{p}_win_pct": (r > 0).mean() * 100 if len(r) else np.nan,
                            f"{p}_total_r": r.sum(), f"{p}_avg2x_r": r2.mean() if len(r2) else np.nan,
                            f"{p}_dd_pct": max_dd_r(r) if len(r) else 0.0,
                            f"{p}_avg_risk_pct": gp.risk.mean() * 100 if len(r) else np.nan,
                            f"{p}_avg_tp_r": (gp.tp_d / gp.risk).mean() if len(r) else np.nan,
                            f"{p}_trades_per_month": len(r) / (60 if p == "dev" else 15)})
            rows.append(row)
    return pd.DataFrame(rows)


def verdict(r: pd.Series, p_dev: float) -> tuple[bool, str]:
    fails = []
    if not (r.dev_avg_r > 0 and r.val_avg_r > 0):
        fails.append("net")
    if not (r.dev_pf >= 1.2 and r.val_pf >= 1.2):
        fails.append("PF")
    if not p_dev < 0.05:
        fails.append("kontrol")
    if not (r.dev_avg2x_r > 0 and r.val_avg2x_r > 0):
        fails.append("2x masraf")
    if not r.val_n >= 30:
        fails.append("az örnek")
    if not (r.dev_dd_pct <= 25 and r.val_dd_pct <= 25):
        fails.append("düşüş")
    return (not fails), ", ".join(fails)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=efb.DATA)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--sets", type=int, default=2000)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    x = efb.load("NAS100", a.data)
    assert x.start.max() < efb.HOLDOUT.value, "holdout data must not be loaded"
    print(f"NAS100 5m bars {len(x.start)}, cleaned {efb.CLEAN.get('NAS100')}, "
          f"{pd.Timestamp(x.start[0], tz='UTC')} -> {pd.Timestamp(x.start[-1], tz='UTC')}")
    lv = Levels(x)
    htf = HTF(x)
    trig = triggers(x)
    print(f"structure-break triggers: {len(trig)} (long {(trig.side > 0).sum()}, short {(trig.side < 0).sum()})")
    funnel: dict = {}
    tr = pd.concat([run_cell(x, lv, htf, trig, c, funnel) for c in CELLS], ignore_index=True)
    pd.DataFrame(funnel).T.to_csv(a.out / "funnel.csv")
    print(pd.DataFrame(funnel).T)
    summ = summarise(tr)
    summ.round(4).to_csv(a.out / "summary.csv", index=False)

    # random-entry control, main cell, per side, dev period
    rng = np.random.default_rng(20261119)
    end = x.start + 5 * MIN
    mins = (end // MIN) % 1440
    main_tr = tr[tr.primary]
    rows = []
    for unit, s in (("long", 1), ("short", -1)):
        g = main_tr[(main_tr.side == s) & (main_tr.period == "dev")]
        pool = np.flatnonzero((mins >= 6 * 60) & (mins <= 19 * 60) & (efb.period_of(end) == "dev"))
        pool = pool[pool < len(x.c) - 300]
        real = g.r1.mean() if len(g) else np.nan
        means = np.empty(a.sets)
        for q in range(a.sets):
            idx = rng.choice(pool, size=len(g))
            means[q] = control_mean(x.start, x.o, x.h, x.lo, x.c, idx.astype(np.int64),
                                    np.full(len(g), s, np.int64), g.risk.to_numpy(float), g.tp_d.to_numpy(float),
                                    MAX_HOLD, 1, COST, SWAP[1], SWAP[-1]) if len(g) else np.nan
        p = (1 + np.sum(means >= real)) / (a.sets + 1)
        r = summ[(summ.cell == "main") & (summ.unit == unit)].iloc[0]
        ok, fails = verdict(r, p)
        rows.append({"unit": unit, "p_dev": round(p, 4), "ctrl_mean_r": round(float(np.nanmean(means)), 4),
                     "real_dev_r": round(float(real), 4), "pass": ok, "failed": fails})
        print(f"{unit}: real dev {real:.4f}R, control {np.nanmean(means):.4f}R, p {p:.4f} -> "
              f"{'PASS' if ok else 'FAIL: ' + fails}")
    pd.DataFrame(rows).to_csv(a.out / "pass.csv", index=False)

    yearly = main_tr.assign(year=pd.to_datetime(main_tr.t_in, utc=True).dt.year).groupby(["year", "side"]).r1.agg(
        ["count", "mean", "sum"]).round(3)
    yearly.to_csv(a.out / "yearly.csv")
    keep = ["cell", "side", "t_in", "t_out", "entry", "stop", "tp", "exit", "why", "risk", "r1", "r2", "period"]
    t = main_tr[keep].copy()
    for col in ("t_in", "t_out"):
        t[col] = pd.to_datetime(t[col], utc=True).dt.tz_convert("Europe/Istanbul").dt.strftime("%Y-%m-%d %H:%M")
    t.round(5).to_csv(a.out / "trades_main.csv", index=False)
    bh = []
    for p, (s0, s1) in (("dev", ("2020-01-02", "2024-12-31")), ("val", ("2025-01-02", "2026-03-31"))):
        i0 = np.searchsorted(x.start, pd.Timestamp(s0, tz="UTC").value)
        i1 = np.searchsorted(x.start, pd.Timestamp(s1, tz="UTC").value) - 1
        seg = x.c[i0:i1 + 1]
        peak = np.maximum.accumulate(seg)
        bh.append({"period": p, "ret_pct": round((seg[-1] / seg[0] - 1) * 100, 2),
                   "dd_pct": round(((peak - seg) / peak).max() * 100, 2)})
    pd.DataFrame(bh).to_csv(a.out / "buy_hold.csv", index=False)
    print(summ[summ.cell == "main"].round(3).to_string())


if __name__ == "__main__":
    main()
