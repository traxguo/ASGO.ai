# Shared daily-bar engine for the short-side research (survivorship-free universe).
# Entry at the next day's open, stop checked on daily high/low (gap through stop fills at the open),
# exit at close after H days, or earlier rule exit. Costs: round trip fee + extra slippage on stops; funding included.
import numpy as np
import pandas as pd

D_PATH = "user_data/data/allc_1d.feather"
F_PATH = "user_data/data/allc_funding.feather"
DEV = ("2020-01-01", "2025-01-01")
VAL = ("2025-01-01", "2026-04-01")


def load():
    D = pd.read_feather(D_PATH)
    F = pd.read_feather(F_PATH)
    F["date"] = F.time.dt.normalize()
    fd = F.groupby(["symbol", "date"]).rate.sum().rename("fund")  # funding paid by longs that UTC day
    D = D.join(fd, on=["symbol", "date"])
    D["has_fund"] = D.fund.notna()
    D["fund"] = D.fund.fillna(0.0)
    D = D[(D.close > 0) & (D.open > 0)].sort_values(["symbol", "date"]).reset_index(drop=True)
    D["age"] = D.groupby("symbol").cumcount()  # days since first bar
    D["last"] = D.groupby("symbol").date.transform("max")
    return D


def panels(D):
    """Wide panels indexed by date, columns symbol."""
    P = {c: D.pivot(index="date", columns="symbol", values=c) for c in ["open", "high", "low", "close", "qv", "fund", "age"]}
    return P


def simulate(P, signals, side, stop, hold, cost=0.002, stop_slip=0.003, exit_fn=None, max_open=None, stop_px=None):
    """signals: list of (signal_date, symbol, rank_key). Entry at open of next date.
    side: +1 long, -1 short. stop: fraction distance (or stop_px dict per signal index for absolute stops).
    Returns DataFrame of trades with net return (fraction of notional) and R."""
    dates = P["open"].index
    di = {d: i for i, d in enumerate(dates)}
    O, H, L, C, F = (P[k].values for k in ["open", "high", "low", "close", "fund"])
    cols = {s: j for j, s in enumerate(P["open"].columns)}
    sig = sorted(signals, key=lambda x: (x[0], x[2]))
    trades, busy_until = [], {}
    open_list = []
    for n, (d, s, key) in enumerate(sig):
        i = di[d] + 1
        if i >= len(dates):
            continue
        j = cols[s]
        if busy_until.get(s, -1) >= i:
            continue
        e = O[i, j]
        if not np.isfinite(e):
            continue
        open_list = [x for x in open_list if x >= i]
        if max_open is not None and len(open_list) >= max_open:
            continue
        sd = stop if stop_px is None else -side * (stop_px[(d, s)] / e - 1)
        if sd <= 0 or sd > 0.6:
            continue
        sp = e * (1 - side * sd)
        fund, k, exit_px, why = 0.0, i, None, "time"
        while True:
            if not np.isfinite(O[k, j]):  # delisted / data gap: exit at last known close
                exit_px, why, k = C[k - 1, j], "delist", k - 1
                break
            o, h, l, c = O[k, j], H[k, j], L[k, j], C[k, j]
            if (side < 0 and o >= sp) or (side > 0 and o <= sp):
                exit_px, why = o * (1 - side * stop_slip), "stop_gap"
                break
            if (side < 0 and h >= sp) or (side > 0 and l <= sp):
                exit_px, why = sp * (1 - side * stop_slip), "stop"
                fund += F[k, j]
                break
            fund += F[k, j]
            if exit_fn is not None and exit_fn(k, j, e, side):
                exit_px, why = c, "rule"
                break
            if k - i + 1 >= hold or k + 1 >= len(dates):
                exit_px = c
                break
            k += 1
        gross = side * (exit_px / e - 1)
        net = gross - cost - side * fund
        trades.append(dict(sig_date=d, symbol=s, entry_date=dates[i], exit_date=dates[k], entry=e, exit=exit_px,
                           why=why, gross=gross, fund=-side * fund, net=net, R=net / sd, stop=sd, days=k - i + 1))
        busy_until[s] = k
        open_list.append(k)
    return pd.DataFrame(trades)


def stats(T, label="", risk=0.01):
    if len(T) == 0:
        return dict(label=label, n=0)
    T = T.sort_values("exit_date")
    eq = (1 + risk * T.R).cumprod()
    dd = (1 - eq / eq.cummax()).max()
    win = T.R[T.R > 0].sum(); loss = -T.R[T.R < 0].sum()
    return dict(label=label, n=len(T), avgR=round(T.R.mean(), 3), medR=round(T.R.median(), 3),
                win=round((T.R > 0).mean(), 2), PF=round(win / loss, 2) if loss > 0 else np.inf,
                avg_net_pct=round(100 * T.net.mean(), 2), fund_pct=round(100 * T.fund.mean(), 2),
                eq_pct=round(100 * (eq.iloc[-1] - 1), 1), maxDD_pct=round(100 * dd, 1),
                stops=round(T.why.str.startswith("stop").mean(), 2), days=round(T.days.mean(), 1))


def split(T):
    return (T[(T.entry_date >= DEV[0]) & (T.entry_date < DEV[1])],
            T[(T.entry_date >= VAL[0]) & (T.entry_date < VAL[1])])


def report(T, label, cost_x2=None):
    dv, vl = split(T)
    rows = [stats(dv, label + " DEV"), stats(vl, label + " VAL")]
    if cost_x2 is not None:
        d2, v2 = split(cost_x2)
        rows += [stats(d2, label + " DEV 2xcost"), stats(v2, label + " VAL 2xcost")]
    return rows


def bh(P, sym, a, b):
    c = P["close"][sym].loc[a:b].dropna()
    return round(100 * (c.iloc[-1] / c.iloc[0] - 1), 1), round(100 * (1 - c / c.cummax()).max(), 1)
