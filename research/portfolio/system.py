"""
ASGO Portfoy system tests (2026-11-06), pre-registered in results/2026-11-06_portfoy_sistem/README.md.

  risk    : the PR #58 portfolio (frozen trades, same slots) at 0.25% and 0.20% risk per trade.
            dev / val drive the choice; holdout is printed only as "already seen".
  coinage : ONE rule, skip crypto trades on coins listed on Binance futures < 180 days before entry.
            Dev + val ONLY: trades entering on/after 2026-04-01 are dropped right after reading,
            daily closes are cut at 2026-03-31. Compared with the same pool without the rule.

    python research/portfolio/system.py research/portfolio/data results/2026-11-06_portfoy_sistem
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import portfolio as pf  # noqa: E402

RISKS = (0.0025, 0.0020)
AGE_DAYS = 180
HOLDOUT_START = pd.Timestamp("2026-04-01", tz="UTC")
LISTINGS = ROOT / "user_data/data/xsec_all_1d.feather"
KEYS = ("return_pct", "cagr_pct", "maxdd_pct", "sharpe", "worst_month_pct", "worst_month", "pos_months", "months")


def listing_dates(path: Path = LISTINGS) -> pd.Series:
    """First daily candle per coin on Binance USD-M futures (data starts 2020-01-01)."""
    d = pd.read_feather(path, columns=["symbol", "date"])
    first = d.groupby("symbol").date.min()
    first.index = first.index.str.replace("USDT$", "", regex=True)
    return pd.to_datetime(first, utc=True)


def coin_age_mask(t: pd.DataFrame, listed: pd.Series, days: int = AGE_DAYS) -> pd.Series:
    """True = trade is allowed. Non-crypto trades are always allowed; a crypto coin with no listing
    date is blocked (unknown age counts as young)."""
    lst = t.pair.map(listed)
    age = (t.t_in - lst).dt.days
    young = (t.market == "crypto") & (lst.isna() | (age < days))
    return ~young


def period_stats(eq, periods):
    out = {}
    for p, (a, b) in periods.items():
        s = pf.stats(eq, a, b)
        out[p] = {k: (round(float(s[k]), 2) if isinstance(s[k], float) else s[k]) for k in KEYS}
    return out


def run_risk(data: Path, out: Path) -> dict:
    t = pf.load(data)
    closes = pf.daily_closes(sorted(set(t[t.strategy.isin(pf.MTM)].pair.unique())))
    res = {}
    for r in RISKS:
        eq, tk, _, gross = pf.simulate(t, closes, r)
        res[f"{r * 100:.2f}"] = {"stats": period_stats(eq, pf.PERIODS), "max_gross": round(float(gross.max()), 2),
                                 "trades": int(len(tk))}
        eq.to_frame("equity").to_csv(out / f"equity_risk{int(r * 10000):03d}.csv")
    return res


def run_coinage(data: Path, out: Path, risk: float) -> dict:
    t = pf.load(data)
    t = t[t.t_in < HOLDOUT_START].reset_index(drop=True)  # holdout never enters the test
    closes = pf.daily_closes(sorted(set(t[t.strategy.isin(pf.MTM)].pair.unique())))
    closes = closes[closes.index < HOLDOUT_START]
    listed = listing_dates()
    keep = coin_age_mask(t, listed)
    periods = {k: v for k, v in pf.PERIODS.items() if k != "holdout"}
    res = {"risk": risk, "skipped_signals": {}}
    for p, (a, b) in periods.items():
        inp = (t.t_in >= a) & (t.t_in < b)
        res["skipped_signals"][p] = {s: int(((~keep) & inp & (t.strategy == s)).sum()) for s in sorted(t.strategy.unique())}
    for label, tt in (("base", t), ("age180", t[keep].reset_index(drop=True))):
        eq, tk, _, _ = pf.simulate(tt, closes, risk)
        res[label] = period_stats(eq, periods)
        res[label + "_by_strategy"] = {
            p: {s: round(float((g.pnl / g.eq_in).sum() * 100), 2)
                for s, g in tk[(tk.t_in >= a) & (tk.t_in < b)].groupby("strategy")}
            for p, (a, b) in periods.items()}
        res[label + "_trades"] = {p: int(((tk.t_in >= a) & (tk.t_in < b)).sum()) for p, (a, b) in periods.items()}
        eq[eq.index < HOLDOUT_START].to_frame("equity").to_csv(out / f"equity_coinage_{label}.csv")
    adopt = all(res["age180"][p]["return_pct"] > res["base"][p]["return_pct"]
                and res["age180"][p]["maxdd_pct"] >= res["base"][p]["maxdd_pct"] for p in periods)
    res["adopt"] = bool(adopt)
    return res


def choose_risk(risk_res: dict, limit: float = 15.0) -> float:
    """Highest tested level whose val max drawdown is within the limit (val only, never holdout)."""
    ok = [float(k) for k, v in risk_res.items() if -v["stats"]["val"]["maxdd_pct"] <= limit]
    return max(ok) / 100 if ok else min(float(k) for k in risk_res) / 100


if __name__ == "__main__":
    data, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    rr = run_risk(data, out)
    chosen = choose_risk(rr)
    ca = run_coinage(data, out, chosen)
    summary = {"risk_levels": rr, "chosen_risk": chosen, "coin_age": ca}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps(summary, indent=1, default=str))
