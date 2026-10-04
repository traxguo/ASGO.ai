from datetime import datetime, timezone

import pytest

from signals.schema import Signal, TriggeredCondition, signal_from_plan
from strategies.common import trade_management as tm


def make_signal():
    p, _ = tm.build_plan("long", 3418.0, 35.0, swing_level=3372.0, model=tm.MODEL_B)
    return signal_from_plan(
        p,
        ts=datetime(2026, 10, 2, 14, tzinfo=timezone.utc),
        pair="ETH/USDT:USDT",
        timeframe="4h",
        strategy="trend_ma",
        conditions=[TriggeredCondition("trend_up", "close 3418 > EMA200 3210")],
        funding_rate=0.0001,
    )


def test_signal_valid_and_roundtrip(tmp_path):
    s = make_signal()
    assert s.signal_id == "2026-10-02T14:00Z_ETHUSDT_trend_ma"
    s.validate()
    path = s.save(tmp_path)
    again = Signal.from_dict(__import__("json").loads(path.read_text()))
    assert again == s


def test_signal_rejects_tampered_target():
    s = make_signal()
    s.targets[0].price += 10  # a level that is not the output of the tested rule
    with pytest.raises(ValueError):
        s.validate()


def test_signal_requires_conditions():
    s = make_signal()
    s.triggered_conditions = []
    with pytest.raises(ValueError):
        s.validate()
