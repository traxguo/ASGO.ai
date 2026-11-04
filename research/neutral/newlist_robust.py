# Robustness of (e) new-listing short (only N7 M30 passed in own_ideas.py). 2026-11-04.
# Neighbour grid N 5/7/10/14, M 20/30/45, stop 30/60%; yearly; best-5-days removed; beta of the result to BTC
# (is the "neutral" book really neutral?). Same rules as own_ideas.py (e).
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "research/neutral")
from common import load, simple_ret, run_weights, stats, PERIODS  # noqa: E402

C, R, U, F = load()
SR = simple_ret(C)
D = pd.read_feather("user_data/data/xsec_all_1d.feather")
Vv = D.pivot(index="date", columns="symbol", values="quote_volume").reindex(C.index)
vr = Vv.rolling(30, min_periods=5).mean().rank(axis=1, ascending=False)
first = C.apply(lambda s: s.first_valid_index())
first = first[(first > pd.Timestamp("2020-02-01", tz="UTC")) & (first.index != "BTCUSDT")]
btc = SR["BTCUSDT"]
cols = {c: i for i, c in enumerate(C.columns)}
PX = C.values


def book(N, M, S):
    pos = np.zeros(C.shape)
    for sym, f in first.items():
        i0 = C.index.get_loc(f) + N
        if i0 >= len(C.index) or not (vr[sym].iat[i0] <= 100):
            continue
        k = cols[sym]
        ent = PX[i0, k]
        for j in range(i0, min(i0 + M, len(C.index))):
            if np.isnan(PX[j, k]) or (j + 1 < len(PX) and np.isnan(PX[j + 1, k])):
                break
            pos[j, k] = -1.0
            if PX[j, k] >= ent * (1 + S):
                break
    pos = pd.DataFrame(pos, index=C.index, columns=C.columns)
    n = (pos < 0).sum(axis=1)
    W = pos.div(n.replace(0, np.nan), axis=0).fillna(0.0) * 0.5
    W["BTCUSDT"] = np.where(n > 0, 0.5, 0.0)
    return W


for N in (5, 7, 10, 14):
    for M in (20, 30, 45):
        for S in (0.3, 0.6):
            W = book(N, M, S)
            out = run_weights(W, SR, F, cost=0.002)
            x2 = run_weights(W, SR, F, cost=0.004)["both"]
            d = out["both"]
            seg = []
            for per, (s, e) in PERIODS.items():
                m = (d.index >= s) & (d.index < e)
                dd = d[m]
                b = np.polyfit(btc[m], dd, 1)[0]
                no5 = ((1 + dd.drop(dd.nlargest(5).index)).prod() - 1) * 100
                st = stats(d, s, e)
                seg.append(f"{per} {st['tot']:+5.0f}% dd{st['dd']:3.0f}% x2 {stats(x2, s, e)['tot']:+5.0f}% no5 {no5:+5.0f}% beta {b:+.2f}")
            yrs = " ".join(f"{y % 100}:{((1 + d[d.index.year == y]).prod() - 1) * 100:+.0f}" for y in range(2020, 2027))
            print(f"N{N:2d} M{M} S{int(S*100)} | " + " | ".join(seg) + f" | {yrs}", flush=True)
