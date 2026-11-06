import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import paper_aslan_nas as pa  # noqa: E402


def walk(days=300, seed=3):
    """Random-walk 1h bars, Sunday 18:00 -> Friday 17:00 New York, like the futures session."""
    idx = pd.date_range("2025-01-05 23:00", periods=days * 24, freq="1h", tz="UTC")
    ny = idx.tz_convert("America/New_York")
    keep = ~((ny.weekday == 5) | ((ny.weekday == 4) & (ny.hour >= 17)) | ((ny.weekday == 6) & (ny.hour < 18))
             | (ny.hour == 17))
    idx = idx[keep]
    rng = np.random.default_rng(seed)
    c = 20000 * np.exp(np.cumsum(rng.normal(0, 0.004, len(idx))))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.002, len(idx))))
    lo = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.002, len(idx))))
    return pd.DataFrame({"open": o, "high": h, "low": lo, "close": c}, index=idx)


def test_closed_bars_drop_running_hour():
    h1 = walk(10)
    now = h1.index[-1] + timedelta(minutes=30)
    assert len(pa.closed_bars(h1, now)) == len(h1) - 1


def test_daily_candles_from_1h_bars_are_kept():
    d = pa.frames_1h(walk(30))["1d"]
    assert 15 <= len(d) <= 25  # weekdays only, no holiday filter dropping full days


def test_logs_only_trades_after_start_and_never_twice():
    h1 = walk()
    start = h1.index[len(h1) // 2]
    end = h1.index[-1] + timedelta(hours=1)
    state = {"started": start.isoformat()}
    msgs = pa.run_once(h1, state, end.to_pydatetime())
    trades = state["trades"]
    assert trades, "random walk should give some trades"
    assert all(pd.Timestamp(t["sig_t"]) >= start for t in trades)
    assert sum(m.startswith("KAPANDI") for m in msgs) == len(trades)
    again = pa.run_once(h1, state, end.to_pydatetime())
    assert not any(m.startswith("KAPANDI") for m in again) and len(state["trades"]) == len(trades)
    # net R = gross R minus the backtest cost; a 2R target win is about +2R
    for t in trades:
        assert t["net_r"] < t["gross_r"]
        assert t["why"] in ("hedef", "stop")


def test_incremental_runs_match_one_full_run():
    h1 = walk()
    start = h1.index[len(h1) // 2]
    inc = {"started": start.isoformat()}
    for t in h1.index[len(h1) // 2::7]:
        pa.run_once(h1, inc, (t + timedelta(hours=1, minutes=5)).to_pydatetime())
    pa.run_once(h1, inc, (h1.index[-1] + timedelta(hours=1)).to_pydatetime())
    full = {"started": start.isoformat()}
    pa.run_once(h1, full, (h1.index[-1] + timedelta(hours=1)).to_pydatetime())
    assert [t["sig_t"] for t in inc["trades"]] == [t["sig_t"] for t in full["trades"]]


def test_first_run_says_tracking_started():
    state = {}
    msgs = pa.run_once(walk(40), state, pd.Timestamp("2025-02-20", tz="UTC").to_pydatetime())
    assert msgs and msgs[0].startswith("Takip başladı") and state["trades"] == []


def test_variant_with_frozen_config_logs_the_same_trades():
    h1 = walk()
    start = h1.index[len(h1) // 2].isoformat()
    end = (h1.index[-1] + timedelta(hours=1)).to_pydatetime()
    a, b = {"started": start}, {"started": start}
    pa.run_once(h1, a, end)
    pa.run_variant(h1, b, end, {}, "test")
    assert a["trades"] == b["trades"]


def test_variant_incremental_runs_match_one_full_run():
    h1 = walk()
    start = h1.index[len(h1) // 2]
    for cfg, _ in pa.VARIANTS.values():
        inc = {"started": start.isoformat()}
        for t in h1.index[len(h1) // 2::7]:
            pa.run_variant(h1, inc, (t + timedelta(hours=1, minutes=5)).to_pydatetime(), cfg, "test")
        msgs = pa.run_variant(h1, inc, (h1.index[-1] + timedelta(hours=1)).to_pydatetime(), cfg, "test")
        full = {"started": start.isoformat()}
        pa.run_variant(h1, full, (h1.index[-1] + timedelta(hours=1)).to_pydatetime(), cfg, "test")
        # with 2 open at once, trades can close in another order than they opened: compare as sets
        key = lambda t: t["sig_t"]  # noqa: E731
        assert sorted(inc["trades"], key=key) == sorted(full["trades"], key=key) and full["trades"]
        assert isinstance(msgs, list)
