"""
kirilim1s_limit ("breakout 1h, limit entry"): fast candidate 3, queue item 1c.
Strategy card: cards/kirilim1s_limit.md (condition ids must match the card).
Rules fixed before the first test.

Same signals as Kirilim1s_B (strategies/retired/kirilim1s.py, imported from
there so the signal code is one and the same; Python imports work from any
folder, Freqtrade only loads classes *defined* in this file). What changes:

1. Entry price (main version): one limit order AT the broken level, i.e. the
   previous 24-candle high (long) / low (short): we wait for a retest. Stop and
   targets are computed from that price with the shared functions (zone width 0).
   Valid for `mgmt.valid_for_candles` 1h candles, cancelled if not filled or if
   price reaches the stop first (shared module).

2. Costs per order type (backtest only), Bitget USDT-M published rates:
     limit entry (resting)          maker 0.02 %, no slippage
     entry already marketable when placed: taker 0.06 % + 0.05 % slippage
     TP1 / TP2 limit exits          maker 0.02 %, no slippage
     stop (market)                  taker 0.06 % + 0.05 % slippage
   Freqtrade keeps one entry and one exit fee rate per trade. The entry rate is
   set when the entry fills; the exit rate is maker while TPs rest and, if the
   trade ends at the stop, the value-weighted blend of all exits, so the total
   fee is exact. `cost_mult` scales all of it (x2 test, zero-cost diagnostic).
   Only the backtest uses these rates (dry-run / live take the exchange's fees).

3. Stricter limit fill rule (against optimistic fills): Freqtrade fills a limit
   order when the candle merely touches it. For this strategy a resting limit
   (entry or TP) only fills when price trades THROUGH it by at least
   max(1 tick, `fill_through_pct` of price). The fill price stays the limit.
   This, and the fee of point 2, is installed as a small wrapper around
   Backtesting._try_close_open_order that only acts on strategies with a
   `fill_through_pct` attribute; every other strategy keeps Freqtrade's normal
   rule and the config fee.

RETIRED 2026-10-10: development period 2020-2024 on 36 coins gave +0.018R per
trade after costs and funding, profit factor 1.00, max drawdown 61%, negative at
double costs. Costs fell (~0.06R -> ~0.03R per trade) but the limit at the
broken level fills mostly on the weak breakouts (adverse selection), so the
pre-cost edge fell from +0.12R to +0.05R. Reason on the card. Kept for the
record; do not use for signals. Running it now needs
FT_STRATEGY_DIR=strategies/retired.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
from pandas import DataFrame  # noqa: E402

from strategies.common import trade_management as tm  # noqa: E402
from strategies.common.freqtrade_mixin import SIDES  # noqa: E402
from strategies.retired.kirilim1s import Kirilim1s_B  # noqa: E402

# Bitget USDT-M futures, standard (VIP 0) published rates.
MAKER_FEE = 0.0002
TAKER_FEE = 0.0006
MARKET_SLIPPAGE = 0.0005  # same pessimistic slippage the project uses for market orders
FILL_THROUGH_PCT = 0.0002  # price must trade this far (and >= 1 tick) beyond a resting limit
TICK_SIZE_MODE = 4  # ccxt.TICK_SIZE


def trade_through_buffer(price: float, tick: float, pct: float) -> float:
    """How far beyond the limit price must trade before the limit counts as filled."""
    return max(tick or 0.0, pct * price)


def limit_filled(order_side: str, price: float, low: float, high: float, buffer: float) -> bool:
    """A buy limit fills when the low trades below it by `buffer`; a sell limit when the high trades above."""
    if order_side == "buy":
        return low <= price - buffer
    return high >= price + buffer


def blended_exit_fee(prior_exit_value: float, final_exit_value: float, limit_fee: float, market_fee: float) -> float:
    """Single exit fee rate giving the exact total of earlier limit exits plus a final market exit."""
    total = prior_exit_value + final_exit_value
    if total <= 0:
        return market_fee
    return (prior_exit_value * limit_fee + final_exit_value * market_fee) / total


def _install_fill_rule() -> None:
    """
    Wraps Backtesting._try_close_open_order (the place where Freqtrade decides that
    an open order fills) for strategies that define `fill_through_pct`:
      - resting limits (entry, tp1, tp2) need the trade-through, not just a touch
      - the order-type fee is written on the trade right before the fill
    Strategy callbacks only get a deep copy of the trade, so this has to happen here.
    """
    try:
        from freqtrade.optimize import backtesting as bt
    except Exception:  # pragma: no cover - freqtrade without optimize extras
        return
    original = bt.Backtesting._try_close_open_order
    if getattr(original, "_asgo_fill_through", False):
        return

    def _try_close_open_order(self, order, trade, current_date, row):
        strat = self.strategy
        pct = getattr(strat, "fill_through_pct", None)
        if order is None or pct is None:
            return original(self, order, trade, current_date, row)
        is_entry = order.ft_order_side == trade.entry_side
        low, high, open_ = row[bt.LOW_IDX], row[bt.HIGH_IDX], row[bt.OPEN_IDX]
        if is_entry or order.ft_order_tag in ("tp1", "tp2"):
            tick = trade.price_precision if trade.precision_mode_price == TICK_SIZE_MODE else 0.0
            buf = trade_through_buffer(order.ft_price, tick, pct)
            if not limit_filled(order.ft_order_side, order.ft_price, low, high, buf):
                return False
        elif not self._get_order_filled(order.ft_price, row):
            return original(self, order, trade, current_date, row)
        # The order fills on this candle: set the fee of its order type first.
        if is_entry:
            placed_now = order.order_date_utc == current_date
            through = open_ <= order.ft_price if order.ft_order_side == "buy" else open_ >= order.ft_price
            taker = placed_now and through
            trade.fee_open = strat.market_cost if taker else strat.limit_cost
            trade.fee_close = strat.limit_cost  # TP orders rest as limits
        elif order.ft_order_tag not in ("tp1", "tp2"):
            prior = sum(o.safe_amount_after_fee * o.safe_price for o in trade.orders
                        if o.ft_order_side == trade.exit_side and not o.ft_is_open and o.filled)
            trade.fee_close = blended_exit_fee(prior, order.safe_amount * order.ft_price,
                                               strat.limit_cost, strat.market_cost)
        return original(self, order, trade, current_date, row)

    _try_close_open_order._asgo_fill_through = True
    bt.Backtesting._try_close_open_order = _try_close_open_order


_install_fill_rule()


class LimitCostMixin:
    """Per-order-type fees and the trade-through fill rule (applied by the backtest wrapper above)."""

    maker_fee = MAKER_FEE
    taker_fee = TAKER_FEE
    market_slippage = MARKET_SLIPPAGE
    fill_through_pct = FILL_THROUGH_PCT
    cost_mult = 1.0

    @property
    def limit_cost(self) -> float:
        return self.cost_mult * self.maker_fee

    @property
    def market_cost(self) -> float:
        return self.cost_mult * (self.taker_fee + self.market_slippage)


class LevelEntryMixin:
    """Entry limit at the broken channel level (zone width 0); stop and targets from that price."""

    def add_plan_columns(self, df: DataFrame) -> DataFrame:
        swings = self.swing_levels(df)
        for side in SIDES:
            level = df["dc_upper"] if side == "long" else df["dc_lower"]
            low, high, mid = tm.entry_zone(side, level, df["atr"], 0.0)
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


class Kirilim1sLimit_B(LimitCostMixin, LevelEntryMixin, Kirilim1s_B):
    """Main version (the card decides on this one): limit at the broken level, 3 candles."""


class Kirilim1sLimit6_B(Kirilim1sLimit_B):
    """Variant (declared on the card): the limit stays 6 candles."""

    mgmt = tm.ManagementParams(valid_for_candles=6)


class Kirilim1sLimitZone_B(LimitCostMixin, Kirilim1s_B):
    """Variant (declared on the card): Kirilim1s_B's own entry price (zone middle), new fee model only."""


class Kirilim1sLimitCost2x_B(Kirilim1sLimit_B):
    """Diagnostic (declared on the card): main version at double costs."""

    cost_mult = 2.0


class Kirilim1sLimitCost0_B(Kirilim1sLimit_B):
    """Diagnostic (declared on the card): main version without fees and slippage (funding stays)."""

    cost_mult = 0.0


class Kirilim1sLimitLowFee_B(Kirilim1sLimit_B):
    """
    Scenario (added at the parent session's request before any result was seen; not used
    for the decision): a low-fee exchange, 0.02 % fee + 0.01 % slippage = 0.03 % flat on
    every order (entry, TP and stop alike). Run with --fee 0.0003.
    """

    @property
    def limit_cost(self) -> float:
        return 0.0003

    @property
    def market_cost(self) -> float:
        return 0.0003
