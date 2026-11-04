# Survivorship check of the two wick catchers that run on the Bitget demo (2026-11-04):
#   up   = Fitil Avcisi  (daily score >= +1, close > EMA20, buy limit at hour-open x 0.95)
#   down = Derin Fitil   (daily score <= -1, close < EMA20, buy limit at hour-open x 0.92)
# Rules are copied from research/scans/wick_catcher.py / wick_catcher_downtrend.py and NOT changed:
# 15m fill only if low <= limit*(1-0.1%), BTC guard 3% (skip if BTC fell 3%+ from the hour open until the fill),
# no stop, market exit 3h after the fill, one trade per coin, portfolio at most 5 open, each equity/5.
# What is new:
#   UNIVERSE=pit  : a coin may only open a trade in a year it is on research/xsec/top36_yearly.json (the 36 most
#                   traded USDT perpetuals as of each January, delisted coins included, same list as DalgaPIT).
#   UNIVERSE=<file>: a fixed Freqtrade pair list (e.g. config/pairs_all36.json) = the old, survivorship-biased test.
#   COST          : total round-trip cost in % (default 0.13 = maker 0.02 in + taker 0.06 out + 0.05 slippage).
#   COOLDOWN      : hours a coin is blocked after a fill (default 0 = live rule). 24 = at most one entry per coin per day.
#   SL            : price stop in % below the entry (default 0 = no stop, live rule). Checked on 15m lows after the
#                   fill; if the fill candle already closes under it, exit at that close. A gap through the stop exits
#                   at the candle open. Stop exit costs the same as the time exit (taker + slippage).
#   FUND          : % charged per funding time (00/08/16 UTC) inside the hold (default 0.01, longs usually pay).
# Daily candles are resampled from the 15m data (UTC days). Data: research/xsec/fetch_klines_15m.py.
# Usage: python research/scans/wick_catcher_pit.py up|down START END
import json, os, sys
import numpy as np, pandas as pd

MODE, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
X = {"up": 0.05, "down": 0.08}[MODE]
H, SC, FILLPAD, GUARD, MAXO = 3, 1, 0.001, 0.03, 5
COOL = int(os.environ.get("COOLDOWN", "0"))  # no new trade on the same coin for N hours after a fill
SL = float(os.environ.get("SL", "0")) / 100
COST = float(os.environ.get("COST", "0.13")) / 100
FUND = float(os.environ.get("FUND", "0.01")) / 100
UNI = os.environ.get("UNIVERSE", "pit")
B = os.environ.get("DATA", "user_data/data/pit15m/")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if UNI == "pit":
    Y = {int(y): {s[:-4] for s in v} for y, v in json.load(open(os.path.join(ROOT, "research/xsec/top36_yearly.json"))).items()}
else:
    fixed = {p.split("/")[0] for p in json.load(open(UNI))["exchange"]["pair_whitelist"]}
    Y = {y: fixed for y in range(2019, 2031)}
coins = sorted(set().union(*Y.values()))


def load(c):
    k = pd.read_feather(B + f"{c}_USDT_USDT-15m-futures.feather").set_index("date")
    return k


bk = load("BTC")
R, missing = [], []
for c in coins:
    try:
        k = load(c)
    except FileNotFoundError:
        missing.append(c)
        continue
    dd = k.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    d = dd.close
    e20, e50 = d.ewm(span=20, adjust=False).mean(), d.ewm(span=50, adjust=False).mean()
    sc = (np.sign(d - e50) + np.sign(e20 - e50) + np.sign(d / d.shift(90) - 1)).shift(1)
    ab = (d > e20).shift(1)
    day = k.index.floor("D")
    score, abv = sc.reindex(day).to_numpy(), ab.reindex(day).to_numpy()
    o, lo, cl = (k[x].to_numpy() for x in ("open", "low", "close"))
    idx = k.index
    n = len(cl)
    inlist = np.array([c in Y.get(t.year, ()) for t in idx]) if UNI == "pit" else np.ones(n, bool)
    trend = (score >= SC) & (abv == True) if MODE == "up" else (score <= -SC) & (abv == False)
    ok = trend & inlist & (idx >= a) & (idx < b) & (idx.minute == 0)
    busy, h = -1, H * 4
    for i in np.where(ok)[0]:
        if i <= busy or i + 4 + h >= n:
            continue
        lim = o[i] * (1 - X)
        f = next((j for j in range(i, i + 4) if lo[j] <= lim * (1 - FILLPAD)), None)
        if f is None:
            continue
        # gaps in delisted coins' data: the exit candle must really be 3h after the fill
        if idx[f + h] - idx[f] != pd.Timedelta(hours=H):
            continue
        t0 = idx[i]
        bo = bk.open.get(t0)
        if bo is not None and bk.low.loc[t0:idx[f]].min() <= bo * (1 - GUARD):
            continue
        e = min(lim, o[f])
        x, jx, stop = cl[f + h], f + h, False
        if SL > 0:
            st = e * (1 - SL)
            if cl[f] <= st:
                x, jx, stop = cl[f], f, True
            else:
                for j in range(f + 1, f + 1 + h):
                    if lo[j] <= st:
                        x, jx, stop = min(st, o[j]), j, True
                        break
        tin, tout = idx[f], idx[jx] + pd.Timedelta(minutes=15)
        nfund = sum(1 for t in pd.date_range(tin.ceil("8h"), tout, freq="8h") if tin < t < tout)
        R.append((tin, c, x / e - 1, nfund, tout, stop))
        busy = max(jx, f + COOL * 4)

D = pd.DataFrame(R, columns=["t", "c", "gross", "nfund", "t_out", "stop"]).sort_values("t").reset_index(drop=True)
D["ret"] = D.gross - COST - D.nfund * FUND
days = (pd.Timestamp(b) - pd.Timestamp(a)).days
top = D.groupby(D.t.dt.floor("D")).ret.sum().nlargest(5).index
Rx = D[~D.t.dt.floor("D").isin(top)]
open_, T = [], []
for r in D.itertuples():
    open_ = [t for t in open_ if t > r.t]
    if len(open_) < MAXO:
        open_.append(r.t_out)
        T.append(r)
T = pd.DataFrame(T)
daily = T.groupby(T.t_out.dt.floor("D")).ret.sum() / MAXO
eq = (1 + daily).cumprod()
btc = bk.close.loc[a:b]
btc_dd = ((btc / btc.cummax()) - 1).min()
out = dict(mode=MODE, universe=UNI, sl_pct=SL * 100, cooldown_h=COOL,
           stops=int(T.stop.sum()) if len(T) else 0, start=a, end=b, cost_pct=COST * 100, fund_pct=FUND * 100,
           missing=missing, coins_traded=int(T.c.nunique()) if len(T) else 0,
           trades=len(T), per_day=round(len(T) / days, 3),
           mean_pct=round(T.ret.mean() * 100, 3), median_pct=round(T.ret.median() * 100, 3),
           gross_mean_pct=round(T.gross.mean() * 100, 3), win_pct=round((T.ret > 0).mean() * 100, 1),
           pf=round(T.ret[T.ret > 0].sum() / -T.ret[T.ret < 0].sum(), 2) if (T.ret < 0).any() else None,
           equity_pct=round((eq.iloc[-1] - 1) * 100, 1), maxdd_pct=round(((eq / eq.cummax()) - 1).min() * 100, 1),
           worst_day_pct=round(daily.min() * 100, 1),
           wo_top5days_mean_pct=round(Rx.ret.mean() * 100, 3),
           by_year_pct=(daily.groupby(daily.index.year).sum() * 100).round(1).to_dict(),
           by_year_trades=T.groupby(T.t.dt.year).size().to_dict(),
           btc_buyhold_pct=round((btc.iloc[-1] / btc.iloc[0] - 1) * 100, 1), btc_maxdd_pct=round(btc_dd * 100, 1))
print(json.dumps(out, default=str))
if os.environ.get("TRADES"):
    T[["t", "c", "gross", "nfund", "ret", "t_out"]].to_csv(os.environ["TRADES"], index=False)
