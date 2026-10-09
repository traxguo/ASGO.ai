import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")
pytest.importorskip("talib")

from strategies.candidates import pusula  # noqa: E402


def daily(closes, start="2021-01-01"):
    closes = np.asarray(closes, dtype=float)
    return pd.DataFrame({
        "date": pd.date_range(start, periods=len(closes), freq="1D", tz="UTC"),
        "open": closes, "high": closes * 1.01, "low": closes * 0.99, "close": closes, "volume": 1.0,
    })


def test_steady_rise_is_up_and_steady_fall_is_down():
    up = pusula.regime_score(daily(np.linspace(100, 300, 200)))
    down = pusula.regime_score(daily(np.linspace(300, 100, 200)))
    assert up.iloc[-1] == 3 and pusula.regime_label(up.iloc[-1]) == "up"
    assert down.iloc[-1] == -3 and pusula.regime_label(down.iloc[-1]) == "down"


def test_no_score_before_enough_history():
    s = pusula.regime_score(daily(np.linspace(100, 300, 200)))
    assert s.iloc[: pusula.MOMENTUM_DAYS].isna().all()
    assert pusula.regime_label(s.iloc[0]) == "unknown"


def test_rise_then_sharp_drop_is_mixed():
    # long rise, then a drop below EMA50 while the 90-day return is still positive
    closes = np.concatenate([np.linspace(100, 300, 180), np.linspace(300, 220, 10)])
    s = pusula.regime_score(daily(closes))
    assert pusula.regime_label(s.iloc[-1]) == "mixed"


def test_score_uses_only_past_data():
    closes = np.concatenate([np.linspace(100, 300, 150), np.linspace(300, 50, 50)])
    full = pusula.regime_score(daily(closes))
    cut = pusula.regime_score(daily(closes[:160]))
    pd.testing.assert_series_equal(full.iloc[:160], cut, check_names=False)


def test_market_score_joined_by_date():
    coin = daily(np.linspace(100, 300, 200))
    btc = daily(np.linspace(300, 100, 200))
    frame = pusula.daily_regime_frame(coin, btc)
    assert frame["score"].iloc[-1] == 3 and frame["mkt_score"].iloc[-1] == -3


def _row(score, mkt, close=100.0):
    return {"close": close, "atr": 2.0, "dc_upper": 102.0, "dc_lower": 95.0, "swing_low": 97.0, "swing_high": 103.0,
            "score_1d": score, "mkt_score_1d": mkt, "ema_slow_1d": 90.0, "mom_1d": 0.25}


def test_commentary_gives_long_plan_in_uptrend():
    v = pusula.commentary(_row(3, 2), "ETH/USDT:USDT")
    assert v["side"] == "long" and v["trigger"] == 102.0
    p = v["plan"]
    assert p["stop"] < p["zone_low"] < p["zone_high"] <= 102.0 < p["tp1"] < p["tp2"]
    assert "LONG tetiği" in v["text"]


def test_commentary_no_trade_when_mixed_or_market_disagrees():
    assert pusula.commentary(_row(1, 2), "ETH/USDT:USDT")["side"] is None
    assert pusula.commentary(_row(-3, 1), "ETH/USDT:USDT")["side"] is None
    assert pusula.commentary(_row(-3, -2), "ETH/USDT:USDT")["side"] == "short"
