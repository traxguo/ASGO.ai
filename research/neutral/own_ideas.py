# Own market-neutral ideas (2026-11-04). Rules fixed before the run; small neighbour grids only.
# (d) Funding carry: long the K coins with the lowest (most negative) funding over the last LB days, short the K
#     highest; hold H days (overlapping). Shorts that pay into crowded longs, longs where shorts are crowded.
# (e) New-listing short, BTC-hedged: N days after a coin's first trading day, short it for M days (0.5 of the book
#     split equally over all open shorts) against 0.5 long BTC. Stop: exit if close >= entry * (1 + S).
#     Only coins in the top 100 by 30-day volume on entry day (tradeable).
# (f) Low-vol minus high-vol, beta-neutral: every 7 days rank the universe by 30-day volatility, long the K
#     calmest, short the K wildest, side sizes set so that both sides carry the same BTC beta (gross 1).
# Universe for (d)/(f): top 50 by 30-day volume, >= 180 days of history, delisted included. BTC excluded in (e)/(f).
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "research/neutral")
from common import load, simple_ret, run_weights, stats, fmt, PERIODS  # noqa: E402

C, R, U, F = load(min_age=180, top_n=50)
SR = simple_ret(C)
which = sys.argv[1] if len(sys.argv) > 1 else "def"


def show(name, W, hold=1):
    line = name
    for cost in (0.0, 0.002, 0.004):
        out = run_weights(W, SR, F, cost=cost, hold=hold)
        seg = []
        for per, (s, e) in PERIODS.items():
            st = stats(out["both"], s, e)
            if cost == 0.002:
                seg.append(f"{per} {fmt(st)} [L {stats(out['long'], s, e)['tot']:+.0f}% S {stats(out['short'], s, e)['tot']:+.0f}%]")
            else:
                seg.append(f"{per} {st['tot']:+.0f}%")
        line += f"\n   cost {cost*100:.1f}%: " + " | ".join(seg)
    print(line, flush=True)


def topbot(score, K, uni):
    sc = score.where(uni)
    rk = sc.rank(axis=1)
    n = sc.notna().sum(axis=1)
    lo = rk.le(K, axis=0).astype(float)
    hi = rk.gt(n - K, axis=0).astype(float)
    return lo, hi, n


if "d" in which:
    print("== (d) funding carry ==")
    for LB in (3, 7, 14):
        fs = F.rolling(LB).sum()
        for K in (5, 10):
            lo, hi, n = topbot(fs, K, U)
            W = ((lo - hi) * 0.5 / K).where(n >= 4 * K, 0.0)
            for H in (1, 7):
                show(f"FUND LB{LB} K{K} H{H}", W, hold=H)

if "e" in which:
    print("== (e) new-listing short ==")
    D = pd.read_feather("user_data/data/xsec_all_1d.feather")
    Vv = D.pivot(index="date", columns="symbol", values="quote_volume").reindex(C.index)
    vr = Vv.rolling(30, min_periods=5).mean().rank(axis=1, ascending=False)
    first = C.apply(lambda s: s.first_valid_index())
    first = first[first > pd.Timestamp("2020-02-01", tz="UTC")]
    for N in (7, 30):
        for M in (30, 90):
            for S in (0.3, 0.6):
                pos = pd.DataFrame(0.0, index=C.index, columns=C.columns)
                for sym, f in first.items():
                    if sym == "BTCUSDT":
                        continue
                    i0 = C.index.get_loc(f) + N
                    if i0 >= len(C.index) or not (vr[sym].iat[i0] <= 100):
                        continue
                    px = C[sym].values
                    ent = px[i0]
                    if np.isnan(ent):
                        continue
                    for j in range(i0, min(i0 + M, len(C.index))):
                        if np.isnan(px[j]) or (j + 1 < len(px) and np.isnan(px[j + 1])):
                            break
                        pos.iat[j, pos.columns.get_loc(sym)] = -1.0
                        if px[j] >= ent * (1 + S):
                            break
                n = (pos < 0).sum(axis=1)
                W = pos.div(n.replace(0, np.nan), axis=0).fillna(0.0) * 0.5
                W["BTCUSDT"] = np.where(n > 0, 0.5, 0.0)
                exposure = (n > 0).mean()
                show(f"NEWLIST N{N} M{M} stop{int(S*100)}% (in market {exposure*100:.0f}% of days, avg {n[n>0].mean():.1f} shorts)", W)

if "f" in which:
    print("== (f) low-vol minus high-vol, beta-neutral ==")
    btc = R["BTCUSDT"]
    beta = R.rolling(60, min_periods=40).cov(btc).div(btc.rolling(60, min_periods=40).var(), axis=0)
    vol = R.rolling(30, min_periods=25).std()
    U2 = U.copy(); U2["BTCUSDT"] = False
    for K in (5, 10):
        lo, hi, n = topbot(vol, K, U2)
        bL = (lo * beta).sum(axis=1) / K
        bS = (hi * beta).sum(axis=1) / K
        a = bS / (bL + bS)                          # long side share so that a*bL == (1-a)*bS
        a = a.clip(0.2, 0.8)
        W = lo.mul(a / K, axis=0) - hi.mul((1 - a) / K, axis=0)
        W = W.where(n >= 4 * K, 0.0)
        idx = W.index[::7]
        W = W.loc[idx].reindex(W.index).ffill().fillna(0.0)
        show(f"LOWVOL K{K} R7", W)
        Wd = (lo - hi).mul(0.5 / K).where(n >= 4 * K, 0.0).loc[idx].reindex(W.index).ffill().fillna(0.0)
        show(f"LOWVOL dollar-neutral K{K} R7", Wd)
