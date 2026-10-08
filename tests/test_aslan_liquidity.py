from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")
pytest.importorskip("talib")

from strategies.candidates import aslan_liquidity as al  # noqa: E402
from strategies.common import news_calendar  # noqa: E402


def candles(rows, start="2024-01-01", freq="1h"):
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"])
    df["date"] = pd.date_range(start, periods=len(df), freq=freq, tz="UTC")
    return df


def test_stop_uses_wick_unless_wick_longer_than_body():
    # long: body 100->110, lower wick 2 -> stop at the wick (low)
    assert al.stop_from_candle("long", 100, 111, 98, 110) == 98
    # long: body 100->101, lower wick 10 -> stop at the body bottom
    assert al.stop_from_candle("long", 100, 102, 90, 101) == 100
    # short mirror
    assert al.stop_from_candle("short", 110, 112, 99, 100) == 112
    assert al.stop_from_candle("short", 101, 120, 99, 100) == 101


def test_pivots_confirmed_shape():
    high = np.array([1, 2, 5, 2, 1, 1, 1], float)
    low = high - 0.5
    ph, pl = al.pivots(high, low)
    assert ph[2] and ph.sum() == 1


def test_sweep_then_mss_long():
    # A known liquidity low at 95, a swing high at 104 before the sweep,
    # then the sweep to 93 and a close above 104 -> MSS long, stop at the sweep wick.
    rows = [
        (100, 101, 99, 100), (100, 102, 99, 101), (101, 104, 100, 103), (103, 103.5, 100, 101),
        (101, 102, 98, 99), (99, 100, 96, 97), (97, 98, 93, 94), (94, 99, 94, 98),
        (98, 103, 97, 102), (102, 106, 101, 105),
    ]
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [95.0], "side": ["low"]})
    sig = al.find_signals(df, levels, setup_window=12)
    k = int(np.flatnonzero(sig["long_trigger"] != "")[0])
    assert k == 9 and sig["long_trigger"].iloc[k] == "mss"
    # extreme candle 6: body 97->94 (3), lower wick 1 -> stop at the low 93
    assert sig["long_struct_stop"].iloc[k] == 93
    assert (sig["short_trigger"] == "").all()


def test_no_signal_without_sweep():
    rows = [(100, 101, 99, 100)] * 4 + [(100, 106, 99.5, 105)]
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [90.0], "side": ["low"]})
    sig = al.find_signals(df, levels, setup_window=12)
    assert (sig["long_trigger"] == "").all()


def test_level_not_used_before_available():
    rows = [(100, 101, 93, 100)] + [(100, 101, 99, 100)] * 3
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[2]], "price": [95.0], "side": ["low"]})
    sig = al.find_signals(df, levels, setup_window=12)
    assert not sig["sweep_low_setup"].iloc[0]


def test_daily_bias_flips_on_close_beyond_swing():
    highs = [10, 11, 15, 11, 10, 12, 16, 13]
    rows = [(h - 1, h, h - 2, h - 0.5) for h in highs]
    d = candles(rows, freq="1D")
    b = al.daily_bias(d)
    # swing high 15 (index 2) confirmed at index 4; index 6 closes 15.5 > 15 -> bullish
    assert b["bias"].iloc[5] == 0 and b["bias"].iloc[6] == 1
    assert b["avail"].iloc[6] == d["date"].iloc[6] + timedelta(days=1)


def test_news_block_window():
    t = pd.Series(pd.to_datetime(["2024-03-12 12:30", "2024-03-12 11:20", "2024-03-12 13:40", "2024-03-13 12:30"], utc=True))
    blocked = news_calendar.blocked(t, timedelta(hours=1), timedelta(hours=1)).tolist()
    assert blocked == [True, False, False, False]  # CPI 2024-03-12 08:30 New York = 12:30 UTC


def test_nfp_rule():
    assert str(news_calendar.nfp_date(2024, 11)) == "2024-11-01"
    assert str(news_calendar.nfp_date(2023, 12)) == "2023-12-08"
    assert str(news_calendar.nfp_date(2021, 1)) == "2021-01-08"
