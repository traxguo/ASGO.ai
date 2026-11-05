# Robustness of (d) funding carry (K = 10 family, the K = 5 family failed validation). 2026-11-04.
# Checks: yearly split, funding vs price contribution, universe 30/80, min history 365 days, top-5 days removed,
# 2x cost. Same rules as own_ideas.py (d); no new parameters.
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "research/neutral")
from common import load, simple_ret, run_weights, stats, PERIODS  # noqa: E402

CFG = [(lb, h) for lb in (3, 7, 14) for h in (1, 7)]
K = 10


def build(F, U, LB):
    fs = F.rolling(LB).sum().where(U)
    rk = fs.rank(axis=1)
    n = fs.notna().sum(axis=1)
    W = (rk.le(K, axis=0).astype(float) - rk.gt(n - K, axis=0).astype(float)) * 0.5 / K
    return W.where(n >= 4 * K, 0.0)


def line(tag, out):
    seg = []
    for per, (s, e) in PERIODS.items():
        st = stats(out["both"], s, e)
        seg.append(f"{per} {st['tot']:+6.0f}% dd {st['dd']:3.0f}%")
    return f"{tag:28s} " + " | ".join(seg)


base = {}
for top_n, age in ((50, 180), (30, 180), (80, 180), (50, 365)):
    C, R, U, F = load(min_age=age, top_n=top_n)
    SR = simple_ret(C)
    Z = F * 0
    print(f"\n== universe top {top_n}, min age {age}d ==")
    for LB, H in CFG:
        W = build(F, U, LB)
        out = run_weights(W, SR, F, cost=0.002, hold=H)
        print(line(f"LB{LB} H{H}", out))
        if (top_n, age) == (50, 180):
            base[(LB, H)] = (W, SR, F, Z, out)

print("\n== decomposition, 2x cost, yearly, without best 5 days (top 50 / 180d) ==")
for (LB, H), (W, SR, F, Z, out) in base.items():
    price = run_weights(W, SR, Z, cost=0.0, hold=H)["both"]
    fund = run_weights(W, SR * 0, F, cost=0.0, hold=H)["both"]
    x2 = run_weights(W, SR, F, cost=0.004, hold=H)["both"]
    d = out["both"]
    yrs = " ".join(f"{y}:{((1 + d[d.index.year == y]).prod() - 1) * 100:+.0f}%" for y in range(2020, 2027))
    print(f"LB{LB} H{H}: {yrs}")
    for per, (s, e) in PERIODS.items():
        dd = d[(d.index >= s) & (d.index < e)]
        no5 = dd.drop(dd.nlargest(5).index)
        tc = (W.reindex(SR.index).fillna(0).rolling(H, min_periods=1).mean().diff().abs().sum(axis=1)[(d.index >= s) & (d.index < e)].mean()) * 365
        print(f"   {per}: net {stats(d, s, e)['tot']:+.0f}% | price only (no cost) {stats(price, s, e)['tot']:+.0f}% | funding only "
              f"{stats(fund, s, e)['tot']:+.0f}% | 2x cost {stats(x2, s, e)['tot']:+.0f}% | w/o best 5 days {((1 + no5).prod() - 1) * 100:+.0f}% "
              f"| turnover {tc:.0f}x/yr")
