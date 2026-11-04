# (b) BTC/ETH ratio, market-neutral (0.5 long one, 0.5 short the other). Rules fixed before the run (2026-11-04):
# Mean reversion: x = log(ETH/BTC); z = (x - rolling mean W) / rolling std W. z <= -E: long ETH / short BTC;
#   z >= E: the reverse. Exit when z crosses 0, stop |z| >= 4, time limit 20 days. Grid E 1.5/2/2.5, W 20/30/60.
# Trend: x above its L-day SMA -> long ETH / short BTC, below -> long BTC / short ETH (always in). Grid L 20/50/100.
#   Variant "trend+flat": in only while |x - SMA| > 2% (no position near the line).
# Decisions at the daily close, traded at that close. Cost 0.20% round trip (x2 check), funding included.
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "research/neutral")
from common import load, simple_ret, run_weights, stats, fmt, PERIODS, buy_hold  # noqa: E402

C, R, U, F = load()
C2 = C[["BTCUSDT", "ETHUSDT"]]
SR = simple_ret(C2)
F2 = F[["BTCUSDT", "ETHUSDT"]]
x = np.log(C2.ETHUSDT / C2.BTCUSDT)

for per, (s, e) in PERIODS.items():
    print(f"{per}: BTC b&h {buy_hold(C, 'BTCUSDT', s, e)[0]:+.0f}%  ETH b&h {buy_hold(C, 'ETHUSDT', s, e)[0]:+.0f}%  "
          f"ETH/BTC ratio {(np.exp(x[x.index < e].iloc[-1] - x[x.index >= s].iloc[0]) - 1) * 100:+.0f}%")


def show(name, W):
    line = name
    for cost in (0.0, 0.002, 0.004):
        out = run_weights(W, SR, F2, cost=cost)
        seg = []
        for per, (s, e) in PERIODS.items():
            st = stats(out["both"], s, e)
            flips = (W.diff().abs().sum(axis=1) > 0)[(W.index >= s) & (W.index < e)].sum()
            seg.append(f"{per} {fmt(st)} trades~{flips}" if cost == 0.002 else f"{per} {st['tot']:+.0f}%")
        line += f"\n   cost {cost*100:.1f}%: " + " | ".join(seg)
    print(line, flush=True)


def to_w(pos):  # pos +1: long ETH short BTC
    return pd.DataFrame({"ETHUSDT": 0.5 * pos, "BTCUSDT": -0.5 * pos}, index=pos.index)


print("== mean reversion ==")
for E in (1.5, 2.0, 2.5):
    for Wn in (20, 30, 60):
        z = (x - x.rolling(Wn).mean()) / x.rolling(Wn).std()
        pos = np.zeros(len(z)); p, age = 0, 0
        for i, zz in enumerate(z.values):
            if p != 0:
                age += 1
                if np.isnan(zz) or p * zz >= 0 or abs(zz) >= 4 or age >= 20:
                    p = 0
            if p == 0 and not np.isnan(zz) and E <= abs(zz) < 4:
                p, age = (1 if zz < 0 else -1), 0
            pos[i] = p
        show(f"MR E{E} W{Wn}", to_w(pd.Series(pos, index=z.index)))

print("== trend ==")
for L in (20, 50, 100):
    sma = x.rolling(L).mean()
    pos = np.sign(x - sma).fillna(0)
    show(f"TREND L{L}", to_w(pos))
    gap = x - sma
    pos2 = pd.Series(np.where(gap > 0.02, 1, np.where(gap < -0.02, -1, 0)), index=x.index)
    show(f"TREND+flat L{L}", to_w(pos2))
