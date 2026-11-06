"""
Aslan's strategy (v2 and v7, exactly as coded for crypto) on Nasdaq, EURUSD and gold.
Owner's question (2026-11-05): does Aslan's strategy fail on crypto because crypto is too
volatile, or does it have no edge at all? Card: cards/aslan_liquidity.md (section "Nasdaq testi").

The signal code is imported unchanged from strategies/candidates/aslan_liquidity*.py.
This file only builds the candles and replays orders the way Freqtrade's backtester does
(freqtrade/optimize/backtesting.py, backtest_loop):
  - signal on candle k -> limit order created on candle k+1 at the planned entry
    (clamped to that candle's high for a long / low for a short)
  - an entry fills only when the limit lies inside a candle's range; it is cancelled after
    `valid_for_candles` x timeframe minutes, or after a candle that touched the stop unfilled
  - one trade at a time per instrument; a long and a short signal on the same candle cancel out
  - per candle: the stop is checked before the target (stop wins a candle that hits both);
    the target order can already fill on the entry candle
  - gaps (weekends, holidays): a stop gapped through exits at the open
Results in R. Costs: fixed round-trip fraction of price (COST), converted to R per trade.

    python research/aslan_nasdaq/sim.py                       # all markets from user_data/forex1m
    python research/aslan_nasdaq/sim.py --btc PATH_TO_BTC_1m  # reproduce the crypto dev numbers
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ftstub  # noqa: E402

ftstub.install()

from strategies.candidates import aslan_liquidity as v1  # noqa: E402
from strategies.candidates import aslan_liquidity_v3 as v3  # noqa: E402
from strategies.candidates import aslan_liquidity_v7 as v7  # noqa: E402
from strategies.common import news_calendar  # noqa: E402

DATA = ROOT / "user_data" / "forex1m"
MARKETS = ["NAS100", "EURUSD", "XAUUSD"]
COST = {"NAS100": 0.00010, "EURUSD": 0.00010, "XAUUSD": 0.00015, "BTC": 0.002}
PERIODS = {"dev": ("2020-01-01", "2025-01-01"), "val": ("2025-01-01", "2026-04-01")}  # holdout untouched
NY = "America/New_York"
RISK = 0.01  # 1% of equity per trade (for the drawdown figure only)
MAX_STOP_PCT = 0.08  # ManagementParams.max_stop_pct
# Freqtrade skips a trade whose 1% risk would need more margin than the account has
# (custom_stake_amount): notional / 20x leverage > ~99% of equity.
MIN_STOP_PCT = RISK / (20.0 * 0.99)


# ---------------------------------------------------------------- candles


def utc_bars(m1: pd.DataFrame, minutes: int) -> pd.DataFrame:
    b = m1.resample(f"{minutes}min", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    return b.dropna().reset_index(names="date")


def session_bars(m1: pd.DataFrame, hours: int, bar_minutes: int = 1) -> pd.DataFrame:
    """
    Daily / 4h candles of the real trading day: 17:00 -> 17:00 New York time (daylight saving
    handled), as on a broker's NAS100 / EURUSD / XAUUSD chart. Weekend and holiday gaps simply
    have no candle. A daily candle with under 30 minutes of trading (holiday stub) is dropped.
    bar_minutes: size of the input bars (1 for the research data, 60 for the live paper tracker).
    """
    local = m1.index.tz_convert(NY).tz_localize(None) + pd.Timedelta(hours=7)
    key = local.floor(f"{hours}h")
    g = m1.groupby(key)
    b = g.agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(m1.index, index=m1.index).groupby(key).min()
    if hours == 24:
        b = b[g.size() * bar_minutes >= 30]
        start = (b.index - pd.Timedelta(hours=7)).tz_localize(NY).tz_convert("UTC")
    else:
        start = first.loc[b.index].dt.floor("h").to_numpy()
    b.index = pd.DatetimeIndex(start)
    return b.reset_index(names="date")


def frames(m1: pd.DataFrame, session: bool) -> dict[str, pd.DataFrame]:
    out = {"1m": m1.reset_index(names="date")}
    for tf, mins in (("5m", 5), ("15m", 15), ("1h", 60)):
        out[tf] = utc_bars(m1, mins)
    if session:
        out["4h"], out["1d"] = session_bars(m1, 4), session_bars(m1, 24)
    else:
        out["4h"], out["1d"] = utc_bars(m1, 240), utc_bars(m1, 1440)
    return out


def close_time(df: pd.DataFrame, minutes: int) -> pd.Series:
    return (pd.to_datetime(df["date"], utc=True) + pd.Timedelta(minutes=minutes)).astype("datetime64[ns, UTC]")


def asof(df: pd.DataFrame, minutes: int, table: pd.DataFrame, col: str) -> np.ndarray:
    base = pd.DataFrame({"t": close_time(df, minutes)}).reset_index()
    m = pd.merge_asof(base, table.rename(columns={"avail": "t"}), on="t", direction="backward").set_index("index")
    return m[col].fillna(0).astype(int).to_numpy()


# ---------------------------------------------------------------- signals (code imported unchanged)


def plan(df, long_ok, short_ok, entry_l, entry_s, stop_l, stop_s, target_r, valid_min):
    out = df[["date", "open", "high", "low", "close"]].copy()
    for side, ok, entry, stop in (("long", long_ok, entry_l, stop_l), ("short", short_ok, entry_s, stop_s)):
        entry = np.asarray(entry, float)
        stop = np.asarray(stop, float)
        stop_pct = np.abs(entry - stop) / entry
        plan_ok = (stop_pct <= MAX_STOP_PCT) & (stop_pct > 0)
        out[f"{side}_sig"] = np.asarray(ok, bool) & plan_ok
        out[f"{side}_entry"] = entry
        out[f"{side}_stop"] = stop
        s = 1 if side == "long" else -1
        out[f"{side}_tp"] = entry + s * target_r * np.abs(entry - stop)
    both = out["long_sig"] & out["short_sig"]
    out.loc[both, ["long_sig", "short_sig"]] = False
    out.attrs["valid_min"] = valid_min
    return out


def signals_v2(f: dict, tf: str, bias: bool) -> pd.DataFrame:
    """AslanLiq2_1h / AslanLiq2_15m (+ _NoBias): strategies/candidates/aslan_liquidity.py."""
    cls = {"1h": v1.AslanLiq2_1h, "15m": v1.AslanLiq2_15m}[tf]
    df, d1, h4 = f[tf], f["1d"], f["4h"]
    mins = {"1h": 60, "15m": 15}[tf]
    levels = pd.concat([v1.htf_levels(d1, 1440, prev_day=True), v1.htf_levels(h4, 240)], ignore_index=True)
    levels = levels.sort_values("avail", kind="stable")
    sig = v1.find_signals(df, levels, cls.setup_window, wick_cap=cls.wick_cap)
    b = asof(df, mins, v1.daily_bias(d1), "bias")
    news = news_calendar.blocked(close_time(df, mins), cls.news_before, cls.news_after).to_numpy()
    c = df["close"].to_numpy(float)
    ls, ss = sig["long_struct_stop"].to_numpy(float), sig["short_struct_stop"].to_numpy(float)
    lt, st = sig["long_trigger"].to_numpy(), sig["short_trigger"].to_numpy()
    long_ok = ((b == 1) | (not bias)) & np.isin(lt, ["mss", "ifvg"]) & (ls < c) & ~news
    short_ok = ((b == -1) | (not bias)) & np.isin(st, ["mss", "ifvg"]) & (ss > c) & ~news
    return plan(df, long_ok, short_ok, c, c, ls, ss, 2.0, cls.mgmt.valid_for_candles * mins)


def signals_v7(f: dict, retest: bool) -> pd.DataFrame:
    """AslanLiq7_1m / AslanLiq7_1m_Retest: strategies/candidates/aslan_liquidity_v7.py."""
    cls = v7.AslanLiq7_1m_Retest if retest else v7.AslanLiq7_1m
    df, m5, h1, h4, d1 = f["1m"], f["5m"], f["1h"], f["4h"], f["1d"]
    levels = v3.all_levels(h1, h4, d1)
    trend = asof(df, 1, v3.structure_trend(h4, 240), "trend")  # trend_filter "4h"
    ct = close_time(df, 1)
    news = news_calendar.blocked(ct, cls.news_before, cls.news_after).to_numpy()
    c = df["close"].to_numpy(float)
    if not retest:
        sig = v7.find_entries_1m(df, v7.mss_events(m5, levels, cls.mss_setup_window), cls.entry_window)
        ls, ss = sig["long_struct_stop"].to_numpy(float), sig["short_struct_stop"].to_numpy(float)
        long_ok = (trend == 1) & np.isin(sig["long_trigger"], ["fvg", "ifvg"]) & (ls < c) & ~news
        short_ok = (trend == -1) & np.isin(sig["short_trigger"], ["fvg", "ifvg"]) & (ss > c) & ~news
        return plan(df, long_ok, short_ok, c, c, ls, ss, 1.0, cls.mgmt.valid_for_candles)
    ev = v7.mss_gap_events(m5, levels, cls.mss_setup_window)
    cols = {}
    for side in ("long", "short"):
        e = ev[ev["side"] == side].set_index("avail")
        e = e[~e.index.duplicated(keep="last")]
        cols[f"{side}_trig"] = ct.isin(e.index).to_numpy()
        cols[f"{side}_stop"] = ct.map(e["stop"]).to_numpy(float)
        cols[f"{side}_edge"] = ct.map(e["edge"]).to_numpy(float)
    le, se = cols["long_edge"], cols["short_edge"]
    ls, ss = cols["long_stop"], cols["short_stop"]
    with np.errstate(invalid="ignore"):
        long_ok = (trend == 1) & cols["long_trig"] & (le < c) & (ls < le) & ~news
        short_ok = (trend == -1) & cols["short_trig"] & (se > c) & (ss > se) & ~news
    le = np.where(np.isnan(le), c, le)
    se = np.where(np.isnan(se), c, se)
    return plan(df, long_ok, short_ok, le, se, ls, ss, 1.0, cls.mgmt.valid_for_candles)


# ---------------------------------------------------------------- order replay


def replay(p: pd.DataFrame) -> pd.DataFrame:
    t = pd.to_datetime(p["date"], utc=True).to_numpy(dtype="datetime64[ns]").astype("int64") // 60_000_000_000
    o, h, lo = (p[c].to_numpy(float) for c in ("open", "high", "low"))
    sig = {s: p[f"{s}_sig"].to_numpy() for s in ("long", "short")}
    ent = {s: p[f"{s}_entry"].to_numpy(float) for s in ("long", "short")}
    stp = {s: p[f"{s}_stop"].to_numpy(float) for s in ("long", "short")}
    tgt = {s: p[f"{s}_tp"].to_numpy(float) for s in ("long", "short")}
    valid = p.attrs["valid_min"]
    rows, skipped = [], 0
    order = pos = None
    for j in range(1, len(p)):
        # 1. pending entry: timeout, or the previous candle touched the stop unfilled
        if order is not None:
            if t[j] >= order["t0"] + valid or order["stop_seen"]:
                order = None
        # 2. new order from the previous candle's signal (only with no trade open)
        if order is None and pos is None:
            for side in ("long", "short"):
                k = j - 1
                if sig[side][k]:
                    stop_pct = abs(ent[side][k] - stp[side][k]) / ent[side][k]
                    if stop_pct < MIN_STOP_PCT:
                        skipped += 1
                        continue
                    price = min(ent[side][k], h[j]) if side == "long" else max(ent[side][k], lo[j])
                    order = {"side": side, "t0": t[j], "price": price, "stop": stp[side][k],
                             "tp": tgt[side][k], "sig_t": t[k], "stop_seen": False}
                    break
        # 3. entry fill
        filled_now = False
        if order is not None:
            if lo[j] <= order["price"] <= h[j]:
                pos = {**order, "entry": order["price"], "t_in": t[j]}
                order, filled_now = None, True
            else:
                s = order["side"]
                order["stop_seen"] = lo[j] <= order["stop"] if s == "long" else h[j] >= order["stop"]
        # 4./5. stop first, then the target order
        if pos is not None:
            s, stop, tp = pos["side"], pos["stop"], pos["tp"]
            exit_px = None
            if s == "long":
                if lo[j] <= stop:
                    exit_px = stop if (o[j] > stop or filled_now) else o[j]
                elif h[j] >= tp:
                    exit_px = tp
            else:
                if h[j] >= stop:
                    exit_px = stop if (o[j] < stop or filled_now) else o[j]
                elif lo[j] <= tp:
                    exit_px = tp
            if exit_px is not None:
                sign = 1 if s == "long" else -1
                risk = abs(pos["entry"] - stop)
                rows.append((pd.Timestamp(pos["t_in"] * 60_000_000_000, tz="UTC"), s, pos["entry"], stop, exit_px,
                             sign * (exit_px - pos["entry"]) / risk, risk / pos["entry"],
                             pd.Timestamp(pos["sig_t"] * 60_000_000_000, tz="UTC"),
                             pd.Timestamp(t[j] * 60_000_000_000, tz="UTC")))
                pos = None
    r = pd.DataFrame(rows, columns=["t_in", "side", "entry", "stop", "exit", "gross_r", "stop_pct", "sig_t", "t_out"])
    r.attrs["skipped_tiny_stop"] = skipped
    # what is still open after the last candle (used by the live paper tracker)
    r.attrs["open_order"] = order
    r.attrs["open_pos"] = pos
    return r


def random_control(p: pd.DataFrame, r: pd.DataFrame, target_r: float, reps: int = 20, seed: int = 1) -> pd.DataFrame:
    """
    Drift control: every real trade is repeated `reps` times at a random candle of the same
    period, same side, same stop distance (%) and same target. Entry at that candle's close,
    stop first when a candle hits both. The mean gross R of these random trades is what the
    market's own up / down drift gives without any Aslan setup.
    """
    rng = np.random.default_rng(seed)
    t = pd.to_datetime(p["date"], utc=True)
    c, h, lo = (p[k].to_numpy(float) for k in ("close", "high", "low"))
    o = p["open"].to_numpy(float)
    rows = []
    for per, (a, b) in PERIODS.items():
        idx = np.flatnonzero((t >= pd.Timestamp(a, tz="UTC")) & (t < pd.Timestamp(b, tz="UTC")))
        tr = r[(r["t_in"] >= pd.Timestamp(a, tz="UTC")) & (r["t_in"] < pd.Timestamp(b, tz="UTC"))]
        if len(idx) < 2 or tr.empty:
            continue
        for side, sp in zip(tr["side"].to_numpy().repeat(reps), tr["stop_pct"].to_numpy().repeat(reps)):
            j = int(rng.choice(idx[:-1]))
            s = 1 if side == "long" else -1
            entry = c[j]
            stop, tp = entry * (1 - s * sp), entry * (1 + s * target_r * sp)
            k, res = j + 1, None
            while res is None and k < len(c):
                e = min(k + 5000, len(c))
                hit_stop = (lo[k:e] <= stop) if s == 1 else (h[k:e] >= stop)
                hit_tp = (h[k:e] >= tp) if s == 1 else (lo[k:e] <= tp)
                any_hit = hit_stop | hit_tp
                if any_hit.any():
                    m = k + int(np.argmax(any_hit))
                    if hit_stop[m - k]:
                        px = stop if (o[m] - stop) * s > 0 else o[m]
                    else:
                        px = tp
                    res = s * (px - entry) / (entry * sp)
                k = e
            if res is not None:
                rows.append((per, side, res))
    return pd.DataFrame(rows, columns=["period", "side", "gross_r"])


# ---------------------------------------------------------------- report


def stats(r: pd.DataFrame, cost: float, target_r: float) -> dict:
    if r.empty:
        return {"n": 0}
    cost_r = cost / r["stop_pct"]
    net = r["gross_r"] - cost_r
    eq = np.cumprod(1 + RISK * net.to_numpy())
    dd = 1 - eq / np.maximum.accumulate(np.maximum(eq, 1.0))
    gains, losses = net[net > 0].sum(), -net[net < 0].sum()
    return {
        "n": len(r),
        "win": (r["gross_r"] > 0).mean(),
        "be": ((1 + cost_r.mean()) / (target_r + 1)),
        "gross": r["gross_r"].mean(),
        "net": net.mean(),
        "pf": gains / losses if losses > 0 else np.inf,
        "dd": dd.max(),
        "stop": r["stop_pct"].median(),
    }


def table(results: dict, market: str, cost: float) -> str:
    lines = [
        f"\n### {market} (round-trip cost {cost * 100:.3f}%)",
        "| Version | Period | Side | Trades | Win | BE win (after cost) | R before cost | Random entry R before cost | "
        "R after cost | PF | DD (1% risk) | Median stop |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, (r, target_r, ctrl) in results.items():
        for per, (a, b) in PERIODS.items():
            rp = r[(r["t_in"] >= pd.Timestamp(a, tz="UTC")) & (r["t_in"] < pd.Timestamp(b, tz="UTC"))]
            for side in ("long", "short", "all"):
                rs = rp if side == "all" else rp[rp["side"] == side]
                s = stats(rs, cost, target_r)
                if s["n"] == 0:
                    lines.append(f"| {name} | {per} | {side} | 0 | | | | | | | | |")
                    continue
                cc = ctrl[ctrl["period"] == per]
                cc = cc if side == "all" else cc[cc["side"] == side]
                rnd = f"{cc['gross_r'].mean():+.3f}" if len(cc) else ""
                lines.append(
                    f"| {name} | {per} | {side} | {s['n']} | {s['win']:.1%} | {s['be']:.1%} | {s['gross']:+.3f} | {rnd} | "
                    f"{s['net']:+.3f} | {s['pf']:.2f} | {s['dd']:.0%} | {s['stop']:.2%} |"
                )
    return "\n".join(lines)


VERSIONS = {
    "v2 1h bias": (lambda f: signals_v2(f, "1h", True), 2.0),
    "v2 1h nobias": (lambda f: signals_v2(f, "1h", False), 2.0),
    "v2 15m bias": (lambda f: signals_v2(f, "15m", True), 2.0),
    "v2 15m nobias": (lambda f: signals_v2(f, "15m", False), 2.0),
    "v7 1m": (lambda f: signals_v7(f, False), 1.0),
    "v7 1m retest": (lambda f: signals_v7(f, True), 1.0),
}


def run_market(name: str, m1: pd.DataFrame, session: bool, out_dir: Path | None) -> dict:
    m1 = m1[m1.index < pd.Timestamp("2026-04-01", tz="UTC")]  # holdout never loaded
    f = frames(m1, session)
    res = {}
    for vname, (fn, target_r) in VERSIONS.items():
        p = fn(f)
        r = replay(p)
        res[vname] = (r, target_r, random_control(p, r, target_r))
        print(f"  {name} {vname}: {len(r)} trades, skipped (stop too small for 20x) {r.attrs['skipped_tiny_stop']}",
              flush=True)
        if out_dir is not None:
            r.to_csv(out_dir / f"{name}_{vname.replace(' ', '_')}.csv", index=False)
    return res


HOLDOUT = ("2026-04-01", "2026-10-01")


def run_holdout(out_dir: Path | None) -> None:
    """Kasa test of the frozen NAS100 v2 1h rules. Judged: bias version; nobias reported alongside."""
    global PERIODS
    m1 = pd.concat([load_1m(DATA / "NAS100_1m.feather"), load_1m(DATA / "NAS100_1m_holdout.feather")]).sort_index()
    m1 = m1[~m1.index.duplicated()]
    m1 = m1[m1.index < pd.Timestamp(HOLDOUT[1], tz="UTC")]
    f = frames(m1, session=True)
    PERIODS = {"holdout": HOLDOUT}
    res = {}
    for vname in ("v2 1h bias", "v2 1h nobias"):
        fn, target_r = VERSIONS[vname]
        p = fn(f)
        r = replay(p)
        r = r[r["t_in"] >= pd.Timestamp(HOLDOUT[0], tz="UTC")]
        res[vname] = (r, target_r, random_control(p, r, target_r))
        if out_dir is not None:
            r.to_csv(out_dir / f"NAS100_holdout_{vname.replace(' ', '_')}.csv", index=False)
    for mult in (1, 2):
        print(table(res, f"NAS100 HOLDOUT{' x2 cost' if mult == 2 else ''}", COST["NAS100"] * mult), flush=True)


def load_1m(path: Path) -> pd.DataFrame:
    m = pd.read_feather(path)
    m["date"] = pd.to_datetime(m["date"], utc=True)
    return m.set_index("date")[["open", "high", "low", "close"]].astype(float).sort_index()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--btc", type=Path, help="BTCUSDT 1m feather: reproduce the crypto dev numbers")
    ap.add_argument("--out", type=Path, help="write the trade lists here")
    ap.add_argument("--holdout", action="store_true",
                    help="ONE approved run (2026-11-05): NAS100 v2 1h on the kasa 2026-04..09, rules frozen as in PR #53")
    a = ap.parse_args()
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
    if a.holdout:
        run_holdout(a.out)
        return
    if a.btc:
        res = run_market("BTC", load_1m(a.btc), session=False, out_dir=a.out)
        print(table(res, "BTC", COST["BTC"]))
        return
    for name in MARKETS:
        res = run_market(name, load_1m(DATA / f"{name}_1m.feather"), session=True, out_dir=a.out)
        for mult in (1, 2):
            print(table(res, f"{name}{' x2 cost' if mult == 2 else ''}", COST[name] * mult), flush=True)


if __name__ == "__main__":
    main()
