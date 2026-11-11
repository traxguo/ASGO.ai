"""
Nasdaq idea batch: N1 news-day direction, N2 intraday momentum in high-volatility regimes.
Rules, costs, controls and the pass bar are pre-registered in results/2026-11-11_nasdaq_batch/README.md.
Data: HistData NAS100 5m bars from research/endeks_forex/fetch.py (dev + validation only, holdout never loaded).

    python research/nasdaq_batch/batch.py            # needs user_data/efb5m/NAS100_5m.feather
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "endeks_forex"))
sys.path.insert(0, str(ROOT))
import batch as efb  # noqa: E402  (data loading, price lookup, stats)
from strategies.common import news_calendar  # noqa: E402

OUT = ROOT / "results" / "2026-11-11_nasdaq_batch"
NY = "America/New_York"
COST = 1e-4          # round trip
SETS = 2000
MIN = efb.MIN
COLS = ["idea", "cell", "primary", "side", "t_in", "t_out", "gross", "day"]


def at(dates, hhmm: str) -> np.ndarray:
    """UTC ns of New York clock time hhmm on each date (0 where the local time does not exist)."""
    return efb.local_times(hhmm, NY, pd.DatetimeIndex(dates))


def trade_rows(x: efb.Inst, idea: str, cell: str, primary: bool, days, t_in, t_out, side) -> pd.DataFrame:
    """One row per day: enter at the open of the bar starting at t_in, exit at the close of the bar ending at t_out."""
    days, t_in, t_out, side = (np.asarray(v) for v in (days, t_in, t_out, side))
    p_in, p_out = x.px_open(t_in), x.px(t_out)
    ok = (side != 0) & np.isfinite(p_in) & np.isfinite(p_out) & (t_in > 0) & (t_out > t_in)
    gross = side * (p_out / p_in - 1)
    df = pd.DataFrame({"idea": idea, "cell": cell, "primary": primary, "side": side, "t_in": t_in, "t_out": t_out,
                       "gross": gross, "day": days})
    return df[ok].reset_index(drop=True)


# ------------------------------------------------------------------ N1: news-day direction

def event_days() -> pd.DataFrame:
    """One row per event day: date, kind ('am' = CPI/NFP 08:30, 'fomc' = 14:00); a day with both keeps 'am'."""
    ev = news_calendar.events()
    ev = ev[ev.time < efb.HOLDOUT]
    local = ev.time.dt.tz_convert(NY)
    ev = ev.assign(day=local.dt.tz_localize(None).dt.normalize(), hour=local.dt.hour)
    ev = ev[~((ev.name == "FOMC") & (ev.hour != 14))]          # the 2020-03-15 emergency meeting (Sunday 17:00)
    ev["kind"] = np.where(ev.name == "FOMC", "fomc", "am")
    ev = ev.sort_values(["day", "kind"]).drop_duplicates("day", keep="first")  # 'am' sorts before 'fomc'
    return ev[["day", "kind"]].reset_index(drop=True)


N1_CLOCK = {"am": ("08:25", "09:35"), "fomc": ("14:00", "14:30")}


def n1(x: efb.Inst, ev: pd.DataFrame) -> pd.DataFrame:
    out = []
    for kind, (h0, h1) in N1_CLOCK.items():
        d = ev.day[ev.kind == kind]
        t0, t1, tx = at(d, h0), at(d, h1), at(d, "16:00")
        move = x.px(t1) / x.px(t0) - 1
        for thr in (0.0, 0.002, 0.004):
            side = np.where(np.isfinite(move) & (np.abs(move) >= thr), np.sign(move), 0.0)
            out.append(trade_rows(x, "N1", f"thr{thr * 100:.2f}", thr == 0.002, d, t1, tx, side))
            out.append(trade_rows(x, "N1", f"thr{thr * 100:.2f}_fade", False, d, t1, tx, -side))
    df = pd.concat(out, ignore_index=True)
    df["kind"] = df.day.map(dict(zip(ev.day, ev.kind)))
    return df


def n1_control(x: efb.Inst, tr: pd.DataFrame, ev: pd.DataFrame, rng) -> np.ndarray:
    """Mean net return of SETS random sets: same period, non-event weekday, same clock, same side."""
    days_all = efb.DATES[~efb.DATES.isin(ev.day)]
    means = np.zeros(SETS)
    total = 0
    for (period, kind), g in tr.groupby([efb.period_of(tr.t_in.to_numpy()), "kind"]):
        pool = days_all[(days_all >= efb.VAL_START.tz_localize(None)) == (period == "val")]
        t1, tx = at(pool, N1_CLOCK[kind][1]), at(pool, "16:00")
        ret = x.px(tx) / x.px_open(t1) - 1
        ret = ret[np.isfinite(ret)]
        pick = rng.integers(0, len(ret), size=(SETS, len(g)))
        means += (ret[pick] * g.side.to_numpy()[None, :] - COST).sum(axis=1)
        total += len(g)
    return means / max(total, 1)


# ------------------------------------------------------------------ N2: intraday momentum by volatility regime

def sessions(x: efb.Inst) -> pd.DataFrame:
    d = efb.DATES
    df = pd.DataFrame({"day": d, "t10": at(d, "10:00"), "t1530": at(d, "15:30"), "t16": at(d, "16:00")})
    df["c"] = x.px(df.t16.to_numpy())
    df["p10"] = x.px(df.t10.to_numpy())
    df["p1530"] = x.px(df.t1530.to_numpy())
    df["o1530"] = x.px_open(df.t1530.to_numpy())
    df = df.dropna().reset_index(drop=True)
    gap = df.day.diff().dt.days.fillna(1)
    df["prev_c"] = df.c.shift(1).where(gap <= efb.GAP_DAYS)      # no signal across a hole in the data
    ret = (df.c / df.prev_c - 1)
    rv = ret.rolling(20).std().shift(1)                           # ends with yesterday
    med = rv.rolling(250).median()                                # also ends with yesterday (rv is already shifted)
    df["tense"] = np.where(rv.notna() & med.notna(), rv > med, np.nan)
    return df


def n2(x: efb.Inst, s: pd.DataFrame) -> pd.DataFrame:
    r_first = s.p10 / s.prev_c - 1
    r_day = s.p1530 / s.prev_c - 1
    known = s.tense.notna()
    out = []
    for cell, sig, mask, primary in [
        ("first30_tense", r_first, known & (s.tense == 1), True),
        ("first30_all", r_first, known, False),
        ("first30_calm", r_first, known & (s.tense == 0), False),
        ("to1530_tense", r_day, known & (s.tense == 1), False),
    ]:
        side = np.where(mask & sig.notna(), np.sign(sig.fillna(0)), 0.0)
        out.append(trade_rows(x, "N2", cell, primary, s.day, s.t1530, s.t16, side))
    return pd.concat(out, ignore_index=True)


def n2_control(tr: pd.DataFrame, s: pd.DataFrame, rng) -> np.ndarray:
    ret_all = (s.c / s.o1530 - 1).to_numpy()
    val = (s.day >= efb.VAL_START.tz_localize(None)).to_numpy()
    means = np.zeros(SETS)
    for period, g in tr.groupby(efb.period_of(tr.t_in.to_numpy())):
        ret = ret_all[val == (period == "val")]
        pick = rng.integers(0, len(ret), size=(SETS, len(g)))
        means += (ret[pick] * g.side.to_numpy()[None, :] - COST).sum(axis=1)
    return means / max(len(tr), 1)


# ------------------------------------------------------------------ report

def max_dd(net: np.ndarray) -> float:
    eq = np.r_[1.0, np.cumprod(1 + net)]
    peak = np.maximum.accumulate(eq)
    return float(((peak - eq) / peak).max() * 100)


def summarise(tr: pd.DataFrame) -> pd.DataFrame:
    rows = []
    tr = tr.assign(period=efb.period_of(tr.t_in.to_numpy()))
    for (idea, cell, primary), g in tr.groupby(["idea", "cell", "primary"]):
        for unit, gu in [("both", g), ("long", g[g.side > 0]), ("short", g[g.side < 0])]:
            row = {"idea": idea, "cell": cell, "primary": primary, "unit": unit}
            for period in ("dev", "val"):
                gp = gu[gu.period == period].sort_values("t_out")
                net, net2 = (gp.gross - COST).to_numpy(), (gp.gross - 2 * COST).to_numpy()
                st = efb.stats(net)
                row.update({f"{period}_n": st["n"], f"{period}_avg_pct": st["avg_pct"], f"{period}_pf": st["pf"],
                            f"{period}_win_pct": st["win_pct"], f"{period}_total_pct": st["total_pct"],
                            f"{period}_avg2x_pct": net2.mean() * 100 if len(net2) else np.nan,
                            f"{period}_dd_pct": max_dd(net) if len(net) else 0.0})
            rows.append(row)
    return pd.DataFrame(rows)


def verdict(r: pd.Series, p_dev: float) -> tuple[bool, str]:
    fails = []
    if not (r.dev_avg_pct > 0 and r.val_avg_pct > 0):
        fails.append("net")
    if not (r.dev_pf >= 1.2 and r.val_pf >= 1.2):
        fails.append("PF")
    if not p_dev < 0.05:
        fails.append("kontrol")
    if not (r.dev_avg2x_pct > 0 and r.val_avg2x_pct > 0):
        fails.append("2x masraf")
    if not r.val_n >= 30:
        fails.append("az örnek")
    if not (r.dev_dd_pct <= 25 and r.val_dd_pct <= 25):
        fails.append("düşüş")
    return (not fails), ", ".join(fails)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    x = efb.load("NAS100", efb.DATA)
    print(f"NAS100 bars {len(x.start)}, cleaned {efb.CLEAN.get('NAS100')}")
    rng = np.random.default_rng(20261111)
    ev = event_days()
    s = sessions(x)
    t1, t2 = n1(x, ev), n2(x, s)
    print(f"event days {len(ev)}, session days {len(s)}, N1 rows {len(t1)}, N2 rows {len(t2)}")
    tr = pd.concat([t1, t2], ignore_index=True)
    summ = summarise(tr)

    # pre-registered judgement units: N1 both directions together (+ each direction positive in dev), N2 per direction
    rows = []
    for idea, units in (("N1", ["both"]), ("N2", ["long", "short"])):
        prim = tr[(tr.idea == idea) & tr.primary]
        for unit in units:
            g = prim if unit == "both" else prim[prim.side > 0] if unit == "long" else prim[prim.side < 0]
            gd = g[efb.period_of(g.t_in.to_numpy()) == "dev"]
            ctrl = n1_control(x, gd, ev, rng) if idea == "N1" else n2_control(gd, s, rng)
            real = (gd.gross - COST).mean() if len(gd) else np.nan
            p = (1 + int((ctrl >= real).sum())) / (SETS + 1) if len(gd) else np.nan
            r = summ[(summ.idea == idea) & summ.primary & (summ.unit == unit)].iloc[0]
            ok, why = verdict(r, p)
            if idea == "N1":
                sides = summ[(summ.idea == idea) & summ.primary & summ.unit.isin(["long", "short"])]
                if not (sides.dev_avg_pct > 0).all():
                    ok, why = False, (why + ", " if why else "") + "bir yön geliştirmede eksi"
            rows.append({"idea": idea, "unit": unit, "p_dev": p, "ctrl_mean_pct": ctrl.mean() * 100 if len(gd) else np.nan,
                         "pass": ok, "failed": why})
    judge = pd.DataFrame(rows)

    # buy and hold over each period (first to last session close)
    bh = []
    for period, m in (("dev", s.day < efb.VAL_START.tz_localize(None)), ("val", s.day >= efb.VAL_START.tz_localize(None))):
        c = s.c[m].to_numpy()
        eq = c / c[0]
        bh.append({"period": period, "ret_pct": (eq[-1] - 1) * 100,
                   "dd_pct": float(((np.maximum.accumulate(eq) - eq) / np.maximum.accumulate(eq)).max() * 100)})

    out_tr = tr[tr.primary].copy()
    for col in ("t_in", "t_out"):
        out_tr[col] = pd.to_datetime(out_tr[col], utc=True).dt.strftime("%Y-%m-%d %H:%M")
    out_tr["net_pct"] = ((out_tr.gross - COST) * 100).round(4)
    out_tr.drop(columns=["gross", "primary"]).to_csv(OUT / "trades_primary.csv", index=False)
    summ.round(4).to_csv(OUT / "summary.csv", index=False)
    judge.round(4).to_csv(OUT / "pass.csv", index=False)
    pd.DataFrame(bh).round(2).to_csv(OUT / "buy_hold.csv", index=False)
    yearly = tr[tr.primary].assign(year=pd.to_datetime(tr.t_in[tr.primary], utc=True).dt.year, net=lambda d: d.gross - COST)
    (yearly.groupby(["idea", "year", "side"]).net.agg(["count", "mean", "sum"]) * [1, 100, 100]).round(3) \
        .to_csv(OUT / "yearly.csv")

    pd.set_option("display.width", 250, "display.max_columns", 40)
    print(summ[summ.primary].round(3).to_string(index=False))
    print(judge.round(4).to_string(index=False))
    print(pd.DataFrame(bh).round(2).to_string(index=False))


if __name__ == "__main__":
    main()
