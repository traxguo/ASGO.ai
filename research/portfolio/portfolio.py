"""
Portfolio backtest of the strategies that passed, with their FROZEN rules (2026-11-05).

One capital pool. Every trade risks the same fixed share of the pool (RISK, default 0.5%):
position = pool equity at entry x RISK / stop distance. Fitil has no stop, so its risk unit is the
4% stop of Derin Fitil (position = 12.5% of the pool at RISK 0.5%). Each strategy keeps its own
slot limit from the live rules; Fitil and Derin Fitil SHARE 5 slots (scripts/bitget_fitil.py MAX_OPEN).
Trades of all strategies run at the same time in the same pool, so correlation is inside the result
(same-day losses add up); the correlation matrix of the daily results is printed on top.

Equity is marked to market once a day for the multi-day strategies (Dalga, Pusula) with the coin's
daily close; the short-hold strategies (Fitil 3h, Aslan intraday) are booked at exit.

    python research/portfolio/portfolio.py research/portfolio/data results/2026-11-05_portfoy
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

RISK = 0.005
START = 10_000.0
SLOTS = {"Fitil": ("wick", 5), "Derin Fitil": ("wick", 5), "Dalga": ("Dalga", 8),
         "PusulaV2": ("PusulaV2", 3), "Aslan NAS": ("Aslan NAS", 1)}
PERIODS = {"dev": ("2020-01-01", "2025-01-01"), "val": ("2025-01-01", "2026-04-01"),
           "holdout": ("2026-04-01", "2026-10-01")}
MTM = {"Dalga", "PusulaV2"}
D1 = Path("user_data/data/binance/futures")


def load(data: Path) -> pd.DataFrame:
    t = pd.concat([pd.read_csv(f, parse_dates=["t_in", "t_out"]) for f in sorted(data.glob("trades_*.csv"))])
    for c in ("t_in", "t_out"):
        t[c] = pd.to_datetime(t[c], utc=True)
    t = t[(t.t_in >= "2020-01-01") & (t.t_in < "2026-10-01")]
    return t.sort_values(["t_in", "strategy"]).reset_index(drop=True)


def daily_closes(pairs) -> pd.DataFrame:
    out = {}
    for p in pairs:
        d = pd.read_feather(D1 / f"{p}_USDT_USDT-1d-futures.feather")
        out[p] = d.set_index(pd.to_datetime(d.date, utc=True)).close
    return pd.DataFrame(out)


def dalga_scores(t: pd.DataFrame) -> pd.Series:
    """Daily trend score (-3..+3) of the coin on the last CLOSED daily candle before each Dalga entry,
    computed with the strategy's own regime_score (needed for Dalga's own sizing rule)."""
    from strategies.candidates.pusula import regime_score
    out = pd.Series(np.nan, index=t.index)
    for pair, g in t[t.strategy == "Dalga"].groupby("pair"):
        d = pd.read_feather(D1 / f"{pair}_USDT_USDT-1d-futures.feather")
        sc = regime_score(d.set_index(pd.to_datetime(d.date, utc=True)))
        prev = sc.reindex(g.t_in.dt.floor("D") - pd.Timedelta(days=1))
        out.loc[g.index] = prev.to_numpy()
    return out


def simulate(t: pd.DataFrame, closes: pd.DataFrame, risk: float, cost_mult: float = 1.0, dalga_own: bool = False):
    """Event loop over entries and exits. Returns daily equity, the taken trades with P&L, daily P&L by strategy."""
    t = t.copy()
    t["r_ret"] = t.ret - (cost_mult - 1) * t.cost
    # at the same timestamp: exits of earlier trades, then entries, then exits of trades that open and close
    # inside the same candle (Aslan's t_out is the exit candle's open time)
    ev = [(r.t_in, 1, i) for i, r in t.iterrows()] + \
         [(r.t_out, 0 if r.t_out > r.t_in else 2, i) for i, r in t.iterrows()]
    ev.sort(key=lambda e: (e[0], e[1]))
    cash, peak, open_ = START, START, {}
    used = {g: 0 for g, _ in SLOTS.values()}
    taken = np.zeros(len(t), bool)
    notional = np.zeros(len(t))
    pnl = np.zeros(len(t))
    eq_in = np.zeros(len(t))
    gross_hist = []
    for ts, kind, i in ev:
        r = t.loc[i]
        g, cap = SLOTS[r.strategy]
        if kind == 1:
            if used[g] >= cap:
                continue
            used[g] += 1
            rk = risk
            if dalga_own and r.strategy == "Dalga":
                # Dalga's frozen sizing (strategies/candidates/dalga.py dynamic_risk), brakes on the pool's drawdown
                from strategies.candidates.dalga import dynamic_risk
                rk = dynamic_risk(r.score, cash, peak)
                if rk <= 0:
                    used[g] -= 1
                    continue
            n = cash * rk / r.stop_pct
            taken[i], notional[i], eq_in[i] = True, n, cash
            open_[i] = n
            gross_hist.append((ts, sum(open_.values()) / cash))
        elif taken[i] and i in open_:
            used[g] -= 1
            pnl[i] = open_.pop(i) * r.r_ret
            cash += pnl[i]
            peak = max(peak, cash)
    t["taken"], t["notional"], t["pnl"], t["eq_in"] = taken, notional, pnl, eq_in
    tk = t[t.taken].copy()
    # daily equity: realized P&L by exit day + open MTM of the multi-day trades
    days = pd.date_range("2020-01-01", "2026-09-30", freq="D", tz="UTC")
    realized = tk.groupby(tk.t_out.dt.floor("D")).pnl.sum().reindex(days, fill_value=0).cumsum() + START
    mtm = pd.Series(0.0, index=days)
    for r in tk[tk.strategy.isin(MTM)].itertuples():
        d0, d1 = r.t_in.floor("D"), r.t_out.floor("D")
        if d1 <= d0:
            continue
        span = days[(days >= d0) & (days < d1)]
        px = closes[r.pair].reindex(span).ffill()
        s = 1 if r.side == "long" else -1
        mtm.loc[span] += (r.notional * s * (px / r.entry - 1)).fillna(0).to_numpy()
    eq = realized + mtm
    by_strat = tk.pivot_table(index=tk.t_out.dt.floor("D"), columns="strategy", values="pnl", aggfunc="sum")
    by_strat = by_strat.reindex(days, fill_value=0).fillna(0)
    gross = pd.DataFrame(gross_hist, columns=["t", "x"]).set_index("t").x
    return eq, tk, by_strat, gross


def stats(eq: pd.Series, a: str, b: str) -> dict:
    e = eq[(eq.index >= pd.Timestamp(a, tz="UTC") - pd.Timedelta(days=1)) & (eq.index < pd.Timestamp(b, tz="UTC"))]
    dr = e.pct_change().dropna()
    m = e.resample("ME").last()
    m = pd.concat([e.iloc[:1], m]).pct_change().dropna()
    m = m[m.index >= pd.Timestamp(a, tz="UTC")]  # drop the zero "month" made by the start day
    dd = (e / e.cummax() - 1).min()
    years = (pd.Timestamp(b) - pd.Timestamp(a)).days / 365.25
    tot = e.iloc[-1] / e.iloc[0] - 1
    return {"return_pct": tot * 100, "cagr_pct": ((1 + tot) ** (1 / years) - 1) * 100, "maxdd_pct": dd * 100,
            "sharpe": dr.mean() / dr.std() * np.sqrt(365) if dr.std() > 0 else np.nan,
            "worst_month_pct": m.min() * 100, "worst_month": m.idxmin().strftime("%Y-%m"),
            "best_month_pct": m.max() * 100, "pos_months": int((m > 0).sum()), "months": len(m),
            "monthly": (m * 100).round(2)}


def bh(series: pd.Series, a, b) -> dict:
    s = series[(series.index >= pd.Timestamp(a, tz="UTC")) & (series.index < pd.Timestamp(b, tz="UTC"))].dropna()
    dr = s.pct_change().dropna()
    return {"return_pct": (s.iloc[-1] / s.iloc[0] - 1) * 100, "maxdd_pct": (s / s.cummax() - 1).min() * 100,
            "sharpe": dr.mean() / dr.std() * np.sqrt(len(dr) / ((s.index[-1] - s.index[0]).days / 365.25))}


if __name__ == "__main__":
    data, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    t = load(data)
    mtm_pairs = sorted(t[t.strategy.isin(MTM)].pair.unique())
    closes = daily_closes(sorted(set(mtm_pairs) | {"BTC"}))
    nas = pd.read_csv(data / "nas100_daily.csv", parse_dates=["date"]).set_index("date").close
    nas.index = pd.to_datetime(nas.index, utc=True)
    t["score"] = dalga_scores(t)
    res = {}
    for label, risk, cm, own in (("main", RISK, 1.0, False), ("cost2x", RISK, 2.0, False),
                                 ("risk1pct", 0.01, 1.0, False), ("risk025", 0.0025, 1.0, False),
                                 ("dalga_own", RISK, 1.0, True),
                                 ("dalga_own_cost2x", RISK, 2.0, True)):
        eq, tk, bs, gross = simulate(t, closes, risk, cm, own)
        res[label] = (eq, tk, bs, gross)
        eq.to_frame("equity").to_csv(out / f"equity_{label}.csv")
        tk.to_csv(out / f"trades_taken_{label}.csv", index=False)
    # diversification view: each strategy alone (same sizing, own pool) and the pool without it
    for name in sorted(t.strategy.unique()):
        k = name.replace(" ", "_")
        res[f"only_{k}"] = simulate(t[t.strategy == name].reset_index(drop=True), closes, RISK)
        res[f"without_{k}"] = simulate(t[t.strategy != name].reset_index(drop=True), closes, RISK)
    import pickle
    pickle.dump({"res": res, "btc": closes["BTC"], "nas": nas, "all_trades": t}, open(out / "_sim.pkl", "wb"))
    print("saved")
