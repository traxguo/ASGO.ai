# Robustness checks for (a): yearly split, heavy stop slippage, concentration, beta control.
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/shortside")
from lib import load, panels, simulate, stats

D = load(); P = panels(D)
first = D.groupby("symbol").date.min(); first = first[first >= "2020-01-15"]
dates = P["open"].index
pd.set_option("display.width", 250)


def sigs(K):
    return [(dates[dates.get_loc(f) + K - 1], s, 0) for s, f in first.items() if dates.get_loc(f) + K < len(dates)]


for K, Hd, S in [(1, 14, 0.40), (1, 7, 0.40), (3, 14, 0.40)]:
    print(f"\n=== K{K} H{Hd} S{int(S*100)} ===")
    T = simulate(P, sigs(K), -1, S, Hd, max_open=10)
    T = T[T.entry_date < "2026-04-01"]
    T["yr"] = T.entry_date.dt.year
    print(pd.DataFrame([stats(g, str(y)) for y, g in T.groupby("yr")]).to_string(index=False))
    for slip in [0.02, 0.05]:
        Ts = simulate(P, sigs(K), -1, S, Hd, max_open=10, stop_slip=slip)
        Ts = Ts[Ts.entry_date < "2026-04-01"]
        print("stop slip", slip, stats(Ts[Ts.entry_date < "2025"], "dev"), stats(Ts[Ts.entry_date >= "2025"], "val"))
    # concentration: drop the best 5% of trades
    for nm, g in [("dev", T[T.entry_date < "2025"]), ("val", T[T.entry_date >= "2025"])]:
        g2 = g.sort_values("R").iloc[: int(len(g) * 0.95)]
        print(nm, "without best 5% trades:", stats(g2, nm))
        print(nm, "share delisted exits", round((g.why == "delist").mean(), 3), "avg net% of delist exits", round(100 * g[g.why == "delist"].net.mean(), 1))
    # beta control: short an equal-weight basket of established top-50 coins over the same entry/exit days
    C = P["close"]; O = P["open"]; Q = P["qv"].rolling(30, min_periods=20).mean(); A = P["age"]
    ctrl = []
    for _, t in T.iterrows():
        d0, d1 = t.entry_date, t.exit_date
        u = Q.loc[d0][(A.loc[d0] >= 180)].nlargest(50).index
        r = (C.loc[d1, u] / O.loc[d0, u] - 1).mean()
        ctrl.append(-r)
    T["ctrl"] = ctrl
    for nm, g in [("dev", T[T.entry_date < "2025"]), ("val", T[T.entry_date >= "2025"])]:
        print(nm, "avg gross% new-listing short", round(100 * g.gross.mean(), 2), "| same days short top-50 old coins", round(100 * g.ctrl.mean(), 2))
