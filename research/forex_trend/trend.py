"""
Forex / gold / Nasdaq trend following on daily and 4h bars, long AND short (2026-11-04).
Rules were written down in cards/forex_trend.md before the first run; only the small neighbour
grids listed there are run. Data: the 5m bid bars from research/forex/fetch_histdata.py
(GitHub runner, cached, never committed).

    python research/forex_trend/trend.py            # normal costs + shuffled-data control
    COST_MULT=2 python research/forex_trend/trend.py  # double spread AND double swap

Execution model: signals on a bar's close, entry at the next bar's open (mid price). Stops and
targets are checked on later bars' high/low; a gap through the level fills at the open; if stop
and target are both inside one bar the stop is assumed first. Costs are charged per trade as a
round-trip fraction of the entry price plus a swap (overnight financing) per calendar day held.
Long and short are simulated as separate books, one position at a time per market and direction.
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "user_data" / "forex"
SYMBOLS = ["EURUSD", "XAUUSD", "NAS100"]
MULT = float(os.environ.get("COST_MULT", "1"))
COST = {"EURUSD": 0.00010, "XAUUSD": 0.00015, "NAS100": 0.00010}  # round trip, fraction of price
# Estimated swap, % of position per year, paid for every calendar day held. Conservative: any
# positive carry a broker might pay is ignored. (long, short)
SWAP = {"EURUSD": (1.5, 1.5), "XAUUSD": (4.0, 2.0), "NAS100": (5.0, 2.5)}
PERIODS = {"dev": ("2020-01-01", "2025-01-01"), "val": ("2025-01-01", "2026-04-01")}  # holdout untouched
RISK = 1.0  # % of equity risked per trade, used for the equity / drawdown figures


# ---------- data ----------

def load_5m(sym: str) -> pd.DataFrame:
    m = pd.read_feather(DATA / f"{sym}_5m.feather").set_index("date")
    return m[m.index < "2026-04-01"]


def bars(m: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    cnt = m.close.resample("1D").count()
    d = m.resample("1D").agg(agg).dropna()
    d = d[cnt.reindex(d.index) >= 60]  # drop the 2-hour Sunday stubs and holidays
    cnt4 = m.close.resample("4h").count()
    h4 = m.resample("4h").agg(agg).dropna()
    h4 = h4[cnt4.reindex(h4.index) >= 12]  # at least one hour of data
    return d, h4


def atr(b: pd.DataFrame, n: int = 20) -> pd.Series:
    tr = pd.concat([b.high - b.low, (b.high - b.close.shift()).abs(), (b.low - b.close.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()


def daily_trend_on(h4: pd.DataFrame, d: pd.DataFrame) -> np.ndarray:
    """+1/-1/0 from the last CLOSED day: close vs EMA100 and EMA50 vs EMA100 agree."""
    e50, e100 = ema(d.close, 50), ema(d.close, 100)
    t = pd.Series(0, index=d.index)
    t[(d.close > e100) & (e50 > e100)] = 1
    t[(d.close < e100) & (e50 < e100)] = -1
    t = t.shift(1)
    return t.reindex(h4.index.floor("D"), method="ffill").to_numpy()


# ---------- simulator ----------

def simulate(b: pd.DataFrame, sym: str, side: int, entry_sig, stop_px, exit_sig=None, trail=None,
             target_r=None, max_bars=None) -> pd.DataFrame:
    """entry_sig/exit_sig: bool arrays evaluated on bar close; stop_px: initial stop price per signal
    bar; trail: ATR array x multiple for a chandelier stop (None = no trail)."""
    o, h, l, c = (b[k].to_numpy() for k in ("open", "high", "low", "close"))
    idx = b.index
    n = len(b)
    rows = []
    i = 0
    while i < n - 1:
        if not entry_sig[i] or np.isnan(stop_px[i]):
            i += 1
            continue
        k = i + 1
        entry, stop = o[k], stop_px[i]
        risk = side * (entry - stop)
        if risk <= 0:
            i += 1
            continue
        tgt = entry + side * target_r * risk if target_r else None
        best = entry
        ex, xj = None, None
        for j in range(k, n):
            if side == 1 and l[j] <= stop:
                ex, xj = min(stop, o[j]), j
            elif side == -1 and h[j] >= stop:
                ex, xj = max(stop, o[j]), j
            elif tgt is not None and side * (h[j] if side == 1 else l[j]) >= side * tgt:
                ex, xj = (max(tgt, o[j]) if side == 1 else min(tgt, o[j])), j
            if ex is not None:
                break
            # close-based checks, acted on at the next open
            if trail is not None:
                best = max(best, c[j]) if side == 1 else min(best, c[j])
                ts = best - side * trail[j]
                stop = max(stop, ts) if side == 1 else min(stop, ts)
            done = (exit_sig is not None and exit_sig[j]) or (max_bars and j - k + 1 >= max_bars)
            if done and j + 1 < n:
                ex, xj = o[j + 1], j + 1
                break
        if ex is None:  # still open at the end of the data: close at the last close
            ex, xj = c[n - 1], n - 1
        days = max((idx[xj] - idx[k]).total_seconds() / 86400, 0)
        swap = SWAP[sym][0 if side == 1 else 1] * MULT / 100 / 365 * days
        cost = COST[sym] * MULT
        gross_pct = side * (ex / entry - 1)
        net_pct = gross_pct - cost - swap
        rows.append((idx[k], idx[xj], side, entry, ex, risk / entry, gross_pct * 100, net_pct * 100,
                     net_pct * entry / risk, gross_pct * entry / risk, days))
        i = xj  # a new signal can come from the exit bar on
    return pd.DataFrame(rows, columns=["t", "t_out", "side", "entry", "exit", "risk_frac", "gross", "net",
                                       "r", "r_gross", "days"])


# ---------- rules (see cards/forex_trend.md) ----------

def donchian(b, sym, side, n):
    """T1: close beyond the prior n-bar high/low; initial stop 2 ATR; exit on close beyond the
    opposite n/2-bar channel."""
    a = atr(b).to_numpy()
    hi, lo = b.high.rolling(n).max().shift(1), b.low.rolling(n).min().shift(1)
    xhi, xlo = b.high.rolling(n // 2).max().shift(1), b.low.rolling(n // 2).min().shift(1)
    c = b.close
    if side == 1:
        sig, stop, ex = (c > hi).to_numpy(), (c - 2 * a).to_numpy(), (c < xlo).to_numpy()
    else:
        sig, stop, ex = (c < lo).to_numpy(), (c + 2 * a).to_numpy(), (c > xhi).to_numpy()
    return simulate(b, sym, side, sig, stop, exit_sig=ex)


def ma_cross(b, sym, side, fast, slow):
    """T2: EMA fast crosses EMA slow; initial stop 3 ATR, chandelier trail 3 ATR from the best
    close; exit on the opposite cross. No re-entry until the next cross."""
    a = atr(b).to_numpy()
    f, s = ema(b.close, fast), ema(b.close, slow)
    up = (f > s).to_numpy()
    cross_up = up & ~np.roll(up, 1)
    cross_dn = ~up & np.roll(up, 1)
    cross_up[0] = cross_dn[0] = False
    cross_up[:slow] = cross_dn[:slow] = False  # warm-up
    c = b.close.to_numpy()
    if side == 1:
        return simulate(b, sym, 1, cross_up, c - 3 * a, exit_sig=~up, trail=3 * a)
    return simulate(b, sym, -1, cross_dn, c + 3 * a, exit_sig=up, trail=3 * a)


def pullback(h4, d, sym, side, target_r):
    """T3 (4h): daily trend in our direction; 4h close returns over (under) EMA20 after closing on the
    other side; stop beyond the 6-bar extreme +- 0.5 ATR; target in R; exit on daily trend loss
    or after 60 bars (10 days)."""
    tr = daily_trend_on(h4, d)
    a = atr(h4).to_numpy()
    e = ema(h4.close, 20).to_numpy()
    c = h4.close.to_numpy()
    above = c > e
    prev_above = np.roll(above, 1)
    prev_above[0] = above[0]
    if side == 1:
        sig = (tr == 1) & above & ~prev_above
        stop = h4.low.rolling(6).min().to_numpy() - 0.5 * a
    else:
        sig = (tr == -1) & ~above & prev_above
        stop = h4.high.rolling(6).max().to_numpy() + 0.5 * a
    return simulate(h4, sym, side, sig, stop, exit_sig=(tr != side), target_r=target_r, max_bars=60)


# ---------- report ----------

def stats(s: pd.DataFrame) -> dict:
    if len(s) == 0:
        return {"n": 0}
    eq = s.sort_values("t_out").r.cumsum() * RISK
    dd = (eq.cummax().clip(lower=0) - eq).max()
    wins, losses = s.r[s.r > 0].sum(), -s.r[s.r < 0].sum()
    return {"n": len(s), "avgR": s.r.mean(), "avgR_gross": s.r_gross.mean(), "win": (s.r > 0).mean() * 100,
            "pf": wins / losses if losses > 0 else np.inf, "sumR": s.r.sum(), "ddR": dd / RISK,
            "days": s.days.mean()}


def bh(b: pd.DataFrame, a: str, z: str) -> float:
    s = b.close[(b.index >= a) & (b.index < z)]
    return (s.iloc[-1] / s.iloc[0] - 1) * 100


def fmt(st: dict) -> str:
    if st["n"] == 0:
        return "0 tr"
    return (f"{st['n']:3d} tr avg {st['avgR']:+.2f}R (gross {st['avgR_gross']:+.2f}) win {st['win']:.0f}% "
            f"PF {st['pf']:.2f} sum {st['sumR']:+.1f}R DD {st['ddR']:.1f}R hold {st['days']:.1f}d")


def run_all(sym: str, d: pd.DataFrame, h4: pd.DataFrame, verbose: bool) -> list[dict]:
    configs = []
    for tf, b in (("1d", d), ("4h", h4)):
        for n in (20, 50, 100):
            configs.append((f"T1 donchian {tf} {n}", lambda s, b=b, n=n: donchian(b, sym, s, n)))
        for f, sl in ((10, 50), (20, 100), (50, 200)):
            configs.append((f"T2 ema {tf} {f}/{sl}", lambda s, b=b, f=f, sl=sl: ma_cross(b, sym, s, f, sl)))
    for t in (1.5, 2.0, 3.0):
        configs.append((f"T3 pullback 4h {t}R", lambda s, t=t: pullback(h4, d, sym, s, t)))
    out = []
    for name, fn in configs:
        for side, lab in ((1, "long"), (-1, "short")):
            r = fn(side)
            row = {"sym": sym, "cfg": name, "side": lab, "years": {}}
            line = []
            for p, (a, z) in PERIODS.items():
                s = r[(r.t >= a) & (r.t < z)]
                row[p] = stats(s)
                line.append(f"{p}: {fmt(row[p])}")
                if p == "dev" and len(s):
                    row["years"] = s.groupby(s.t.dt.year).r.sum().round(1).to_dict()
            if verbose:
                print(f"{sym} {name:22s} {lab:5s} | " + " | ".join(line), flush=True)
                print(f"{'':36s} dev years sumR {row['years']}")
            out.append(row)
    return out


def passes(row: dict) -> bool:
    """Fixed before the first run (cards/forex_trend.md)."""
    dv, vl = row["dev"], row["val"]
    if dv["n"] < 30 or vl["n"] < 8:
        return False
    pos_years = sum(1 for v in row["years"].values() if v > 0)
    return dv["avgR"] > 0 and vl["avgR"] > 0 and dv["pf"] >= 1.15 and pos_years >= 3


def shuffled(d5: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Control data: the real 5m bars with whole days put in random order. Volatility, intraday shape
    and fat tails stay; any multi-day trend persistence is destroyed."""
    lc = np.log(d5.close)
    lr = lc.diff().fillna(0).to_numpy()
    off = {k: (np.log(d5[k]) - lc).to_numpy() for k in ("open", "high", "low")}
    days = d5.index.floor("D")
    groups = [g for g in pd.Series(np.arange(len(d5)), index=days).groupby(level=0).indices.values()]
    order = rng.permutation(len(groups))
    ix = np.concatenate([groups[i] for i in order])
    close = d5.close.iat[0] * np.exp(np.cumsum(lr[ix]))
    out = pd.DataFrame({"close": close}, index=d5.index)
    for k, v in off.items():
        out[k] = close * np.exp(v[ix])
    return out[["open", "high", "low", "close"]]


def main() -> None:
    print(f"COST_MULT={MULT}  (round-trip cost and swap both multiplied)")
    summary = []
    raw = {}
    for sym in SYMBOLS:
        raw[sym] = load_5m(sym)
        d, h4 = bars(raw[sym])
        print(f"\n== {sym}: {len(d)} daily bars {d.index[0].date()} -> {d.index[-1].date()}, {len(h4)} 4h bars")
        for p, (a, z) in PERIODS.items():
            print(f"   buy & hold {p}: {bh(d, a, z):+.1f}%  (short buy & hold {-bh(d, a, z):+.1f}% before swap)")
        summary += run_all(sym, d, h4, verbose=True)

    print("\n== PASS CHECK (dev>=30 & val>=8 trades, avgR>0 in dev and val, dev PF>=1.15, >=3/5 dev years positive)")
    real = [r for r in summary if passes(r)]
    for row in real:
        dv, vl = row["dev"], row["val"]
        print(f"PASS {row['sym']} {row['cfg']:22s} {row['side']:5s} dev {dv['avgR']:+.2f}R PF {dv['pf']:.2f} "
              f"({dv['n']} tr, DD {dv['ddR']:.1f}R) | val {vl['avgR']:+.2f}R PF {vl['pf']:.2f} ({vl['n']} tr, DD {vl['ddR']:.1f}R)")
    print(f"real data: {len(real)} of {len(summary)} configs pass")

    # Control: how many configs pass on day-shuffled data (no real trends)? 90 configs are many tries.
    n_ctrl = int(os.environ.get("CONTROL_RUNS", "20"))
    counts, per = [], {}
    rng = np.random.default_rng(42)
    for k in range(n_ctrl):
        c = 0
        for sym in SYMBOLS:
            d, h4 = bars(shuffled(raw[sym], rng))
            for row in run_all(sym, d, h4, verbose=False):
                if passes(row):
                    c += 1
                    key = (row["sym"], row["cfg"], row["side"])
                    per[key] = per.get(key, 0) + 1
        counts.append(c)
        print(f"   control run {k + 1}: {c} pass", flush=True)
    if counts:
        print(f"control (day-shuffled data, {n_ctrl} runs): mean {np.mean(counts):.1f} pass, "
              f"90th pct {np.percentile(counts, 90):.0f}, max {max(counts)}")
        for row in real:
            key = (row["sym"], row["cfg"], row["side"])
            print(f"   {key}: passes on shuffled data in {per.get(key, 0)}/{n_ctrl} runs")


if __name__ == "__main__":
    main()
