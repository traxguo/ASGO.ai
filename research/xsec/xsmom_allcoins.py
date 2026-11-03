# Survivorship-free check of weekly_xsmom: universe at each rebalance = the TOP_N most traded USDT perps
# (30-day average quote volume) among ALL ever-listed ones, delisted included (fetch_all_daily.py).
# A coin that stops trading during the hold exits at its last available close. Funding not included here.
import sys, numpy as np, pandas as pd

COST = float(sys.argv[1]) if len(sys.argv) > 1 else 0.002
TOP_N = int(sys.argv[2]) if len(sys.argv) > 2 else 80
MIN_AGE = int(sys.argv[3]) if len(sys.argv) > 3 else 0   # days of history a coin needs to be ranked
PERIODS = {"dev": ("2020-01-01", "2025-01-01"), "val": ("2025-01-01", "2026-04-01")}
D = pd.read_feather("user_data/data/xsec_all_1d.feather")
C = D.pivot(index="date", columns="symbol", values="close").sort_index()
V = D.pivot(index="date", columns="symbol", values="quote_volume").reindex(C.index)
VOL30 = V.rolling(30, min_periods=30).mean()
AGE = C.notna().cumsum()
VOL30 = VOL30.where(AGE >= MIN_AGE)
LASTC = C.ffill()
alive_until = C.apply(lambda s: s.last_valid_index())
print(f"{C.shape[1]} symbols, cost {COST}, top {TOP_N}, min age {MIN_AGE}d")


def run(L, R, K, start, end, side="both"):
    past = C / C.shift(L) - 1
    idx = C.index[(C.index >= start) & (C.index < end)][::R]
    out = []
    for t in idx:
        loc = C.index.get_loc(t)
        if loc + R >= len(C.index):
            break
        t2 = C.index[loc + R]
        uni = VOL30.loc[t].dropna().nlargest(TOP_N).index
        r = past.loc[t, uni].dropna()
        if len(r) < 4 * K:
            continue
        top, bot = r.nlargest(K).index, r.nsmallest(K).index
        fwd = LASTC.loc[t2] / C.loc[t] - 1   # delisted: last close before t2
        l, s = fwd[top].mean() - COST, -fwd[bot].mean() - COST
        out.append({"both": (l + s) / 2, "long": l, "short": s}[side])
    a = np.array(out)
    eq = np.cumprod(1 + a)
    return len(a), a.mean() * 100, (eq[-1] - 1) * 100, (1 - eq / np.maximum.accumulate(eq)).max() * 100


def sh(s, o):
    return str((pd.Timestamp(s) + pd.Timedelta(days=o)).date())


for L in (10, 14, 21):
    for K in (3, 5, 8):
        for R in (14, 21):
            res = []
            for per in ("dev", "val"):
                s, e = PERIODS[per]
                rr = [run(L, R, K, sh(s, o), e) for o in range(0, R, 3)]
                res.append(f"{per} avg {np.mean([x[1] for x in rr]):+.2f}% tot {np.mean([x[2] for x in rr]):+5.0f}% dd {np.mean([x[3] for x in rr]):3.0f}%")
            print(f"L{L:2d} K{K} R{R}  " + " | ".join(res), flush=True)
