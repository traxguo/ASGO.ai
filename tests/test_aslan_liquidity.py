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


def test_stop_wick_cap_175():
    # body 100->101 (1), lower wick 1.5 <= 1.75 -> stop at the wick
    assert al.stop_from_candle("long", 100, 102, 98.5, 101, 1.75) == 98.5
    # lower wick 10 > 1.75 -> cut at body bottom - 1.75 x body
    assert al.stop_from_candle("long", 100, 102, 90, 101, 1.75) == 98.25
    assert al.stop_from_candle("short", 101, 120, 99, 100, 1.75) == 102.75


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


# ---------------------------------------------------------------- v3

from strategies.candidates import aslan_liquidity_v3 as v3  # noqa: E402


def test_single_1r_target_model_allowed():
    assert v3.MODEL_1R.tp2_r == 1.0 and v3.MODEL_1R.tp1_close_pct == 0


def test_session_levels_available_after_session_end():
    rows = [(100, 100 + i, 99 - i, 100) for i in range(24)]
    d = candles(rows)
    s = v3.session_levels(d)
    asia = s[(s.side == "high") & (s.avail == pd.Timestamp("2024-01-01 07:00", tz="UTC"))]
    assert asia.price.iloc[0] == 106  # highest high of hours 0-6


def test_structure_trend_hh_hl():
    highs = [10, 12, 10, 9, 11, 14, 11, 10, 12, 16, 13, 12]
    lows = [h - 3 for h in highs]
    rows = [(h - 1, h, lo, h - 1) for h, lo in zip(highs, lows)]
    tr = v3.structure_trend(candles(rows, freq="4h"), 240)
    assert tr["trend"].iloc[-1] == 1


def test_v3_break_trades_in_break_direction():
    # a liquidity high at 105 is closed through -> long (break), not short
    rows = [(100, 101, 99, 100), (100, 103, 99, 102), (102, 104, 101, 103), (103, 103.5, 100, 101),
            (101, 102, 99.5, 101.5), (101.5, 108, 101, 107.5)]
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [105.0], "side": ["high"]})
    sig = v3.find_signals_v3(df, levels, setup_window=12)
    assert sig["long_kind"].iloc[5] == "break" and sig["long_trigger"].iloc[5] == "mss"
    assert (sig["short_trigger"] == "").all()


def test_v3_sweep_trades_reversal():
    rows = [(100, 101, 99, 100), (100, 102, 99, 101), (101, 104, 100, 103), (103, 103.5, 100, 101),
            (101, 102, 98, 99), (99, 100, 96, 97), (97, 98, 93, 96), (96, 99, 95, 98),
            (98, 103, 97, 102), (102, 106, 101, 105)]
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [95.0], "side": ["low"]})
    sig = v3.find_signals_v3(df, levels, setup_window=12)
    k = int(np.flatnonzero(sig["long_trigger"] != "")[0])
    assert sig["long_kind"].iloc[k] == "sweep"


# ---------------------------------------------------------------- v4

from strategies.candidates import aslan_liquidity_v4 as v4  # noqa: E402


def test_v4_zones_fvg_and_ob():
    rows = [(100, 101, 99, 100), (100, 100.5, 98, 99), (99, 104, 99, 103.5), (103.5, 106, 102, 105)]
    z = v4.poi_zones(candles(rows))
    fvg = z[(z.kind == "fvg") & (z.side == "long")]
    assert len(fvg) == 1 and fvg.bottom.iloc[0] == 100.5 and fvg.top.iloc[0] == 102
    ob = z[(z.kind == "ob") & (z.side == "long")]
    assert ob.bottom.iloc[0] == 98 and ob.top.iloc[0] == 100.5  # bearish candle 1


def test_v4_touch_then_engulf_breaking_mini_high():
    rows = [(110, 111, 109, 110), (110, 112, 109.5, 111), (111, 111.5, 108, 108.5), (108.5, 109, 104, 104.5),
            (104.5, 105, 101, 102), (102, 103.5, 101.5, 103), (103, 103.2, 102, 102.2), (102.1, 113, 102, 112.5)]
    df = candles(rows, freq="5min")
    zones = pd.DataFrame({"avail": [df["date"].iloc[0]], "bottom": [100.0], "top": [102.5], "side": ["long"], "kind": ["fvg"]})
    sig = v4.find_signals_v4(df, zones, setup_window=36)
    assert sig["long_trigger"].iloc[7] == "engulf" and sig["long_kind"].iloc[7] == "fvg"
    assert sig["long_struct_stop"].iloc[7] == 101


def test_v5_sweep_only_stop_beyond_extreme_and_ob():
    rows = [(100, 101, 99, 100), (100, 102, 99, 101), (101, 104, 100, 103), (103, 103.5, 100, 101),
            (101, 102, 98, 99), (99, 100, 96, 97), (97, 98, 93, 96), (96, 99, 95, 98),
            (98, 103, 97, 102), (102, 106, 101, 105)]
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [95.0], "side": ["low"]})
    sig = v3.find_signals_v3(df, levels, 12, allow_break=False, use_ob=True, stop_buffer_pct=0.001)
    k = int(np.flatnonzero(sig["long_trigger"] != "")[0])
    # candle 7 closes 98 above the high (98) of the last bearish candle 6? no: 98 is not > 98;
    # candle 8 closes 102 > 98 -> order block confirmation before the MSS at candle 9
    assert k == 8 and sig["long_trigger"].iloc[k] == "ob"
    assert sig["long_struct_stop"].iloc[k] == pytest.approx(93 * 0.999)


def test_v5_break_not_traded():
    rows = [(100, 101, 99, 100), (100, 103, 99, 102), (102, 104, 101, 103), (103, 103.5, 100, 101),
            (101, 102, 99.5, 101.5), (101.5, 108, 101, 107.5)]
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [105.0], "side": ["high"]})
    sig = v3.find_signals_v3(df, levels, 12, allow_break=False, use_ob=True, stop_buffer_pct=0.001)
    assert (sig["long_trigger"] == "").all() and (sig["short_trigger"] == "").all()


# ---------------------------------------------------------------- v6


def test_v6_ignores_gap_formed_before_sweep():
    # bearish gap at candles 2-4 (before the sweep at 6); v5 takes it as iFVG, v6 must not
    rows = [(110, 111, 109, 110), (110, 110.5, 108, 108.5), (108.5, 109, 104, 104.5), (104.5, 105, 101, 101.5),
            (101.5, 102, 98, 98.5), (98.5, 99, 97, 98), (98, 98.5, 93, 97), (97, 100, 96.5, 99.5),
            (99.5, 108.8, 98, 108.7)]
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [95.0], "side": ["low"]})
    old = v3.find_signals_v3(df, levels, 12, allow_break=False, stop_buffer_pct=0.001)
    new = v3.find_signals_v3(df, levels, 12, allow_break=False, stop_buffer_pct=0.001, post_sweep=True)
    assert old["long_trigger"].iloc[8] == "ifvg"  # gap 105-108 (candles 1-3) closed above
    assert (new["long_trigger"] == "").all()


def test_v6_new_fvg_after_sweep_confirms():
    rows = [(100, 101, 99, 100), (100, 100.5, 98, 98.5), (98.5, 99, 96, 96.5), (96.5, 97, 93, 96),
            (96, 97.5, 95.5, 97.2), (97.2, 99.5, 97.1, 99.4), (99.4, 101, 98.2, 100.5)]
    df = candles(rows)
    levels = pd.DataFrame({"avail": [df["date"].iloc[0]], "price": [94.0], "side": ["low"]})
    sig = v3.find_signals_v3(df, levels, 12, allow_break=False, stop_buffer_pct=0.001, post_sweep=True)
    k = int(np.flatnonzero(sig["long_trigger"] != "")[0])
    assert k == 5 and sig["long_trigger"].iloc[k] == "fvg"  # low 97.1 > high of candle 3 (97)
    assert sig["long_struct_stop"].iloc[k] == pytest.approx(93 * 0.999)
