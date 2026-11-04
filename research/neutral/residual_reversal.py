# (c) Residual reversal, market-neutral. Rules fixed before the run (2026-11-04):
# - Universe each day: top 50 USDT perps by 30-day avg quote volume, >= 180 days of history (delisted included).
# - Beta: 60-day OLS beta of daily log returns vs BTC. Residual = sum of last L daily log returns - beta * BTC's.
# - Long the K most negative residuals, short the K most positive (equal weight, 0.5 per side), BTC itself excluded.
# - Hold H days as overlapping portfolios. Cost 0.20% round trip (x2 check), funding included.
# Small neighbour grid: L 1/2/3, H 1/2/3, K 5/10.
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "research/neutral")
from common import load, simple_ret, run_weights, stats, fmt, PERIODS, buy_hold  # noqa: E402

C, R, U, F = load(min_age=180, top_n=50)
SR = simple_ret(C)
btc = R["BTCUSDT"]
cov = R.rolling(60, min_periods=40).cov(btc)
beta = cov.div(btc.rolling(60, min_periods=40).var(), axis=0)
U = U.drop(columns="BTCUSDT")


def weights(L, K, sign=+1):
    res = R.rolling(L).sum() - beta.mul(btc.rolling(L).sum(), axis=0)
    res = res[U.columns].where(U)
    rk = res.rank(axis=1)
    n = res.notna().sum(axis=1)
    lo = rk.le(K, axis=0)                           # biggest losers
    hi = rk.gt(n - K, axis=0)                       # biggest winners
    W = (lo.astype(float) - hi.astype(float)) * 0.5 / K * sign
    return W.where(n >= 4 * K, 0.0)


for per, (s, e) in PERIODS.items():
    bh, dd = buy_hold(C, "BTCUSDT", s, e)
    print(f"BTC buy&hold {per}: {bh:+.0f}% (dd {dd:.0f}%)")
for L in (1, 2, 3):
    for H in (1, 2, 3):
        for K in (5, 10):
            W = weights(L, K)
            line = f"L{L} H{H} K{K:2d}"
            for cost in (0.0, 0.002, 0.004):
                out = run_weights(W, SR, F, cost=cost, hold=H)
                seg = []
                for per, (s, e) in PERIODS.items():
                    st = stats(out["both"], s, e)
                    if cost == 0.002:
                        seg.append(f"{per} {fmt(st)} [L {stats(out['long'], s, e)['tot']:+.0f}% S {stats(out['short'], s, e)['tot']:+.0f}%]")
                    else:
                        seg.append(f"{per} {st['tot']:+.0f}%")
                line += f"\n   cost {cost*100:.1f}%: " + " | ".join(seg)
            print(line, flush=True)
