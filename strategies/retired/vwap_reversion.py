"""
vwap_reversion: mean reversion to EMA20 / session VWAP after a stretch (5m).
Strategy card: cards/vwap_reversion.md (condition ids must match the card).
Rules fixed before the first test (2026-10-11).

Faithful test of the owner's rules (source asks for 3m; 3m data is not
available here, so 5m is used - see the card):

  indicators : session VWAP (reset every UTC day 00:00), EMA20, RSI14 (Wilder)
  long       : stretched_down  = (candle i or i-1 closed below VWAP and EMA20)
                                 and RSI14 < 30 on any of candles i, i-1, i-2
               bullish_reversal = pinbar_bull | engulfing_bull | morning_star
  short      : mirror (above both, RSI > 70, bearish patterns)
  entry      : limit at the reversal candle close, valid for 1 candle
  stop       : lowest low of the last 10 candles * (1 - 0.0005)
               (short: highest high * (1 + 0.0005)); 1R = |entry - stop|
  targets    : EMA20 and VWAP values of the signal candle. TP1 (50%) = the
               nearer one, TP2 = the farther one. Both must be on the profit
               side and >= 0.3R away, else no trade. After TP1 the stop moves to
               the exact entry price.
  sizing     : 1% equity risk per trade, leverage up to 10x (liquidation
               >= 2x stop distance away); skip when the 1R size does not fit.
  halt       : after 3 consecutive losing trades, no new entry for 24h.

It reuses the order plumbing of strategies/common (ManagedStrategy: limit
entry, resting TP limit orders, partial exit via adjust_trade_position, stop
via custom_stoploss, size via custom_stake_amount) but replaces the plan
columns with the levels of this card.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from freqtrade.persistence import Trade  # noqa: E402
from freqtrade.strategy import stoploss_from_absolute  # noqa: E402

from strategies.common import trade_management as tm  # noqa: E402
from strategies.common.freqtrade_mixin import ManagedStrategy  # noqa: E402

EMA_LEN = 20
RSI_LEN = 14
RSI_LOW = 30.0
RSI_HIGH = 70.0
SWING_LEN = 10
STOP_BUFFER = 0.0005
MIN_TARGET_R = 0.3
PIN_WICK_BODY = 2.0
STAR_FIRST_BODY_RANGE = 0.5
STAR_MIDDLE_BODY = 0.3
TP1_CLOSE_PCT = 50.0
MAX_LEVERAGE = 10.0
LOSS_STREAK = 3
HALT_HOURS = 24

MGMT = tm.ManagementParams(valid_for_candles=1, max_leverage=MAX_LEVERAGE, risk_per_trade=0.01,
                           max_stop_pct=0.08)


# ----------------------------------------------------------------- indicators


def session_vwap(df: pd.DataFrame) -> pd.Series:
    """VWAP that restarts at every UTC day 00:00 (current candle included)."""
    day = df["date"].dt.floor("D")
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = (tp * df["volume"]).groupby(day).cumsum()
    vol = df["volume"].groupby(day).cumsum()
    return pv / vol.replace(0, np.nan)


def rsi_wilder(close: pd.Series, length: int = RSI_LEN) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    rs = gain / loss
    return 100 - 100 / (1 + rs)


def vwap_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Adds indicator columns. Uses only the current and past candles."""
    df["vwap"] = session_vwap(df)
    df["ema20"] = df["close"].ewm(span=EMA_LEN, adjust=False, min_periods=EMA_LEN).mean()
    df["rsi14"] = rsi_wilder(df["close"])
    df["rsi_min3"] = df["rsi14"].rolling(3).min()
    df["rsi_max3"] = df["rsi14"].rolling(3).max()
    df["swing_low"] = df["low"].rolling(SWING_LEN).min()
    df["swing_high"] = df["high"].rolling(SWING_LEN).max()
    return df


def candle_patterns(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Reversal patterns on candle i (ids match the card)."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    body = (c - o).abs()
    rng = h - l
    lower_wick = np.minimum(o, c) - l
    upper_wick = h - np.maximum(o, c)
    mid = (h + l) / 2.0
    o1, c1, body1 = o.shift(1), c.shift(1), body.shift(1)
    o2, c2, body2, rng2 = o.shift(2), c.shift(2), body.shift(2), rng.shift(2)
    green, red = c > o, c < o

    pinbar_bull = (rng > 0) & (lower_wick > 0) & (lower_wick >= PIN_WICK_BODY * body) & (c >= mid)
    pinbar_bear = (rng > 0) & (upper_wick > 0) & (upper_wick >= PIN_WICK_BODY * body) & (c <= mid)
    engulfing_bull = (c1 < o1) & green & (c >= o1) & (o <= c1) & (body > body1)
    engulfing_bear = (c1 > o1) & red & (c <= o1) & (o >= c1) & (body > body1)
    first_big = body2 >= STAR_FIRST_BODY_RANGE * rng2
    middle_small = body1 <= STAR_MIDDLE_BODY * body2
    morning_star = (c2 < o2) & first_big & middle_small & green & (c >= (o2 + c2) / 2.0)
    evening_star = (c2 > o2) & first_big & middle_small & red & (c <= (o2 + c2) / 2.0)
    out = {
        "pinbar_bull": pinbar_bull, "engulfing_bull": engulfing_bull, "morning_star": morning_star,
        "pinbar_bear": pinbar_bear, "engulfing_bear": engulfing_bear, "evening_star": evening_star,
    }
    return {k: v.fillna(False).astype(bool) for k, v in out.items()}


def signal_conditions(df: pd.DataFrame) -> dict[str, dict[str, pd.Series]]:
    """Condition id -> boolean Series, per side. Ids match the card."""
    p = candle_patterns(df)
    below = (df["close"] < df["vwap"]) & (df["close"] < df["ema20"])
    above = (df["close"] > df["vwap"]) & (df["close"] > df["ema20"])
    below2 = below | below.shift(1, fill_value=False)
    above2 = above | above.shift(1, fill_value=False)
    return {
        "long": {
            "stretched_down": below2 & (df["rsi_min3"] < RSI_LOW),
            "bullish_reversal": p["pinbar_bull"] | p["engulfing_bull"] | p["morning_star"],
        },
        "short": {
            "stretched_up": above2 & (df["rsi_max3"] > RSI_HIGH),
            "bearish_reversal": p["pinbar_bear"] | p["engulfing_bear"] | p["evening_star"],
        },
    }


def pattern_name(df: pd.DataFrame, side: str) -> pd.Series:
    """First matching pattern id (for the tag / explanation)."""
    p = candle_patterns(df)
    names = ("pinbar_bull", "engulfing_bull", "morning_star") if side == "long" else \
        ("pinbar_bear", "engulfing_bear", "evening_star")
    out = pd.Series("", index=df.index, dtype=object)
    for n in reversed(names):
        out = out.where(~p[n], n)
    return out


def plan_columns(df: pd.DataFrame, min_tp1_r: float = MIN_TARGET_R) -> pd.DataFrame:
    """Entry, stop, TP1, TP2 and plan_ok for both sides (vectorised, signal candle values)."""
    entry = df["close"]
    for side in ("long", "short"):
        s = 1 if side == "long" else -1
        if side == "long":
            stop = df["swing_low"] * (1 - STOP_BUFFER)
            near = np.minimum(df["ema20"], df["vwap"])
            far = np.maximum(df["ema20"], df["vwap"])
        else:
            stop = df["swing_high"] * (1 + STOP_BUFFER)
            near = np.maximum(df["ema20"], df["vwap"])
            far = np.minimum(df["ema20"], df["vwap"])
        risk = s * (entry - stop)
        near_r = s * (near - entry) / risk
        far_r = s * (far - entry) / risk
        df[f"{side}_entry"] = entry
        df[f"{side}_zone_low"] = entry
        df[f"{side}_zone_high"] = entry
        df[f"{side}_stop"] = stop
        df[f"{side}_tp1"] = near
        df[f"{side}_tp2"] = far
        df[f"{side}_tp1_r"] = near_r
        df[f"{side}_tp2_r"] = far_r
        df[f"{side}_tp1_is_vwap"] = (near == df["vwap"]) & (df["vwap"] != df["ema20"])
        ok = (risk > 0) & (near_r >= max(MIN_TARGET_R, min_tp1_r)) & (far_r >= MIN_TARGET_R)
        df[f"{side}_plan_ok"] = ok.fillna(False)
    return df


def halt_until(closed_trades: list, streak_len: int = LOSS_STREAK, hours: int = HALT_HOURS):
    """
    Walks closed trades in close order. Every run of `streak_len` consecutive
    losing trades (net profit < 0) starts a pause of `hours` from the close of
    the last loss; the counter restarts after each pause. Returns the end of
    the latest pause (or None).
    """
    streak = 0
    until = None
    for t in sorted(closed_trades, key=lambda x: x.close_date_utc):
        if (t.close_profit_abs or 0.0) < 0:
            streak += 1
            if streak >= streak_len:
                until = t.close_date_utc + timedelta(hours=hours)
                streak = 0
        else:
            streak = 0
    return until


# ------------------------------------------------------------------- strategy


class VwapReversion(ManagedStrategy):
    """Main version (the card decides on this one)."""

    timeframe = "5m"
    can_short = True
    startup_candle_count = 300  # EMA/RSI warm-up and at least one full VWAP day
    mgmt = MGMT
    min_tp1_r = MIN_TARGET_R

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        return vwap_indicators(dataframe)

    def signal_conditions(self, df: pd.DataFrame) -> dict[str, dict[str, pd.Series]]:
        return signal_conditions(df)

    def add_plan_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        return plan_columns(df, self.min_tp1_r)

    def populate_entry_trend(self, df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        df = self.add_plan_columns(df)
        conds = self.signal_conditions(df)
        df["enter_long"] = 0
        df["enter_short"] = 0
        df["enter_tag"] = None
        for side in ("long", "short"):
            mask = df[f"{side}_plan_ok"].copy()
            for s in conds[side].values():
                mask &= s.fillna(False).astype(bool)
            df.loc[mask, f"enter_{side}"] = 1
            tags = (f"{side} " + pattern_name(df, side) + " stop="
                    + df[f"{side}_stop"].map("{:.10g}".format).astype(str))
            df.loc[mask, "enter_tag"] = tags[mask]
        return df

    # ---- sizing: 1% risk, leverage <= 10x with liquidation >= 2x stop away
    def leverage(self, pair, current_time, current_rate, proposed_leverage, max_leverage, entry_tag,
                 side, **kwargs) -> float:
        row = self._last_row(pair)
        if row is None:
            return 1.0
        lev = tm.safe_leverage(side, float(row[f"{side}_entry"]), float(row[f"{side}_stop"]), self.mgmt)
        return min(lev or 1.0, max_leverage)

    # ---- 3 consecutive losses -> 24h pause (all pairs)
    def confirm_trade_entry(self, pair, order_type, amount, rate, time_in_force, current_time,
                            entry_tag, side, **kwargs) -> bool:
        until = halt_until(Trade.get_trades_proxy(is_open=False))
        return not (until is not None and current_time < until)

    # ---- stop: plan stop, exact entry price after TP1
    def custom_stoploss(self, pair, trade, current_time, current_rate, current_profit, after_fill,
                        **kwargs) -> float | None:
        plan = self._plan_for_trade(trade)
        if plan is None:
            return None
        stop = trade.open_rate if trade.nr_of_successful_exits >= 1 else plan["stop"]
        return stoploss_from_absolute(stop, current_rate, is_short=trade.is_short, leverage=trade.leverage)

    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, min_stake,
                              max_stake, **kwargs):
        if trade.has_open_orders:
            return None
        if trade.nr_of_successful_exits == 0:
            return -trade.stake_amount * TP1_CLOSE_PCT / 100, "tp1"
        return -trade.stake_amount, "tp2"


class VwapReversionTp1R(VwapReversion):
    """Pre-declared variant: the first target must be >= 1R away (project rule TP1 >= 1R)."""

    min_tp1_r = 1.0
