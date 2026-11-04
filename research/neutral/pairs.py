# (a) Pair trading of co-moving coins on the survivorship-free universe. Rules fixed before the run (2026-11-04):
# - Each month (close of the month's last day): universe = top 50 by 30-day avg quote volume, >= 180 days history.
#   Pairs: highest correlation of daily log returns over the last 180 days, each coin in at most 2 pairs, P pairs.
#   Hedge ratio b = OLS slope of log(A) on log(B) over those 180 days (pairs with b <= 0 skipped).
# - Spread = log(A) - b*log(B); z = (spread - rolling mean W) / rolling std W (past data incl. today's close).
# - Entry at the close when |z| >= ENTRY (z high: short A / long B; z low: the reverse), only during the month
#   after selection. Exit when z crosses 0, stop when |z| >= 4, time limit 20 days, or if a coin stops trading.
# - Notional split A: 1/(1+b), B: b/(1+b) (gross 1 per pair). At most P open pairs, each gets 1/P of capital.
# - Cost 0.20% round trip on the pair's gross notional (x2 check), funding included.
# Neighbour grid: ENTRY 1.5/2/2.5, W 20/30/60, P 10/20.
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "research/neutral")
from common import load, simple_ret, stats, fmt, PERIODS  # noqa: E402

C, R, U, F = load(min_age=180, top_n=50)
SR = simple_ret(C)
LC = np.log(C)
dates = C.index
month_ends = [d for d in dates[:-1] if d.month != dates[dates.get_loc(d) + 1].month and d >= pd.Timestamp("2019-12-31", tz="UTC")]
STOP, TMAX = 4.0, 20


def select(t, P):
    loc = dates.get_loc(t)
    if loc < 180:
        return []
    cands = U.loc[t][U.loc[t]].index
    win = R.iloc[loc - 179:loc + 1][cands].dropna(axis=1)
    corr = win.corr().where(np.triu(np.ones((win.shape[1],) * 2, bool), 1)).stack().sort_values(ascending=False)
    used, out = {}, []
    lp = LC.iloc[loc - 179:loc + 1]
    for (a, b), c in corr.items():
        if used.get(a, 0) >= 2 or used.get(b, 0) >= 2:
            continue
        beta = np.polyfit(lp[b], lp[a], 1)[0]
        if beta <= 0:
            continue
        out.append((a, b, beta))
        used[a] = used.get(a, 0) + 1
        used[b] = used.get(b, 0) + 1
        if len(out) == P:
            break
    return out


SEL = {}


def run(ENTRY, W, P, cost):
    daily = pd.Series(0.0, index=dates)
    trades = []
    open_ = {}                                       # key -> dict
    for m_i, t0 in enumerate(month_ends):
        key = (t0, P)
        if key not in SEL:
            SEL[key] = select(t0, P)
        pairs = SEL[key]
        if not pairs:
            continue
        t1 = month_ends[m_i + 1] if m_i + 1 < len(month_ends) else dates[-1]
        Z = {}
        for a, b, beta in pairs:
            sp = LC[a] - beta * LC[b]
            Z[(a, b)] = ((sp - sp.rolling(W, min_periods=W).mean()) / sp.rolling(W, min_periods=W).std(), beta)
        run.Z.update({(a, b, t0): v for (a, b), v in Z.items()})
        run.window.append((t0, t1, [(a, b) for a, b, _ in pairs]))
    # day loop
    active = {}
    wi = 0
    for i in range(1, len(dates)):
        d = dates[i]
        # pnl of open trades for day d
        for k in list(open_):
            tr = open_[k]
            a, b, side, wa, wb = tr["a"], tr["b"], tr["side"], tr["wa"], tr["wb"]
            r = side * (wa * SR.at[d, a] - wb * SR.at[d, b]) - side * (wa * F.at[d, a] - wb * F.at[d, b])
            daily.iat[i] += r / P
            tr["ret"] += r
            tr["days"] += 1
            z = tr["Z"].iat[i]
            dead = np.isnan(C.at[d, a]) or np.isnan(C.at[d, b]) or (i + 1 < len(dates) and (np.isnan(C[a].iat[i + 1]) or np.isnan(C[b].iat[i + 1])))
            if dead or np.isnan(z) or side * z >= 0 or abs(z) >= STOP or tr["days"] >= TMAX:
                daily.iat[i] -= cost / 2 / P
                tr["ret"] -= cost
                tr["exit"] = d
                tr["why"] = "dead" if dead else "stop" if abs(z) >= STOP else "time" if tr["days"] >= TMAX else "mean"
                trades.append(tr)
                del open_[k]
        # entries: pairs whose selection window covers day d
        while wi + 1 < len(run.window) and run.window[wi + 1][0] < d:
            wi += 1
        if not run.window or run.window[wi][0] >= d or d > run.window[wi][1]:
            continue
        t0, t1, prs = run.window[wi]
        cand = []
        for a, b in prs:
            if (a, b) in open_:
                continue
            z, beta = run.Z[(a, b, t0)]
            zz = z.iat[i]
            if np.isnan(zz) or abs(zz) < ENTRY or abs(zz) >= STOP:
                continue
            if i + 1 >= len(dates) or np.isnan(C[a].iat[i + 1]) or np.isnan(C[b].iat[i + 1]):
                continue
            cand.append((abs(zz), a, b, z, beta, zz))
        for _, a, b, z, beta, zz in sorted(cand, reverse=True):
            if len(open_) >= P:
                break
            open_[(a, b)] = {"a": a, "b": b, "side": -1 if zz > 0 else 1, "wa": 1 / (1 + beta), "wb": beta / (1 + beta),
                             "Z": z, "ret": -cost / 2, "days": 0, "entry": d}
            daily.iat[i] -= cost / 2 / P
    return daily, pd.DataFrame(trades)


for per, (s, e) in PERIODS.items():
    pass
for ENTRY in (1.5, 2.0, 2.5):
    for W in (20, 30, 60):
        for P in (10, 20):
            line = f"ENTRY {ENTRY} W{W} P{P}"
            for cost in (0.0, 0.002, 0.004):
                run.Z, run.window = {}, []
                daily, T = run(ENTRY, W, P, cost)
                seg = []
                for per, (s, e) in PERIODS.items():
                    st = stats(daily, s, e)
                    t = T[(T.entry >= s) & (T.entry < e)] if len(T) else T
                    if cost == 0.002:
                        lo, sh = t[t.side == 1], t[t.side == -1]
                        seg.append(f"{per} {fmt(st)} n{len(t)} avg {t.ret.mean()*100:+.2f}% win {(t.ret>0).mean()*100:.0f}% "
                                   f"stop {(t.why=='stop').mean()*100:.0f}% time {(t.why=='time').mean()*100:.0f}%")
                    else:
                        seg.append(f"{per} {st['tot']:+.0f}% avg {t.ret.mean()*100:+.2f}%")
                line += f"\n   cost {cost*100:.1f}%: " + " | ".join(seg)
            print(line, flush=True)
