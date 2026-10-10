from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")

from strategies.candidates import momentum_5m as m  # noqa: E402


def _frame(closes, opens=None, spread=0.1):
    closes = np.asarray(closes, dtype=float)
    opens = closes if opens is None else np.asarray(opens, dtype=float)
    spread = np.broadcast_to(np.asarray(spread, dtype=float), closes.shape)
    hi = np.maximum(opens, closes) + spread
    lo = np.minimum(opens, closes) - spread
    return pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=len(closes), freq="5min", tz="UTC"),
        "open": opens, "high": hi, "low": lo, "close": closes, "volume": 1.0,
    })


def _signals(cls, df):
    s = cls({})
    out = s.populate_entry_trend(s.populate_indicators(df.copy(), {"pair": "BTC/USDT:USDT"}),
                                 {"pair": "BTC/USDT:USDT"})
    return out


def _quiet_then(last_open, last_close, last_spread):
    """69 quiet candles drifting slightly, then one candle under test."""
    base = 100 + np.sin(np.arange(69)) * 0.2
    closes = np.append(base, last_close)
    opens = np.append(base, last_open)
    spread = np.append(np.full(69, 0.1), last_spread)
    return _frame(closes, opens, spread)


def test_condition_ids_match_the_card():
    df = m.momentum_indicators(_frame(np.full(80, 100.0)))
    conds = m.signal_conditions(df)
    assert set(conds["long"]) == {"vol_expanding", "momentum_up", "breakout_up", "green_candle"}
    assert set(conds["short"]) == {"vol_expanding", "momentum_down", "breakout_down", "red_candle"}


def test_parameters_are_the_owners_rules():
    s = m.Momentum5m
    assert s.timeframe == "5m" and s.can_short
    assert s.stoploss == -0.015 and m.TP_PCT == 0.03
    assert (m.VOL_FAST, m.VOL_SLOW, m.LOOKBACK) == (10, 50, 20)
    assert s.use_exit_signal is False and s.trailing_stop is False
    assert m.Momentum5mLows.short_uses_lows and not s.short_uses_lows


def test_long_on_big_green_breakout_candle():
    # Big green candle closing far above the last 20 closes; its range expands the SMA10.
    out = _signals(m.Momentum5m, _quiet_then(100.0, 105.0, 3.0))
    assert out["enter_long"].iloc[-1] == 1
    assert out.get("enter_short", pd.Series(0, index=out.index)).fillna(0).iloc[-1] == 0


def test_short_on_big_red_breakdown_candle():
    out = _signals(m.Momentum5m, _quiet_then(100.0, 95.0, 3.0))
    assert out["enter_short"].iloc[-1] == 1
    assert out.get("enter_long", pd.Series(0, index=out.index)).fillna(0).iloc[-1] == 0


def test_red_candle_above_highs_is_not_a_long():
    # Opens at 106 and closes at 105: breakout and momentum true, but red.
    out = _signals(m.Momentum5m, _quiet_then(106.0, 105.0, 3.0))
    assert out.get("enter_long", pd.Series(0, index=out.index)).fillna(0).iloc[-1] == 0


def test_no_signal_without_volatility_expansion():
    # Tiny candle at the new high: range does not expand (SMA10 <= SMA50).
    df = _quiet_then(100.25, 100.30, 0.0)
    df.loc[:59, ["high", "low"]] = df.loc[:59, ["high", "low"]].values + np.array([1.0, -1.0])
    conds = m.signal_conditions(m.momentum_indicators(df.copy()))
    assert bool(conds["long"]["breakout_up"].iloc[-1])
    assert not bool(conds["long"]["vol_expanding"].iloc[-1])
    out = _signals(m.Momentum5m, df)
    assert out.get("enter_long", pd.Series(0, index=out.index)).fillna(0).iloc[-1] == 0


def test_breakout_excludes_the_current_bar():
    df = m.momentum_indicators(_frame(np.arange(1, 80, dtype=float)))
    # Rising closes: previous-20 max is the previous close, so every bar breaks out.
    assert df["hh_close_20"].iloc[-1] == 78.0
    assert bool(m.signal_conditions(df)["long"]["breakout_up"].iloc[-1])


def test_lows_variant_changes_only_the_short_channel():
    df = _quiet_then(100.0, 95.0, 3.0)
    a = m.momentum_indicators(df.copy(), short_uses_lows=False)
    b = m.momentum_indicators(df.copy(), short_uses_lows=True)
    assert a["ll_close_20"].iloc[-1] == df["close"].iloc[-21:-1].min()
    assert b["ll_close_20"].iloc[-1] == df["low"].iloc[-21:-1].min()
    pd.testing.assert_series_equal(a["hh_close_20"], b["hh_close_20"])


@pytest.mark.parametrize("is_short", [False, True])
@pytest.mark.parametrize("fee", [0.0, 0.0003, 0.001, 0.002])
def test_take_profit_is_exactly_three_percent_of_price(is_short, fee):
    from freqtrade.enums import TradingMode
    from freqtrade.persistence import LocalTrade

    trade = LocalTrade(
        pair="BTC/USDT:USDT", open_rate=100.0, amount=10.0, stake_amount=1000.0,
        fee_open=fee, fee_close=fee, is_short=is_short, leverage=1.0,
        open_date=datetime(2023, 1, 1, tzinfo=timezone.utc), exchange="binance",
        trading_mode=TradingMode.FUTURES,
    )
    s = m.Momentum5m({})
    roi = s.custom_roi("BTC/USDT:USDT", trade, trade.open_date, 0, None,
                       "short" if is_short else "long")
    target = trade.calc_close_rate_for_roi(roi)
    assert target == pytest.approx(97.0 if is_short else 103.0, rel=1e-6)  # profit ratio is rounded to 8 decimals
