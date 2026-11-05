# Event short: short the USDT perp after Binance delisting / monitoring-tag announcements.
# Pre-registered in cards/olay_short.md (commit b4e83be) before any return was seen.
# Inputs: research/events/binance_announcements.csv (+ _bodies.csv), user_data/data/pit1h/*.feather (1h, delisted incl.),
#         user_data/data/allc_funding.feather. Output: research/events/out_*.csv
import re, itertools, os
import numpy as np, pandas as pd

rng = np.random.default_rng(5)
OUT = "research/events/"
DEV = (pd.Timestamp("2020-01-01", tz="UTC"), pd.Timestamp("2025-01-01", tz="UTC"))
VAL = (pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-04-01", tz="UTC"))
PIT = "user_data/data/pit1h/"
SYMS = {f.split("_USDT")[0] + "USDT" for f in os.listdir(PIT)}

A = pd.read_csv(OUT + "binance_announcements.csv").drop_duplicates("code")
A["t"] = pd.to_datetime(A.release_ms, unit="ms", utc=True)
B = pd.read_csv(OUT + "binance_announcement_bodies.csv") if os.path.exists(OUT + "binance_announcement_bodies.csv") else pd.DataFrame(columns=["code", "body"])
body = dict(zip(B.code, B.body.fillna("")))


def tickers(text):
    out = []
    for w in re.findall(r"\b[A-Z0-9]{2,}\b", text):
        for s in (w + "USDT", "1000" + w + "USDT", w):
            if s in SYMS and s not in out and s.endswith("USDT"):
                out.append(s); break
    return out


def classify(title):
    t = title
    if re.search(r"monitoring tag", t, re.I) and not re.search(r"remove", t, re.I):
        return "E2"
    if re.search(r"delist", t, re.I):
        if re.search(r"futures|perpetual|usdⓈ-m", t, re.I):
            return "E3"
        if not re.search(r"margin|trading pair|earn|convert", t, re.I):
            return "E1"
    return None


rows = []
for _, a in A.iterrows():
    typ = classify(a.title)
    if typ is None:
        continue
    t = a.title
    if typ == "E2":
        seg = re.split(r"include", t, flags=re.I)[-1]
        seg = re.split(r" on 20\d\d|, remove", seg, flags=re.I)[0]
        coins = tickers(seg)
    elif typ == "E1":
        seg = re.split(r"delist", t, flags=re.I)[-1]
        seg = re.split(r" on 20\d\d| on \d|\(", seg)[0]
        coins = tickers(seg)
    else:  # E3: contract names in title/body (XXXUSDT), else tickers in the title
        txt = t + " " + body.get(a.code, "")
        coins = [s for s in dict.fromkeys(re.findall(r"\b((?:1000)?[A-Z0-9]+USDT)\b", txt)) if s in SYMS]
        if not coins:
            seg = re.split(r"delist", t, flags=re.I)[-1]
            coins = tickers(seg)
    for c in coins:
        rows.append(dict(code=a.code, t=a.t, typ=typ, sym=c, title=t))
EV = pd.DataFrame(rows).sort_values("t").reset_index(drop=True)
EV.to_csv(OUT + "out_events_raw.csv", index=False)

# 30-day dedupe per coin across types (first event counts)
keep, last = [], {}
for i, r in EV.iterrows():
    if r.sym in last and (r.t - last[r.sym]).days < 30:
        continue
    last[r.sym] = r.t; keep.append(i)
EV = EV.loc[keep].reset_index(drop=True)

# ---------- hourly data ----------
HC = {}


def hdata(s):
    if s not in HC:
        f = PIT + f"{s[:-4]}_USDT_USDT-1h-futures.feather"
        HC[s] = pd.read_feather(f).set_index("date").sort_index() if os.path.exists(f) else None
    return HC[s]


F = pd.read_feather("user_data/data/allc_funding.feather")
FD = {s: g.set_index("time").rate.sort_index() for s, g in F.groupby("symbol")}


def trade(s, t_entry, hold_h, stop, cost, slip=0.003):
    """short at the open of the first bar >= t_entry; stop on highs; exit close after hold_h bars or at data end."""
    x = hdata(s)
    if x is None:
        return None
    i = x.index.searchsorted(t_entry)
    if i >= len(x) or (x.index[i] - t_entry) > pd.Timedelta(hours=6):
        return None
    e = x.open.iloc[i]
    if not np.isfinite(e) or e <= 0:
        return None
    sp = e * (1 + stop)
    seg = x.iloc[i:i + hold_h]
    hit = np.nonzero(seg.high.values >= sp)[0]
    if len(hit):
        k = hit[0]
        ex = (max(seg.open.values[k], sp) if k > 0 else sp) * (1 + slip)  # gap through the stop fills at the open
        why = "stop"
    else:
        k = len(seg) - 1; ex = seg.close.values[k]; why = "time" if len(seg) == hold_h else "data_end"
    t0, t1 = seg.index[0], seg.index[k] + pd.Timedelta(hours=1)
    fr = FD.get(s)
    fund = fr[(fr.index > t0) & (fr.index <= t1)].sum() if fr is not None else 0.0
    gross = -(ex / e - 1)
    net = gross - cost + fund
    return dict(entry=t0, exit=t1, entry_px=e, exit_px=ex, why=why, gross=gross, fund=fund, net=net, R=net / stop, hours=k + 1)


def per_of(t):
    return "DEV" if DEV[0] <= t < DEV[1] else ("VAL" if VAL[0] <= t < VAL[1] else None)


def run(delay, hold_d, stop, cost=0.002, max_open=10, events=EV):
    out, opn = [], []
    for _, r in events.iterrows():
        te = r.t.floor("h") + pd.Timedelta(hours=delay)
        p = per_of(te)
        if p is None:
            continue
        tr = trade(r.sym, te, hold_d * 24, stop, cost)
        if tr is None:
            continue
        opn = [x for x in opn if x > tr["entry"]]
        if len(opn) >= max_open:
            continue
        opn.append(tr["exit"])
        out.append(dict(per=p, typ=r.typ, sym=r.sym, title=r.title, **tr))
    return pd.DataFrame(out)


def st(T, risk=0.01):
    if len(T) == 0:
        return dict(n=0)
    T = T.sort_values("exit")
    eq = (1 + risk * T.R).cumprod(); dd = (1 - eq / eq.cummax()).max()
    w = T.R[T.R > 0].sum(); l = -T.R[T.R < 0].sum()
    top3 = T.R.sort_values(ascending=False).iloc[3:].mean() if len(T) > 3 else np.nan
    return dict(n=len(T), avgR=round(T.R.mean(), 3), medR=round(T.R.median(), 3), PF=round(w / l, 2) if l > 0 else np.inf,
                win=round((T.R > 0).mean(), 2), avg_net_pct=round(100 * T.net.mean(), 2), fund_pct=round(100 * T.fund.mean(), 2),
                eq_pct=round(100 * (eq.iloc[-1] - 1), 1), maxDD_pct=round(100 * dd, 1), stops=round((T.why == "stop").mean(), 2),
                avgR_wo_top3=round(top3, 3))


ROWS = []
for delay, hold_d, stop in itertools.product([1, 2, 24], [3, 7, 14, 30], [0.2, 0.3, 0.5]):
    base = (delay, hold_d, stop) == (2, 7, 0.3)
    T = run(delay, hold_d, stop); T2 = run(delay, hold_d, stop, cost=0.004)
    for per in ("DEV", "VAL"):
        for typ in ("ALL", "E1", "E2", "E3"):
            t = T[(T.per == per) & ((T.typ == typ) | (typ == "ALL"))] if len(T) else T
            t2 = T2[(T2.per == per) & ((T2.typ == typ) | (typ == "ALL"))] if len(T2) else T2
            ROWS.append(dict(cfg=f"d{delay} H{hold_d} S{int(stop*100)}", base=base, per=per, typ=typ, **st(t), avgR_2x=st(t2).get("avgR")))
    if base:
        Tb = T
        T.to_csv(OUT + "out_base_trades.csv", index=False)
R = pd.DataFrame(ROWS); R.to_csv(OUT + "out_grid.csv", index=False)

# ---------- random-date control: same coins, same period, >=30 days from that coin's events ----------
ev_times = EV.groupby("sym").t.apply(list).to_dict()
CT = []
for per, (a, z) in (("DEV", DEV), ("VAL", VAL)):
    nb = Tb[Tb.per == per]
    if len(nb) == 0:
        continue
    pool = []
    for s in nb.sym:
        x = hdata(s)
        idx = x.index[(x.index >= a) & (x.index < z - pd.Timedelta(days=7))]
        if len(idx) == 0:
            continue
        far = np.ones(len(idx), bool)
        for te in ev_times.get(s, []):
            far &= np.abs((idx - te).total_seconds()) > 30 * 86400
        idx = idx[far]
        for t0 in idx[rng.integers(0, len(idx), min(30, len(idx)))] if len(idx) else []:
            tr = trade(s, t0, 7 * 24, 0.3, 0.002)
            if tr is not None:
                pool.append(tr["R"])
    pool = np.array(pool)
    m = np.array([pool[rng.integers(0, len(pool), len(nb))].mean() for _ in range(2000)])
    CT.append(dict(per=per, n=len(nb), base_avgR=round(nb.R.mean(), 3), ctrl_meanR=round(m.mean(), 3),
                   ctrl_p95=round(np.percentile(m, 95), 3), p_value=round((m >= nb.R.mean()).mean(), 3), pool=len(pool)))
CT = pd.DataFrame(CT); CT.to_csv(OUT + "out_control.csv", index=False)

pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); pd.set_option("display.max_columns", 30)
print("events after dedupe:", len(EV), EV.groupby("typ").size().to_dict())
print(R[R.base].to_string(index=False))
print(CT.to_string(index=False))
g = R[(R.typ == "ALL")].pivot_table(index="cfg", columns="per", values="avgR")
print("neighbours positive in both periods:", int(((g.DEV > 0) & (g.VAL > 0)).sum()), "of", len(g))
print(g.to_string())
