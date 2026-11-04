# Medium-horizon cross-sectional momentum / reversal on daily data, market-neutral long/short.
# Question (2026-11-03): all our bots are long-only and idle in down markets. Does ranking coins
# against each other (not against time) give an edge that works in both directions?
# Every R days: rank coins by past L-day return (skipping the last S days); long top K, short bottom K,
# equal weight, hold R days. Only coins with full data at the rebalance date (no future listings).
# Costs: 0.20% round trip per leg per rebalance (taker in/out + slippage, full turnover assumed).
# Funding: longs pay / shorts receive the realized funding over the hold.
import json, sys, numpy as np, pandas as pd

PF = sys.argv[1] if len(sys.argv) > 1 else "config/pairs_wide81.json"
COST = 0.002
PERIODS = {"dev": ("2020-01-01", "2025-01-01"), "val": ("2025-01-01", "2026-04-01")}
pl = [p.split("/")[0] for p in json.load(open(PF))["exchange"]["pair_whitelist"]]
base = "user_data/data/binance/futures/{}_USDT_USDT-{}.feather"
C, F = {}, {}
for p in pl:
    try:
        C[p] = pd.read_feather(base.format(p, "1d-futures")).set_index("date").close
    except FileNotFoundError:
        continue
    try:
        fr = pd.read_feather(base.format(p, "1h-funding_rate")).set_index("date").funding_rate
        F[p] = fr.resample("1D").sum()
    except FileNotFoundError:
        pass
C = pd.DataFrame(C).sort_index()
F = pd.DataFrame(F).reindex(C.index).reindex(columns=C.columns).fillna(0.0)
print(f"{PF}: {C.shape[1]} coins, funding for {int((F != 0).any().sum())}")


def run(L, S, R, K, mode, start, end, side="both"):
    past = C.shift(S) / C.shift(S + L) - 1
    idx = C.index[(C.index >= start) & (C.index < end)][::R]
    weekly = []
    for t in idx:
        loc = C.index.get_loc(t)
        if loc + R >= len(C.index):
            break
        t2 = C.index[loc + R]
        r = past.loc[t].dropna()
        r = r[C.loc[t2, r.index].notna()]
        if len(r) < 4 * K:
            continue
        top, bot = r.nlargest(K).index, r.nsmallest(K).index
        longs, shorts = (top, bot) if mode == "mom" else (bot, top)
        fwd = C.loc[t2] / C.loc[t] - 1
        fund = F.iloc[loc + 1: loc + R + 1].sum()
        lret = (fwd[longs] - fund[longs]).mean() - COST
        sret = (-fwd[shorts] + fund[shorts]).mean() - COST
        weekly.append({"both": (lret + sret) / 2, "long": lret, "short": sret}[side])
    a = np.array(weekly)
    if len(a) == 0:
        return None
    eq = np.cumprod(1 + a)
    dd = (1 - eq / np.maximum.accumulate(eq)).max()
    return len(a), a.mean() * 100, (a > 0).mean(), (eq[-1] - 1) * 100, dd * 100


rows = []
for mode in ("mom", "rev"):
    for L in (7, 14, 28, 56):
        for S in (0, 1):
            for R in (7, 14):
                for K in (5, 10):
                    d = run(L, S, R, K, mode, *PERIODS["dev"])
                    v = run(L, S, R, K, mode, *PERIODS["val"])
                    if d and v:
                        rows.append((mode, L, S, R, K, *d, *v))
cols = ["mode", "L", "S", "R", "K", "n_d", "avg_d", "win_d", "tot_d", "dd_d", "n_v", "avg_v", "win_v", "tot_v", "dd_v"]
D = pd.DataFrame(rows, columns=cols).round(2)
pd.set_option("display.width", 200)
print(D.sort_values("avg_d", ascending=False).to_string(index=False))
