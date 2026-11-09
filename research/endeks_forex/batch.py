"""
Index/forex batch: 8 documented ideas, pre-registered in results/2026-11-09_endeks_forex_batch/README.md.

Reads the 5-minute HistData bars from research/endeks_forex/fetch.py (user_data/efb5m/, dev + val only; any bar
on or after 2026-04-01 is dropped on load) and writes the result CSVs into the results folder.

    python research/endeks_forex/batch.py [--data DIR] [--out DIR] [--sets 2000]

Conventions (see the README):
  * price at time T = close of the 5m bar that ends at T (bar start <= T - 5 min, at most 30 min stale)
  * close-based rules enter/exit 10 minutes after the session close
  * net = gross - mult * (round-trip cost + overnight swap); mult 1 and 2 are both written
  * a trade belongs to the period of its entry time
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "user_data" / "efb5m"
OUT = ROOT / "results" / "2026-11-09_endeks_forex_batch"
HOLDOUT = pd.Timestamp("2026-04-01", tz="UTC")
VAL_START = pd.Timestamp("2025-01-01", tz="UTC")
DEV_START = pd.Timestamp("2020-01-01", tz="UTC")
MIN = 60_000_000_000  # one minute in ns
DAY_NS = 1440 * MIN
STALE = 30 * MIN
SPIKE = 0.05
GAP_DAYS = 5  # consecutive daily rows further apart than this = missing data; no trade spans such a gap
CLEAN: dict = {}

COST = {"NAS100": 1e-4, "SPX500": 1e-4, "GER40": 1e-4, "EURUSD": 1e-4, "GBPUSD": 1e-4, "XAUUSD": 1.5e-4}
# yearly overnight financing (long, short), pessimistic estimates
SWAP = {"NAS100": (0.05, 0.025), "SPX500": (0.05, 0.025), "GER40": (0.05, 0.025),
        "XAUUSD": (0.04, 0.02), "EURUSD": (0.015, 0.015), "GBPUSD": (0.015, 0.015)}
NY, FRA, LDN = "America/New_York", "Europe/Berlin", "Europe/London"
DXY_W = {"EURUSD": -0.576, "USDJPY": 0.136, "GBPUSD": -0.119, "USDCAD": 0.091, "USDSEK": 0.042, "USDCHF": 0.036}


# ------------------------------------------------------------------ data

@dataclass
class Inst:
    name: str
    start: np.ndarray   # bar start, int64 ns UTC
    o: np.ndarray
    h: np.ndarray
    lo: np.ndarray
    c: np.ndarray

    def px(self, t) -> np.ndarray:
        """Price at time(s) t: close of the 5m bar ending at t (NaN when the last bar is too old)."""
        t = np.asarray(t, dtype=np.int64)
        q = t - 5 * MIN
        i = np.searchsorted(self.start, q, side="right") - 1
        ok = (i >= 0) & (q - self.start[np.clip(i, 0, None)] <= STALE)
        out = np.where(ok, self.c[np.clip(i, 0, None)], np.nan)
        return out

    def has_bar(self, t) -> np.ndarray:
        t = np.asarray(t, dtype=np.int64)
        i = np.searchsorted(self.start, t)
        i2 = np.clip(i, 0, len(self.start) - 1)
        return (i < len(self.start)) & (self.start[i2] == t)

    def span(self, a: int, b: int) -> slice:
        """Bars whose start is in [a, b)."""
        return slice(np.searchsorted(self.start, a), np.searchsorted(self.start, b))


def load(name: str, data: Path) -> Inst:
    d = pd.read_feather(data / f"{name}_5m.feather")
    t = pd.DatetimeIndex(d["date"])
    t = t.tz_localize("UTC") if t.tz is None else t.tz_convert("UTC")
    keep = t < HOLDOUT
    t = t[keep].as_unit("ns")
    d = d[keep].reset_index(drop=True)
    # data cleaning (fix after the first run, see README): drop bad prints, i.e. bars whose close, high or low is
    # more than SPIKE away from the centered median close of the surrounding 25 bars
    med = d.close.rolling(25, center=True, min_periods=5).median()
    bad = ((d.close / med - 1).abs() > SPIKE) | (d.high / med - 1 > SPIKE) | (1 - d.low / med > SPIKE)
    CLEAN[name] = int(bad.sum())
    t, d = t[~bad.to_numpy()], d[~bad]
    return Inst(name, t.asi8.copy(), d.open.to_numpy(float), d.high.to_numpy(float), d.low.to_numpy(float),
                d.close.to_numpy(float))


DATES = pd.date_range("2020-01-01", "2026-03-31", freq="B")


def local_times(hhmm: str, tz: str, dates=DATES) -> np.ndarray:
    hh, mm = map(int, hhmm.split(":"))
    naive = pd.DatetimeIndex(dates) + pd.Timedelta(hours=hh, minutes=mm)
    loc = naive.tz_localize(tz, ambiguous="NaT", nonexistent="NaT").tz_convert("UTC").as_unit("ns")
    return loc.asi8.copy()


def nights(t_in, t_out) -> np.ndarray:
    """New York 17:00 rollovers between t_in and t_out (weekend = 3)."""
    def day(t):
        x = pd.DatetimeIndex(np.asarray(t, dtype=np.int64)).tz_localize("UTC").tz_convert(NY) - pd.Timedelta(hours=17)
        return x.tz_localize(None).normalize().as_unit("ns").asi8 // DAY_NS
    return day(t_out) - day(t_in)


def period_of(t) -> np.ndarray:
    t = np.asarray(t, dtype=np.int64)
    return np.where(t >= VAL_START.value, "val", "dev")


def swap_rate(inst: str, side: int) -> float:
    return SWAP[inst][0 if side > 0 else 1]


def session_table(x: Inst, open_hm: str, close_hm: str, tz: str) -> pd.DataFrame:
    """One row per weekday with a cash open and close bar: open/close prices and the close+10 min entry price."""
    to, tc = local_times(open_hm, tz), local_times(close_hm, tz)
    te = tc + 10 * MIN
    ok = (to > 0) & (tc > 0)
    df = pd.DataFrame({"date": DATES, "t_open": to, "t_close": tc, "t_ent": te})[ok].reset_index(drop=True)
    df["p_open"] = x.px(df.t_open.to_numpy())
    df["p_close"] = x.px(df.t_close.to_numpy())
    df["p_ent"] = x.px(df.t_ent.to_numpy())
    return df.dropna().reset_index(drop=True)


# ------------------------------------------------------------------ trades and controls

TRADE_COLS = ["idea", "cell", "primary", "side", "inst", "t_in", "t_out", "gross", "cost", "swap", "kind", "i", "j"]


@dataclass
class Daily:
    """A daily entry grid for the random control: entry times and prices (one or two instruments)."""
    t: np.ndarray
    p: dict
    legs: list  # [(inst, sign)] relative to the trade side

    def __post_init__(self):
        gap = np.r_[0, (np.diff(self.t) > GAP_DAYS * DAY_NS).astype(int)]
        self.cgap = np.cumsum(gap)  # rows i..j span a data gap when cgap[j] != cgap[i]


@dataclass
class Book:
    rows: list = field(default_factory=list)
    grids: dict = field(default_factory=dict)       # key -> Daily
    pools: dict = field(default_factory=dict)       # key -> (Inst, entry times array)

    def add(self, idea, cell, primary, side, inst, t_in, t_out, gross, cost, swap, kind, i=-1, j=-1):
        self.rows.append((idea, cell, primary, side, inst, int(t_in), int(t_out), float(gross), float(cost),
                          float(swap), kind, int(i), int(j)))


def daily_trade(book, key, idea, cell, primary, side, i, j):
    g = book.grids[key]
    if g.cgap[j] != g.cgap[i]:
        return  # missing data inside the holding period
    gross, cost, sw = 0.0, 0.0, 0.0
    n = int(nights([g.t[i]], [g.t[j]])[0])
    for inst, sign in g.legs:
        s = side * sign
        gross += s * (g.p[inst][j] / g.p[inst][i] - 1)
        cost += COST[inst]
        sw += n * swap_rate(inst, s) / 365
    book.add(idea, cell, primary, side, key, g.t[i], g.t[j], gross, cost, sw, "daily", i, j)


def control_daily(book, tr: pd.DataFrame, rng, sets: int) -> np.ndarray:
    """Random net returns (sets x trades): same grid, side and number of days, entry anywhere in the same period."""
    out = np.empty((sets, len(tr)))
    for k, r in enumerate(tr.itertuples()):
        g = book.grids[r.inst]
        per = period_of(g.t)
        hold = r.j - r.i
        idx = np.arange(len(g.t))
        okh = idx + hold < len(g.t)
        okh[okh] = g.cgap[idx[okh] + hold] == g.cgap[idx[okh]]
        cand = np.flatnonzero((per == period_of([r.t_in])[0]) & okh)
        ii = rng.choice(cand, sets)
        jj = ii + hold
        n = nights(g.t[ii], g.t[jj])
        net = np.zeros(sets)
        for inst, sign in g.legs:
            s = r.side * sign
            net += s * (g.p[inst][jj] / g.p[inst][ii] - 1) - COST[inst] - n * swap_rate(inst, s) / 365
        out[:, k] = net
    return out


def control_pool(book, tr: pd.DataFrame, rng, sets: int, pool_key) -> np.ndarray:
    """Random net returns: entry drawn from the idea's pool of entry times, same side and same hold (minutes)."""
    out = np.empty((sets, len(tr)))
    for k, r in enumerate(tr.itertuples()):
        x, pool = book.pools[(pool_key, r.inst)]
        per = period_of(pool)
        cand = pool[per == period_of([r.t_in])[0]]
        ti = rng.choice(cand, sets)
        to = ti + (r.t_out - r.t_in)
        pi, po = x.px(ti), x.px(to)
        net = r.side * (po / pi - 1) - COST[r.inst] - nights(ti, to) * swap_rate(r.inst, r.side) / 365
        out[:, k] = np.where(np.isfinite(net), net, 0.0)
    return out


# ------------------------------------------------------------------ indicators

def rsi_wilder(c: pd.Series, n: int = 2) -> pd.Series:
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


# ------------------------------------------------------------------ ideas

def i1_overnight(book, tabs):
    for inst in ("NAS100", "SPX500"):
        d = tabs[inst]
        x = book.pools_inst[inst]
        sma = d.p_close.rolling(200).mean().to_numpy()
        pc, po = d.p_close.to_numpy(), d.p_open.to_numpy()
        tc, to = d.t_close.to_numpy(), d.t_open.to_numpy()
        gap_days = (to[1:] - tc[:-1]) / DAY_NS
        for k in range(len(d) - 1):
            if gap_days[k] > 4.5:
                continue
            n = int(nights([tc[k]], [to[k + 1]])[0])
            g = po[k + 1] / pc[k] - 1
            for cell, ok in (("all", True), ("sma200", np.isfinite(sma[k]) and pc[k] > sma[k])):
                if ok:
                    book.add("I1", cell, cell == "all", 1, inst, tc[k], to[k + 1], g, COST[inst],
                             n * swap_rate(inst, 1) / 365, "pool")
        for k in range(1, len(d)):
            g = -(pc[k] / po[k] - 1)
            for cell, ok in (("all", True), ("sma200", np.isfinite(sma[k - 1]) and pc[k - 1] < sma[k - 1])):
                if ok:
                    book.add("I1", cell, cell == "all", -1, inst, to[k], tc[k], g, COST[inst], 0.0, "pool")
        # control pool: any 5m moment of a trading day
        days = set(pd.DatetimeIndex(d.date).normalize().as_unit("ns").asi8 // DAY_NS)
        loc = pd.DatetimeIndex(x.start + 5 * MIN).tz_localize("UTC").tz_convert(NY).tz_localize(None)
        dd = loc.normalize().as_unit("ns").asi8 // DAY_NS
        mask = np.isin(dd, np.fromiter(days, dtype=np.int64))
        book.pools[("I1", inst)] = (x, (x.start + 5 * MIN)[mask])


def i2_tom(book, tabs):
    for inst in ("NAS100", "SPX500", "GER40"):
        key = f"{inst}:close"
        d = tabs[inst]
        ym = pd.DatetimeIndex(d.date).to_period("M")
        last_idx = pd.Series(np.arange(len(d))).groupby(np.asarray(ym.astype(str))).max().sort_index().to_numpy()
        for L in last_idx[:-1]:
            for ent_name, e in (("-2", L - 1), ("-1", L)):
                for ex_name, xx in (("+1", L + 1), ("+3", L + 3)):
                    if e < 0 or xx >= len(d):
                        continue
                    cell = f"in{ent_name}_out{ex_name}"
                    daily_trade(book, key, "I2", cell, cell == "in-2_out+3", 1, e, xx)


def _stream(book, key, idea, cell, primary, side, n, entry_fn, exit_fn):
    """One position at a time: enter at day i when entry_fn(i), exit at first j>i with exit_fn(i, j)."""
    i = 0
    while i < n:
        if entry_fn(i):
            j = i + 1
            while j < n and not exit_fn(i, j):
                j += 1
            if j >= n:
                break
            daily_trade(book, key, idea, cell, primary, side, i, j)
            i = j
        else:
            i += 1


def i3_rsi2(book, tabs):
    for inst in ("NAS100", "SPX500", "GER40"):
        key = f"{inst}:close"
        c = tabs[inst].p_close
        r, s200, s5 = rsi_wilder(c).to_numpy(), c.rolling(200).mean().to_numpy(), c.rolling(5).mean().to_numpy()
        cv = c.to_numpy()
        for lo, hi in ((5, 95), (10, 90), (25, 75)):
            for ex in ("sma5", "rsi"):
                cell = f"{lo}/{hi}_{ex}"
                prim = cell == "10/90_sma5"

                def ent_l(i, lo=lo):
                    return np.isfinite(s200[i]) and cv[i] > s200[i] and r[i] < lo

                def ent_s(i, hi=hi):
                    return np.isfinite(s200[i]) and cv[i] < s200[i] and r[i] > hi

                def ex_l(i, j, ex=ex):
                    return j - i >= 10 or (cv[j] > s5[j] if ex == "sma5" else r[j] > 70)

                def ex_s(i, j, ex=ex):
                    return j - i >= 10 or (cv[j] < s5[j] if ex == "sma5" else r[j] < 30)

                _stream(book, key, "I3", cell, prim, 1, len(cv), ent_l, ex_l)
                _stream(book, key, "I3", cell, prim, -1, len(cv), ent_s, ex_s)


def i4_gap(book, tabs):
    for inst in ("NAS100", "SPX500"):
        d = tabs[inst]
        x = book.pools_inst[inst]
        pc, po = d.p_close.to_numpy(), d.p_open.to_numpy()
        tc, to = d.t_close.to_numpy(), d.t_open.to_numpy()
        for k in range(1, len(d)):
            if (to[k] - tc[k - 1]) / DAY_NS > 4.5:
                continue
            gap = po[k] / pc[k - 1] - 1
            side = -1 if gap > 0 else 1
            target = pc[k - 1]
            sl = x.span(to[k], tc[k])
            hit = np.flatnonzero(x.h[sl] >= target) if side > 0 else np.flatnonzero(x.lo[sl] <= target)
            for thr in (0.0015, 0.0025, 0.005):
                if abs(gap) <= thr:
                    continue
                for ex in ("fill", "close"):
                    cell = f"{thr * 100:.2f}%_{ex}"
                    if ex == "fill" and len(hit):
                        t_out, p_out = x.start[sl][hit[0]] + 5 * MIN, target
                    else:
                        t_out, p_out = tc[k], pc[k]
                    book.add("I4", cell, cell == "0.25%_fill", side, inst, to[k], t_out,
                             side * (p_out / po[k] - 1), COST[inst], 0.0, "pool")
        book.pools[("I4", inst)] = (x, to[1:])


def i5_streak(book, tabs):
    for inst in ("NAS100", "SPX500", "GER40"):
        key = f"{inst}:close"
        cv = tabs[inst].p_close.to_numpy()
        up = np.r_[False, cv[1:] > cv[:-1]]
        dn = np.r_[False, cv[1:] < cv[:-1]]
        for ex in ("first", "1d", "5d"):
            prim = ex == "first"

            def ent_l(i):
                return i >= 3 and dn[i] and dn[i - 1] and dn[i - 2]

            def ent_s(i):
                return i >= 3 and up[i] and up[i - 1] and up[i - 2]

            def mk_exit(fav, ex=ex):
                def f(i, j):
                    if ex == "1d":
                        return j - i >= 1
                    if ex == "5d":
                        return j - i >= 5
                    return j - i >= 5 or fav[j]
                return f

            _stream(book, key, "I5", ex, prim, 1, len(cv), ent_l, mk_exit(up))
            _stream(book, key, "I5", ex, prim, -1, len(cv), ent_s, mk_exit(dn))


def i6_gold_dxy(book, insts):
    t = local_times("16:00", NY)
    t = t[t > 0]
    g = insts["XAUUSD"].px(t)
    logd = np.log(50.14348112) + sum(w * np.log(insts[s].px(t)) for s, w in DXY_W.items())
    te = t + 10 * MIN
    ge = insts["XAUUSD"].px(te)
    ok = np.isfinite(g) & np.isfinite(logd) & np.isfinite(ge)
    t, g, logd, te, ge = t[ok], g[ok], logd[ok], te[ok], ge[ok]
    book.grids["XAUUSD:dxy"] = Daily(te, {"XAUUSD": ge}, [("XAUUSD", 1)])
    lg = pd.Series(np.log(g))
    ld = pd.Series(logd)
    dg, dd = lg.diff(), ld.diff()
    beta = dg.rolling(60).cov(dd) / dd.rolling(60).var()
    resid = dg - beta * dd
    sd = resid.rolling(60).std()
    e = lg.diff(5) - beta * ld.diff(5)
    z = (e / (sd * np.sqrt(5))).to_numpy()
    n = len(z)
    for thr in (1.5, 2.0, 2.5):
        for hold in (3, 5, 10):
            cell = f"z{thr}_h{hold}"
            prim = cell == "z2.0_h5"
            i = 0
            while i < n - hold:
                if np.isfinite(z[i]) and abs(z[i]) > thr:
                    side = 1 if z[i] < 0 else -1
                    daily_trade(book, "XAUUSD:dxy", "I6", cell, prim, side, i, i + hold)
                    i += hold
                else:
                    i += 1


def i7_spread(book, insts):
    t = local_times("11:00", NY)
    t = t[t > 0]
    D, N = insts["GER40"].px(t), insts["NAS100"].px(t)
    te = t + 10 * MIN
    De, Ne = insts["GER40"].px(te), insts["NAS100"].px(te)
    ok = np.isfinite(D) & np.isfinite(N) & np.isfinite(De) & np.isfinite(Ne)
    D, N, De, Ne, te = D[ok], N[ok], De[ok], Ne[ok], te[ok]
    book.grids["GER40-NAS100"] = Daily(te, {"GER40": De, "NAS100": Ne}, [("GER40", 1), ("NAS100", -1)])
    s = pd.Series(np.log(D) - np.log(N))
    for lb in (20, 60):
        z = ((s - s.rolling(lb).mean()) / s.rolling(lb).std()).to_numpy()
        n = len(z)
        for thr in (1.5, 2.0, 2.5):
            cell = f"z{thr}_lb{lb}"
            prim = cell == "z2.0_lb20"
            i = 0
            while i < n:
                if np.isfinite(z[i]) and abs(z[i]) > thr:
                    side = 1 if z[i] < 0 else -1
                    j = i + 1
                    while j < n and not (j - i >= 10 or (z[j] >= 0 if side > 0 else z[j] <= 0)):
                        j += 1
                    if j >= n:
                        break
                    daily_trade(book, "GER40-NAS100", "I7", cell, prim, side, i, j)
                    i = j
                else:
                    i += 1


def i8_london(book, insts):
    t0, t7, t16 = local_times("00:00", LDN), local_times("07:00", LDN), local_times("16:00", LDN)
    hours = [local_times(f"{h:02d}:00", LDN) for h in (8, 9, 10, 11)]
    for inst in ("EURUSD", "GBPUSD"):
        x = insts[inst]
        pool = []
        for k in range(len(DATES)):
            if min(t0[k], t7[k], t16[k]) <= 0:
                continue
            sl = x.span(t0[k], t7[k])
            if sl.stop - sl.start < 60:
                continue
            hi, lo = x.h[sl].max(), x.lo[sl].min()
            hs = np.array([hh[k] for hh in hours])
            pc = x.px(hs)
            pool.extend(hs[np.isfinite(pc)].tolist())
            sig = None
            for T, p in zip(hs, pc):
                if not np.isfinite(p):
                    continue
                if p > hi:
                    sig = (T, p, 1)
                    break
                if p < lo:
                    sig = (T, p, -1)
                    break
            if sig is None:
                continue
            T, p, side = sig
            stop = lo if side > 0 else hi
            risk = abs(p - stop)
            if risk <= 0:
                continue
            bs = x.span(T, t16[k])
            for tgt_name, kR in (("none", None), ("1R", 1.0), ("2R", 2.0)):
                tgt = None if kR is None else p + side * kR * risk
                t_out, p_out = t16[k], x.px([t16[k]])[0]
                for b in range(bs.start, bs.stop):
                    o, h, l = x.o[b], x.h[b], x.lo[b]
                    if side > 0:
                        if o <= stop:
                            t_out, p_out = x.start[b], o
                            break
                        if l <= stop:
                            t_out, p_out = x.start[b] + 5 * MIN, stop
                            break
                        if tgt is not None and h >= tgt:
                            t_out, p_out = x.start[b] + 5 * MIN, max(tgt, o)
                            break
                    else:
                        if o >= stop:
                            t_out, p_out = x.start[b], o
                            break
                        if h >= stop:
                            t_out, p_out = x.start[b] + 5 * MIN, stop
                            break
                        if tgt is not None and l <= tgt:
                            t_out, p_out = x.start[b] + 5 * MIN, min(tgt, o)
                            break
                if not np.isfinite(p_out):
                    continue
                book.add("I8", tgt_name, tgt_name == "none", side, inst, T, t_out, side * (p_out / p - 1),
                         COST[inst], 0.0, "pool")
        book.pools[("I8", inst)] = (x, np.array(pool, dtype=np.int64))


# ------------------------------------------------------------------ stats

def stats(net: np.ndarray) -> dict:
    n = len(net)
    if n == 0:
        return {"n": 0, "avg_pct": np.nan, "pf": np.nan, "win_pct": np.nan, "total_pct": 0.0}
    pos, neg = net[net > 0].sum(), -net[net < 0].sum()
    return {"n": n, "avg_pct": net.mean() * 100, "pf": pos / neg if neg > 0 else np.inf,
            "win_pct": (net > 0).mean() * 100, "total_pct": net.sum() * 100}


# instruments per idea: the equity is split equally among them (README addendum 2026-11-09)
K = {"I1": 2, "I2": 3, "I3": 3, "I4": 2, "I5": 3, "I6": 1, "I7": 1, "I8": 2}


def max_dd(g: pd.DataFrame, k: int, mult: int = 1) -> float:
    """Largest peak-to-trough fall (%) of equity x (1 + net / k), trades compounded in exit-time order."""
    if g.empty:
        return 0.0
    g = g.sort_values("t_out")
    eq = np.cumprod(1 + (g.gross - mult * (g.cost + g.swap)).to_numpy() / k)
    eq = np.r_[1.0, eq]
    peak = np.maximum.accumulate(eq)
    return float(((peak - eq) / peak).max() * 100)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(DATA))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--sets", type=int, default=2000)
    a = ap.parse_args()
    data, out = Path(a.data), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    names = ["NAS100", "SPX500", "GER40", "EURUSD", "GBPUSD", "XAUUSD", "USDJPY", "USDCAD", "USDSEK", "USDCHF"]
    insts = {n: load(n, data) for n in names if (data / f"{n}_5m.feather").exists()}
    for n, x in insts.items():
        print(f"{n}: {len(x.start)} bars {pd.Timestamp(x.start[0], tz='UTC')} -> {pd.Timestamp(x.start[-1], tz='UTC')}",
              flush=True)
    assert all(x.start[-1] < HOLDOUT.value for x in insts.values()), "holdout data loaded"

    book = Book()
    book.pools_inst = insts
    tabs = {}
    for inst, (o, c, tz) in {"NAS100": ("09:30", "16:00", NY), "SPX500": ("09:30", "16:00", NY),
                             "GER40": ("09:00", "17:30", FRA)}.items():
        if inst in insts:
            tabs[inst] = session_table(insts[inst], o, c, tz)
            d = tabs[inst]
            book.grids[f"{inst}:close"] = Daily(d.t_ent.to_numpy(), {inst: d.p_ent.to_numpy()}, [(inst, 1)])
            print(f"{inst}: {len(d)} sessions {d.date.iloc[0].date()} -> {d.date.iloc[-1].date()}", flush=True)
    # data check: bad prints removed, sessions per year and data gaps in the daily tables
    chk = []
    for n, x in insts.items():
        row = {"inst": n, "bars": len(x.start), "bad_prints_removed": CLEAN.get(n, 0)}
        if n in tabs:
            d = tabs[n]
            yrs = pd.DatetimeIndex(d.date).year
            row.update({f"sessions_{y}": int((yrs == y).sum()) for y in range(2020, 2027)})
            gaps = np.diff(d.t_ent.to_numpy()) / DAY_NS
            row["gaps_over_5d"] = int((gaps > GAP_DAYS).sum())
            row["longest_gap_days"] = round(float(gaps.max()), 1)
        chk.append(row)
        print("data check", row, flush=True)
    pd.DataFrame(chk).to_csv(out / "data_check.csv", index=False)

    steps = [("I1", lambda: i1_overnight(book, tabs)), ("I2", lambda: i2_tom(book, tabs)),
             ("I3", lambda: i3_rsi2(book, tabs)), ("I4", lambda: i4_gap(book, tabs)),
             ("I5", lambda: i5_streak(book, tabs)), ("I6", lambda: i6_gold_dxy(book, insts)),
             ("I7", lambda: i7_spread(book, insts)), ("I8", lambda: i8_london(book, insts))]
    for name, fn in steps:
        try:
            fn()
            print(f"{name}: done, {len(book.rows)} trades so far", flush=True)
        except KeyError as e:  # an instrument failed to download
            print(f"{name}: skipped, missing data {e}", flush=True)

    tr = pd.DataFrame(book.rows, columns=TRADE_COLS)
    tr["period"] = period_of(tr.t_in.to_numpy())
    tr["inst_group"] = tr.inst.str.split(":").str[0]

    # summary: every idea x cell x side x period x cost multiple, all instruments and per instrument
    rows = []
    for (idea, cell, side), g in tr.groupby(["idea", "cell", "side"]):
        prim = bool(g.primary.iloc[0])
        for per in ("dev", "val"):
            gp = g[g.period == per]
            for mult in (1, 2):
                for inst, gi in [("ALL", gp)] + list(gp.groupby("inst_group")):
                    net = (gi.gross - mult * (gi.cost + gi.swap)).to_numpy()
                    rows.append({"idea": idea, "cell": cell, "primary": prim, "side": "long" if side > 0 else "short",
                                 "period": per, "cost_mult": mult, "inst": inst, **stats(net),
                                 "maxdd_pct": max_dd(gi, K[idea] if inst == "ALL" else 1, mult),
                                 "gross_avg_pct": gi.gross.mean() * 100 if len(gi) else np.nan})
    summ = pd.DataFrame(rows)

    # random-entry control: primary cells, each side, each period
    rng = np.random.default_rng(20261109)
    ctrl = []
    prim = tr[tr.primary]
    for (idea, side, per), g in prim.groupby(["idea", "side", "period"]):
        net = (g.gross - g.cost - g.swap).to_numpy()
        if g.kind.iloc[0] == "daily":
            rnd = control_daily(book, g, rng, a.sets)
        else:
            rnd = control_pool(book, g, rng, a.sets, idea)
        means = rnd.mean(axis=1)
        p = (1 + (means >= net.mean()).sum()) / (a.sets + 1)
        ctrl.append({"idea": idea, "side": "long" if side > 0 else "short", "period": per, "n": len(g),
                     "real_avg_pct": net.mean() * 100, "random_avg_pct": means.mean() * 100,
                     "random_p95_pct": np.percentile(means, 95) * 100, "random_win_pct": (rnd > 0).mean() * 100,
                     "p_value": p})
        print(f"control {idea} {side:+d} {per}: real {net.mean() * 100:+.4f}% random {means.mean() * 100:+.4f}% p={p:.4f}",
              flush=True)
    ctrl = pd.DataFrame(ctrl)

    # pass table (pre-registered bar; criterion 5 = max drawdown <= 25% at the tested sizing, addendum 2026-11-09)
    pas = []
    s = summ[(summ.primary) & (summ.inst == "ALL")]
    for (idea, side), g in s.groupby(["idea", "side"]):
        def v(per, mult, col):
            r = g[(g.period == per) & (g.cost_mult == mult)]
            return float(r[col].iloc[0]) if len(r) else np.nan
        cp = ctrl[(ctrl.idea == idea) & (ctrl.side == side) & (ctrl.period == "dev")]
        p = float(cp.p_value.iloc[0]) if len(cp) else np.nan
        c1 = all(v(pp, 1, "avg_pct") > 0 and v(pp, 1, "pf") >= 1.2 for pp in ("dev", "val"))
        c2 = p < 0.05
        c3 = all(v(pp, 2, "avg_pct") > 0 for pp in ("dev", "val"))
        c4 = v("val", 1, "n") >= 30
        gt = tr[(tr.idea == idea) & tr.primary & (tr.side == (1 if side == "long" else -1))]
        dd = {pp: max_dd(gt[gt.period == pp], K[idea]) for pp in ("dev", "val")}
        c5 = all(dd[pp] <= 25 for pp in ("dev", "val"))
        pas.append({"idea": idea, "side": side, "cell": g.cell.iloc[0],
                    "dev_n": v("dev", 1, "n"), "dev_avg_pct": v("dev", 1, "avg_pct"), "dev_pf": v("dev", 1, "pf"),
                    "dev_win_pct": v("dev", 1, "win_pct"), "val_n": v("val", 1, "n"),
                    "val_avg_pct": v("val", 1, "avg_pct"), "val_pf": v("val", 1, "pf"),
                    "val_win_pct": v("val", 1, "win_pct"), "dev_avg_2x": v("dev", 2, "avg_pct"),
                    "val_avg_2x": v("val", 2, "avg_pct"), "p_control_dev": p,
                    "dev_maxdd_pct": dd["dev"], "val_maxdd_pct": dd["val"],
                    "c1_net_pf": c1, "c2_control": c2, "c3_2x": c3, "c4_val30": c4, "c5_dd25": c5,
                    "PASS": c1 and c2 and c3 and c4 and c5})
    pas = pd.DataFrame(pas)

    # yearly breakdown of primary cells
    prim = prim.assign(year=pd.DatetimeIndex(prim.t_in).year, net=prim.gross - prim.cost - prim.swap)
    yearly = (prim.groupby(["idea", "side", "year"]).net
              .agg(n="count", avg_pct=lambda x: x.mean() * 100, win_pct=lambda x: (x > 0).mean() * 100)
              .reset_index())
    yearly["side"] = np.where(yearly.side > 0, "long", "short")

    # buy and hold per instrument and period (session close or 16:00 NY snapshot)
    bh = []
    for n, x in insts.items():
        if n not in COST:
            continue
        for per, (lo, hi) in {"dev": (DEV_START, VAL_START), "val": (VAL_START, HOLDOUT)}.items():
            sl = x.span(lo.value, hi.value)
            if sl.stop - sl.start < 2:
                continue
            bh.append({"inst": n, "period": per, "first": x.c[sl.start], "last": x.c[sl.stop - 1],
                       "buy_hold_pct": (x.c[sl.stop - 1] / x.c[sl.start] - 1) * 100})
    bh = pd.DataFrame(bh)

    tr_out = prim.drop(columns=["i", "j", "kind", "primary"]).copy()
    for c in ("t_in", "t_out"):
        tr_out[c] = pd.DatetimeIndex(tr_out[c]).tz_localize("UTC").strftime("%Y-%m-%d %H:%M")
    tr_out["side"] = np.where(tr_out.side > 0, "long", "short")
    for c in ("gross", "cost", "swap", "net"):
        tr_out[c] = (tr_out[c] * 100).round(5)

    fmt = {"float_format": "%.5g", "index": False}
    summ.to_csv(out / "summary.csv", **fmt)
    ctrl.to_csv(out / "control.csv", **fmt)
    pas.to_csv(out / "pass.csv", **fmt)
    yearly.to_csv(out / "yearly_primary.csv", **fmt)
    bh.to_csv(out / "buy_hold.csv", **fmt)
    tr_out.to_csv(out / "trades_primary.csv", **fmt)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print(pas.to_string(index=False))
    print(bh.to_string(index=False))


if __name__ == "__main__":
    main()
