"""
sfp_sweep: Swing Failure Pattern on 5m against 15m swing highs / lows.
Strategy card: cards/sfp_sweep.md (condition ids must match the card).
Rules fixed before the first test (2026-10-11).

Owner's rules (faithful test):
  context : swing highs / lows of the 15m chart (variant SfpSweep1h: 1h), resampled
            from the 5m candles inside the strategy. Pivot = 3 candles left (strictly
            higher) / 3 right (higher or equal); usable only by 5m candles that open
            after the 3rd right-side candle has closed. Incomplete higher-TF candles
            are dropped.
  short   : the 5m high pierces the most recent confirmed swing high (first 5m
            candle above that level since it was confirmed; one try per level),
            the candle closes back below it, upper wick >= 50% of the range.
  long    : mirror at the most recent confirmed swing low (lower wick >= 50%).
  entry   : rule says "at the signal candle close"; Freqtrade sees the closed candle
            and enters at the next candle open (order at the proposed rate = open).
  stop    : 0.1% beyond the wick extreme.
  TP1     : 50% at EQ = (current swing high + current swing low) / 2, then stop to
            the exact entry price (breakeven). Signal skipped if EQ is on the wrong
            side of the entry. TP1 may be < 1R (project rule TP1 >= 1R): such
            signals are NOT filtered, they are counted in the report.
  TP2     : rest at the opposite swing level.
General rules for this family: 1% risk per trade (leverage <= 10x), max 1 open
position (--max-open-trades 1), 3 losing trades in a row -> no entries for 24h.

The Freqtrade plumbing (stake from R, leverage, stop, resting TP limit orders) comes
from strategies/common/freqtrade_mixin.ManagedStrategy; only the levels differ.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from pandas import DataFrame  # noqa: E402

from freqtrade.persistence import Trade  # noqa: E402
from freqtrade.strategy import stoploss_from_absolute  # noqa: E402

from strategies.candidates.aslan_liquidity import pivots  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402
from strategies.common.freqtrade_mixin import ManagedStrategy  # noqa: E402

PIVOT_N = 3
WICK_MIN = 0.5
STOP_BUFFER = 0.001
BASE_MINUTES = 5
LOSS_STREAK = 3
HALT = timedelta(hours=24)


def htf_swing_events(df: DataFrame, tf_minutes: int, n: int = PIVOT_N) -> tuple[DataFrame, DataFrame]:
    """Swing highs / lows of the resampled higher timeframe as [avail, price] events.

    `avail` is the close time of the n-th right-side candle: from then on the pivot
    is known. Only complete higher-TF candles are used.
    """
    dates = pd.to_datetime(df["date"], utc=True)
    key = dates.dt.floor(f"{tf_minutes}min")
    g = pd.DataFrame({"key": key, "high": df["high"].to_numpy(float), "low": df["low"].to_numpy(float)})
    agg = g.groupby("key").agg(high=("high", "max"), low=("low", "min"), cnt=("high", "size"))
    agg = agg[agg["cnt"] == tf_minutes // BASE_MINUTES]
    h = agg["high"].to_numpy(float)
    lo = agg["low"].to_numpy(float)
    starts = agg.index
    ph, pl = pivots(h, lo, n)
    step = pd.Timedelta(minutes=tf_minutes)
    out = []
    for mask, values in ((ph, h), (pl, lo)):
        idx = np.flatnonzero(mask)
        idx = idx[idx + n < len(starts)]
        ev = pd.DataFrame({"avail": starts[idx + n] + step, "price": values[idx]})
        ev["avail"] = ev["avail"].astype("datetime64[ns, UTC]")
        out.append(ev.drop_duplicates("avail", keep="last").reset_index(drop=True))
    return out[0], out[1]


def _map_level(dates: pd.Series, events: DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Most recent level available at each 5m candle open: (price, level id)."""
    left = pd.DataFrame({"date": pd.to_datetime(dates, utc=True).astype("datetime64[ns, UTC]")})
    ev = events.copy()
    ev["lid"] = np.arange(len(ev), dtype=float)
    m = pd.merge_asof(left, ev, left_on="date", right_on="avail", direction="backward")
    return m["price"].to_numpy(float), m["lid"].to_numpy(float)


def sfp_indicators(df: DataFrame, tf_minutes: int) -> DataFrame:
    """Adds swing levels, SFP flags and the trade plan columns. Past data only."""
    highs, lows = htf_swing_events(df, tf_minutes)
    sh, sh_id = _map_level(df["date"], highs)
    sl, sl_id = _map_level(df["date"], lows)
    df["swing_high"] = sh
    df["swing_low"] = sl
    hi = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    op = df["open"].to_numpy(float)
    cl = df["close"].to_numpy(float)

    # first 5m candle beyond the level since the level became known (one try per level)
    prior_max = pd.Series(hi).groupby(sh_id).cummax().groupby(sh_id).shift().to_numpy(float)
    prior_min = pd.Series(lo).groupby(sl_id).cummin().groupby(sl_id).shift().to_numpy(float)
    with np.errstate(invalid="ignore"):
        df["first_touch_high"] = (hi > sh) & ~(prior_max > sh)
        df["first_touch_low"] = (lo < sl) & ~(prior_min < sl)
        rng = hi - lo
        df["upper_wick_ok"] = (rng > 0) & (hi - np.maximum(op, cl) >= WICK_MIN * rng)
        df["lower_wick_ok"] = (rng > 0) & (np.minimum(op, cl) - lo >= WICK_MIN * rng)

    eq = (sh + sl) / 2.0
    df["eq"] = eq
    df["short_entry"] = cl
    df["short_stop"] = hi * (1 + STOP_BUFFER)
    df["short_tp1"] = eq
    df["short_tp2"] = sl
    df["long_entry"] = cl
    df["long_stop"] = lo * (1 - STOP_BUFFER)
    df["long_tp1"] = eq
    df["long_tp2"] = sh
    for side in ("long", "short"):
        risk = np.abs(df[f"{side}_entry"] - df[f"{side}_stop"])
        df[f"{side}_tp1_r"] = np.abs(df[f"{side}_tp1"] - df[f"{side}_entry"]) / risk
    return df


def signal_conditions(df: DataFrame) -> dict[str, dict[str, pd.Series]]:
    """Condition id -> boolean Series, per side. Ids match the card."""
    return {
        "short": {
            "sweep_swing_high": df["first_touch_high"],
            "close_back_below": df["close"] < df["swing_high"],
            "upper_wick_50": df["upper_wick_ok"],
            "eq_below_entry": (df["eq"] < df["close"]) & (df["short_tp2"] < df["eq"]),
        },
        "long": {
            "sweep_swing_low": df["first_touch_low"],
            "close_back_above": df["close"] > df["swing_low"],
            "lower_wick_50": df["lower_wick_ok"],
            "eq_above_entry": (df["eq"] > df["close"]) & (df["long_tp2"] > df["eq"]),
        },
    }


def halt_until(closed: list[tuple[datetime, float]], streak_len: int = LOSS_STREAK,
               halt: timedelta = HALT) -> datetime | None:
    """End of the latest loss-streak pause.

    `closed` = (close time, net profit) of closed trades. A pause starts when
    `streak_len` losing trades (net < 0) close in a row; the counter restarts
    from zero after each pause trigger. Returns None if there never was one.
    """
    until = None
    streak = 0
    for t, profit in sorted(closed, key=lambda x: x[0]):
        if profit < 0:
            streak += 1
            if streak >= streak_len:
                until = t + halt
                streak = 0
        else:
            streak = 0
    return until


class SfpSweep(ManagedStrategy):
    """Main version (the card decides on this one): 15m swings."""

    timeframe = "5m"
    htf_minutes = 15
    startup_candle_count = 1200
    order_types = {
        # rule: entry at the signal close -> next candle open. A limit order at the
        # proposed rate (= next open in backtesting) fills at once, like a market order
        # (market entries would need entry_pricing.price_side = "other" in the config).
        "entry": "limit",
        "exit": "limit",  # TP orders rest at their exact level
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }
    mgmt = tm.ManagementParams(
        entry_zone_atr=0.0,
        valid_for_candles=1,
        stop_method="structural",
        stop_buffer_atr=0.0,
        max_stop_pct=0.08,
        max_leverage=10.0,
        risk_per_trade=0.01,
    )

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        return sfp_indicators(df, self.htf_minutes)

    def add_plan_columns(self, df: DataFrame) -> DataFrame:
        for side in ("long", "short"):
            stop_pct = np.abs(df[f"{side}_entry"] - df[f"{side}_stop"]) / df[f"{side}_entry"]
            df[f"{side}_plan_ok"] = (stop_pct <= self.mgmt.max_stop_pct) & (stop_pct > 0)
        return df

    def signal_conditions(self, df: DataFrame):
        return signal_conditions(df)

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_entry_trend(df, metadata)
        for side in ("long", "short"):
            m = df.get(f"enter_{side}", pd.Series(0, index=df.index)).fillna(0) == 1
            if not m.any():
                continue
            df.loc[m, "enter_tag"] = df.loc[m, "enter_tag"] + " tp1r=" + df.loc[m, f"{side}_tp1_r"].map("{:.3f}".format).astype(str)
        return df

    def custom_entry_price(self, pair, trade, current_time, proposed_rate, entry_tag, side, **kwargs) -> float:
        return proposed_rate

    def confirm_trade_entry(self, pair, order_type, amount, rate, time_in_force, current_time,
                            entry_tag, side, **kwargs) -> bool:
        until = halt_until([(t.close_date_utc, t.close_profit_abs or 0.0)
                            for t in Trade.get_trades_proxy(is_open=False)])
        if until is not None and current_time < until:
            return False
        row = self._last_row(pair)
        if row is None:
            return False
        # the next-open fill must still sit between the stop and EQ
        if side == "short":
            return bool(row["short_tp1"] < rate < row["short_stop"])
        return bool(row["long_stop"] < rate < row["long_tp1"])

    def custom_stoploss(self, pair, trade, current_time, current_rate, current_profit, after_fill, **kwargs):
        plan = self._plan_for_trade(trade)
        if plan is None:
            return None
        stop = plan["stop"]
        if trade.nr_of_successful_exits >= 1:
            stop = trade.open_rate  # breakeven: exact entry price (card)
        return stoploss_from_absolute(stop, current_rate, is_short=trade.is_short, leverage=trade.leverage)


class SfpSweep1h(SfpSweep):
    """Pre-declared variant (diagnostic): 1h swings."""

    htf_minutes = 60
