"""
donchian_breakout: close breaks the previous N-candle high/low (turtle-style breakout).
Strategy card: cards/donchian_breakout.md (condition ids below must match the card).

Two classes so both TP models can be backtested side by side:
  DonchianBreakout_B  -> Model B (50% at TP1, stop to break even, rest at TP2)
  DonchianBreakout_A  -> Model A (single exit at TP2, break even after 2R)
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


class DonchianBreakout_B(ManagedStrategy):
    timeframe = "4h"
    tp_model_name = "B"

    # Fixed before the first test; range documented in the card.
    channel = IntParameter(15, 55, default=20, space="buy", optimize=False)
    swing_lookback = 10
    # ATR (Wilder smoothing) drifts 0.03% with 100 candles, ~0% with 300 (recursive-analysis).
    startup_candle_count = 300

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        n = self.channel.value
        # Channel from the candles BEFORE the signal candle (shift 1): no lookahead,
        # and the signal candle's own high cannot be part of the level it breaks.
        df["dc_upper"] = df["high"].rolling(n).max().shift(1)
        df["dc_lower"] = df["low"].rolling(n).min().shift(1)
        df["atr"] = ta.ATR(df, timeperiod=14)
        df["swing_low"] = df["low"].rolling(self.swing_lookback).min()
        df["swing_high"] = df["high"].rolling(self.swing_lookback).max()
        return df

    def swing_levels(self, df: DataFrame):
        return {"long": df["swing_low"], "short": df["swing_high"]}

    def signal_conditions(self, df: DataFrame):
        above = df["close"] > df["dc_upper"]
        below = df["close"] < df["dc_lower"]
        return {
            "long": {"breakout_up": above & ~above.shift(1, fill_value=False)},
            "short": {"breakout_down": below & ~below.shift(1, fill_value=False)},
        }


class DonchianBreakout_A(DonchianBreakout_B):
    tp_model_name = "A"
