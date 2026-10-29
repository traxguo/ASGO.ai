"""
First forex scan (2026-10-28, owner's question: is scalping easier in forex?). Rules were written
down before the first run (cards/forex_tarama.md). Runs on a GitHub runner on the 5m bid/ask bars
from fetch_histdata.py. Costs: a fixed round-trip cost per instrument (COST) is applied as an ask-bid gap; market buys pay
the ask, market sells get the bid, limit orders fill only if the opposite side trades through.

    python research/forex/scan.py
"""

import os

import numpy as np
import pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "user_data" / "forex"
SYMBOLS = ["EURUSD", "XAUUSD", "NAS100"]
# Round-trip cost (spread + commission) of a typical ECN account, as a fraction of price. The bars are
# bid only, so this is applied as a fixed ask-bid gap. COST_MULT=2 reruns everything at double cost.
COST = {"EURUSD": 0.00010, "XAUUSD": 0.00015, "NAS100": 0.00010}
COMMISSION = {s: 0.0 for s in SYMBOLS}
PERIODS = {"dev": ("2020-01-01", "2025-01-01"), "val": ("2025-01-01", "2026-04-01")}  # holdout untouched
SESSIONS = {"EURUSD": ("Europe/London", "08:00", "13:00"), "XAUUSD": ("Europe/London", "08:00", "13:00"),
            "NAS100": ("America/New_York", "09:30", "12:00")}


def load(sym: str) -> pd.DataFrame:
    bid = pd.read_feather(DATA / f"{sym}_5m.feather").set_index("date")
    gap = bid.close * COST[sym] * float(os.environ.get("COST_MULT", "1"))
    df = pd.DataFrame(index=bid.index)
    for c in ("open", "high", "low", "close"):
        df[f"bid_{c}"] = bid[c]
        df[f"ask_{c}"] = bid[c] + gap
    df["mid_open"] = (df.bid_open + df.ask_open) / 2
    df["mid_high"] = (df.bid_high + df.ask_high) / 2
    df["mid_low"] = (df.bid_low + df.ask_low) / 2
    df["mid_close"] = (df.bid_close + df.ask_close) / 2
    return df


def daily_trend(df: pd.DataFrame) -> pd.Series:
    """+1 uptrend / -1 downtrend / 0, from the last CLOSED UTC day (as in the crypto Fitil filter)."""
    d = df.mid_close.resample("1D").last().dropna()
    e20, e50 = d.ewm(span=20, adjust=False).mean(), d.ewm(span=50, adjust=False).mean()
    score = np.sign(d - e50) + np.sign(e20 - e50) + np.sign(d / d.shift(90) - 1)
    t = pd.Series(0, index=d.index)
    t[(score >= 1) & (d > e20)] = 1
    t[(score <= -1) & (d < e20)] = -1
    return t.shift(1)  # usable from the next day on


def trend_at(df: pd.DataFrame, trend: pd.Series) -> np.ndarray:
    return trend.reindex(df.index.floor("D")).to_numpy()


def result(rows: list[tuple], sym: str) -> pd.DataFrame:
    """rows: (time, side, entry, exit, mid_entry, mid_exit); returns net and gross % per trade."""
    r = pd.DataFrame(rows, columns=["t", "side", "entry", "exit", "mid_in", "mid_out"])
    c = 2 * COMMISSION[sym]
    r["net"] = (r.side * (r.exit / r.entry - 1) - c) * 100
    r["gross"] = (r.side * (r.mid_out / r.mid_in - 1)) * 100
    return r


def limit_fade(df, sym, trend, k, hold_h):
    """A: hourly limit k x ATR(1h,14) against the hour open, in the daily trend direction; time exit."""
    h = df.mid_close.resample("1h").last().dropna()
    hh, hl = df.mid_high.resample("1h").max().reindex(h.index), df.mid_low.resample("1h").min().reindex(h.index)
    tr = pd.concat([hh - hl, (hh - h.shift()).abs(), (hl - h.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().shift(1)  # last closed hour
    tr_at = trend_at(df, trend)
    idx = df.index
    pos = {t: i for i, t in enumerate(idx)}
    rows, busy = [], idx[0]
    n_hold = hold_h * 12
    for hour, a in atr.dropna().items():
        i = pos.get(hour)
        if i is None or hour < busy or i + 12 + n_hold >= len(idx):
            continue
        side = tr_at[i]
        if side not in (1, -1):
            continue
        o = df.mid_open.iat[i]
        lim = o - side * k * a
        for j in range(i, i + 12):  # rests for one hour
            if idx[j] >= hour + pd.Timedelta(hours=1):
                break
            if side == 1 and df.ask_low.iat[j] < lim:
                entry = min(lim, df.ask_open.iat[j])
            elif side == -1 and df.bid_high.iat[j] > lim:
                entry = max(lim, df.bid_open.iat[j])
            else:
                continue
            x = min(j + n_hold, len(idx) - 1)
            ex = df.bid_open.iat[x] if side == 1 else df.ask_open.iat[x]
            mid_in = entry - side * (df.ask_open.iat[j] - df.bid_open.iat[j]) / 2
            rows.append((idx[j], side, entry, ex, mid_in, df.mid_open.iat[x]))
            busy = idx[x]
            break
    return result(rows, sym)


def opening_range(df, sym, target_r, with_trend):
    """B: first-hour range of the session; trade the first 5m close beyond it; stop at the other side."""
    tz, start, end = SESSIONS[sym]
    local = df.index.tz_convert(tz)
    tr_at = trend_at(df, daily_trend(df)) if with_trend else None
    rows = []
    s_min = int(start[:2]) * 60 + int(start[3:])
    e_min = int(end[:2]) * 60 + int(end[3:])
    mins = local.hour * 60 + local.minute
    days = pd.Series(np.arange(len(df)), index=local.normalize())
    for day, ix in days.groupby(level=0):
        ix = ix.to_numpy()
        m = mins[ix]
        rng = ix[(m >= s_min) & (m < s_min + 60)]
        sess = ix[(m >= s_min + 60) & (m < e_min)]
        if len(rng) < 10 or len(sess) < 6:
            continue
        hi, lo = df.mid_high.iloc[rng].max(), df.mid_low.iloc[rng].min()
        for p, j in enumerate(sess[:-1]):
            c = df.mid_close.iat[j]
            side = 1 if c > hi else -1 if c < lo else 0
            if side == 0:
                continue
            if with_trend and tr_at[j] != side:
                break
            k = j + 1
            entry = df.ask_open.iat[k] if side == 1 else df.bid_open.iat[k]
            stop = lo if side == 1 else hi
            risk = abs(entry - stop)
            if risk <= 0:
                break
            tgt = entry + side * target_r * risk
            ex, xk = None, None
            for q in sess[p + 1:]:
                if side == 1:
                    if df.bid_low.iat[q] <= stop:
                        ex, xk = min(stop, df.bid_open.iat[q]), q
                        break
                    if df.bid_high.iat[q] >= tgt:
                        ex, xk = tgt, q
                        break
                else:
                    if df.ask_high.iat[q] >= stop:
                        ex, xk = max(stop, df.ask_open.iat[q]), q
                        break
                    if df.ask_low.iat[q] <= tgt:
                        ex, xk = tgt, q
                        break
            if ex is None:
                xk = sess[-1]
                ex = df.bid_close.iat[xk] if side == 1 else df.ask_close.iat[xk]
            rows.append((df.index[k], side, entry, ex, df.mid_open.iat[k], (ex + (df.ask_close.iat[xk] - df.bid_close.iat[xk]) / 2 * side)))
            break
    return result(rows, sym)


def rsi2(df, sym, trend, hold_h):
    """C: 15m RSI(2) extreme in the daily trend direction; exit on RSI back over 70 / under 30 or time."""
    m = df.resample("15min").agg({"mid_close": "last", "bid_open": "first", "ask_open": "first", "mid_open": "first"}).dropna()
    d = m.mid_close.diff()
    up, dn = d.clip(lower=0).ewm(alpha=0.5, adjust=False).mean(), (-d.clip(upper=0)).ewm(alpha=0.5, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn.replace(0, np.nan))).to_numpy()
    tr_at = trend.reindex(m.index.floor("D")).to_numpy()
    rows, i, n = [], 0, len(m)
    while i < n - 2:
        side = tr_at[i]
        if (side == 1 and rsi[i] < 5) or (side == -1 and rsi[i] > 95):
            k = i + 1
            entry = m.ask_open.iat[k] if side == 1 else m.bid_open.iat[k]
            x = min(k + hold_h * 4, n - 1)
            for j in range(k, min(k + hold_h * 4, n - 1)):
                if (side == 1 and rsi[j] > 70) or (side == -1 and rsi[j] < 30):
                    x = j + 1
                    break
            ex = m.bid_open.iat[x] if side == 1 else m.ask_open.iat[x]
            rows.append((m.index[k], side, entry, ex, m.mid_open.iat[k], m.mid_open.iat[x]))
            i = x
        i += 1
    return result(rows, sym)


def report(name: str, sym: str, r: pd.DataFrame) -> None:
    out = []
    for p, (a, b) in PERIODS.items():
        s = r[(r.t >= a) & (r.t < b)]
        days = (pd.Timestamp(b) - pd.Timestamp(a)).days
        if len(s) == 0:
            out.append(f"{p}: 0 tr")
            continue
        yrs = s.groupby(s.t.dt.year).net.mean().round(3).to_dict() if p == "dev" else ""
        out.append(f"{p}: {len(s)} tr ({len(s) / days:.2f}/day) net {s.net.mean():+.3f}% gross {s.gross.mean():+.3f}% "
                   f"win {(s.net > 0).mean() * 100:.0f}% sum {s.net.sum():+.1f}% long {s[s.side == 1].net.mean():+.3f} "
                   f"short {s[s.side == -1].net.mean():+.3f} {yrs}")
    print(f"{sym:14s} {name:22s} | " + " | ".join(out), flush=True)


def main() -> None:
    for sym in SYMBOLS:
        df = load(sym)
        spread = ((df.ask_close - df.bid_close) / df.mid_close * 100)
        print(f"== {sym}: {len(df)} bars, median spread {spread.median():.4f}%, "
              f"median daily range {((df.mid_high.resample('1D').max() / df.mid_low.resample('1D').min() - 1) * 100).median():.2f}%")
        trend = daily_trend(df)
        for k in (1.0, 1.5, 2.0):
            for hold in (1, 3):
                report(f"A limit k{k} hold{hold}h", sym, limit_fade(df, sym, trend, k, hold))
        for tgt in (1.0, 2.0):
            for wt in (False, True):
                report(f"B ORB {tgt}R trend={int(wt)}", sym, opening_range(df, sym, tgt, wt))
        for hold in (2, 4):
            report(f"C RSI2 hold{hold}h", sym, rsi2(df, sym, trend, hold))


if __name__ == "__main__":
    main()
