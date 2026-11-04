"""
Shared helpers for the market-neutral (long+short) research, 2026-11-04.

Data (not committed, see research/xsec/fetch_all_daily.py and research/neutral/fetch_funding_daily.py):
  user_data/data/xsec_all_1d.feather          daily close + quote volume, every USDT perp ever listed (delisted incl.)
  user_data/data/xsec_all_funding_1d.feather  funding summed per UTC day (>0: longs pay shorts)

Everything here is close-to-close on daily bars. A decision made with data up to the close of day t trades at
that close; returns are earned from day t+1 on. A coin that stops trading exits at its last available close.
"""
import numpy as np
import pandas as pd

PERIODS = {"dev": ("2020-01-01", "2025-01-01"), "val": ("2025-01-01", "2026-04-01")}
HOLDOUT_START = "2026-04-01"   # never used here


def load(min_age=180, top_n=50, vol_days=30):
    D = pd.read_feather("user_data/data/xsec_all_1d.feather")
    C = D.pivot(index="date", columns="symbol", values="close").sort_index()
    C = C[C.index < HOLDOUT_START]
    V = D.pivot(index="date", columns="symbol", values="quote_volume").reindex(C.index)
    R = np.log(C).diff()                          # daily log return, NaN when the coin is not trading
    VOL = V.rolling(vol_days, min_periods=vol_days).mean()
    AGE = C.notna().cumsum()
    VOL = VOL.where((AGE >= min_age) & C.notna())
    # point-in-time universe: top_n by trailing average quote volume among coins with enough history
    rank = VOL.rank(axis=1, ascending=False)
    U = rank <= top_n
    try:
        F = pd.read_feather("user_data/data/xsec_all_funding_1d.feather")
        F = F.pivot(index="date", columns="symbol", values="funding").reindex(C.index).reindex(columns=C.columns)
        F = F.fillna(0.0)
    except FileNotFoundError:
        F = pd.DataFrame(0.0, index=C.index, columns=C.columns)
    return C, R, U, F


def simple_ret(C):
    """Arithmetic daily return; when a coin dies, its last return is to its last close and later days are 0."""
    return (C / C.ffill().shift(1) - 1).fillna(0.0)


def stats(daily, start, end):
    """daily: pd.Series of portfolio returns (already net of costs). Returns dict of summary numbers."""
    d = daily[(daily.index >= start) & (daily.index < end)]
    eq = (1 + d).cumprod()
    yrs = max(len(d) / 365.0, 1e-9)
    dd = (1 - eq / eq.cummax()).max()
    tot = eq.iloc[-1] - 1 if len(eq) else 0.0
    cagr = (1 + tot) ** (1 / yrs) - 1 if tot > -1 else -1.0
    sharpe = d.mean() / d.std() * np.sqrt(365) if d.std() > 0 else 0.0
    return {"tot": tot * 100, "cagr": cagr * 100, "dd": dd * 100, "sharpe": sharpe}


def fmt(s):
    return f"tot {s['tot']:+7.1f}% cagr {s['cagr']:+6.1f}% dd {s['dd']:5.1f}% sh {s['sharpe']:+.2f}"


def buy_hold(C, sym, start, end):
    c = C[sym][(C.index >= start) & (C.index < end)].dropna()
    eq = c / c.iloc[0]
    return (eq.iloc[-1] - 1) * 100, (1 - eq / eq.cummax()).max() * 100


def run_weights(W, SR, F, cost=0.002, hold=1):
    """
    W: target weights formed at the close of each day (rows = dates, cols = symbols), long > 0, short < 0,
       normally sum(long) = 0.5 and sum(short) = -0.5 (gross exposure 1, no leverage).
    hold: overlapping portfolios, each formation is held `hold` days with weight 1/hold.
    cost: round trip cost per unit notional (0.002 = 0.20%), charged as cost/2 on every unit traded.
    Returns dict of daily series: both / long / short (legs scaled to 1 unit of notional each).
    """
    W = W.reindex(index=SR.index, columns=SR.columns).fillna(0.0)
    Wp = W.rolling(hold, min_periods=1).mean()
    trade = (Wp - Wp.shift(1).fillna(0.0)).abs()
    held = Wp.shift(1).fillna(0.0)                     # weights held during day t+1
    pnl = held * SR - held * F                         # long pays positive funding, short receives it
    tc = (trade * cost / 2).shift(1).fillna(0.0)
    out = {"both": pnl.sum(axis=1) - tc.sum(axis=1)}
    for side, Ws in (("long", Wp.clip(lower=0)), ("short", Wp.clip(upper=0))):
        h = Ws.shift(1).fillna(0.0)
        t = ((Ws - h).abs() * cost / 2).shift(1).fillna(0.0)
        out[side] = 2 * ((h * SR - h * F).sum(axis=1) - t.sum(axis=1))
    return out


def report(name, series, C, extra=""):
    lines = []
    for per, (s, e) in PERIODS.items():
        parts = [f"{k[0].upper()}:{fmt(stats(v, s, e))}" for k, v in series.items()]
        lines.append(f"  {per}: " + " | ".join(parts[:1]) + "   [long " + f"{stats(series['long'], s, e)['tot']:+.0f}%"
                     + f", short {stats(series['short'], s, e)['tot']:+.0f}%]")
    return f"{name} {extra}\n" + "\n".join(lines)
