"""
Frozen Nasdaq rules (AslanLiq2_1h, daily bias filter, 2R) on other stock indices, no tuning
(supervisor request 2026-11-05: more trades per month). Same code and same order replay as sim.py.

Markets (HistData 1m, EST -> UTC, same 17:00 New York trading day as the Nasdaq test):
  NAS100 (reference), SPX500 (S&P 500), GER40 (DAX), UK100 (FTSE 100), JPN225 (Nikkei 225).
  HistData has no Dow Jones (its UDXUSD is the US dollar index, not US30), so US30 is not tested.
Costs: typical CFD spread as a round-trip fraction of price (COST below), also at 2x.
Windows: dev 2020-2024, val 2025-01..2026-03, holdout 2026-04..09. These indices are new markets for
frozen rules, so their holdout window is used here for the first time; for NAS100 it repeats the
already reported holdout run.
Pass (per index, set before the run): net R > 0 in all three windows and gross R above the random-entry
control in all three windows.

    python research/aslan_nasdaq/fetch_indices.py
    python research/aslan_nasdaq/indices.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim  # noqa: E402

DATA = sim.ROOT / "user_data" / "indices1m"
COST = {"NAS100": 0.00010, "SPX500": 0.00010, "GER40": 0.00010, "UK100": 0.00015, "JPN225": 0.00025}
WINDOWS = {"dev": ("2020-01-01", "2025-01-01"), "val": ("2025-01-01", "2026-04-01"),
           "holdout": ("2026-04-01", "2026-10-01")}


def run(name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    m1 = sim.load_1m(DATA / f"{name}_1m.feather")
    m1 = m1[m1.index < pd.Timestamp(WINDOWS["holdout"][1], tz="UTC")]
    f = sim.frames(m1, session=True)
    p = sim.signals_v2(f, "1h", True)
    r = sim.replay(p)
    sim.PERIODS = WINDOWS  # used by random_control and table
    return r, sim.random_control(p, r, 2.0)


def verdict(r: pd.DataFrame, ctrl: pd.DataFrame, cost: float) -> tuple[bool, list[str]]:
    ok, notes = True, []
    for per, (a, b) in WINDOWS.items():
        rp = r[(r["t_in"] >= pd.Timestamp(a, tz="UTC")) & (r["t_in"] < pd.Timestamp(b, tz="UTC"))]
        s = sim.stats(rp, cost, 2.0)
        cc = ctrl[ctrl["period"] == per]["gross_r"].mean() if len(ctrl) else np.nan
        if s["n"] == 0:
            ok = False
            notes.append(f"{per}: no trades")
            continue
        good = s["net"] > 0 and s["gross"] > cc
        ok &= good
        months = (pd.Timestamp(b) - pd.Timestamp(a)).days / 30.44
        notes.append(f"{per}: {s['n']} trades ({s['n'] / months:.1f}/month), net {s['net']:+.3f}R, "
                     f"gross {s['gross']:+.3f} vs random {cc:+.3f} -> {'ok' if good else 'FAIL'}")
    return ok, notes


def overlap(r: pd.DataFrame, ref: pd.DataFrame, cost: float, ref_cost: float) -> str:
    """Share of trade days also NAS100 trade days, and correlation of daily net R on common days."""
    def daily(x, c):
        net = x["gross_r"] - c / x["stop_pct"]
        return net.groupby(x["t_in"].dt.floor("D")).sum()
    a, b = daily(r, cost), daily(ref, ref_cost)
    both = a.index.intersection(b.index)
    corr = a.reindex(both).corr(b.reindex(both)) if len(both) > 5 else np.nan
    # also daily series on the union, zero when no trade
    u = a.index.union(b.index)
    corr_u = a.reindex(u, fill_value=0).corr(b.reindex(u, fill_value=0))
    return (f"{len(both)}/{len(a)} trade days shared with NAS100 ({len(both) / max(len(a), 1):.0%}); "
            f"daily net R correlation on shared days {corr:+.2f}, on all days {corr_u:+.2f}")


def main() -> None:
    res = {}
    for name in COST:
        path = DATA / f"{name}_1m.feather"
        if not path.exists():
            print(f"{name}: no data, skipped", flush=True)
            continue
        res[name] = run(name)
        print(f"{name}: {len(res[name][0])} trades", flush=True)
    for name, (r, ctrl) in res.items():
        for mult in (1, 2):
            print(sim.table({"v2 1h bias": (r, 2.0, ctrl)}, f"{name}{' x2 cost' if mult == 2 else ''}",
                            COST[name] * mult), flush=True)
    print("\n## Verdict (pass: net > 0 and gross above random in dev, val and holdout)")
    for name, (r, ctrl) in res.items():
        ok, notes = verdict(r, ctrl, COST[name])
        print(f"\n### {name}: {'PASS' if ok else 'FAIL'}")
        for n in notes:
            print(f"- {n}")
        if name != "NAS100" and "NAS100" in res:
            print(f"- {overlap(r, res['NAS100'][0], COST[name], COST['NAS100'])}")


if __name__ == "__main__":
    main()
