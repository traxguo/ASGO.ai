"""Per-year long/short P&L and equity chart for the pre-registered TSMOM test (no new configs)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tsmom as T

px = T.load_prices(); fund = T.load_funding(px.index)
rows = []
res_all = {}
for n, kind, vt in T.GRID:
    cfg = f"N{n}_{kind}_vt{int(vt*100)}"
    res = T.run(px, fund, n, kind, vt); res_all[cfg] = res
    m = res["port"].index >= T.DEV[0]
    c = res["contrib"][m]; side = np.sign(res["w"][m])
    yr = c.index.year
    for asset in T.ASSETS:
        g = pd.DataFrame({"long": c[asset].where(side[asset] > 0, 0.0), "short": c[asset].where(side[asset] < 0, 0.0)}).groupby(yr).sum()
        for y, r in g.iterrows():
            rows.append({"config": cfg, "asset": asset, "year": y, "long_pnl": r["long"], "short_pnl": r["short"]})
yd = pd.DataFrame(rows)
yd.to_csv(os.path.join(T.OUT, "yearly_long_short_by_asset.csv"), index=False)
pd.set_option("display.width", 200)
print(yd.groupby(["config", "year"])[["long_pnl", "short_pnl"]].sum().unstack().round(3).to_string())
print(yd.groupby(["config", "asset"])[["short_pnl"]].sum().unstack().round(3))

# chart: equity (log) of all configs + 50/50 buy-hold, dev+val
fig, ax = plt.subplots(figsize=(11, 6))
start = T.DEV[0]
r = px.pct_change().fillna(0.0)
bh = (0.5 * r - 0.5 * fund).sum(axis=1)
for cfg, res in res_all.items():
    p = res["port"][res["port"].index >= start]
    hi = cfg in ("N60_sma_vt20", "N120_sma_vt20")
    ax.plot((1 + p).cumprod(), lw=2.0 if hi else 0.8, alpha=1 if hi else 0.45, label=cfg if hi else None)
b = bh[bh.index >= start]
ax.plot((1 + b).cumprod(), color="black", lw=1.5, ls="--", label="Al-tut 50/50 BTC+ETH (1x)")
ax.axvline(T.VAL[0], color="gray", ls=":"); ax.text(T.VAL[0], ax.get_ylim()[1] if False else 1.0, " doğrulama →", color="gray")
ax.set_yscale("log"); ax.set_ylabel("Sermaye (başlangıç = 1, log)")
ax.set_title("BTC+ETH zaman serisi momentumu: 12 ayar (ince çizgiler) ve al-tut, 2020-05 → 2026-03")
ax.legend(loc="upper left"); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(T.OUT, "equity_curves.png"), dpi=120)
