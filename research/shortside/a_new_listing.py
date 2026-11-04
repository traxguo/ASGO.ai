# (a) Short newly listed USDT perps: enter at the open of day K after the first daily bar, hold H days, stop S.
# Survivorship-free: every symbol ever listed (delisted included). Card: cards/yeni_coin_short.md
import sys, itertools
import pandas as pd
sys.path.insert(0, "research/shortside")
from lib import load, panels, simulate, report, bh, DEV, VAL

D = load(); P = panels(D)
first = D.groupby("symbol").date.min()
first = first[first >= "2020-01-15"]  # archive starts 2019-09/2020-01; earlier bars are not real listing days
print(len(first), "listings after 2020-01-15;", "dev", ((first < DEV[1])).sum(), "val", ((first >= VAL[0]) & (first < VAL[1])).sum())
dates = P["open"].index
rows = []
BASE = (1, 14, 0.40)
for K, Hd, S in itertools.product([1, 3, 7], [7, 14, 30], [0.25, 0.40, 0.60]):
    sig = []
    for s, f in first.items():
        i = dates.get_loc(f) + K - 1  # signal day -> entry at open of day index K
        if i + 1 < len(dates):
            sig.append((dates[i], s, 0))
    T = simulate(P, sig, -1, S, Hd, max_open=10)
    T2 = simulate(P, sig, -1, S, Hd, cost=0.004, max_open=10)
    tag = f"K{K} H{Hd} S{int(S*100)}" + (" *BASE*" if (K, Hd, S) == BASE else "")
    rows += report(T, tag, T2)
    if (K, Hd, S) == BASE:
        T.to_csv("research/shortside/out_a_base_trades.csv", index=False)
R = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
print(R.to_string(index=False))
R.to_csv("research/shortside/out_a_grid.csv", index=False)
for a, b in [DEV, VAL]:
    print("BTC buy&hold", a, b, bh(P, "BTCUSDT", a, b))
