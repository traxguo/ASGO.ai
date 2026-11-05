"""
Trade list of the frozen Aslan NAS100 v2 1h (with daily bias) rule, 2020-01 -> 2026-09, for the
portfolio backtest (research/portfolio/portfolio.py). Same code path as research/aslan_nasdaq/sim.py
(signals_v2 "1h", bias=True, replay). Runs on a GitHub runner only (HistData is not reachable from the
research container); the CSV is printed to the job log between markers and copied into
research/portfolio/data/aslan_nas_trades.csv. Also prints NAS100 daily closes for the buy-and-hold line.
The holdout months (2026-04..09) were already used once (PR #54/#55); this run does not judge them again.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "aslan_nasdaq"))
import sim  # noqa: E402

m1 = pd.concat([sim.load_1m(sim.DATA / "NAS100_1m.feather"), sim.load_1m(sim.DATA / "NAS100_1m_holdout.feather")])
m1 = m1[~m1.index.duplicated()].sort_index()
m1 = m1[m1.index < pd.Timestamp("2026-10-01", tz="UTC")]
f = sim.frames(m1, session=True)
r = sim.replay(sim.signals_v2(f, "1h", True))
r = r[["t_in", "t_out", "side", "entry", "stop", "exit", "gross_r", "stop_pct"]]
print("=====TRADES_BEGIN=====")
print(r.to_csv(index=False), end="")
print("=====TRADES_END=====")
d = m1["close"].resample("1D").last().dropna()
print("=====NASDAILY_BEGIN=====")
print(d.round(2).to_csv(header=["close"], index_label="date"), end="")
print("=====NASDAILY_END=====")
