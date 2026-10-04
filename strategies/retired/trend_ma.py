"""
trend_ma: moving-average crossover with a long-term trend filter.
Strategy card: cards/trend_ma.md (condition ids below must match the card).

Two classes so both TP models can be backtested side by side:
  TrendMA_B  -> Model B (default: 50% at TP1, stop to break even, rest at TP2)
  TrendMA_A  -> Model A (single exit at TP2, break even after 2R)
"""

import sys
from pathlib import Path

# Make the repo root importable when Freqtrade loads this file directly.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import talib.abstract as ta  # noqa: E402
from freqtrade.strategy import IntParameter  # noqa: E402
from pandas import DataFrame  # noqa: E402

from strategies.common.freqtrade_mixin import ManagedStrategy  # noqa: E402


class TrendMA_B(ManagedStrategy):
    timeframe = "4h"
    tp_model_name = "B"

    # Parameters (kept few on purpose; ranges documented in the card)
    ema_fast = IntParameter(10, 30, default=20, space="buy", optimize=False)
    ema_slow = IntParameter(40, 60, default=50, space="buy", optimize=False)
    ema_trend = IntParameter(150, 250, default=200, space="buy", optimize=False)
    swing_lookback = 10
    # EMA200 needs a long warm-up: recursive-analysis showed ~2% drift with 250 candles, ~0% with 1000.
    startup_candle_count = 1000

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df["ema_fast"] = ta.EMA(df, timeperiod=self.ema_fast.value)
        df["ema_slow"] = ta.EMA(df, timeperiod=self.ema_slow.value)
        df["ema_trend"] = ta.EMA(df, timeperiod=self.ema_trend.value)
        df["atr"] = ta.ATR(df, timeperiod=14)
        # Swing levels use only past candles (no lookahead).
        df["swing_low"] = df["low"].rolling(self.swing_lookback).min()
        df["swing_high"] = df["high"].rolling(self.swing_lookback).max()
        return df

    def swing_levels(self, df: DataFrame):
        return {"long": df["swing_low"], "short": df["swing_high"]}

    def signal_conditions(self, df: DataFrame):
        fast, slow = df["ema_fast"], df["ema_slow"]
        cross_up = (fast > slow) & (fast.shift(1) <= slow.shift(1))
        cross_down = (fast < slow) & (fast.shift(1) >= slow.shift(1))
        return {
            "long": {
                "trend_up": df["close"] > df["ema_trend"],
                "ma_cross_up": cross_up,
            },
            "short": {
                "trend_down": df["close"] < df["ema_trend"],
                "ma_cross_down": cross_down,
            },
        }


class TrendMA_A(TrendMA_B):
    tp_model_name = "A"
