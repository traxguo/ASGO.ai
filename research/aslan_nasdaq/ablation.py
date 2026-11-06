"""
One-filter-at-a-time ablation of the frozen Nasdaq rule (AslanLiq2_1h, daily bias filter, 2R) on NAS100,
dev (2020-01..2024-12) and val (2025-01..2026-03) only. The holdout is spent and not loaded.

Pre-registered (results/2026-11-06_aslan_ablasyon/README.md, written and committed before the first run):
each variant loosens or removes exactly ONE filter of the rejection funnel (funnel.py), everything else frozen.

  A  window24   confirmation window 12 -> 24 1h candles after the last liquidity sweep
  B  nobias     daily bias filter removed (trades both ways whatever the daily bias)
  C  nonews     FOMC / CPI / NFP 1-hour block removed
  D  nomaxstop  8% maximum stop distance removed
  E  nominstop  minimum stop distance (1% risk at 20x leverage) removed
  F  maxopen2   up to 2 trades / orders open at the same time instead of 1
  G  valid4     limit order valid 4 candles instead of 2
  combined      every variant above that passes on its own, together (only if 2 or more pass)

Not ablated: "stop on the wrong side of the close" (no valid trade exists) and "long and short signal on
the same candle" (one trade per instrument cannot take both).

Pass (vs the frozen rule, every condition in BOTH dev and val):
  1. more trades per month,
  2. higher total net R at the normal cost (0.010% round trip),
  3. average net R > 0 at 2x cost,
  4. average gross R above the random-entry control.

    python research/aslan_nasdaq/fetch_1m.py
    python research/aslan_nasdaq/ablation.py
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim  # noqa: E402
from sim import news_calendar, v1  # noqa: E402

CLS = v1.AslanLiq2_1h
COST = sim.COST["NAS100"]
MONTHS = {"dev": 60, "val": 15}

FROZEN = dict(window=CLS.setup_window, bias=True, news=True, max_stop=sim.MAX_STOP_PCT,
              min_stop=sim.MIN_STOP_PCT, max_open=1, valid=CLS.mgmt.valid_for_candles)
VARIANTS = {
    "frozen": {},
    "A window24": {"window": 24},
    "B nobias": {"bias": False},
    "C nonews": {"news": False},
    "D nomaxstop": {"max_stop": np.inf},
    "E nominstop": {"min_stop": 0.0},
    "F maxopen2": {"max_open": 2},
    "G valid4": {"valid": 4},
}


@contextmanager
def max_stop(v: float):
    old = sim.MAX_STOP_PCT
    sim.MAX_STOP_PCT = v
    try:
        yield
    finally:
        sim.MAX_STOP_PCT = old


def signals(f: dict, window: int, bias: bool, news: bool, max_stop_pct: float, valid: int) -> pd.DataFrame:
    """sim.signals_v2(f, '1h', bias) with the filters as parameters."""
    df, d1, h4 = f["1h"], f["1d"], f["4h"]
    mins = 60
    levels = pd.concat([v1.htf_levels(d1, 1440, prev_day=True), v1.htf_levels(h4, 240)], ignore_index=True)
    levels = levels.sort_values("avail", kind="stable")
    sig = v1.find_signals(df, levels, window, wick_cap=CLS.wick_cap)
    b = sim.asof(df, mins, v1.daily_bias(d1), "bias")
    nb = news_calendar.blocked(sim.close_time(df, mins), CLS.news_before, CLS.news_after).to_numpy() if news \
        else np.zeros(len(df), bool)
    c = df["close"].to_numpy(float)
    ls, ss = sig["long_struct_stop"].to_numpy(float), sig["short_struct_stop"].to_numpy(float)
    lt, st = sig["long_trigger"].to_numpy(), sig["short_trigger"].to_numpy()
    long_ok = ((b == 1) | (not bias)) & np.isin(lt, ["mss", "ifvg"]) & (ls < c) & ~nb
    short_ok = ((b == -1) | (not bias)) & np.isin(st, ["mss", "ifvg"]) & (ss > c) & ~nb
    with max_stop(max_stop_pct):
        return sim.plan(df, long_ok, short_ok, c, c, ls, ss, 2.0, valid * mins)


def replay(p: pd.DataFrame, max_open: int, min_stop: float) -> pd.DataFrame:
    """sim.replay with up to `max_open` orders + positions at once (sim.replay is max_open=1)."""
    t = pd.to_datetime(p["date"], utc=True).to_numpy(dtype="datetime64[ns]").astype("int64") // 60_000_000_000
    o, h, lo = (p[c].to_numpy(float) for c in ("open", "high", "low"))
    sig = {s: p[f"{s}_sig"].to_numpy() for s in ("long", "short")}
    ent = {s: p[f"{s}_entry"].to_numpy(float) for s in ("long", "short")}
    stp = {s: p[f"{s}_stop"].to_numpy(float) for s in ("long", "short")}
    tgt = {s: p[f"{s}_tp"].to_numpy(float) for s in ("long", "short")}
    valid = p.attrs["valid_min"]
    rows, orders, poss = [], [], []
    for j in range(1, len(p)):
        orders = [od for od in orders if not (t[j] >= od["t0"] + valid or od["stop_seen"])]
        if len(orders) + len(poss) < max_open:
            k = j - 1
            for side in ("long", "short"):
                if sig[side][k]:
                    if abs(ent[side][k] - stp[side][k]) / ent[side][k] < min_stop:
                        continue
                    price = min(ent[side][k], h[j]) if side == "long" else max(ent[side][k], lo[j])
                    orders.append({"side": side, "t0": t[j], "price": price, "stop": stp[side][k],
                                   "tp": tgt[side][k], "sig_t": t[k], "stop_seen": False})
                    break
        new_orders = []
        for od in orders:
            if lo[j] <= od["price"] <= h[j]:
                poss.append({**od, "entry": od["price"], "t_in": t[j], "now": True})
            else:
                s = od["side"]
                od["stop_seen"] = lo[j] <= od["stop"] if s == "long" else h[j] >= od["stop"]
                new_orders.append(od)
        orders = new_orders
        keep = []
        for pos in poss:
            s, stop, tp, filled_now = pos["side"], pos["stop"], pos["tp"], pos.pop("now", False)
            px = None
            if s == "long":
                if lo[j] <= stop:
                    px = stop if (o[j] > stop or filled_now) else o[j]
                elif h[j] >= tp:
                    px = tp
            else:
                if h[j] >= stop:
                    px = stop if (o[j] < stop or filled_now) else o[j]
                elif lo[j] <= tp:
                    px = tp
            if px is None:
                keep.append(pos)
                continue
            sign = 1 if s == "long" else -1
            risk = abs(pos["entry"] - stop)
            rows.append((pd.Timestamp(pos["t_in"] * 60_000_000_000, tz="UTC"), s, pos["entry"], stop, px,
                         sign * (px - pos["entry"]) / risk, risk / pos["entry"],
                         pd.Timestamp(pos["sig_t"] * 60_000_000_000, tz="UTC"),
                         pd.Timestamp(t[j] * 60_000_000_000, tz="UTC")))
        poss = keep
    r = pd.DataFrame(rows, columns=["t_in", "side", "entry", "stop", "exit", "gross_r", "stop_pct", "sig_t", "t_out"])
    r = r.sort_values("t_in", kind="stable").reset_index(drop=True)
    # what is still open after the last candle (used by the live paper tracker)
    r.attrs["open_orders"], r.attrs["open_poss"] = orders, poss
    return r


def run(f: dict, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    c = {**FROZEN, **cfg}
    p = signals(f, c["window"], c["bias"], c["news"], c["max_stop"], c["valid"])
    r = replay(p, c["max_open"], c["min_stop"])
    return r, sim.random_control(p, r, 2.0)


def summary(r: pd.DataFrame, ctrl: pd.DataFrame) -> dict:
    out = {}
    for per, (a, b) in sim.PERIODS.items():
        rp = r[(r["t_in"] >= pd.Timestamp(a, tz="UTC")) & (r["t_in"] < pd.Timestamp(b, tz="UTC"))]
        n = len(rp)
        net1 = (rp["gross_r"] - COST / rp["stop_pct"]) if n else pd.Series(dtype=float)
        net2 = (rp["gross_r"] - 2 * COST / rp["stop_pct"]) if n else pd.Series(dtype=float)
        cc = ctrl[ctrl["period"] == per]["gross_r"]
        out[per] = {"n": n, "per_month": n / MONTHS[per], "gross": rp["gross_r"].mean() if n else np.nan,
                    "random": cc.mean() if len(cc) else np.nan, "avg_net": net1.mean() if n else np.nan,
                    "total_net": net1.sum(), "avg_net2x": net2.mean() if n else np.nan,
                    "total_net2x": net2.sum(), "long": int((rp["side"] == "long").sum()),
                    "short": int((rp["side"] == "short").sum())}
    return out


def verdict(s: dict, base: dict) -> tuple[bool, list[str]]:
    why = []
    for per in sim.PERIODS:
        x, b = s[per], base[per]
        if not x["per_month"] > b["per_month"]:
            why.append(f"{per}: no more trades")
        if not x["total_net"] > b["total_net"]:
            why.append(f"{per}: total net R not higher ({x['total_net']:+.1f} vs {b['total_net']:+.1f})")
        if not x["avg_net2x"] > 0:
            why.append(f"{per}: avg R at 2x cost {x['avg_net2x']:+.3f} <= 0")
        if not x["gross"] > x["random"]:
            why.append(f"{per}: gross {x['gross']:+.3f} not above random {x['random']:+.3f}")
    return not why, why


def main() -> None:
    m1 = sim.load_1m(Path(sys.argv[1]) if len(sys.argv) > 1 else sim.DATA / "NAS100_1m.feather")
    m1 = m1[m1.index < pd.Timestamp(sim.PERIODS["val"][1], tz="UTC")]  # dev + val only
    f = sim.frames(m1, session=True)

    # the frozen variant through this code must be exactly the frozen rule
    p0 = sim.signals_v2(f, "1h", True)
    r0 = sim.replay(p0)
    r_chk, _ = run(f, {})[0], None
    assert len(r0) == len(r_chk) and np.allclose(r0["gross_r"], r_chk["gross_r"]), "frozen variant differs"

    res = {name: summary(*run(f, cfg)) for name, cfg in VARIANTS.items()}
    base = res["frozen"]
    passed = []
    verdicts = {}
    for name in VARIANTS:
        if name == "frozen":
            continue
        ok, why = verdict(res[name], base)
        verdicts[name] = (ok, why)
        if ok:
            passed.append(name)
    if len(passed) >= 2:
        cfg = {}
        for name in passed:
            cfg.update(VARIANTS[name])
        res["combined"] = summary(*run(f, cfg))
        verdicts["combined"] = verdict(res["combined"], base)
        print(f"combined = {' + '.join(passed)}", flush=True)

    lines = ["| Variant | Period | Trades | Per month | Long / short | Gross R | Random R | Avg net R | "
             "Total net R | Avg net R 2x cost | Total net R 2x cost |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, s in res.items():
        for per in sim.PERIODS:
            x = s[per]
            lines.append(f"| {name} | {per} | {x['n']} | {x['per_month']:.1f} | {x['long']} / {x['short']} | "
                         f"{x['gross']:+.3f} | {x['random']:+.3f} | {x['avg_net']:+.3f} | {x['total_net']:+.1f} | "
                         f"{x['avg_net2x']:+.3f} | {x['total_net2x']:+.1f} |")
    lines += ["", "## Verdict (pass: more trades/month, higher total net R, avg R > 0 at 2x cost, gross above random;"
              " all in both dev and val)", ""]
    for name, (ok, why) in verdicts.items():
        lines.append(f"- {name}: {'PASS' if ok else 'FAIL'}" + ("" if ok else " (" + "; ".join(why) + ")"))
    if len(passed) < 2:
        lines.append(f"- combined: not run ({len(passed)} variant(s) passed on their own)")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
