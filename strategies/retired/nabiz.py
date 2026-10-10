"""
nabiz ("pulse"): fast candidate on 1h candles. Strategy card: cards/nabiz.md
(condition ids below must match the card). Rules fixed before the first test.

Daily regime: exactly Pusula's score (strategies/candidates/pusula.py), from the
last CLOSED daily candle, for the coin and for BTC.

1h trigger in the regime's direction only (end of a pullback):
  long : RSI(14) crosses back up through 35 (previous candle < 35, this one >= 35)
  short: RSI(14) crosses back down through 65 (previous candle > 65, this one <= 65)

Trade management: shared module (entry zone 0.25 ATR, wider of 1.5 ATR /
10-candle swing stop, Model B 2R/4R, 3-candle validity, max 3x).

merge_informative_pair shifts the daily data so a 1h candle only sees daily
candles that had already closed (no lookahead).

RETIRED 2026-10-10: development period 2020-2024 on 36 coins gave -0.09R per
trade after costs and funding (about 0R before costs), max drawdown 97%.
Reason on the card. Kept for the record; do not use for signals.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import talib.abstract as ta  # noqa: E402
from freqtrade.strategy import merge_informative_pair  # noqa: E402
from pandas import DataFrame, Series  # noqa: E402

from strategies.candidates.pusula import EMA_FAST, EMA_SLOW, MARKET_PAIR, MOMENTUM_DAYS, REGIME_TF, daily_regime_frame  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402
from strategies.common.freqtrade_mixin import ManagedStrategy  # noqa: E402

RSI_PERIOD = 14
RSI_LOW = 35
RSI_HIGH = 65


def cross_up(series: Series, level: float) -> Series:
    """True on the candle where series moves from below level to level or above."""
    return (series.shift(1) < level) & (series >= level)


def cross_down(series: Series, level: float) -> Series:
    """True on the candle where series moves from above level to level or below."""
    return (series.shift(1) > level) & (series <= level)


class Nabiz_B(ManagedStrategy):
    """Main version (card decides on this one)."""

    timeframe = "1h"
    tp_model_name = "B"
    swing_lookback = 10
    # 1h warm-up for RSI/ATR; the daily data gets the same count of daily candles,
    # enough for EMA50 and the 90-day momentum.
    startup_candle_count = 400
    rsi_period = RSI_PERIOD
    rsi_low = RSI_LOW
    rsi_high = RSI_HIGH

    def informative_pairs(self):
        pairs = [(pair, REGIME_TF) for pair in self.dp.current_whitelist()]
        if (MARKET_PAIR, REGIME_TF) not in pairs:
            pairs.append((MARKET_PAIR, REGIME_TF))
        return pairs

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df["atr"] = ta.ATR(df, timeperiod=14)
        df["rsi"] = ta.RSI(df, timeperiod=self.rsi_period)
        df["swing_low"] = df["low"].rolling(self.swing_lookback).min()
        df["swing_high"] = df["high"].rolling(self.swing_lookback).max()
        daily = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=REGIME_TF)
        market = self.dp.get_pair_dataframe(pair=MARKET_PAIR, timeframe=REGIME_TF)
        regime = daily_regime_frame(daily, market, EMA_FAST, EMA_SLOW, MOMENTUM_DAYS)
        return merge_informative_pair(df, regime, self.timeframe, REGIME_TF, ffill=True)

    def swing_levels(self, df: DataFrame):
        return {"long": df["swing_low"], "short": df["swing_high"]}

    def signal_conditions(self, df: DataFrame):
        score = df[f"score_{REGIME_TF}"]
        mkt = df[f"mkt_score_{REGIME_TF}"]
        return {
            "long": {
                "regime_up": score >= 3,
                "market_up": mkt >= 1,
                "pullback_end_up": cross_up(df["rsi"], self.rsi_low),
            },
            "short": {
                "regime_down": score <= -3,
                "market_down": mkt <= -1,
                "pullback_end_down": cross_down(df["rsi"], self.rsi_high),
            },
        }


class NabizWide_B(Nabiz_B):
    """Diagnostic variant (declared on the card before testing): stop 3 ATR instead of 1.5."""

    mgmt = tm.ManagementParams(stop_atr=3.0)
