# ONE-OFF holdout run for Yeni Coin Short (approved by the supervisor 2026-11-04). Do not re-run to tune.
# Needs SUFFIX=_full data (fetch_all.py with LAST=2026-10). Entries 2026-04-01..2026-09-30; exits may run into October.
import os, sys
os.environ.setdefault("SUFFIX", "_full")
import pandas as pd
sys.path.insert(0, "research/shortside")
from lib import load, panels, simulate, stats, bh, HOLD

D = load(); P = panels(D)
dates = P["open"].index
first = D.groupby("symbol").date.min(); first = first[first >= "2020-01-15"]
sig = [(dates[dates.get_loc(f)], s, 0) for s, f in first.items() if dates.get_loc(f) + 1 < len(dates)]
print("data ends", dates.max().date(), "| listings with entry in holdout:",
      sum(HOLD[0] <= str(dates[dates.get_loc(f) + 1].date()) < HOLD[1] for s, f in first.items() if dates.get_loc(f) + 1 < len(dates)))
rows = []
for Hd, tag in [(7, "K1 H7 S40 (judged)"), (14, "K1 H14 S40 (pre-fixed base)")]:
    for cost, slip, nm in [(0.002, 0.003, ""), (0.004, 0.003, " 2xcost"), (0.002, 0.05, " slip5%")]:
        T = simulate(P, sig, -1, 0.40, Hd, cost=cost, stop_slip=slip, max_open=10)
        T = T[(T.entry_date >= HOLD[0]) & (T.entry_date < HOLD[1])]
        rows.append(stats(T, tag + nm))
        if nm == "":
            T.to_csv(f"research/shortside/out_a_holdout_h{Hd}.csv", index=False)
            T["m"] = T.entry_date.dt.strftime("%Y-%m")
            print(tag, "by month:\n", pd.DataFrame([stats(g, m) for m, g in T.groupby("m")])[["label", "n", "avgR", "PF", "avg_net_pct", "eq_pct"]].to_string(index=False))
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).to_string(index=False))
print("BTC buy&hold holdout (ret%, maxDD%):", bh(P, "BTCUSDT", *HOLD))
