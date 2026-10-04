"""
Freqtrade glue for the shared trade management rules.

A strategy inherits ManagedStrategy, implements populate_indicators and a
`signal_conditions` method, and gets the whole section-7 management for free:

- entry as a limit order at the middle of the entry zone (custom_entry_price)
- the order is cancelled after `valid_for_candles` candles (unfilledtimeout)
  or when price reaches the stop before the entry fills (check_entry_timeout)
- stop at the planned level (custom_stoploss), moved to break even by the TP model
- TP1 partial exit and TP2 exit as resting limit orders (adjust_trade_position)
- leverage chosen so liquidation stays >= 2x stop distance away (leverage)
- position size from R: a stop-out loses `risk_per_trade` of equity (custom_stake_amount)

All levels are written to dataframe columns on the signal candle, so the
callbacks only ever look them up; they never recalculate anything with newer data.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.exchange import timeframe_to_minutes, timeframe_to_prev_date
from freqtrade.persistence import Order, Trade
from freqtrade.strategy import IStrategy, stoploss_from_absolute

from . import trade_management as tm

SIDES = ("long", "short")


class ManagedStrategy(IStrategy):
    """Base class. Subclasses set `tp_model_name` and implement `signal_conditions`."""

    INTERFACE_VERSION = 3
    can_short = True
    use_custom_stoploss = True
    position_adjustment_enable = True
    use_exit_signal = False
    process_only_new_candles = True
    startup_candle_count = 250

    # Very wide static stop: the real stop always comes from custom_stoploss.
    stoploss = -0.99
    minimal_roi = {"0": 100}  # ROI disabled; exits come from the TP model only
    trailing_stop = False

    order_types = {
        "entry": "limit",
        "exit": "limit",  # TP orders rest at their exact level
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }

    # Which TP model this strategy runs with ("A" or "B"). Override per test.
    tp_model_name: str = "B"
    mgmt: tm.ManagementParams = tm.DEFAULT_PARAMS

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        # Signal validity (7.1): the entry limit order lives N candles, TP orders rest until filled.
        self.unfilledtimeout = {
            "entry": self.mgmt.valid_for_candles * timeframe_to_minutes(self.timeframe),
            "exit": 10_000_000,
            "unit": "minutes",
        }

    # --------------------------------------------------------------- helpers

    @property
    def tp_model(self) -> tm.TPModel:
        return tm.TP_MODELS[self.tp_model_name]

    def signal_conditions(self, df: DataFrame) -> dict[str, dict[str, pd.Series]]:
        """
        Return {"long": {condition_id: bool Series, ...}, "short": {...}}.
        A side's signal fires when ALL its conditions are true.
        Condition ids must match the strategy card.
        """
        raise NotImplementedError

    def swing_levels(self, df: DataFrame) -> dict[str, pd.Series | None]:
        """Optional structural stop levels: {"long": swing_low, "short": swing_high}."""
        return {"long": None, "short": None}

    def add_plan_columns(self, df: DataFrame) -> DataFrame:
        """Vectorised: writes entry zone, stop, R, TPs for both sides on every candle."""
        swings = self.swing_levels(df)
        for side in SIDES:
            low, high, mid = tm.entry_zone(side, df["close"], df["atr"], self.mgmt.entry_zone_atr)
            stop = tm.stop_price(side, mid, df["atr"], swings.get(side), self.mgmt)
            tp1, tp2 = tm.targets(side, mid, stop, self.tp_model)
            df[f"{side}_zone_low"] = low
            df[f"{side}_zone_high"] = high
            df[f"{side}_entry"] = mid
            df[f"{side}_stop"] = stop
            df[f"{side}_tp1"] = tp1
            df[f"{side}_tp2"] = tp2
            stop_pct = np.abs(mid - stop) / mid
            df[f"{side}_plan_ok"] = (stop_pct <= self.mgmt.max_stop_pct) & (stop_pct > 0)
        return df

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = self.add_plan_columns(df)
        conditions = self.signal_conditions(df)
        for side in SIDES:
            conds = conditions.get(side, {})
            if not conds:
                continue
            mask = df[f"{side}_plan_ok"].copy()
            for series in conds.values():
                mask &= series.fillna(False).astype(bool)
            df.loc[mask, f"enter_{side}"] = 1
            # The planned stop travels with the trade in its tag, so reports can
            # compute results in R exactly (scripts/make_report.py parses it).
            tags = f"{side} stop=" + df[f"{side}_stop"].map("{:.10g}".format).astype(str)
            df.loc[mask, "enter_tag"] = tags[mask]
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        return df  # no indicator exits; the TP model decides

    def _signal_row(self, pair: str, signal_time: datetime) -> pd.Series | None:
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty:
            return None
        rows = df.loc[df["date"] == signal_time]
        return None if rows.empty else rows.iloc[-1]

    def _signal_time_for_trade(self, trade: Trade) -> datetime:
        # Order is placed during the candle after the signal candle.
        return timeframe_to_prev_date(self.timeframe, trade.open_date_utc) - timedelta(
            minutes=timeframe_to_minutes(self.timeframe)
        )

    def _plan_for_trade(self, trade: Trade) -> dict | None:
        cached = trade.get_custom_data("plan")
        if cached:
            return cached
        row = self._signal_row(trade.pair, self._signal_time_for_trade(trade))
        if row is None:
            return None
        side = "short" if trade.is_short else "long"
        plan = {
            "side": side,
            "entry": float(row[f"{side}_entry"]),
            "stop": float(row[f"{side}_stop"]),
            "tp1": float(row[f"{side}_tp1"]),
            "tp2": float(row[f"{side}_tp2"]),
        }
        trade.set_custom_data("plan", plan)
        return plan

    def _last_row(self, pair: str) -> pd.Series | None:
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        return None if df is None or df.empty else df.iloc[-1]

    # ------------------------------------------------------------- callbacks

    def custom_entry_price(self, pair, trade, current_time, proposed_rate, entry_tag, side, **kwargs) -> float:
        row = self._last_row(pair)
        if row is None:
            return proposed_rate
        return float(row[f"{side}_entry"])

    def leverage(self, pair, current_time, current_rate, proposed_leverage, max_leverage, entry_tag, side, **kwargs) -> float:
        row = self._last_row(pair)
        if row is None:
            return 1.0
        lev = tm.safe_leverage(side, float(row[f"{side}_entry"]), float(row[f"{side}_stop"]), self.mgmt)
        return min(lev or 1.0, max_leverage)

    def custom_stake_amount(self, pair, current_time, current_rate, proposed_stake, min_stake, max_stake, leverage, entry_tag, side, **kwargs) -> float:
        row = self._last_row(pair)
        if row is None:
            return 0.0
        equity = self.wallets.get_total_stake_amount()
        notional = tm.position_notional(equity, float(row[f"{side}_entry"]), float(row[f"{side}_stop"]), self.mgmt)
        stake = notional / leverage
        if stake > max_stake:
            # Not enough free margin to take the full 1R size: skip instead of
            # silently taking a different risk than tested.
            return 0.0
        return stake

    def check_entry_timeout(self, pair: str, trade: Trade, order: Order, current_time: datetime, **kwargs) -> bool:
        """Cancel the pending entry if price touched the stop before filling (7.1)."""
        plan = self._plan_for_trade(trade)
        last = self._last_row(pair)
        if plan is None or last is None:
            return False
        if last["date"] < self._signal_time_for_trade(trade) + timedelta(minutes=timeframe_to_minutes(self.timeframe)):
            return False
        if trade.is_short:
            return bool(last["high"] >= plan["stop"])
        return bool(last["low"] <= plan["stop"])

    def custom_stoploss(self, pair, trade, current_time, current_rate, current_profit, after_fill, **kwargs) -> float | None:
        plan = self._plan_for_trade(trade)
        if plan is None:
            return None
        side = plan["side"]
        model = self.tp_model
        stop = plan["stop"]
        risk = abs(plan["entry"] - plan["stop"])
        if model.breakeven_trigger == "TP1" and model.tp1_close_pct > 0:
            be_active = trade.nr_of_successful_exits >= 1
        else:
            best = trade.min_rate if trade.is_short else trade.max_rate
            if best is None:  # first call right after the entry fill
                best = trade.open_rate
            moved_r = (best - trade.open_rate) / risk * (1 if side == "long" else -1)
            be_active = moved_r >= model.breakeven_r
        if be_active:
            stop = tm.breakeven_stop(side, trade.open_rate, self.mgmt)
        return stoploss_from_absolute(stop, current_rate, is_short=trade.is_short, leverage=trade.leverage)

    def adjust_trade_position(self, trade: Trade, current_time, current_rate, current_profit, min_stake, max_stake, **kwargs):
        """Places TP orders as resting limit orders (one at a time)."""
        if trade.has_open_orders:
            return None
        model = self.tp_model
        if model.tp1_close_pct > 0 and trade.nr_of_successful_exits == 0:
            return -trade.stake_amount * model.tp1_close_pct / 100, "tp1"
        return -trade.stake_amount, "tp2"

    def custom_exit_price(self, pair, trade, current_time, proposed_rate, current_profit, exit_tag, **kwargs) -> float:
        plan = self._plan_for_trade(trade)
        if plan is None:
            return proposed_rate
        if exit_tag == "tp1":
            return plan["tp1"]
        if exit_tag == "tp2":
            return plan["tp2"]
        return proposed_rate
