from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")

from strategies.candidates import vwap_reversion as v  # noqa: E402


def _frame(rows, start="2023-01-01 00:00"):
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*rows))
    return pd.DataFrame({
        "date": pd.date_range(start, periods=len(rows), freq="5min", tz="UTC"),
        "open": o, "high": h, "low": l, "close": c, "volume": 1.0,
    })


def test_condition_ids_match_the_card():
    df = v.vwap_indicators(_frame([(100, 101, 99, 100)] * 50))
    conds = v.signal_conditions(df)
    assert set(conds["long"]) == {"stretched_down", "bullish_reversal"}
    assert set(conds["short"]) == {"stretched_up", "bearish_reversal"}
    assert set(v.candle_patterns(df)) == {"pinbar_bull", "engulfing_bull", "morning_star",
                                         "pinbar_bear", "engulfing_bear", "evening_star"}


def test_parameters_fixed_in_card():
    assert (v.EMA_LEN, v.RSI_LEN, v.RSI_LOW, v.RSI_HIGH) == (20, 14, 30, 70)
    assert (v.SWING_LEN, v.STOP_BUFFER, v.MIN_TARGET_R) == (10, 0.0005, 0.3)
    assert (v.LOSS_STREAK, v.HALT_HOURS, v.MAX_LEVERAGE) == (3, 24, 10)
    assert v.VwapReversion.timeframe == "5m" and v.VwapReversion.mgmt.valid_for_candles == 1
    assert v.VwapReversion.min_tp1_r == 0.3 and v.VwapReversionTp1R.min_tp1_r == 1.0


def test_session_vwap_resets_at_utc_midnight():
    rows = [(10, 10, 10, 10)] * 3 + [(20, 20, 20, 20)] * 3
    df = _frame(rows, start="2023-01-01 23:45")
    vw = v.session_vwap(df)
    assert vw.iloc[2] == 10 and vw.iloc[3] == 20  # 00:00 candle starts a new day


def test_patterns():
    pin = v.candle_patterns(_frame([(100, 100.2, 99.8, 100), (100, 100.1, 98, 100.05)]))
    assert pin["pinbar_bull"].iloc[-1] and not pin["pinbar_bear"].iloc[-1]
    eng = v.candle_patterns(_frame([(100, 100.1, 99, 99.2), (99.2, 100.5, 99.1, 100.3)]))
    assert eng["engulfing_bull"].iloc[-1]
    star = v.candle_patterns(_frame([(102, 102.1, 99.9, 100), (100, 100.3, 99.7, 100.1),
                                     (100.1, 101.5, 100, 101.4)]))
    assert star["morning_star"].iloc[-1]
    est = v.candle_patterns(_frame([(100, 102.1, 99.9, 102), (102, 102.3, 101.7, 101.9),
                                    (101.9, 102, 100.4, 100.5)]))
    assert est["evening_star"].iloc[-1]
    # a red candle that does not reach the middle of the first body is not a star
    no = v.candle_patterns(_frame([(102, 102.1, 99.9, 100), (100, 100.3, 99.7, 100.1),
                                   (100.1, 101, 100, 100.9)]))
    assert not no["morning_star"].iloc[-1]


def _plan_row(close, ema, vwap, swing_low, swing_high=200.0, min_r=0.3):
    df = pd.DataFrame({"close": [close], "ema20": [ema], "vwap": [vwap],
                       "swing_low": [swing_low], "swing_high": [swing_high]})
    return v.plan_columns(df, min_r).iloc[0]


def test_plan_targets_order_and_filters():
    r = _plan_row(100, ema=101, vwap=103, swing_low=99)
    assert r.long_tp1 == 101 and r.long_tp2 == 103 and r.long_plan_ok
    assert r.long_stop == pytest.approx(99 * 0.9995)
    # VWAP nearer than EMA20 -> TP1 is VWAP
    r = _plan_row(100, ema=103, vwap=101, swing_low=99)
    assert r.long_tp1 == 101 and r.long_tp2 == 103 and r.long_tp1_is_vwap
    # nearest target below 0.3R -> no trade
    assert not _plan_row(100, ema=100.2, vwap=103, swing_low=99).long_plan_ok
    # target on the wrong side -> no trade
    assert not _plan_row(100, ema=99.5, vwap=103, swing_low=99).long_plan_ok
    # Tp1R variant needs TP1 >= 1R
    assert _plan_row(100, ema=100.5, vwap=103, swing_low=99).long_plan_ok
    assert not _plan_row(100, ema=100.5, vwap=103, swing_low=99, min_r=1.0).long_plan_ok


def test_halt_after_three_losses():
    t0 = datetime(2023, 1, 1, tzinfo=timezone.utc)
    mk = lambda h, p: SimpleNamespace(close_date_utc=t0 + timedelta(hours=h), close_profit_abs=p)  # noqa: E731
    assert v.halt_until([mk(0, -1), mk(1, -1)]) is None
    assert v.halt_until([mk(0, -1), mk(1, 2), mk(2, -1), mk(3, -1)]) is None
    assert v.halt_until([mk(0, -1), mk(1, -1), mk(2, -1)]) == t0 + timedelta(hours=26)
    # counter restarts after a pause: one more loss does not start a new pause
    assert v.halt_until([mk(0, -1), mk(1, -1), mk(2, -1), mk(30, -1)]) == t0 + timedelta(hours=26)


def test_long_signal_end_to_end():
    # 60 flat candles, a slide (RSI < 30, below EMA20 and VWAP), then a bullish pinbar.
    rows = [(100, 100.1, 99.9, 100)] * 60
    p = 100.0
    for _ in range(12):
        rows.append((p, p + 0.05, p - 0.45, p - 0.4))
        p -= 0.4
    rows.append((p, p + 0.05, p - 1.5, p + 0.02))
    s = v.VwapReversion({})
    df = s.populate_entry_trend(s.populate_indicators(_frame(rows), {"pair": "BTC/USDT:USDT"}),
                                {"pair": "BTC/USDT:USDT"})
    last = df.iloc[-1]
    assert last["enter_long"] == 1 and last["enter_short"] == 0
    assert last["enter_tag"].startswith("long pinbar_bull stop=")
    assert last["long_stop"] == pytest.approx(df["low"].iloc[-10:].min() * 0.9995)
    assert last["long_tp1"] == pytest.approx(min(last["ema20"], last["vwap"]))
