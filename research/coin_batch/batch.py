"""Coin idea batch (8 daily ideas, long and short), pre-registered in results/2026-11-09_coin_batch/README.md.

Holdout (>= 2026-04-01) is cut at load time and never used.
Run: /home/user/ftenv/bin/python -I research/coin_batch/batch.py
"""
from __future__ import annotations

import glob
import io
import json
import os
import zipfile

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "user_data", "data")
OUT = os.path.join(ROOT, "results", "2026-11-09_coin_batch")
HOLDOUT = pd.Timestamp("2026-04-01", tz="UTC")
PERIODS = {"dev": (pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2024-12-31", tz="UTC")),
           "val": (pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-03-31", tz="UTC"))}
COST = 0.002          # round trip
N_RAND = 1000
SEED = 20261109
STABLES = {"USDCUSDT", "BUSDUSDT", "TUSDUSDT", "USDPUSDT", "FDUSDUSDT", "DAIUSDT"}
SLOTS = {"F1": 2, "F2": 36, "F3": 3, "F4": 10, "F5": 1, "F6": 36, "F7": 1, "F8": 36}
MAIN = {"F1": "N120", "F2": "L60", "F3": "k0.5_H1", "F4": "z2.5_H3", "F5": "main", "F6": "X0.95_H14",
        "F7": "N50", "F8": "p5_H5", "F3real": "k0.5_H1_real"}
UNI = {int(y): set(v) for y, v in json.load(open(os.path.join(ROOT, "research/xsec/top36_yearly.json"))).items()}
DAY = pd.Timedelta(days=1)


# ------------------------------------------------------------------ data

def load_xsec():
    d = pd.read_feather(os.path.join(DATA, "xsec_all_1d.feather"))
    d = d[d["date"] < HOLDOUT]
    C = d.pivot(index="date", columns="symbol", values="close").sort_index()
    V = d.pivot(index="date", columns="symbol", values="quote_volume").sort_index()
    full = pd.date_range(PERIODS["dev"][0], C.index.max(), freq="D", tz="UTC")
    assert C.index.max() < HOLDOUT
    return C.reindex(full), V.reindex(full)


def funding_events(sym: str) -> pd.Series:
    """Funding events (rate per event, timestamp rounded to the hour), holdout cut."""
    base = sym[:-4]
    f = os.path.join(DATA, "binance/futures", f"{base}_USDT_USDT-1h-funding_rate.feather")
    if os.path.exists(f):
        d = pd.read_feather(f)
        s = pd.Series(d["funding_rate"].values, index=pd.to_datetime(d["date"], utc=True))
    else:
        rows = []
        for z in sorted(glob.glob(os.path.join(DATA, f"binance_vision_raw/fundingRate/{sym}/*.zip"))):
            ym = z.rsplit("-fundingRate-", 1)[1][:7]
            if pd.Timestamp(ym + "-01", tz="UTC") >= HOLDOUT:
                continue
            with zipfile.ZipFile(z) as zf:
                rows.append(pd.read_csv(io.BytesIO(zf.read(zf.namelist()[0]))))
        if not rows:
            return pd.Series(dtype=float)
        d = pd.concat(rows)
        s = pd.Series(d["last_funding_rate"].values, index=pd.to_datetime(d["calc_time"], unit="ms", utc=True))
    s.index = s.index.round("h")
    s = s[~s.index.duplicated()].sort_index()
    return s[s.index < HOLDOUT]


def funding_daily(syms, index):
    """FD[t] = sum of events in (t 00:00, t+1 00:00] (charged to the position held over day t);
    FM[t] = mean of events in [t 00:00, t+1 00:00) (known at the close of day t). Missing symbols listed."""
    fd, fm, missing = {}, {}, []
    for s in syms:
        e = funding_events(s)
        if e.empty:
            missing.append(s)
            continue
        fd[s] = e.groupby((e.index - pd.Timedelta(seconds=1)).floor("D")).sum()
        fm[s] = e.groupby(e.index.floor("D")).mean()
    FD = pd.DataFrame(fd).reindex(index=index, columns=list(syms)).fillna(0.0)
    FM = pd.DataFrame(fm).reindex(index=index, columns=list(syms))
    return FD, FM, missing


def load_ohlc(assets, index):
    o, h, l, c = {}, {}, {}, {}
    for a in assets:
        d = pd.read_feather(os.path.join(DATA, "binance/futures", f"{a}_USDT_USDT-1d-futures.feather"))
        d = d[d["date"] < HOLDOUT].set_index("date")
        o[a + "USDT"], h[a + "USDT"], l[a + "USDT"], c[a + "USDT"] = d["open"], d["high"], d["low"], d["close"]
    f = lambda x: pd.DataFrame(x).reindex(index)
    return f(o), f(h), f(l), f(c)


def universe_mask(C: pd.DataFrame) -> pd.DataFrame:
    m = pd.DataFrame(False, index=C.index, columns=C.columns)
    for y, syms in UNI.items():
        rows = C.index.year == y
        cols = [s for s in syms if s in C.columns]
        m.loc[rows, cols] = True
    return m & C.notna()


def vol30(C: pd.DataFrame) -> pd.DataFrame:
    return np.log(C).diff().rolling(30, min_periods=30).std() * np.sqrt(365)


# ------------------------------------------------------------------ panel + evaluation

class Panel:
    """Prices and funding as numpy arrays on the common daily index."""

    def __init__(self, C, FD, O=None, S=None, M=None):
        self.dates = C.index
        self.cols = list(C.columns)
        self.C = C.values.astype(float)
        self.O = None if O is None else O[self.cols].values.astype(float)
        self.CF = np.cumsum(FD[self.cols].fillna(0.0).values, axis=0)
        self.S = np.ones_like(self.C) if S is None else S[self.cols].values.astype(float)
        self.M = C.notna().values if M is None else M[self.cols].values
        self.T = len(self.dates)
        self.pidx = {p: (int(self.dates.searchsorted(s)), int(self.dates.searchsorted(e, side="right")) - 1)
                     for p, (s, e) in PERIODS.items()}

    def period_of(self, i):
        for p, (a, b) in self.pidx.items():
            if a <= i <= b:
                return p
        return None

    def trade(self, j, side, e, x, kind="close", entry_px=None, size=None):
        size = self.S[e, j] if size is None else size
        if kind == "close":
            px_in, f = self.C[e, j], self.CF[x, j] - self.CF[e, j]
        else:  # entered during day e at entry_px (or the open), funding of day e..x charged
            px_in = self.O[e, j] if entry_px is None else entry_px
            f = self.CF[x, j] - (self.CF[e - 1, j] if e > 0 else 0.0)
        gross = side * (self.C[x, j] / px_in - 1.0) - side * f
        return {"sym": self.cols[j], "j": j, "side": side, "e": e, "x": x, "kind": kind, "size": size,
                "gross": size * gross, "net": size * (gross - COST), "net2x": size * (gross - 2 * COST),
                "period": self.period_of(e), "entry": self.dates[e], "exit": self.dates[x]}

    def rand_vec(self, j, side, h, period, kind):
        """Net returns of every eligible random entry (same coin, side, hold, period, universe rule)."""
        a, b = self.pidx[period]
        e = np.arange(max(a, 1), b + 1)
        x = e + h if kind == "close" else e + h - 1
        ok = x <= self.T - 1
        e, x = e[ok], x[ok]
        ok = self.M[e, j] & np.isfinite(self.C[e, j]) & np.isfinite(self.C[x, j]) & np.isfinite(self.S[e, j])
        if kind == "open":
            ok &= np.isfinite(self.O[e, j])
        e, x = e[ok], x[ok]
        if kind == "close":
            px_in, f = self.C[e, j], self.CF[x, j] - self.CF[e, j]
        else:
            px_in, f = self.O[e, j], self.CF[x, j] - self.CF[e - 1, j]
        g = side * (self.C[x, j] / px_in - 1.0) - side * f
        return self.S[e, j] * (g - COST)


def profit_factor(r):
    w, l = r[r > 0].sum(), -r[r < 0].sum()
    return np.inf if l == 0 else w / l


def max_dd(trades: list[dict], k: int) -> float:
    """Exit-based shared equity (1.0 start), P&L = equity at entry x (1/k) x net (paper_portfoy logic)."""
    ev = []
    for i, t in enumerate(trades):
        ev.append((t["entry"] + pd.Timedelta(hours=12 if t["kind"] == "open" else 23, minutes=0 if t["kind"] == "open" else 59), 1, i))
        ev.append((t["exit"] + pd.Timedelta(hours=23, minutes=59), 0, i))  # exit at the close of day x
    ev.sort(key=lambda z: (z[0], z[1]))
    eq, peak, dd, eq_in = 1.0, 1.0, 0.0, {}
    for _, kind, i in ev:
        if kind == 1:
            eq_in[i] = eq
            continue
        eq += eq_in[i] / k * trades[i]["net"]
        peak = max(peak, eq)
        dd = max(dd, 1 - eq / peak)
    return dd


def evaluate(panel: Panel, trades: list[dict], idea: str, cfg: str, rng, control=True) -> list[dict]:
    rows = []
    for side in (1, -1):
        for per in PERIODS:
            tt = [t for t in trades if t["side"] == side and t["period"] == per]
            if not tt:
                continue
            r = np.array([t["net"] for t in tt])
            row = {"idea": idea, "config": cfg, "side": "long" if side > 0 else "short", "period": per,
                   "trades": len(tt), "avg_net_pct": r.mean() * 100, "pf": profit_factor(r),
                   "win_rate": (r > 0).mean() * 100, "avg_net_2x_pct": np.mean([t["net2x"] for t in tt]) * 100,
                   "sum_net": r.sum(), "avg_hold_days": np.mean([t["x"] - t["e"] + (t["kind"] == "open") for t in tt]),
                   "avg_size": np.mean([t["size"] for t in tt]), "max_dd_pct": max_dd(tt, SLOTS[idea]) * 100}
            if control:
                cache, sums, used = {}, np.zeros(N_RAND), 0
                for t in tt:
                    h = t["x"] - t["e"] + (1 if t["kind"] == "open" else 0)
                    key = (t["j"], side, h, per, t["kind"])
                    if key not in cache:
                        cache[key] = panel.rand_vec(t["j"], side, h, per, t["kind"])
                    v = cache[key]
                    if len(v) == 0:
                        continue
                    sums += v[rng.integers(0, len(v), N_RAND)]
                    used += 1
                rm = sums / max(used, 1)
                row["rand_avg_pct"] = rm.mean() * 100
                row["p_rand"] = (1 + (rm >= r.mean()).sum()) / (N_RAND + 1)
            rows.append(row)
    return rows


# ------------------------------------------------------------------ the 8 ideas

def f1_trades(P: Panel, sma: np.ndarray) -> list[dict]:
    out = []
    for j in range(len(P.cols)):
        e = None
        for t in range(P.T):
            c, m = P.C[t, j], sma[t, j]
            if not np.isfinite(m) or not np.isfinite(c):
                continue
            if e is None and c > m and np.isfinite(P.S[t, j]):
                e = t
            elif e is not None and c <= m:
                out.append(P.trade(j, 1, e, t)); e = None
        if e is not None and e < P.T - 1:
            out.append(P.trade(j, 1, e, P.T - 1))
    return out


def f2_trades(P: Panel, sgn: np.ndarray, U: np.ndarray, next_ok: np.ndarray) -> list[dict]:
    """sgn: entry signal (+1/-1/nan), U: in universe, next_ok[t,j]: coin stays (False on 31 Dec if not in next list)."""
    out = []
    for j in range(len(P.cols)):
        pos, e = 0, None
        for t in range(P.T):
            last = t == P.T - 1 or not np.isfinite(P.C[t + 1, j])
            s = sgn[t, j]
            if pos != 0 and (s != pos or last or not next_ok[t, j]):
                out.append(P.trade(j, pos, e, t)); pos, e = 0, None
            if pos == 0 and U[t, j] and np.isfinite(s) and s != 0 and not last and next_ok[t, j] and np.isfinite(P.S[t, j]):
                pos, e = int(s), t
    return out


def fixed_hold(P: Panel, sig: np.ndarray, side: int, h: int) -> list[dict]:
    """Enter at the close of a signal day, exit h days later (or at the last close of the coin)."""
    out = []
    for j in range(len(P.cols)):
        busy = -1
        for t in np.where(sig[:, j])[0]:
            if t <= busy or t >= P.T - 1:
                continue
            x = min(t + h, P.T - 1)
            while not np.isfinite(P.C[x, j]):
                x -= 1
            if x <= t:
                continue
            out.append(P.trade(j, side, t, x)); busy = x
    return out


def f3_trades(P: Panel, H_: np.ndarray, L_: np.ndarray, atr: np.ndarray, k: float, hold: int,
              skip_both: bool = True) -> list[dict]:
    """skip_both=True is the pre-registered rule (no trade on a day both levels were hit). That rule looks ahead:
    whether the other level is hit later in the day is unknown at the entry. skip_both=False is the realistic
    stand-alone side (a stop entry at the level fills whenever the level is touched, exit at the close)."""
    out = []
    up, dn = P.O + k * atr, P.O - k * atr
    hit_up, hit_dn = H_ >= up, L_ <= dn
    if skip_both:
        hit_up, hit_dn = hit_up & ~hit_dn, hit_dn & ~(H_ >= up)
    for j in range(len(P.cols)):
        for side, hit, lvl in ((1, hit_up, up), (-1, hit_dn, dn)):
            busy = -1
            for t in np.where(hit[:, j] & np.isfinite(atr[:, j]))[0]:
                if t <= busy:
                    continue
                x = min(t + hold - 1, P.T - 1)
                out.append(P.trade(j, side, t, x, kind="open", entry_px=lvl[t, j])); busy = x
    return out


def f7_regimes(P: Panel, alt_on: np.ndarray, valid: np.ndarray) -> list[dict]:
    out, cur, e = [], None, None
    for t in range(P.T):
        if not valid[t]:
            continue
        want = 0 if alt_on[t] else 1  # column 0 = ALT basket, 1 = BTC
        if cur is None:
            cur, e = want, t
        elif want != cur:
            out.append(P.trade(cur, 1, e, t)); cur, e = want, t
    if cur is not None and e < P.T - 1:
        out.append(P.trade(cur, 1, e, P.T - 1))
    return out


def buy_hold(C, FD, U):
    rows = []
    r = C.pct_change(fill_method=None)
    btc = r["BTCUSDT"].fillna(0) - FD["BTCUSDT"]
    ew = (r.where(U.shift(1, fill_value=False) & U) - FD.where(U)).mean(axis=1).fillna(0)
    for name, s in (("BTC 1x long", btc), ("PIT top-36 eşit ağırlık 1x long", ew)):
        for per, (a, b) in PERIODS.items():
            p = s[(s.index >= a) & (s.index <= b)]
            eq = (1 + p).cumprod()
            rows.append({"benchmark": name, "period": per, "total_ret_pct": (eq.iloc[-1] - 1) * 100,
                         "cagr_pct": (eq.iloc[-1] ** (365 / len(p)) - 1) * 100,
                         "max_dd_pct": (1 - eq / eq.cummax()).max() * 100})
    return pd.DataFrame(rows)


def main():
    rng = np.random.default_rng(SEED)
    C, V = load_xsec()
    idx = C.index
    U_all = universe_mask(C)
    vol_q = V.rolling(30, min_periods=30).mean()
    top10 = vol_q.drop(columns=[s for s in STABLES if s in vol_q.columns]).rank(axis=1, ascending=False) <= 10
    top10 = top10 & C.notna()
    pit = sorted({s for v in UNI.values() for s in v})
    need = sorted(set(pit) | set(top10.columns[top10.any()]) | {"BTCUSDT", "ETHUSDT", "SOLUSDT"})
    FD, FM, missing = funding_daily(need, idx)
    print("funding missing for:", missing)
    rows, trades_all = [], []

    def run(idea, cfg, P, tr, control=True):
        res = evaluate(P, tr, idea, cfg, rng, control)
        rows.extend(res)
        if cfg in (MAIN[idea], MAIN.get(idea + "real")):
            trades_all.extend({**{k: v for k, v in t.items() if k != "j"}, "idea": idea} for t in tr)
        for r in res:
            print(f"{idea} {cfg:10s} {r['side']:5s} {r['period']} n={r['trades']:5d} avg={r['avg_net_pct']:+.3f}% "
                  f"pf={r['pf']:.2f} win={r['win_rate']:.0f}% 2x={r['avg_net_2x_pct']:+.3f}% dd={r['max_dd_pct']:.1f}% "
                  f"p={r.get('p_rand', float('nan')):.3f}", flush=True)

    # F1 BTC/ETH trend long-or-cash
    c1 = C[["BTCUSDT", "ETHUSDT"]]
    S1 = (0.20 / vol30(c1)).clip(upper=3.0)
    for n in (60, 120, 200):
        sma = c1.rolling(n, min_periods=n).mean()
        P = Panel(c1, FD, S=S1, M=c1.notna() & sma.notna())
        run("F1", f"N{n}", P, f1_trades(P, sma.values))

    # F2 coin TSMOM, PIT top-36
    cu = C[[s for s in pit if s in C.columns]]
    Uu = U_all[cu.columns]
    S2 = (0.50 / vol30(cu)).clip(upper=2.0)
    nxt = pd.DataFrame(True, index=idx, columns=cu.columns)
    for y in UNI:
        d = pd.Timestamp(f"{y}-12-31", tz="UTC")
        if d in idx:
            nxt.loc[d] = [s in UNI.get(y + 1, set()) for s in cu.columns]
    age = cu.notna().cumsum()
    for L in (20, 60, 120):
        sg = np.sign(cu / cu.shift(L) - 1).where(age >= L + 30)
        P = Panel(cu, FD, S=S2, M=Uu & sg.notna())
        run("F2", f"L{L}", P, f2_trades(P, sg.values, Uu.values, nxt.values))

    # F3 daily volatility breakout, BTC/ETH/SOL
    O3, H3, L3, C3 = load_ohlc(["BTC", "ETH", "SOL"], idx)
    tr_ = pd.concat({"a": H3 - L3, "b": (H3 - C3.shift(1)).abs(), "c": (L3 - C3.shift(1)).abs()}).groupby(level=1).max()
    tr_ = tr_.reindex(idx)
    atr = tr_.rolling(14, min_periods=14).mean().shift(1)
    P3 = Panel(C3, FD, O=O3, M=atr.notna() & O3.notna())
    for k in (0.3, 0.5, 0.8):
        for h in (1, 3):
            run("F3", f"k{k}_H{h}", P3, f3_trades(P3, H3.values, L3.values, atr.values, k, h))
            # lookahead-free version of the same rule (see f3_trades); the verdict is also given on this one
            run("F3", f"k{k}_H{h}_real", P3, f3_trades(P3, H3.values, L3.values, atr.values, k, h, skip_both=False))

    # F4 extreme down day, top-10 by volume
    c4 = C[top10.columns[top10.any()]]
    t4 = top10[c4.columns]
    r4 = c4.pct_change(fill_method=None)
    sd = r4.rolling(60, min_periods=60).std().shift(1)
    P4 = Panel(c4, FD, M=t4 & sd.notna())
    for z in (2.0, 2.5, 3.0):
        sig = (t4 & (r4 <= -z * sd)).values
        for h in (1, 3, 5):
            run("F4", f"z{z}_H{h}", P4, fixed_hold(P4, sig, 1, h))

    # F5 day of week, BTC
    c5 = C[["BTCUSDT"]]
    P5 = Panel(c5, FD)
    wd = idx.weekday.values
    lm = fixed_hold(P5, (wd == 6)[:, None], 1, 1)        # Sunday close -> Monday close
    sm = fixed_hold(P5, (wd == 4)[:, None], -1, 2)       # Friday close -> Sunday close
    run("F5", "main", P5, lm + sm)
    names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    for d in range(7):
        prev = (d - 1) % 7
        tr5 = fixed_hold(P5, (wd == prev)[:, None], 1, 1) + fixed_hold(P5, (wd == prev)[:, None], -1, 1)
        run("F5", f"day_{names[d]}", P5, tr5, control=False)

    # F6 52-week-high proximity, PIT top-36
    hi = cu.rolling(365, min_periods=365).max()
    ratio = cu / hi
    P6 = Panel(cu, FD, M=Uu & ratio.notna())
    sunday = (idx.weekday == 6)[:, None]
    for X in (0.90, 0.95):
        sig = (Uu & (ratio >= X)).values & sunday
        for h in (7, 14, 28):
            run("F6", f"X{X:.2f}_H{h}", P6, fixed_hold(P6, sig, 1, h))

    # F7 BTC dominance regime: ALT basket vs BTC
    alts = [s for s in cu.columns if s != "BTCUSDT"]
    ra = cu[alts].pct_change(fill_method=None)
    ok = Uu[alts] & Uu[alts].shift(1, fill_value=False) & ra.notna()
    basket = ra.where(ok).mean(axis=1).fillna(0.0)
    fbask = FD[alts].where(ok).mean(axis=1).fillna(0.0)
    alt_idx = (1 + basket).cumprod()
    c7 = pd.DataFrame({"ALT": alt_idx, "BTCUSDT": C["BTCUSDT"]})
    fd7 = pd.DataFrame({"ALT": fbask, "BTCUSDT": FD["BTCUSDT"]})
    rat = c7["ALT"] / c7["BTCUSDT"]
    for n in (20, 50, 100):
        sm7 = rat.rolling(n, min_periods=n).mean()
        P7 = Panel(c7, fd7, M=pd.DataFrame({"ALT": sm7.notna(), "BTCUSDT": sm7.notna()}))
        tr7 = f7_regimes(P7, (rat > sm7).values, sm7.notna().values)
        run("F7", f"N{n}", P7, tr7)
        for leg in ("ALT", "BTCUSDT"):
            run("F7", f"N{n}_{leg}", P7, [t for t in tr7 if t["sym"] == leg], control=(n == 50))

    # F8 daily funding extreme + turn, PIT top-36
    fm = FM[cu.columns]
    lo5 = cu.shift(1).rolling(5, min_periods=5).min()
    hi5 = cu.shift(1).rolling(5, min_periods=5).max()
    P8 = Panel(cu, FD, M=Uu & fm.notna())
    for p in (5, 10):
        qh = fm.rolling(365, min_periods=180).quantile(1 - p / 100).shift(1)
        ql = fm.rolling(365, min_periods=180).quantile(p / 100).shift(1)
        sig_s = (Uu & (fm >= qh) & (fm > 0) & (cu < lo5)).values
        sig_l = (Uu & (fm <= ql) & (cu > hi5)).values
        for h in (3, 5, 10):
            run("F8", f"p{p}_H{h}", P8, fixed_hold(P8, sig_l, 1, h) + fixed_hold(P8, sig_s, -1, h))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "all_configs.csv"), index=False)
    pd.DataFrame(trades_all).to_csv(os.path.join(OUT, "main_trades.csv"), index=False)
    bh = buy_hold(C, FD, U_all)
    bh.to_csv(os.path.join(OUT, "buy_hold.csv"), index=False)
    print(bh.round(1).to_string())

    # verdicts (main config only)
    ver = []
    for key, cfg in MAIN.items():
        idea = key[:2]
        m = df[(df.idea == idea) & (df.config == cfg)]
        for side in ("long", "short"):
            s = m[m.side == side].set_index("period")
            if not {"dev", "val"} <= set(s.index):
                continue
            g = lambda c, p: s.loc[p, c]
            checks = {
                "net_pos": g("avg_net_pct", "dev") > 0 and g("avg_net_pct", "val") > 0,
                "pf_1.2": g("pf", "dev") >= 1.2 and g("pf", "val") >= 1.2,
                "rand_p<0.05_dev": g("p_rand", "dev") < 0.05,
                "cost2x_pos": g("avg_net_2x_pct", "dev") > 0 and g("avg_net_2x_pct", "val") > 0,
                "val_30": g("trades", "val") >= 30,
                "dd_25": g("max_dd_pct", "dev") <= 25 and g("max_dd_pct", "val") <= 25,
            }
            ver.append({"idea": idea, "config": cfg, "side": side, **checks, "PASS": all(checks.values())})
    v = pd.DataFrame(ver)
    v.to_csv(os.path.join(OUT, "pass_fail.csv"), index=False)
    print(v.to_string())


if __name__ == "__main__":
    main()
