import pandas as pd
import pytest

pytest.importorskip("freqtrade")
pytest.importorskip("talib")

from strategies.retired import nabiz  # noqa: E402


def test_cross_up_fires_only_on_the_crossing_candle():
    rsi = pd.Series([50, 40, 30, 34, 35, 40, 30, 36])
    assert nabiz.cross_up(rsi, 35).tolist() == [False, False, False, False, True, False, False, True]


def test_cross_down_fires_only_on_the_crossing_candle():
    rsi = pd.Series([50, 60, 70, 66, 65, 60, 70, 64])
    assert nabiz.cross_down(rsi, 65).tolist() == [False, False, False, False, True, False, False, True]


def test_wide_variant_only_changes_the_stop_distance():
    assert nabiz.NabizWide_B.mgmt.stop_atr == 3.0
    assert nabiz.Nabiz_B.mgmt.stop_atr == 1.5
    assert nabiz.NabizWide_B.mgmt.entry_zone_atr == nabiz.Nabiz_B.mgmt.entry_zone_atr
    assert nabiz.NabizWide_B.tp_model_name == nabiz.Nabiz_B.tp_model_name == "B"
