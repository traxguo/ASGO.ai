from datetime import datetime, timezone
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")
pytest.importorskip("talib")

from freqtrade.optimize import backtesting as bt  # noqa: E402

from strategies.retired import kirilim1s_limit as kl  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402
from strategies.retired import kirilim1s  # noqa: E402


class _FakeDP:
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


def test_card_rates_and_variants():
    assert kl.MAKER_FEE == 0.0002 and kl.TAKER_FEE == 0.0006 and kl.MARKET_SLIPPAGE == 0.0005
    main = kl.Kirilim1sLimit_B
    s = main({})
    assert s.limit_cost == pytest.approx(0.0002) and s.market_cost == pytest.approx(0.0011)
    assert s.mgmt.valid_for_candles == 3 and s.unfilledtimeout["entry"] == 180
    # Same signal rules as the retired Kirilim1s_B.
    assert issubclass(main, kirilim1s.Kirilim1s_B)
    assert main.channel == 24 and main.tp_model_name == "B" and main.use_market_filter
    six = kl.Kirilim1sLimit6_B({})
    assert six.mgmt == tm.ManagementParams(valid_for_candles=6) and six.unfilledtimeout["entry"] == 360
    assert kl.Kirilim1sLimitZone_B.mgmt == tm.DEFAULT_PARAMS
    assert not issubclass(kl.Kirilim1sLimitZone_B, kl.LevelEntryMixin)
    assert kl.Kirilim1sLimitCost2x_B({}).market_cost == pytest.approx(0.0022)
    assert kl.Kirilim1sLimitCost0_B({}).limit_cost == 0 and kl.Kirilim1sLimitCost0_B({}).market_cost == 0


def test_limit_sits_at_the_broken_level_and_plan_follows_shared_rules():
    daily = _daily(np.linspace(100, 300, 200))
    closes = [100.0] * 40 + [103.0] + [103.0] * 5
    s = _strategy(kl.Kirilim1sLimit_B, daily)
    df = s.populate_indicators(_hourly(closes, "2021-07-10"), {"pair": "ETH/USDT:USDT"})
    df = s.populate_entry_trend(df, {"pair": "ETH/USDT:USDT"})
    assert df.index[df["enter_long"] == 1].tolist() == [40]
    row = df.iloc[40]
    assert row["long_entry"] == pytest.approx(100.5)  # previous 24-candle high, not the close
    assert row["long_zone_low"] == row["long_zone_high"] == row["long_entry"]
    stop = tm.stop_price("long", 100.5, row["atr"], row["swing_low"], s.mgmt)
    assert row["long_stop"] == pytest.approx(stop)
    tp1, tp2 = tm.targets("long", 100.5, stop, tm.MODEL_B)
    assert row["long_tp1"] == pytest.approx(tp1) and row["long_tp2"] == pytest.approx(tp2)
    assert f"stop={row['long_stop']:.10g}" in row["enter_tag"]
    # Same signal candles as the retired Kirilim1s_B; only the entry price differs.
    k = _strategy(kirilim1s.Kirilim1s_B, daily)
    kdf = k.populate_entry_trend(k.populate_indicators(_hourly(closes, "2021-07-10"), {"pair": "ETH/USDT:USDT"}),
                                 {"pair": "ETH/USDT:USDT"})
    assert kdf.index[kdf["enter_long"] == 1].tolist() == [40]
    assert kdf.iloc[40]["long_entry"] > row["long_entry"]


def test_zone_variant_keeps_kirilim1s_entry_price():
    daily = _daily(np.linspace(100, 300, 200))
    closes = [100.0] * 40 + [103.0] + [103.0] * 5
    z = _strategy(kl.Kirilim1sLimitZone_B, daily)
    k = _strategy(kirilim1s.Kirilim1s_B, daily)
    meta = {"pair": "ETH/USDT:USDT"}
    zdf = z.populate_entry_trend(z.populate_indicators(_hourly(closes, "2021-07-10"), meta), meta)
    kdf = k.populate_entry_trend(k.populate_indicators(_hourly(closes, "2021-07-10"), meta), meta)
    pd.testing.assert_series_equal(zdf["long_entry"], kdf["long_entry"])
    pd.testing.assert_series_equal(zdf["long_stop"], kdf["long_stop"])


def test_trade_through_rule():
    # buffer = max(1 tick, 0.02 % of price)
    assert kl.trade_through_buffer(100.0, 0.001, 0.0002) == pytest.approx(0.02)
    assert kl.trade_through_buffer(0.01, 0.00001, 0.0002) == pytest.approx(0.00001)
    # buy limit at 100: a touch is not enough
    assert not kl.limit_filled("buy", 100.0, 100.0, 101.0, 0.02)
    assert not kl.limit_filled("buy", 100.0, 99.99, 101.0, 0.02)
    assert kl.limit_filled("buy", 100.0, 99.98, 101.0, 0.02)
    # sell limit (short entry or long TP) at 100
    assert not kl.limit_filled("sell", 100.0, 99.0, 100.01, 0.02)
    assert kl.limit_filled("sell", 100.0, 99.0, 100.02, 0.02)


def test_blended_exit_fee_gives_exact_total():
    # TP1 half filled at maker, rest stopped at taker + slippage
    v_tp, v_stop = 1200.0, 1000.0
    fee = kl.blended_exit_fee(v_tp, v_stop, 0.0002, 0.0011)
    assert fee * (v_tp + v_stop) == pytest.approx(v_tp * 0.0002 + v_stop * 0.0011)
    assert kl.blended_exit_fee(0.0, 500.0, 0.0002, 0.0011) == pytest.approx(0.0011)


def _fake_bt(strategy, touch_fills):
    return SimpleNamespace(strategy=strategy, _get_order_filled=lambda rate, row: touch_fills)


def _row(open_, high, low, close):
    row = [None] * 10
    row[bt.OPEN_IDX], row[bt.HIGH_IDX], row[bt.LOW_IDX], row[bt.CLOSE_IDX] = open_, high, low, close
    return tuple(row)


def test_backtest_wrapper_is_installed_and_blocks_touch_fills():
    wrapped = bt.Backtesting._try_close_open_order
    assert getattr(wrapped, "_asgo_fill_through", False)
    now = datetime(2021, 1, 1, tzinfo=timezone.utc)
    trade = SimpleNamespace(entry_side="buy", exit_side="sell", price_precision=0.01, precision_mode_price=4,
                            orders=[], fee_open=0.001, fee_close=0.001)
    order = SimpleNamespace(ft_order_side="buy", ft_order_tag="long stop=95", ft_price=100.0, order_date_utc=now)
    strat = kl.Kirilim1sLimit_B({})
    # low touches the limit exactly: no fill, fees untouched
    assert wrapped(_fake_bt(strat, True), order, trade, now, _row(101, 102, 100.0, 101)) is False
    assert trade.fee_open == 0.001
    # TP order touched but not traded through: no fill
    tp = SimpleNamespace(ft_order_side="sell", ft_order_tag="tp1", ft_price=110.0, order_date_utc=now)
    assert wrapped(_fake_bt(strat, True), tp, trade, now, _row(105, 110.01, 104, 105)) is False


def test_backtest_wrapper_leaves_other_strategies_alone():
    wrapped = bt.Backtesting._try_close_open_order
    now = datetime(2021, 1, 1, tzinfo=timezone.utc)
    trade = SimpleNamespace(entry_side="buy", exit_side="sell", price_precision=0.01, precision_mode_price=4,
                            orders=[], fee_open=0.001, fee_close=0.001)
    order = SimpleNamespace(ft_order_side="buy", ft_order_tag="x", ft_price=100.0, order_date_utc=now)
    other = SimpleNamespace()  # no fill_through_pct -> Freqtrade's own rule decides
    assert wrapped(_fake_bt(other, False), order, trade, now, _row(101, 102, 100.0, 101)) is False
    assert trade.fee_open == 0.001
