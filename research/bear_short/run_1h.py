# Bear-market coin short, round 2 on 1h bars (pre-registered in cards/ayi_short.md, commit 22d7a70): H6-H8.
# Universe/regime from daily data of the PREVIOUS day (no lookahead). 260 symbols incl. delisted (pit1h).
# Needs: user_data/data/pit1h/*.feather (research/bear_short/fetch_klines.py), allc_1d/allc_funding feathers.
import sys, glob, itertools
import numpy as np, pandas as pd
sys.path.insert(0, "research/shortside")
from lib import load, panels, DEV, VAL

rng = np.random.default_rng(11)
OUT = "research/bear_short/"
# ---------- daily context ----------
D = load(); P = panels(D)
C, Q, A, Fd = P["close"], P["qv"], P["age"], P["fund"]
L1d = P["low"]
e20 = C.ewm(span=20, adjust=False, min_periods=20).mean()
qv30 = Q.rolling(30, min_periods=20).mean()
U = (qv30.rank(axis=1, ascending=False) <= 50) & (A >= 180)
b = C["BTCUSDT"]; b50 = b.ewm(span=50, adjust=False).mean()
BEAR = (b < b50) & (b50 < b50.shift(5))

# ---------- hourly panel ----------
files = sorted(glob.glob("user_data/data/pit1h/*-1h-futures.feather"))
syms = [f.split("/")[-1].split("_USDT")[0] + "USDT" for f in files]
hidx = pd.date_range("2020-01-01", "2026-03-31 23:00", freq="h", tz="UTC")
NH, NS = len(hidx), len(syms)
HO, HH, HL, HC = (np.full((NH, NS), np.nan, dtype=np.float64) for _ in range(4))
for j, f in enumerate(files):
    x = pd.read_feather(f).set_index("date").reindex(hidx)
    HO[:, j], HH[:, j], HL[:, j], HC[:, j] = x.open.values, x.high.values, x.low.values, x.close.values
jbtc = syms.index("BTCUSDT")
hour = hidx.hour.values
day = hidx.normalize()
nd = len(np.unique(day))
days = pd.DatetimeIndex(np.unique(day))
d_of_h = np.searchsorted(days.values, day.values)  # day number of each hour
# previous-day context per day (shift by one day)
def prev(df):
    return df.reindex(index=days, columns=syms).shift(1)
U_p = prev(U.astype(float)).fillna(0).values.astype(bool)
BEAR_p = BEAR.reindex(days).shift(1).fillna(False).values.astype(bool)
below20_p = prev((C < e20).astype(float)).fillna(0).values.astype(bool)
low_p = prev(L1d).values
fund_d = Fd.reindex(index=days, columns=syms).fillna(0).values  # sum of funding that day (paid by longs)
fset = np.isin(hour, [0, 8, 16])


def per_of(t):
    return "DEV" if t < pd.Timestamp(DEV[1], tz="UTC") else "VAL"


def sim(events, cost=0.002, slip=0.001, max_open=10):
    """events: list of (signal_hour, j, stop_level, max_exit_hour). short at open of signal_hour+1.
    exit on stop (high >= stop) or at close of max_exit_hour. Funding: each 00/08/16 hour passed earns 1/3 day funding."""
    ev = sorted(events, key=lambda x: (x[0], x[1]))
    out, busy, opn = [], {}, []
    for h, j, sp, hx in ev:
        i = h + 1
        if i >= NH or busy.get(j, -1) >= i:
            continue
        e = HO[i, j]
        if not np.isfinite(e) or not np.isfinite(sp):
            continue
        sd = sp / e - 1
        if sd <= 0.002 or sd > 0.25:
            continue
        opn = [x for x in opn if x >= i]
        if max_open and len(opn) >= max_open:
            continue
        k, why, ex, fund = i, "time", None, 0.0
        hx = min(hx, NH - 1)
        while True:
            if not np.isfinite(HO[k, j]):
                ex, why, k = HC[k - 1, j], "gap", k - 1
                break
            if fset[k] and k > i:
                fund += fund_d[d_of_h[k], j] / 3
            if HO[k, j] >= sp:
                ex, why = HO[k, j] * (1 + slip), "stop_gap"; break
            if HH[k, j] >= sp:
                ex, why = sp * (1 + slip), "stop"; break
            if k >= hx:
                ex = HC[k, j]; break
            k += 1
        if not np.isfinite(ex):
            continue
        gross = -(ex / e - 1)
        net = gross - cost + fund
        out.append(dict(entry=hidx[i], sym=syms[j], why=why, gross=gross, fund=fund, net=net, R=net / sd, stop=sd, hours=k - i + 1))
        busy[j] = k; opn.append(k)
    T = pd.DataFrame(out)
    if len(T):
        T["per"] = [per_of(t) for t in T.entry]
    return T


def st(T, risk=0.01):
    if len(T) == 0:
        return dict(n=0)
    eq = (1 + risk * T.R).cumprod(); dd = (1 - eq / eq.cummax()).max()
    w = T.R[T.R > 0].sum(); l = -T.R[T.R < 0].sum()
    return dict(n=len(T), avgR=round(T.R.mean(), 3), PF=round(w / l, 2) if l > 0 else np.inf, win=round((T.R > 0).mean(), 2),
                avg_net_pct=round(100 * T.net.mean(), 3), eq_pct=round(100 * (eq.iloc[-1] - 1), 1), maxDD_pct=round(100 * dd, 1),
                hours=round(T.hours.mean(), 1))


ROWS, CTRL = [], []


def record(hyp, cfg, base, T, T2):
    for per in ("DEV", "VAL"):
        t = T[T.per == per] if len(T) else T; t2 = T2[T2.per == per] if len(T2) else T2
        ROWS.append(dict(hyp=hyp, cfg=cfg, base=base, per=per, **st(t), avgR_2x=st(t2).get("avgR")))


def control(hyp, Tb, make_pool, lab):
    for per in ("DEV", "VAL"):
        nb = Tb[Tb.per == per]; pool = make_pool(per)
        pool = pool[pool.per == per] if len(pool) else pool
        if len(nb) == 0 or len(pool) == 0:
            continue
        m = np.array([pool.R.values[rng.integers(0, len(pool), len(nb))].mean() for _ in range(2000)])
        CTRL.append(dict(hyp=hyp, control=lab, per=per, n=len(nb), base_avgR=round(nb.R.mean(), 3), ctrl_meanR=round(m.mean(), 3),
                         ctrl_p95=round(np.percentile(m, 95), 3), p_value=round((m >= nb.R.mean()).mean(), 3)))


def per_mask(per):
    a, z = (DEV, VAL)[per == "VAL"]
    return (hidx >= pd.Timestamp(a, tz="UTC")) & (hidx < pd.Timestamp(z, tz="UTC"))


# ================= H6 Gün Dibi Kırılımı =====================================================
def h6_events(exit_mode, buf):
    ev = []
    elig = U_p & BEAR_p[:, None] & below20_p  # per day x sym
    for dn, js in zip(*np.nonzero(elig)):
        h0 = np.searchsorted(d_of_h, dn)
        if h0 + 24 > NH:
            continue
        pl = low_p[dn, js]
        c = HC[h0:h0 + 20, js]
        hit = np.nonzero(c < pl)[0]
        if len(hit) == 0:
            continue
        h = h0 + hit[0]
        if h - 2 < 0:
            continue
        sp = np.nanmax(HH[h - 2:h + 1, js]) * (1 + buf)
        e_est = HC[h, js]
        if not (0.01 <= sp / e_est - 1 <= 0.06):
            continue
        hx = {"day": h0 + 23, "6h": h + 6, "24h": h + 24}[exit_mode]
        ev.append((h, js, sp, hx))
    return ev


for ex_m, buf in itertools.product(["day", "6h", "24h"], [0.002, 0.005]):
    ev = h6_events(ex_m, buf)
    base = (ex_m, buf) == ("day", 0.002)
    T = sim(ev); T2 = sim(ev, cost=0.004)
    record("H6", f"exit={ex_m} buf={buf}", base, T, T2)
    if base:
        T.to_csv(OUT + "out_H6_base_trades.csv", index=False)
        H6base = T

# controls for H6: random hour 0-19 on eligible days (A: U only, any regime; B: U & BEAR)
def h6_random(per, bear_only, n=4000):
    elig = U_p & (BEAR_p[:, None] if bear_only else True)
    dn_all, js_all = np.nonzero(elig)
    a, z = (DEV, VAL)[per == "VAL"]
    dmask = (days[dn_all] >= pd.Timestamp(a, tz="UTC")) & (days[dn_all] < pd.Timestamp(z, tz="UTC"))
    dn_all, js_all = dn_all[dmask], js_all[dmask]
    pick = rng.choice(len(dn_all), size=min(n, len(dn_all)), replace=False)
    ev = []
    for p in pick:
        dn, js = dn_all[p], js_all[p]
        h0 = np.searchsorted(d_of_h, dn); h = h0 + rng.integers(2, 20)
        if h0 + 24 > NH or not np.isfinite(HC[h, js]):
            continue
        sp = np.nanmax(HH[h - 2:h + 1, js]) * 1.002
        if not (0.01 <= sp / HC[h, js] - 1 <= 0.06):
            continue
        ev.append((h, js, sp, h0 + 23))
    return sim(ev, max_open=None)


control("H6", H6base, lambda per: h6_random(per, False), "A_all_days")
control("H6", H6base, lambda per: h6_random(per, True), "B_bear_days")
print("H6 done", flush=True)

# ================= H7 Saat Penceresi (two stage) ============================================
# basket short return per BEAR day for every (start hour, length) window, equal weight over U_p coins (no BTC)
lr_cols = [j for j in range(NS) if j != jbtc]
win_rows = []
bear_days = np.nonzero(BEAR_p)[0]
for dn in bear_days:
    h0 = np.searchsorted(d_of_h, dn)
    js = [j for j in lr_cols if U_p[dn, j]]
    if not js or h0 + 24 + 12 > NH:
        continue
    for s in range(24):
        for Lh in (4, 6, 8, 12):
            i, k = h0 + s, h0 + s + Lh - 1
            o, c = HO[i, js], HC[k, js]
            r = -(c / o - 1)
            nf = sum(fset[i + 1:k + 1])  # funding hours passed (approx: crossing 00/08/16)
            fd = fund_d[dn, js] / 3 * nf
            v = np.isfinite(r)
            if v.sum() < 5:
                continue
            win_rows.append((days[dn], s, Lh, np.nanmean((r + fd)[v])))
W = pd.DataFrame(win_rows, columns=["day", "start", "len", "gross_plus_fund"])
W["per"] = np.where(W.day < pd.Timestamp(DEV[1], tz="UTC"), "DEV", "VAL")
for cst in (0.002, 0.004):
    W[f"net_{cst}"] = W.gross_plus_fund - cst
G = W.groupby(["per", "start", "len"]).agg(n=("net_0.002", "size"), net=("net_0.002", "mean"), net2x=("net_0.004", "mean")).reset_index()
G.to_csv(OUT + "out_H7_windows.csv", index=False)
best = G[G.per == "DEV"].sort_values("net", ascending=False).iloc[0]
s0, L0 = int(best.start), int(best["len"])
for per in ("DEV", "VAL"):
    g = G[(G.per == per) & (G.start == s0) & (G["len"] == L0)].iloc[0]
    ROWS.append(dict(hyp="H7", cfg=f"start={s0} len={L0} (chosen in DEV)", base=True, per=per, n=int(g.n),
                     avg_net_pct=round(100 * g.net, 3), avgR_2x=None, avg_net2x_pct=round(100 * g.net2x, 3)))
    # control: random windows of same length on BEAR days in that period
    pool = W[(W.per == per) & (W["len"] == L0)]["net_0.002"].values
    m = np.array([pool[rng.integers(0, len(pool), int(g.n))].mean() for _ in range(2000)])
    CTRL.append(dict(hyp="H7", control="random window same len, BEAR days", per=per, n=int(g.n), base_avgR=round(100 * g.net, 3),
                     ctrl_meanR=round(100 * m.mean(), 3), ctrl_p95=round(100 * np.percentile(m, 95), 3), p_value=round((m >= g.net).mean(), 3)))
print("H7 done", flush=True)

# ================= H8 BTC Şoku Gecikmesi ====================================================
hr = HC / HO - 1
def h8_events(hold, stop):
    ev = []
    shock = np.nonzero((hr[:, jbtc] <= -0.015) & BEAR_p[d_of_h])[0]
    for h in shock:
        dn = d_of_h[h]
        for j in range(NS):
            if j == jbtc or not U_p[dn, j] or not np.isfinite(hr[h, j]):
                continue
            if hr[h, j] >= hr[h, jbtc] + 0.01:
                ev.append((h, j, HC[h, j] * (1 + stop), h + hold))
    return ev


for hold, stop in itertools.product([1, 4, 12], [0.02, 0.03, 0.05]):
    ev = h8_events(hold, stop)
    base = (hold, stop) == (4, 0.03)
    T = sim(ev); T2 = sim(ev, cost=0.004)
    record("H8", f"hold={hold}h stop={stop}", base, T, T2)
    if base:
        H8base = T; T.to_csv(OUT + "out_H8_base_trades.csv", index=False)


def h8_random(per, bear_only, n=4000):
    m = per_mask(per) & (BEAR_p[d_of_h] if bear_only else True)
    hs = np.nonzero(m)[0]
    ev = []
    for _ in range(n):
        h = hs[rng.integers(0, len(hs))]; dn = d_of_h[h]
        js = np.nonzero(U_p[dn])[0]
        if len(js) == 0:
            continue
        j = js[rng.integers(0, len(js))]
        if np.isfinite(HC[h, j]):
            ev.append((h, j, HC[h, j] * 1.03, h + 4))
    return sim(ev, max_open=None)


control("H8", H8base, lambda per: h8_random(per, False), "A_all_hours")
control("H8", H8base, lambda per: h8_random(per, True), "B_bear_hours")
print("H8 done", flush=True)

pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); pd.set_option("display.max_columns", 30)
R = pd.DataFrame(ROWS); R.to_csv(OUT + "out_1h_grid.csv", index=False)
CT = pd.DataFrame(CTRL); CT.to_csv(OUT + "out_1h_controls.csv", index=False)
print(R.to_string(index=False)); print(CT.to_string(index=False))
print(G[G.per == "DEV"].sort_values("net", ascending=False).head(10).to_string(index=False))
