import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")
pytest.importorskip("talib")

from strategies.candidates import ams_liquidity_mss as ams  # noqa: E402


def candles(rows, start="2024-01-02 12:30"):
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"])
    df["date"] = pd.date_range(start, periods=len(df), freq="15min", tz="UTC")
    return df


def test_killzones_utc():
    d = pd.Series(pd.to_datetime(["2024-01-02 06:45", "2024-01-02 07:00", "2024-01-02 08:45", "2024-01-02 09:00",
                                  "2024-01-02 12:30", "2024-01-02 14:45", "2024-01-02 15:00"], utc=True))
    assert ams.in_killzone(d).tolist() == [False, True, True, False, True, True, False]


def test_v27_model_is_in_the_fixed_grid():
    from strategies.common import trade_management as tm
    grid = {(m.tp1_r, m.tp2_r, m.tp1_close_pct, m.breakeven_trigger) for m in tm.tp_variant_grid()}
    assert (1.5, 3.0, 50, "TP1") in grid


def _long_rows():
    # fractal high at candle 2 (105), sweep of the 95 level at candle 5 (wick 94, close 96),
    # displacement up leaves an FVG (high of 6 = 98 < low of 8 = 100), close 106 > 105 = MSS
    return [(101, 102, 100, 101), (101, 103, 100, 102), (102, 105, 101, 103), (103, 104, 99, 100),
            (100, 101, 97, 98), (98, 99, 94, 96), (96, 98, 95.5, 97.5), (97.5, 101, 97, 100.5),
            (100.5, 103, 100, 102.5), (102.5, 107, 102, 106)]


def test_sweep_mss_fvg_long_limit_at_far_edge():
    df = candles(_long_rows())
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [95.0], "side": ["low"], "kind": ["eq"]})
    s = ams.find_signals(df, levels)
    k = int(np.flatnonzero(s["long_trigger"] != "")[0])
    assert k == 9
    assert s["long_edge"].iloc[k] == 101  # newest gap (candles 7-9): high of its first candle
    assert s["long_struct_stop"].iloc[k] == pytest.approx(94 * 0.999)


def test_no_signal_outside_killzone():
    df = candles(_long_rows(), start="2024-01-02 03:00")
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [95.0], "side": ["low"], "kind": ["eq"]})
    assert (ams.find_signals(df, levels)["long_trigger"] == "").all()


def test_two_closes_beyond_is_a_break():
    rows = _long_rows()
    rows[5] = (98, 99, 94, 94.5)  # closes below 95
    rows[6] = (94.5, 95, 93, 94)  # second close below: break
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [95.0], "side": ["low"], "kind": ["eq"]})
    assert (ams.find_signals(df, levels)["long_trigger"] == "").all()
