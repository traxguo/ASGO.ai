# (b) Fade extreme multi-day pumps: 3-day return >= X and high funding -> short next open, hold H days, stop S.
# Coins at least 30 days old (new listings are idea (a)), daily quote volume >= $10M. Card: cards/pompa_sondur.md
import sys, itertools
import numpy as np, pandas as pd
sys.path.insert(0, "research/shortside")
from lib import load, panels, simulate, report, bh, DEV, VAL

D = load(); P = panels(D)
C, Q, F, A = P["close"], P["qv"], P["fund"], P["age"]
r3 = C / C.shift(3) - 1
f3 = F.rolling(3, min_periods=3).mean()  # avg daily funding sum over the last 3 days (0.0003 = normal 0.01%/8h)
ok = (A >= 30) & (Q >= 10e6)
rows = []
BASE = (0.5, 0.0006, 3, 0.25)
for X, FT, Hd, S in itertools.product([0.4, 0.5, 0.6], [None, 0.0006], [1, 3, 5], [0.15, 0.25, 0.35]):
    m = ok & (r3 >= X) & (r3.shift(1) < X)  # first day over the threshold
    if FT is not None:
        m &= f3 >= FT
    st = m.stack(); st = st[st]
    sig = [(d, s, -r3.at[d, s]) for d, s in st.index]
    T = simulate(P, sig, -1, S, Hd, max_open=5)
    T2 = simulate(P, sig, -1, S, Hd, cost=0.004, max_open=5)
    tag = f"X{int(X*100)} F{'-' if FT is None else FT} H{Hd} S{int(S*100)}" + (" *BASE*" if (X, FT, Hd, S) == BASE else "")
    rows += report(T, tag, T2)
    if (X, FT, Hd, S) == BASE:
        T.to_csv("research/shortside/out_b_base_trades.csv", index=False)
R = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 1000)
print(R.to_string(index=False))
R.to_csv("research/shortside/out_b_grid.csv", index=False)
