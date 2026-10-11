import pandas as pd
import pytest

pytest.importorskip("freqtrade")
pytest.importorskip("talib")

from strategies.candidates import pusula  # noqa: E402
from strategies.retired import pusula_hizli  # noqa: E402


def _strategy(cls):
    # signal_conditions only reads class attributes; no Freqtrade config needed.
    return object.__new__(cls)


def _frame(scores, mkt, close, dc_upper=102.0, dc_lower=95.0):
    n = len(scores)
    return pd.DataFrame({
        "score_1d": scores,
        "mkt_score_1d": [mkt] * n if not isinstance(mkt, list) else mkt,
        "close": close,
        "dc_upper": [dc_upper] * n,
        "dc_lower": [dc_lower] * n,
    })


def _fires(conds):
    out = None
    for s in conds.values():
        out = s.fillna(False) if out is None else out & s.fillna(False)
    return out.tolist()


def test_condition_ids_match_card():
    df = _frame([2.0], 1.0, [103.0])
    conds = _strategy(pusula_hizli.PusulaHizli_B).signal_conditions(df)
    assert set(conds["long"]) == {"regime_up", "market_up", "breakout_up"}
    assert set(conds["short"]) == {"regime_down", "market_down", "breakout_down"}


def test_long_fires_with_score_two_and_btc_up():
    # score +2, BTC +1, close breaks the channel on the second candle only
    df = _frame([2.0, 2.0, 2.0], 1.0, [100.0, 103.0, 104.0])
    conds = _strategy(pusula_hizli.PusulaHizli_B).signal_conditions(df)
    assert _fires(conds["long"]) == [False, True, False]  # first candle of the breakout run only


def test_score_one_is_mixed_no_trade():
    df = _frame([1.0, 1.0], 3.0, [100.0, 103.0])
    conds = _strategy(pusula_hizli.PusulaHizli_B).signal_conditions(df)
    assert _fires(conds["long"]) == [False, False]


def test_btc_must_be_on_the_same_side():
    df = _frame([2.0, 2.0], 0.0, [100.0, 103.0])
    conds = _strategy(pusula_hizli.PusulaHizli_B).signal_conditions(df)
    assert _fires(conds["long"]) == [False, False]


def test_short_fires_with_score_minus_two_and_btc_down():
    df = _frame([-2.0, -2.0], -1.0, [100.0, 94.0])
    conds = _strategy(pusula_hizli.PusulaHizli_B).signal_conditions(df)
    assert _fires(conds["short"]) == [False, True]
    assert _fires(conds["long"]) == [False, False]


def test_strict_variant_needs_score_three():
    df = _frame([2.0, 2.0], 1.0, [100.0, 103.0])
    assert _fires(_strategy(pusula_hizli.PusulaHizli3_B).signal_conditions(df)["long"]) == [False, False]
    df3 = _frame([3.0, 3.0], 1.0, [100.0, 103.0])
    assert _fires(_strategy(pusula_hizli.PusulaHizli3_B).signal_conditions(df3)["long"]) == [False, True]


def test_strict_variant_matches_pusula_b_entries():
    df = _frame([3.0, 3.0, 2.0, -3.0, -3.0], [1.0, 1.0, 1.0, -1.0, -1.0], [100.0, 103.0, 104.0, 100.0, 94.0])
    hizli = _strategy(pusula_hizli.PusulaHizli3_B).signal_conditions(df)
    base = _strategy(pusula.Pusula_B).signal_conditions(df)
    for side in ("long", "short"):
        assert _fires(hizli[side]) == _fires(base[side])


def test_fixed_exits_model_b_no_trend_exit():
    s = pusula_hizli.PusulaHizli_B
    assert s.tp_model_name == "B"
    assert s.use_exit_signal is False
    assert s.timeframe == "4h"
    assert s.channel == pusula.CHANNEL


def test_score_is_odd_so_two_equals_three():
    # Why the first round's ">= +2" did not loosen anything: the score is a sum of three +-1 signs.
    import numpy as np
    closes = np.concatenate([np.linspace(100, 300, 150), np.linspace(300, 120, 80), np.linspace(120, 200, 80)])
    s = pusula.regime_score(pd.DataFrame({"date": pd.date_range("2021-01-01", periods=len(closes), freq="1D", tz="UTC"),
                                          "close": closes})).dropna()
    assert set(s.unique()) <= {-3.0, -1.0, 1.0, 3.0}


def test_corrected_version_takes_two_of_three():
    df = _frame([1.0, 1.0], 1.0, [100.0, 103.0])
    assert _fires(_strategy(pusula_hizli.PusulaHizli1_B).signal_conditions(df)["long"]) == [False, True]
    dfs = _frame([-1.0, -1.0], -1.0, [100.0, 94.0])
    assert _fires(_strategy(pusula_hizli.PusulaHizli1_B).signal_conditions(dfs)["short"]) == [False, True]
    df0 = _frame([0.0, 0.0], 1.0, [100.0, 103.0])
    assert _fires(_strategy(pusula_hizli.PusulaHizli1_B).signal_conditions(df0)["long"]) == [False, False]
