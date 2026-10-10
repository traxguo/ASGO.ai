"""
rsi_reversion: RSI leaves oversold/overbought in the direction of the EMA200 trend.
Strategy card: cards/rsi_reversion.md (condition ids below must match the card).

  RSIReversion_B  -> Model B (50% at TP1, stop to break even, rest at TP2)
  RSIReversion_A  -> Model A (single exit at TP2, break even after 2R)
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


class RSIReversion_B(ManagedStrategy):
    timeframe = "4h"
    tp_model_name = "B"

    # Fixed before the first test; ranges documented in the card.
    rsi_period = IntParameter(7, 21, default=14, space="buy", optimize=False)
    rsi_low = IntParameter(20, 35, default=30, space="buy", optimize=False)
    rsi_high = IntParameter(65, 80, default=70, space="buy", optimize=False)
    ema_trend = IntParameter(150, 250, default=200, space="buy", optimize=False)
    swing_lookback = 10
    startup_candle_count = 1000  # EMA200 warm-up (measured on trend_ma)

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df["ema_trend"] = ta.EMA(df, timeperiod=self.ema_trend.value)
        df["rsi"] = ta.RSI(df, timeperiod=self.rsi_period.value)
        df["atr"] = ta.ATR(df, timeperiod=14)
        df["swing_low"] = df["low"].rolling(self.swing_lookback).min()
        df["swing_high"] = df["high"].rolling(self.swing_lookback).max()
        return df

    def swing_levels(self, df: DataFrame):
        return {"long": df["swing_low"], "short": df["swing_high"]}

    def signal_conditions(self, df: DataFrame):
        rsi, prev = df["rsi"], df["rsi"].shift(1)
        return {
            "long": {
                "trend_up": df["close"] > df["ema_trend"],
                "rsi_exit_oversold": (rsi > self.rsi_low.value) & (prev <= self.rsi_low.value),
            },
            "short": {
                "trend_down": df["close"] < df["ema_trend"],
                "rsi_exit_overbought": (rsi < self.rsi_high.value) & (prev >= self.rsi_high.value),
            },
        }


class RSIReversion_A(RSIReversion_B):
    tp_model_name = "A"
