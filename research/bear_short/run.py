# Bear-market coin short family H1-H5 (pre-registered in cards/ayi_short.md, commit d434d10).
# Daily bars, survivorship-free universe (680 Binance USDT perps incl. delisted).
# For each hypothesis: base rule + neighbour grid, 2x cost, random-entry controls A (no regime/trigger) and
# B (BEAR days only), bootstrapped from a pool of independent random trades with the same stop/exit rules.
# Usage: python research/bear_short/run.py  -> research/bear_short/out_*.csv
import sys, itertools
import numpy as np, pandas as pd
sys.path.insert(0, "research/shortside")
from lib import load, panels, simulate, stats, split, DEV, VAL

rng = np.random.default_rng(7)
D = load(); P = panels(D)
O, H, L, C, Q, A, Fd = (P[k] for k in ["open", "high", "low", "close", "qv", "age", "fund"])
dates = C.index
cols = list(C.columns)
jb = cols.index("BTCUSDT")

# --- indicators -------------------------------------------------------------------------------
e20 = C.ewm(span=20, adjust=False, min_periods=20).mean()
e50 = C.ewm(span=50, adjust=False, min_periods=50).mean()
s200 = C.rolling(200, min_periods=200).mean()
tr = pd.concat([(H - L).stack(), (H - C.shift(1)).abs().stack(), (L - C.shift(1)).abs().stack()], axis=1).max(axis=1).unstack()
atr = tr.reindex(index=C.index, columns=C.columns).rolling(14, min_periods=14).mean()
qv30 = Q.rolling(30, min_periods=20).mean()
qv365 = Q.rolling(365, min_periods=300).mean()
rank = qv30.rank(axis=1, ascending=False)
U = (rank <= 50) & (A >= 180)
b = C["BTCUSDT"]; b50 = b.ewm(span=50, adjust=False).mean()
BEAR = (b < b50) & (b50 < b50.shift(5))
bearM = pd.DataFrame(np.repeat(BEAR.values[:, None], len(cols), 1), index=dates, columns=cols)
ret = C.pct_change(fill_method=None)
Cv = C.values
bmax10 = b.shift(1).rolling(10).max().values
bv = b.values


def mk_sig(mask, key=None):
    st = mask.fillna(False).astype(bool).stack(); st = st[st]
    if key is None:
        return [(d, s, 0.0) for d, s in st.index]
    kv = key.stack().reindex(st.index).fillna(0).values
    return [(d, s, k) for (d, s), k in zip(st.index, kv)]


def stops_from(level, sig, lo=0.03, hi=0.25):
    """absolute stop level per signal; drop signals whose distance from signal close is outside [lo, hi]."""
    out, sp = [], {}
    for d, s, k in sig:
        lv = level.at[d, s]; c = C.at[d, s]
        if not np.isfinite(lv) or not (lo <= lv / c - 1 <= hi):
            continue
        out.append((d, s, k)); sp[(d, s)] = lv
    return out, sp


def sim_indep(sig, stop, hold, exit_fn=None, stop_px=None, cost=0.002):
    """independent trades (no portfolio cap, no per-coin busy), used for the random-control pools."""
    T = []
    for x in sig:
        t = simulate(P, [x], -1, stop, hold, cost=cost, exit_fn=exit_fn, stop_px=stop_px)
        if len(t):
            T.append(t)
    return pd.concat(T) if T else pd.DataFrame()


def pool_sample(eligible, n):
    st = eligible.fillna(False).astype(bool).stack(); st = st[st]
    idx = st.index
    pick = rng.choice(len(idx), size=min(n, len(idx)), replace=False)
    return [(idx[i][0], idx[i][1], 0.0) for i in pick]


def control(T_base, eligible, make_trades, n_pool=3000, boots=2000):
    """bootstrap distribution of mean R for len(base trades) random trades, per period."""
    res = {}
    for nm, (a, z) in (("DEV", DEV), ("VAL", VAL)):
        el = eligible.copy(); el.loc[(el.index < a) | (el.index >= z)] = False
        pool = make_trades(pool_sample(el, n_pool))
        pool = pool[(pool.entry_date >= a) & (pool.entry_date < z)]
        nb = T_base[(T_base.entry_date >= a) & (T_base.entry_date < z)]
        n = len(nb)
        if n == 0 or len(pool) == 0:
            res[nm] = (np.nan, np.nan, np.nan); continue
        means = np.array([pool.R.values[rng.integers(0, len(pool), n)].mean() for _ in range(boots)])
        res[nm] = (round(means.mean(), 3), round(np.percentile(means, 95), 3), round((means >= nb.R.mean()).mean(), 3))
    return res


ROWS, CTRL = [], []


def run(name, tag, sig, stop, hold, exit_fn=None, stop_px=None, base=False, max_open=10):
    T = simulate(P, sig, -1, stop, hold, exit_fn=exit_fn, max_open=max_open, stop_px=stop_px)
    T2 = simulate(P, sig, -1, stop, hold, cost=0.004, exit_fn=exit_fn, max_open=max_open, stop_px=stop_px)
    if len(T) == 0:
        ROWS.append(dict(hyp=name, cfg=tag, base=base, per="DEV", n=0)); return T
    for per, t, t2 in zip(("DEV", "VAL"), split(T), split(T2)):
        r = stats(t, ""); r.pop("label", None)
        r2 = stats(t2, "")
        ROWS.append(dict(hyp=name, cfg=tag, base=base, per=per, **r, avgR_2x=r2.get("avgR")))
    if base:
        T.to_csv(f"research/bear_short/out_{name}_base_trades.csv", index=False)
    return T


def yearly(T, name):
    T = T.copy(); T["yr"] = T.entry_date.dt.year
    g = T.groupby("yr").R.agg(["count", "mean", "sum"]).round(3)
    g["hyp"] = name
    return g.reset_index()


YEARS = []


def finish_base(name, T, eligA, eligB, mk):
    YEARS.append(yearly(T, name))
    for lab, el in (("A_all_days", eligA), ("B_bear_days", eligB)):
        r = control(T, el, mk)
        for per in ("DEV", "VAL"):
            CTRL.append(dict(hyp=name, control=lab, per=per, ctrl_meanR=r[per][0], ctrl_p95=r[per][1], p_value=r[per][2]))


# ================= H1 Kırılım Short ============================================================
def h1(N, X, base=False):
    lowN = C.shift(1).rolling(N, min_periods=N).min()
    m = U & bearM & (C < lowN) & (C < e50)
    key = C / C.shift(20) - 1
    sig, sp = stops_from(C + 2 * atr, mk_sig(m, key))
    hiX = C.shift(1).rolling(X, min_periods=X).max().values

    def ex(k, j, e, side):
        return Cv[k, j] > hiX[k, j]
    T = run("H1", f"N{N} X{X}", sig, None, 40, exit_fn=ex, stop_px=sp, base=base)
    if base:
        def mk(sg):
            sg2, sp2 = stops_from(C + 2 * atr, sg)
            return sim_indep(sg2, None, 40, exit_fn=ex, stop_px=sp2)
        finish_base("H1", T, U, U & bearM, mk)


for N, X in itertools.product([10, 20, 40], [5, 10, 20]):
    h1(N, X, base=(N, X) == (20, 10))
print("H1 done", flush=True)

# ================= H2 BTC Kırılım Sepeti =======================================================
lr = np.log(C).diff()
beta90 = lr.rolling(90, min_periods=60).cov(lr["BTCUSDT"]).div(lr["BTCUSDT"].rolling(90, min_periods=60).var(), axis=0)
btc_bd = BEAR & (b < b.shift(1).rolling(20).min())


def ex_btc(k, j, e, side):
    return bv[k] > bmax10[k]


def h2(K, S, base=False):
    el = U.copy(); el["BTCUSDT"] = False
    br = beta90.where(el).rank(axis=1, ascending=False)
    m = (br <= K) & pd.DataFrame(np.repeat(btc_bd.values[:, None], len(cols), 1), index=dates, columns=cols)
    sig = mk_sig(m, -beta90)
    T = run("H2", f"K{K} S{int(S*100)}", sig, S, 20, exit_fn=ex_btc, base=base, max_open=max(10, K))
    if base:
        def mk(sg):
            return sim_indep(sg, S, 20, exit_fn=ex_btc)
        finish_base("H2", T, el, el & bearM, mk)


for K, S in itertools.product([5, 10, 20], [0.10, 0.15, 0.25]):
    h2(K, S, base=(K, S) == (10, 0.15))
print("H2 done", flush=True)

# ================= H3 Zombi Coin ===============================================================
U3 = (A >= 365) & (qv30 >= 2e6)
r180 = C / C.shift(180) - 1
qvr = qv30 / qv365


def h3(R, Hd, base=False):
    m = U3 & (C < s200) & (r180 <= R) & (qvr <= 0.4)
    sig = mk_sig(m, qvr)
    T = run("H3", f"R{int(R*100)} H{Hd}", sig, 0.30, Hd, base=base)
    if base:
        def mk(sg):
            return sim_indep(sg, 0.30, Hd)
        finish_base("H3", T, U3, U3 & bearM, mk)


for R, Hd in itertools.product([-0.4, -0.6, -0.8], [14, 30, 60]):
    h3(R, Hd, base=(R, Hd) == (-0.6, 30))
print("H3 done", flush=True)

# ================= H4 Funding Tuzağı ===========================================================
f3 = Fd.rolling(3, min_periods=3).mean()
r7 = C / C.shift(7) - 1


def h4(FT, Hd, base=False):
    m = U & (C < e20) & (e20 < e50) & (r7 <= -0.10) & (f3 >= FT)
    sig, sp = stops_from(C + 2 * atr, mk_sig(m, -f3))
    T = run("H4", f"F{FT*100:.2f} H{Hd}", sig, None, Hd, stop_px=sp, base=base)
    if base:
        def mk(sg):
            sg2, sp2 = stops_from(C + 2 * atr, sg)
            return sim_indep(sg2, None, Hd, stop_px=sp2)
        finish_base("H4", T, U, U & bearM, mk)


for FT, Hd in itertools.product([0.0003, 0.0005, 0.0008], [3, 7, 14]):
    h4(FT, Hd, base=(FT, Hd) == (0.0005, 7))
print("H4 done", flush=True)

# ================= H5 Hacimli Çöküş Devamı =====================================================
pos = (C - L) / (H - L).replace(0, np.nan)
qvprev = Q.shift(1).rolling(30, min_periods=20).mean()


def h5(X, Hd, base=False):
    m = U & bearM & (ret <= X) & (Q >= 3 * qvprev) & (pos <= 0.25)
    sig, sp = stops_from(H * 1.01, mk_sig(m, ret))
    T = run("H5", f"X{int(X*100)} H{Hd}", sig, None, Hd, stop_px=sp, base=base)
    if base:
        def mk(sg):
            sg2, sp2 = stops_from(H * 1.01, sg)
            return sim_indep(sg2, None, Hd, stop_px=sp2)
        finish_base("H5", T, U, U & bearM, mk)


for X, Hd in itertools.product([-0.05, -0.08, -0.12], [2, 5, 10]):
    h5(X, Hd, base=(X, Hd) == (-0.08, 5))
print("H5 done", flush=True)

# BTC short-and-hold benchmark per period
bench = []
for nm, (a, z) in (("DEV", DEV), ("VAL", VAL)):
    c = b.loc[a:z].dropna()
    bench.append(dict(per=nm, btc_short_hold_pct=round(-100 * (c.iloc[-1] / c.iloc[0] - 1), 1),
                      bear_day_share=round(BEAR.loc[a:z].mean(), 2)))

pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); pd.set_option("display.max_columns", 30)
R = pd.DataFrame(ROWS); R.to_csv("research/bear_short/out_grid.csv", index=False)
CT = pd.DataFrame(CTRL); CT.to_csv("research/bear_short/out_controls.csv", index=False)
Y = pd.concat(YEARS); Y.to_csv("research/bear_short/out_yearly.csv", index=False)
print(R.to_string(index=False)); print(CT.to_string(index=False)); print(Y.to_string(index=False)); print(pd.DataFrame(bench))
