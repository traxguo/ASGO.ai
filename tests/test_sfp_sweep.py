from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")

from strategies.retired import sfp_sweep as m  # noqa: E402

T0 = datetime(2023, 1, 1, tzinfo=timezone.utc)


def _frame(highs, lows, opens=None, closes=None):
    highs = np.asarray(highs, float)
    lows = np.asarray(lows, float)
    mid = (highs + lows) / 2
    opens = mid if opens is None else np.asarray(opens, float)
    closes = mid if closes is None else np.asarray(closes, float)
    return pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=len(highs), freq="5min", tz="UTC"),
        "open": opens, "high": highs, "low": lows, "close": closes, "volume": 1.0,
    })


def _base_15m():
    """15m candles (3 x 5m each): a swing high of 110 at 15m candle 4, swing low 90 at candle 8."""
    h15 = [100, 101, 102, 103, 110, 104, 103, 102, 95, 96, 97, 98, 98.2, 98.4, 98.6, 98.8]
    l15 = [98, 99, 100, 101, 105, 100, 99, 98, 90, 94, 95, 96, 97, 97, 97, 97]
    highs, lows = [], []
    for h, lo in zip(h15, l15):
        highs += [h, h - 0.5, h - 0.5]
        lows += [lo + 0.5, lo, lo + 0.5]
    return highs, lows


def test_condition_ids_match_the_card():
    h, lo = _base_15m()
    df = m.sfp_indicators(_frame(h, lo), 15)
    conds = m.signal_conditions(df)
    assert set(conds["short"]) == {"sweep_swing_high", "close_back_below", "upper_wick_50", "eq_below_entry"}
    assert set(conds["long"]) == {"sweep_swing_low", "close_back_above", "lower_wick_50", "eq_above_entry"}


def test_parameters_fixed_on_the_card():
    assert (m.PIVOT_N, m.WICK_MIN, m.STOP_BUFFER) == (3, 0.5, 0.001)
    assert m.SfpSweep.timeframe == "5m" and m.SfpSweep.htf_minutes == 15 and m.SfpSweep1h.htf_minutes == 60
    assert m.SfpSweep.mgmt.risk_per_trade == 0.01 and m.SfpSweep.mgmt.max_leverage == 10.0
    assert m.SfpSweep.tp_model_name == "B" and m.tm.TP_MODELS["B"].tp1_close_pct == 50


def test_swing_is_known_only_after_three_right_candles_close():
    h, lo = _base_15m()
    df = m.sfp_indicators(_frame(h, lo), 15)
    # 15m candle 4 (5m rows 12-14) is the high; right side = 15m candles 5,6,7 -> known from 5m row 24.
    assert np.isnan(df["swing_high"].iloc[23])
    assert df["swing_high"].iloc[24] == 110
    # swing low 90 at 15m candle 8 -> known from 15m candle 12 = 5m row 36
    assert np.isnan(df["swing_low"].iloc[35]) and df["swing_low"].iloc[36] == 90


def test_bearish_sfp_and_levels():
    h, lo = _base_15m()
    o = list((np.array(h) + np.array(lo)) / 2)
    c = list(o)
    # extra 5m candle: high 111 > 110, opens 108.6, closes 108.5, low 108 -> upper wick 2.4 of 3.0
    h.append(111.0); lo.append(108.0); o.append(108.6); c.append(108.5)
    df = _frame(h, lo, o, c)
    s = m.SfpSweep({})
    out = s.populate_entry_trend(s.populate_indicators(df.copy(), {"pair": "BTC/USDT:USDT"}), {"pair": "BTC/USDT:USDT"})
    last = out.iloc[-1]
    assert last["enter_short"] == 1
    assert last["short_stop"] == pytest.approx(111 * 1.001)
    assert last["short_tp1"] == pytest.approx(100.0)  # EQ of 110 / 90
    assert last["short_tp2"] == pytest.approx(90.0)
    assert "tp1r=" in last["enter_tag"] and last["enter_tag"].startswith("short stop=")


def test_only_first_touch_counts_and_close_above_is_no_signal():
    h, lo = _base_15m()
    o = list((np.array(h) + np.array(lo)) / 2)
    c = list(o)
    # first candle above 110 closes above it (no SFP), the second is a perfect SFP -> still no signal
    h += [111.0, 111.5]; lo += [109.0, 108.0]; o += [109.2, 108.6]; c += [110.5, 108.5]
    df = m.sfp_indicators(_frame(h, lo, o, c), 15)
    conds = m.signal_conditions(df)
    mask = np.logical_and.reduce([v.fillna(False).to_numpy(bool) for v in conds["short"].values()])
    assert not mask[-2:].any()


def test_small_wick_is_no_signal():
    h, lo = _base_15m()
    o = list((np.array(h) + np.array(lo)) / 2)
    c = list(o)
    h.append(111.0); lo.append(106.0); o.append(110.5); c.append(106.5)  # upper wick 0.5 of 5
    df = m.sfp_indicators(_frame(h, lo, o, c), 15)
    assert not bool(m.signal_conditions(df)["short"]["upper_wick_50"].iloc[-1])


def test_resample_has_no_lookahead():
    h, lo = _base_15m()
    full = m.sfp_indicators(_frame(h, lo), 15)
    for cut in range(20, len(h)):
        part = m.sfp_indicators(_frame(h[:cut], lo[:cut]), 15)
        pd.testing.assert_series_equal(part["swing_high"], full["swing_high"].iloc[:cut], check_names=False)
        pd.testing.assert_series_equal(part["swing_low"], full["swing_low"].iloc[:cut], check_names=False)


def test_three_losses_halt_24h_then_counter_restarts():
    t = [T0 + timedelta(hours=i) for i in range(10)]
    assert m.halt_until([(t[0], -1), (t[1], -1), (t[2], 5)]) is None
    assert m.halt_until([(t[0], -1), (t[1], -1), (t[2], -1)]) == t[2] + timedelta(hours=24)
    # 4th loss right after a pause does not start a new pause (counter restarted)
    assert m.halt_until([(t[0], -1), (t[1], -1), (t[2], -1), (t[3], -1)]) == t[2] + timedelta(hours=24)
    # 6 losses -> second pause from the 6th
    six = [(t[i], -1) for i in range(6)]
    assert m.halt_until(six) == t[5] + timedelta(hours=24)
    # order of input does not matter
    assert m.halt_until(list(reversed(six))) == t[5] + timedelta(hours=24)
