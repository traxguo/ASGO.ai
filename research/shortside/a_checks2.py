# More checks for (a): later start date (archive artefacts), max_open, worst trades, frequency, funding share.
import sys
import pandas as pd
sys.path.insert(0, "research/shortside")
from lib import load, panels, simulate, stats

D = load(); P = panels(D)
dates = P["open"].index
f0 = D.groupby("symbol").date.min()
for start in ["2020-01-15", "2020-03-01", "2021-01-01"]:
    first = f0[f0 >= start]
    sig = [(dates[dates.get_loc(f)], s, 0) for s, f in first.items() if dates.get_loc(f) + 1 < len(dates)]
    for Hd in [7, 14]:
        for mo in [5, 10, None]:
            T = simulate(P, sig, -1, 0.40, Hd, max_open=mo)
            T = T[T.entry_date < "2026-04-01"]
            dv, vl = T[T.entry_date < "2025"], T[T.entry_date >= "2025"]
            a, b = stats(dv), stats(vl)
            print(f"start {start} H{Hd} max_open {mo}: DEV n{a['n']} R{a['avgR']} PF{a['PF']} DD{a['maxDD_pct']} | VAL n{b['n']} R{b['avgR']} PF{b['PF']} DD{b['maxDD_pct']} eq{b['eq_pct']}")
T = simulate(P, [(dates[dates.get_loc(f)], s, 0) for s, f in f0[f0 >= "2020-01-15"].items() if dates.get_loc(f) + 1 < len(dates)], -1, 0.40, 7, max_open=10)
T = T[T.entry_date < "2026-04-01"]
print("worst 8 trades:\n", T.nsmallest(8, "R")[["symbol", "entry_date", "why", "net", "R"]].to_string(index=False))
print("best 8 trades:\n", T.nlargest(8, "R")[["symbol", "entry_date", "why", "net", "R"]].to_string(index=False))
print("trades per month (val):", round(len(T[T.entry_date >= "2025"]) / 15, 1), "(dev):", round(len(T[T.entry_date < "2025"]) / 60, 1))
print("exit reasons:", T.why.value_counts().to_dict())
T.to_csv("research/shortside/out_a_k1h7s40_trades.csv", index=False)
