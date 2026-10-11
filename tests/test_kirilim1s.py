import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")
pytest.importorskip("talib")

from strategies.candidates import pusula  # noqa: E402
from strategies.retired import kirilim1s  # noqa: E402


class _FakeDP:
    """Serves the same daily frame for the coin and for BTC."""

    def __init__(self, daily):
        self.daily = daily

    def get_pair_dataframe(self, pair, timeframe):
        return self.daily.copy()


def _daily(closes, start="2021-01-01"):
    closes = np.asarray(closes, dtype=float)
    return pd.DataFrame({
        "date": pd.date_range(start, periods=len(closes), freq="1D", tz="UTC"),
        "open": closes, "high": closes * 1.01, "low": closes * 0.99, "close": closes, "volume": 1.0,
    })


def _hourly(closes, start):
    closes = np.asarray(closes, dtype=float)
    return pd.DataFrame({
        "date": pd.date_range(start, periods=len(closes), freq="1h", tz="UTC"),
        "open": closes, "high": closes + 0.5, "low": closes - 0.5, "close": closes, "volume": 1.0,
    })


def _strategy(cls, daily):
    s = cls({})
    s.dp = _FakeDP(daily)
    return s


def test_variants_differ_only_in_what_the_card_declares():
    main = kirilim1s.Kirilim1s_B
    assert main.timeframe == "1h" and main.channel == 24 and main.tp_model_name == "B"
    assert main.use_market_filter is True
    assert main.mgmt == kirilim1s.Kirilim1s12_B.mgmt == kirilim1s.Kirilim1sNoBTC_B.mgmt
    assert kirilim1s.Kirilim1s12_B.channel == 12 and kirilim1s.Kirilim1s12_B.use_market_filter is True
    assert kirilim1s.Kirilim1sNoBTC_B.channel == 24 and kirilim1s.Kirilim1sNoBTC_B.use_market_filter is False
    # Regime rules come from Pusula unchanged.
    assert issubclass(main, pusula.PusulaBase)


def test_condition_ids_match_the_card():
    daily = _daily(np.linspace(100, 300, 200))
    s = _strategy(kirilim1s.Kirilim1s_B, daily)
    h = _hourly(np.full(100, 300.0), "2021-07-10")
    conds = s.signal_conditions(s.populate_indicators(h, {"pair": "ETH/USDT:USDT"}))
    assert set(conds["long"]) == {"regime_up", "market_up", "breakout_up"}
    assert set(conds["short"]) == {"regime_down", "market_down", "breakout_down"}
    s2 = _strategy(kirilim1s.Kirilim1sNoBTC_B, daily)
    conds2 = s2.signal_conditions(s2.populate_indicators(h.copy(), {"pair": "ETH/USDT:USDT"}))
    assert set(conds2["long"]) == {"regime_up", "breakout_up"}


def test_breakout_fires_once_per_run_and_uses_previous_24_candles_only():
    daily = _daily(np.linspace(100, 300, 200))  # strong uptrend for coin and BTC
    flat = [100.0] * 40
    # candle 40 breaks the 24h high, 41-42 stay above (same run), 43 falls back, 44 breaks again
    closes = flat + [102.0, 103.0, 104.0, 100.0, 105.0] + [100.0] * 5
    s = _strategy(kirilim1s.Kirilim1s_B, daily)
    df = s.populate_indicators(_hourly(closes, "2021-07-10"), {"pair": "ETH/USDT:USDT"})
    # channel excludes the current candle
    assert df["dc_upper"].iloc[40] == pytest.approx(100.5)
    df = s.populate_entry_trend(df, {"pair": "ETH/USDT:USDT"})
    fired = df.index[df["enter_long"] == 1].tolist()
    assert fired == [40, 44]
    assert "enter_short" not in df or df["enter_short"].fillna(0).sum() == 0


def test_no_signal_when_regime_is_not_strong():
    # mixed regime: long rise, then a sharp drop
    daily = _daily(np.concatenate([np.linspace(100, 300, 180), np.linspace(300, 220, 20)]))
    closes = [100.0] * 40 + [102.0] + [100.0] * 5
    s = _strategy(kirilim1s.Kirilim1s_B, daily)
    df = s.populate_indicators(_hourly(closes, "2021-07-20"), {"pair": "ETH/USDT:USDT"})
    df = s.populate_entry_trend(df, {"pair": "ETH/USDT:USDT"})
    assert df.get("enter_long", pd.Series(dtype=float)).fillna(0).sum() == 0


def test_daily_regime_seen_by_1h_candles_is_from_a_closed_day():
    closes = np.concatenate([np.linspace(100, 300, 150), np.linspace(300, 50, 50)])
    daily = _daily(closes)
    s = _strategy(kirilim1s.Kirilim1s_B, daily)
    h = _hourly(np.full(48, 100.0), daily["date"].iloc[160])
    df = s.populate_indicators(h, {"pair": "ETH/USDT:USDT"})
    scores = pusula.regime_score(daily)
    # every hour of day 160 sees the score of day 159 (the last closed day)
    assert (df["score_1d"].iloc[:24] == scores.iloc[159]).all()
    assert (df["score_1d"].iloc[24:] == scores.iloc[160]).all()
