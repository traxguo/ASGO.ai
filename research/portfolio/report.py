"""
Tables and charts for the portfolio backtest (reads the _sim.pkl that portfolio.py writes).
    python research/portfolio/report.py results/2026-11-05_portfoy
Writes summary.json, monthly_<period>.csv, correlation_<period>.csv and the charts; prints the tables.
"""
import json
import pickle
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from portfolio import PERIODS, START, bh, stats  # noqa: E402

out = Path(sys.argv[1])
S = pickle.load(open(out / "_sim.pkl", "rb"))
res, btc, nas = S["res"], S["btc"], S["nas"]
STRATS = ["Fitil", "Derin Fitil", "Dalga", "PusulaV2", "Aslan NAS"]
summary = {}


def contrib(tk, a, b, key):
    """Trades closed in the period: count, mean R and the summed result as % of the pool at each entry
    (sum of pnl / pool at entry). Additive, so long + short (or the five strategies) add up."""
    x = tk[(tk.t_out >= pd.Timestamp(a, tz="UTC")) & (tk.t_out < pd.Timestamp(b, tz="UTC"))].copy()
    x["R"] = x.r_ret / x.stop_pct
    x["p"] = x.pnl / x.eq_in * 100
    g = x.groupby(key).agg(n=("R", "size"), mean_R=("R", "mean"), sum_R=("R", "sum"),
                           win_pct=("R", lambda r: (r > 0).mean() * 100), pct_of_pool=("p", "sum"))
    return g


for per, (a, b) in PERIODS.items():
    row = {}
    for label, (eq, tk, bs, gross) in res.items():
        if label.startswith(("only_", "without_")):
            continue
        s = stats(eq, a, b)
        s["monthly"].to_csv(out / f"monthly_{per}_{label}.csv", header=["return_pct"])
        s = {k: v for k, v in s.items() if k != "monthly"}
        x = tk[(tk.t_in >= pd.Timestamp(a, tz="UTC")) & (tk.t_in < pd.Timestamp(b, tz="UTC"))]
        s["trades"] = len(x)
        s["trades_per_day"] = len(x) / (pd.Timestamp(b) - pd.Timestamp(a)).days
        s["mean_r"] = float((x.r_ret / x.stop_pct).mean())
        g = gross[(gross.index >= pd.Timestamp(a, tz="UTC")) & (gross.index < pd.Timestamp(b, tz="UTC"))]
        s["max_gross_x"] = float(g.max()) if len(g) else 0.0
        s["by_side"] = contrib(tk, a, b, "side").round(3).to_dict("index")
        s["by_strategy"] = contrib(tk, a, b, "strategy").round(3).to_dict("index")
        s["by_strategy_side"] = {f"{k[0]} {k[1]}": v for k, v in
                                 contrib(tk, a, b, ["strategy", "side"]).round(3).to_dict("index").items()}
        row[label] = s
    row["variants"] = {}
    for label, (eq_, *_r) in res.items():
        if label.startswith(("only_", "without_")):
            v = stats(eq_, a, b)
            row["variants"][label] = {k: v[k] for k in ("return_pct", "maxdd_pct", "sharpe", "worst_month_pct")}
    row["btc_buyhold"] = bh(btc, a, b)
    row["nas_buyhold"] = bh(nas, a, b)
    # correlation of the daily results (P&L / equity of the day before), main run
    eq, tk, bs, _ = res["main"]
    m = (bs.index >= pd.Timestamp(a, tz="UTC")) & (bs.index < pd.Timestamp(b, tz="UTC"))
    dr = bs[m].div(eq.shift(1)[m], axis=0)
    dr["BTC"] = btc.pct_change().reindex(dr.index)
    dr["NAS100"] = nas.reindex(dr.index).ffill().pct_change()
    cor = dr.corr().round(2)
    cor.to_csv(out / f"correlation_{per}.csv")
    row["correlation"] = cor.to_dict()
    # how many strategies lost money on the same day (main run)
    lose = (bs[m][[c for c in STRATS if c in bs.columns]] < 0).sum(axis=1)
    row["days_2plus_strategies_losing"] = int((lose >= 2).sum())
    # stand-alone result of each strategy with the same sizing (same trades, own pool) for a diversification view
    summary[per] = row

json.dump(summary, open(out / "summary.json", "w"), indent=1, default=str)

# ---- charts
eq = res["main"][0]
eq2 = res["cost2x"][0]
fig, axes = plt.subplots(3, 1, figsize=(11, 12))
for ax, (per, (a, b)) in zip(axes, PERIODS.items()):
    sl = lambda s: s[(s.index >= pd.Timestamp(a, tz="UTC")) & (s.index < pd.Timestamp(b, tz="UTC"))].dropna()
    e, e2, bt, nq = sl(eq), sl(eq2), sl(btc), sl(nas)
    ax.plot(e.index, e / e.iloc[0] * 100, label="Portföy (normal masraf)", color="#1f77b4", lw=1.8)
    ax.plot(e2.index, e2 / e2.iloc[0] * 100, label="Portföy (masraf x2)", color="#1f77b4", lw=1, ls="--")
    ax.plot(bt.index, bt / bt.iloc[0] * 100, label="BTC al-tut", color="#ff7f0e", lw=1)
    ax.plot(nq.index, nq / nq.iloc[0] * 100, label="Nasdaq al-tut", color="#2ca02c", lw=1)
    name = {"dev": "Geliştirme 2020-2024", "val": "Doğrulama 2025-01 → 2026-03",
            "holdout": "Kasa 2026-04 → 2026-09 (daha önce bakıldı, taze test DEĞİL)"}[per]
    ax.set_title(name)
    ax.set_ylabel("Başlangıç = 100")
    ax.set_yscale("log" if per == "dev" else "linear")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
fig.tight_layout()
fig.savefig(out / "portfoy_sermaye.png", dpi=110)

fig, ax = plt.subplots(figsize=(11, 4))
m = eq.resample("ME").last().pct_change().dropna() * 100
ax.bar(m.index, m.values, width=20, color=np.where(m.values >= 0, "#2ca02c", "#d62728"))
ax.set_title("Portföy aylık getiri % (normal masraf, işlem başı risk %0.5)")
ax.axvline(pd.Timestamp("2025-01-01", tz="UTC"), color="k", lw=0.8, ls=":")
ax.axvline(pd.Timestamp("2026-04-01", tz="UTC"), color="k", lw=0.8, ls=":")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(out / "portfoy_aylik.png", dpi=110)

dd = (eq / eq.cummax() - 1) * 100
fig, ax = plt.subplots(figsize=(11, 3))
ax.fill_between(dd.index, dd.values, 0, color="#d62728", alpha=0.5)
ax.set_title("Portföy düşüşü (zirveden %)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(out / "portfoy_dusus.png", dpi=110)
print(json.dumps({p: {k: v for k, v in r.items() if k in ("main", "cost2x", "risk1pct", "btc_buyhold", "nas_buyhold")}
                  for p, r in summary.items()}, indent=1, default=str))
