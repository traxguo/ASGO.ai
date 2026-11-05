# Realistic book for the new-listing short (2026-11-04): positions are NOT rebalanced daily (run_weights does
# that, which quietly shrinks a short while the coin squeezes). Each trade: at entry, short 5% of equity in the
# coin (isolated, 1x: the loss is capped at the 5% margin = liquidation) and long 5% of equity in BTC as hedge.
# Max 20 open trades. Close-based 30/60% stop, exit after M days or when the coin stops trading.
# Cost 0.10% per order (0.20% round trip) on both legs, funding on both legs. Grid N 5/7/10/14, M 20/30/45, S 30/60%.
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "research/neutral")
from common import load, PERIODS, buy_hold  # noqa: E402

SLOT, MAXOPEN = 0.05, 20
# INTRA=1: the stop is checked on 1h highs (research/neutral/fetch_newlist_1h.py) and fills at
# max(hour open, stop) + 0.2% extra slippage, instead of only at the daily close.
INTRA = len(sys.argv) > 1 and sys.argv[1] == "intra"
if INTRA:
    H = pd.read_feather("user_data/data/newlist_1h.feather")
    HG = {s: g.set_index("date").sort_index() for s, g in H.groupby("symbol")}
C, R, U, F = load()
D = pd.read_feather("user_data/data/xsec_all_1d.feather")
Vv = D.pivot(index="date", columns="symbol", values="quote_volume").reindex(C.index)
vr = Vv.rolling(30, min_periods=5).mean().rank(axis=1, ascending=False)
first = C.apply(lambda s: s.first_valid_index())
first = first[(first > pd.Timestamp("2020-02-01", tz="UTC")) & (first.index != "BTCUSDT")]
PX, FX = C.values, F.values
cols = {c: i for i, c in enumerate(C.columns)}
kb = cols["BTCUSDT"]
start_at = {}
for sym, f in first.items():
    i0 = C.index.get_loc(f)
    start_at.setdefault(i0, []).append(sym)


def intra_stop(sym, i, p0, S, M):
    g = HG.get(sym)
    if g is None:
        return None, None
    a = C.index[i] + pd.Timedelta(days=1)
    h = g[(g.index >= a) & (g.index < a + pd.Timedelta(days=M))]
    lvl = p0 * (1 + S)
    x = h[h.high >= lvl]
    if not len(x):
        return None, None
    r = x.iloc[0]
    day = x.index[0].floor("D")
    return C.index.get_loc(day), max(r.open, lvl) * 1.002


def sim(N, M, S, cost=0.002, start="2020-01-01", end="2026-04-01"):
    idx = C.index
    i_s, i_e = idx.searchsorted(pd.Timestamp(start, tz="UTC")), idx.searchsorted(pd.Timestamp(end, tz="UTC"))
    eq = 1.0
    curve, open_, trades = [], [], []
    for i in range(i_s, i_e):
        pnl = 0.0
        keep = []
        for t in open_:
            k = t["k"]
            p, pp = PX[i, k], PX[i - 1, k]
            hit = t["xi"] == i
            if hit:
                p = t["xp"]
            dead = np.isnan(p)
            if not dead:
                d = -t["u"] * (p - pp) - t["u"] * pp * FX[i, k] * -1      # short: receives positive funding
                t["coin"] += d
            hb = t["ub"] * (PX[i, kb] - PX[i - 1, kb]) - t["ub"] * PX[i - 1, kb] * FX[i, kb]
            t["hedge"] += hb
            pnl += (0 if dead else d) + hb
            liq = t["coin"] <= -t["m"]
            if liq:
                pnl += -t["m"] - t["coin"]
                t["coin"] = -t["m"]
            age = i - t["i0"]
            stop = hit or ((not INTRA) and (not dead) and p >= t["p0"] * (1 + S))
            nxt_dead = i + 1 < len(idx) and np.isnan(PX[i + 1, k])
            if liq or dead or stop or age >= M or nxt_dead or i == i_e - 1:
                c = cost / 2 * ((0 if liq or dead else t["u"] * p) + t["ub"] * PX[i, kb])
                pnl -= c
                trades.append({"ret": (t["coin"] + t["hedge"] - c - t["c0"]) / (2 * t["m"]), "why": "liq" if liq else "stop" if stop else "end",
                               "coin": t["coin"] / t["m"], "hedge": t["hedge"] / t["m"], "entry": idx[t["i0"]], "open": len(open_)})
            else:
                keep.append(t)
        open_ = keep
        eq += pnl
        for sym in start_at.get(i - N, []):
            k = cols[sym]
            if len(open_) >= MAXOPEN or not (vr[sym].iat[i] <= 100) or np.isnan(PX[i, k]) or (i + 1 < len(idx) and np.isnan(PX[i + 1, k])):
                continue
            m = SLOT * eq
            c0 = cost / 2 * 2 * m
            eq -= c0
            xi, xp = intra_stop(sym, i, PX[i, k], S, M) if INTRA else (None, None)
            open_.append({"xi": xi, "xp": xp, "k": k, "i0": i, "p0": PX[i, k], "u": m / PX[i, k], "ub": m / PX[i, kb], "m": m, "coin": 0.0, "hedge": 0.0, "c0": c0})
        curve.append(eq)
    cv = pd.Series(curve, index=idx[i_s:i_e])
    T = pd.DataFrame(trades)
    sim.T = T
    return (cv.iloc[-1] - 1) * 100, (1 - cv / cv.cummax()).max() * 100, len(T), T.ret.mean() * 100 if len(T) else 0, (T.why == "liq").sum() if len(T) else 0, cv


for per, (s, e) in PERIODS.items():
    print(f"{per}: BTC buy&hold {buy_hold(C, 'BTCUSDT', s, e)[0]:+.0f}%")
for N in ((5, 7, 10, 14) if len(sys.argv) < 3 else ()):
    for M in (20, 30, 45):
        for S in (0.3, 0.6):
            seg = []
            for per, (s, e) in PERIODS.items():
                tot, dd, n, avg, liq, cv = sim(N, M, S, 0.002, s, e)
                tot2 = sim(N, M, S, 0.004, s, e)[0]
                yrs = ""
                if per == "dev":
                    y = cv.resample("YE").last()
                    y = (y / y.shift(1).fillna(1) - 1) * 100
                    yrs = " [" + " ".join(f"{d.year % 100}:{v:+.0f}" for d, v in y.items()) + "]"
                seg.append(f"{per} {tot:+5.0f}% dd {dd:3.0f}% x2 {tot2:+5.0f}% n{n} avg {avg:+.2f}% liq {liq}{yrs}")
            print(f"N{N:2d} M{M} S{int(S*100)} | " + " | ".join(seg), flush=True)


# Card rule detail: N7 M30 stop 30% (cards/yeni_coin_short.md)
if len(sys.argv) > 2 and sys.argv[2] == "card":
    for per, (s, e) in PERIODS.items():
        tot, dd, n, avg, liq, cv = sim(7, 30, 0.3, 0.002, s, e)
        T = sim.T
        m = cv.resample("ME").last()
        worst = (m / m.shift(1).fillna(1) - 1).nsmallest(3)
        print(f"{per}: tot {tot:+.0f}% dd {dd:.0f}% trades {n} ({n / ((pd.Timestamp(e) - pd.Timestamp(s)).days / 30.4):.1f}/month) "
              f"avg/trade {avg:+.2f}% median {T.ret.median()*100:+.2f}% win {(T.ret > 0).mean()*100:.0f}% stops {(T.why == 'stop').mean()*100:.0f}%")
        print(f"   short leg avg {T.coin.mean()*100:+.2f}% of margin, BTC hedge leg avg {T.hedge.mean()*100:+.2f}%, "
              f"worst trade {T.ret.min()*100:+.1f}%, best {T.ret.max()*100:+.1f}%, avg open trades at entry {T.open.mean():.1f}")
        print("   worst months: " + ", ".join(f"{d:%Y-%m} {v*100:+.0f}%" for d, v in worst.items()))
        y = cv.resample("YE").last()
        print("   years: " + " ".join(f"{d.year}:{v:+.0f}%" for d, v in ((y / y.shift(1).fillna(1) - 1) * 100).items()))
