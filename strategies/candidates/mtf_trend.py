"""
mtf_trend: daily trend direction first, then a 4h entry trigger in that direction.
Strategy card: cards/mtf_trend.md (condition ids below must match the card).

Shared daily filter (fixed before testing):
  trend_1d_up   : last CLOSED daily candle close > daily EMA(50)
  trend_1d_down : last CLOSED daily candle close < daily EMA(50)
merge_informative_pair shifts the daily data so a 4h candle only sees daily
candles that had already closed (no lookahead).

Entry triggers (4h), one class each:
  MTFDonchian_B   : close breaks the previous 20-candle high/low (first close beyond)
  MTFPullback_B   : RSI(14) crosses back above 40 (long) / below 60 (short)
  MTFSupertrend_B : Supertrend(10, 3) flips to up (long) / down (short)
  MTFSqueeze_B    : Bollinger(20, 2) was inside Keltner(20, 1.5 ATR) on the previous
                    candle (squeeze) and close breaks out of the Bollinger band
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import talib.abstract as ta  # noqa: E402
from freqtrade.strategy import merge_informative_pair  # noqa: E402
from pandas import DataFrame, Series  # noqa: E402

from strategies.common.freqtrade_mixin import ManagedStrategy  # noqa: E402

TREND_TF = "1d"
TREND_EMA = 50


def first_true(cond: Series) -> Series:
    """True only on the first candle of a run of True values."""
    return cond & ~cond.shift(1, fill_value=False)


def supertrend_direction(df: DataFrame, period: int = 10, mult: float = 3.0) -> Series:
    """+1 / -1 Supertrend direction, computed candle by candle from past data only."""
    hl2 = ((df["high"] + df["low"]) / 2).to_numpy()
    atr = ta.ATR(df, timeperiod=period).to_numpy()
    close = df["close"].to_numpy()
    n = len(df)
    upper = hl2 + mult * atr
    lower = hl2 - mult * atr
    fu, fl = upper.copy(), lower.copy()
    direction = np.zeros(n)
    for i in range(1, n):
        if np.isnan(atr[i]) or np.isnan(atr[i - 1]):
            continue
        fu[i] = upper[i] if (upper[i] < fu[i - 1] or close[i - 1] > fu[i - 1]) else fu[i - 1]
        fl[i] = lower[i] if (lower[i] > fl[i - 1] or close[i - 1] < fl[i - 1]) else fl[i - 1]
        prev = direction[i - 1] if direction[i - 1] != 0 else 1
        if prev == 1 and close[i] < fl[i]:
            direction[i] = -1
        elif prev == -1 and close[i] > fu[i]:
            direction[i] = 1
        else:
            direction[i] = prev
    return Series(direction, index=df.index)


class MTFBase(ManagedStrategy):
    timeframe = "4h"
    tp_model_name = "B"
    swing_lookback = 10
    startup_candle_count = 400  # 4h candles; the daily EMA50 gets the same count of daily candles
    trend_ema = TREND_EMA
    channel = 20

    def informative_pairs(self):
        return [(pair, TREND_TF) for pair in self.dp.current_whitelist()]

    def add_daily_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        daily = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=TREND_TF)
        daily = daily.copy()
        daily["ema_trend"] = ta.EMA(daily, timeperiod=self.trend_ema)
        df = merge_informative_pair(df, daily[["date", "close", "ema_trend"]], self.timeframe, TREND_TF, ffill=True)
        return df

    def base_indicators(self, df: DataFrame) -> DataFrame:
        df["atr"] = ta.ATR(df, timeperiod=14)
        df["swing_low"] = df["low"].rolling(self.swing_lookback).min()
        df["swing_high"] = df["high"].rolling(self.swing_lookback).max()
        return df

    def swing_levels(self, df: DataFrame):
        return {"long": df["swing_low"], "short": df["swing_high"]}

    def trend_conditions(self, df: DataFrame):
        return (
            {"trend_1d_up": df[f"close_{TREND_TF}"] > df[f"ema_trend_{TREND_TF}"]},
            {"trend_1d_down": df[f"close_{TREND_TF}"] < df[f"ema_trend_{TREND_TF}"]},
        )

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = self.base_indicators(df)
        df = self.trigger_indicators(df)
        return self.add_daily_trend(df, metadata)

    def trigger_indicators(self, df: DataFrame) -> DataFrame:
        return df

    def triggers(self, df: DataFrame):
        raise NotImplementedError

    def signal_conditions(self, df: DataFrame):
        up, down = self.trend_conditions(df)
        long_t, short_t = self.triggers(df)
        return {"long": {**up, **long_t}, "short": {**down, **short_t}}


class MTFDonchian_B(MTFBase):
    def trigger_indicators(self, df):
        df["dc_upper"] = df["high"].rolling(self.channel).max().shift(1)
        df["dc_lower"] = df["low"].rolling(self.channel).min().shift(1)
        return df

    def triggers(self, df):
        return ({"breakout_up": first_true(df["close"] > df["dc_upper"])},
                {"breakout_down": first_true(df["close"] < df["dc_lower"])})


class MTFPullback_B(MTFBase):
    def trigger_indicators(self, df):
        df["rsi"] = ta.RSI(df, timeperiod=14)
        return df

    def triggers(self, df):
        rsi, prev = df["rsi"], df["rsi"].shift(1)
        return ({"rsi_pullback_end_up": (rsi > 40) & (prev <= 40)},
                {"rsi_pullback_end_down": (rsi < 60) & (prev >= 60)})


class MTFSupertrend_B(MTFBase):
    def trigger_indicators(self, df):
        df["st_dir"] = supertrend_direction(df, 10, 3.0)
        return df

    def triggers(self, df):
        d, prev = df["st_dir"], df["st_dir"].shift(1)
        return ({"supertrend_flip_up": (d == 1) & (prev == -1)},
                {"supertrend_flip_down": (d == -1) & (prev == 1)})


class MTFSqueeze_B(MTFBase):
    def trigger_indicators(self, df):
        mid = df["close"].rolling(20).mean()
        sd = df["close"].rolling(20).std(ddof=0)
        df["bb_upper"], df["bb_lower"] = mid + 2 * sd, mid - 2 * sd
        kc_atr = ta.ATR(df, timeperiod=20)
        ema20 = ta.EMA(df, timeperiod=20)
        df["kc_upper"], df["kc_lower"] = ema20 + 1.5 * kc_atr, ema20 - 1.5 * kc_atr
        df["squeeze"] = (df["bb_upper"] < df["kc_upper"]) & (df["bb_lower"] > df["kc_lower"])
        return df

    def triggers(self, df):
        was_squeezed = df["squeeze"].shift(1, fill_value=False)
        return ({"squeeze_break_up": was_squeezed & (df["close"] > df["bb_upper"])},
                {"squeeze_break_down": was_squeezed & (df["close"] < df["bb_lower"])})


class MTFDonchian_A(MTFDonchian_B):
    tp_model_name = "A"


class MTFPullback_A(MTFPullback_B):
    tp_model_name = "A"


class MTFSupertrend_A(MTFSupertrend_B):
    tp_model_name = "A"


class MTFSqueeze_A(MTFSqueeze_B):
    tp_model_name = "A"


class MTFDonchianATR_B(MTFDonchian_B):
    """MTFDonchian + the ATR filter from atr_filtered.py (best Level 1 candidate + daily trend)."""

    vol_window = 200

    def trigger_indicators(self, df):
        df = super().trigger_indicators(df)
        df["atr_pct"] = df["atr"] / df["close"]
        df["atr_pct_median"] = df["atr_pct"].rolling(self.vol_window).median()
        return df

    def triggers(self, df):
        long_t, short_t = super().triggers(df)
        vol_ok = df["atr_pct"] > df["atr_pct_median"]
        return {**long_t, "vol_ok": vol_ok}, {**short_t, "vol_ok": vol_ok}


class MTFDonchianATR_A(MTFDonchianATR_B):
    tp_model_name = "A"
