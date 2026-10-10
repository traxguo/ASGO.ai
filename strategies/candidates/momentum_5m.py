"""
momentum_5m: 5-minute momentum + breakout scalp with a volatility filter.
Strategy card: cards/momentum_5m.md (condition ids must match the card).
Rules fixed before the first test (2026-10-10).

This is a faithful test of the owner's rules from a video. It does NOT use the
shared trade-management module (strategies/common/):

  range = high - low
  long  : SMA(range,10) > SMA(range,50), close > close[20 bars ago],
          close > highest close of the previous 20 bars (current bar excluded),
          green candle
  short : mirror (lowest close of the previous 20 bars; variant: lowest low)
  entry : market, next candle open (normal Freqtrade behaviour)
  exits : stop -1.5% and take-profit +3% of the entry PRICE, both intrabar;
          if both are touched in one candle the stop counts first (Freqtrade
          checks stoploss before ROI). No other exit. Leverage 1x.

Freqtrade's minimal_roi is a net-of-fees profit ratio, so ROI 0.03 would put
the target ~3.2% away with 0.1% fees. custom_roi turns the +3% PRICE target
into the matching profit ratio for each trade (trade.calc_profit_ratio is the
exact inverse of the backtester's calc_close_rate_for_roi), so the target is
entry * 1.03 (short: * 0.97) for every --fee setting. 1R = 1.5%.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
from freqtrade.strategy import IStrategy

VOL_FAST = 10
VOL_SLOW = 50
LOOKBACK = 20
STOP_PCT = 0.015
TP_PCT = 0.03


def momentum_indicators(df: pd.DataFrame, short_uses_lows: bool = False) -> pd.DataFrame:
    """Adds the indicator columns. Uses only the current and past candles."""
    rng = df["high"] - df["low"]
    df["range_sma_fast"] = rng.rolling(VOL_FAST).mean()
    df["range_sma_slow"] = rng.rolling(VOL_SLOW).mean()
    df["close_20"] = df["close"].shift(LOOKBACK)
    prev_close = df["close"].shift(1)
    df["hh_close_20"] = prev_close.rolling(LOOKBACK).max()
    if short_uses_lows:
        df["ll_close_20"] = df["low"].shift(1).rolling(LOOKBACK).min()
    else:
        df["ll_close_20"] = prev_close.rolling(LOOKBACK).min()
    return df


def signal_conditions(df: pd.DataFrame) -> dict[str, dict[str, pd.Series]]:
    """Condition id -> boolean Series, per side. Ids match the card."""
    vol = df["range_sma_fast"] > df["range_sma_slow"]
    return {
        "long": {
            "vol_expanding": vol,
            "momentum_up": df["close"] > df["close_20"],
            "breakout_up": df["close"] > df["hh_close_20"],
            "green_candle": df["close"] > df["open"],
        },
        "short": {
            "vol_expanding": vol,
            "momentum_down": df["close"] < df["close_20"],
            "breakout_down": df["close"] < df["ll_close_20"],
            "red_candle": df["close"] < df["open"],
        },
    }


def all_true(conds: dict[str, pd.Series]) -> pd.Series:
    out = None
    for s in conds.values():
        s = s.fillna(False).astype(bool)
        out = s if out is None else (out & s)
    return out


class Momentum5m(IStrategy):
    """Main version (the card decides on this one)."""

    INTERFACE_VERSION = 3
    timeframe = "5m"
    can_short = True
    startup_candle_count = VOL_SLOW + LOOKBACK

    stoploss = -STOP_PCT
    # Effectively disabled; the +3% price target comes from custom_roi.
    minimal_roi = {"0": 100.0}
    use_custom_roi = True
    trailing_stop = False
    use_exit_signal = False
    process_only_new_candles = True

    short_uses_lows = False

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        return momentum_indicators(dataframe, self.short_uses_lows)

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        conds = signal_conditions(dataframe)
        long_ = all_true(conds["long"])
        short = all_true(conds["short"])
        dataframe.loc[long_, ["enter_long", "enter_tag"]] = (1, "momentum_5m_long")
        dataframe.loc[short, ["enter_short", "enter_tag"]] = (1, "momentum_5m_short")
        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        return dataframe

    def custom_roi(self, pair: str, trade, current_time: datetime, trade_duration: int,
                   entry_tag: str | None, side: str, **kwargs) -> float | None:
        """Profit ratio that corresponds to a +3% (short: -3%) PRICE move from entry."""
        target = trade.open_rate * (1 - TP_PCT if trade.is_short else 1 + TP_PCT)
        return trade.calc_profit_ratio(target)

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: str | None,
                 side: str, **kwargs) -> float:
        return 1.0


class Momentum5mLows(Momentum5m):
    """Diagnostic variant (declared on the card): short breakout uses the lowest LOW."""

    short_uses_lows = True
