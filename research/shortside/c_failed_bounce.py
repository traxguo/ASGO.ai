# (c) BTC daily downtrend + coin rallies into its daily EMA20 and closes back below -> short next open.
# Stop just above the rejection day's high (+1%), exit on a daily close above EMA20 or after H days.
# Mirror long (BTC uptrend, dip to EMA20 that closes back above) reported separately. Card: cards/basarisiz_tepki.md
import sys, itertools
import numpy as np, pandas as pd
sys.path.insert(0, "research/shortside")
from lib import load, panels, simulate, report, DEV, VAL

D = load(); P = panels(D)
O, H, L, C, Q, A = (P[k] for k in ["open", "high", "low", "close", "qv", "age"])
e20 = C.ewm(span=20, adjust=False, min_periods=20).mean()
e50 = C.ewm(span=50, adjust=False, min_periods=50).mean()
b = C["BTCUSDT"]; b50 = b.ewm(span=50, adjust=False).mean()
btc_dn = (b < b50) & (b50 < b50.shift(5))
btc_up = (b > b50) & (b50 > b50.shift(5))
qv30 = Q.rolling(30, min_periods=20).mean()
rank = qv30.rank(axis=1, ascending=False)
E20v = e20.values; Cv = C.values


def exit_short(k, j, e, side):
    return Cv[k, j] > E20v[k, j]


def exit_long(k, j, e, side):
    return Cv[k, j] < E20v[k, j]


rows = []
BASE = (30, 5)
for TOP, Hd in itertools.product([10, 30, 60], [3, 5, 10]):
    uni = (rank <= TOP) & (A >= 90)
    for side in (-1, 1):
        if side < 0:
            m = uni & btc_dn.values[:, None] & (C < e50) & (C.shift(1) < e20.shift(1)) & (H >= e20) & (C < e20)
            stop_level = H * 1.01
        else:
            m = uni & btc_up.values[:, None] & (C > e50) & (C.shift(1) > e20.shift(1)) & (L <= e20) & (C > e20)
            stop_level = L * 0.99
        st = m.stack(); st = st[st]
        sig = [(d, s, 0) for d, s in st.index]
        sp = {(d, s): stop_level.at[d, s] for d, s in st.index}
        # stop is relative to the actual entry (next open); simulate converts it; require >= 2% so costs stay small
        sig = [x for x in sig if abs(sp[(x[0], x[1])] / C.at[x[0], x[1]] - 1) >= 0.02]
        fn = exit_short if side < 0 else exit_long
        T = simulate(P, sig, side, None, Hd, exit_fn=fn, max_open=5, stop_px=sp)
        T2 = simulate(P, sig, side, None, Hd, cost=0.004, exit_fn=fn, max_open=5, stop_px=sp)
        tag = f"{'SHORT' if side < 0 else 'LONG '} top{TOP} H{Hd}" + (" *BASE*" if (TOP, Hd) == BASE else "")
        rows += report(T, tag, T2)
        if (TOP, Hd) == BASE:
            T.to_csv(f"research/shortside/out_c_base_{'short' if side < 0 else 'long'}.csv", index=False)
R = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
print(R.to_string(index=False))
R.to_csv("research/shortside/out_c_grid.csv", index=False)
