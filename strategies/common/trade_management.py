"""
Shared trade management rules (PROJECT_BRIEF section 7.1 - 7.6).

Every strategy, the backtest, the dry-run and the signal message use these
functions, so the numbers in a signal are always the numbers that were tested.

All price functions work on plain floats AND on numpy arrays / pandas Series,
so the same code can be used vectorised inside populate_entry_trend and on
single values inside Freqtrade callbacks.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

import numpy as np

Side = Literal["long", "short"]


# ---------------------------------------------------------------------------
# TP models (section 7.3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TPModel:
    """A 2-TP exit model. Distances are multiples of R (risk unit)."""

    name: str
    tp1_r: float
    tp2_r: float
    tp1_close_pct: float  # 0 = Model A (no partial exit), 50 = Model B
    breakeven_trigger: Literal["TP1", "2R"]

    def __post_init__(self) -> None:
        if self.tp1_r < 1.0:
            raise ValueError("TP1 can never be smaller than 1R (brief 7.3)")
        # A single-target model (no partial exit) may put its only target at TP1.
        single_target = self.tp1_close_pct == 0 and self.tp2_r == self.tp1_r
        if self.tp2_r <= self.tp1_r and not single_target:
            raise ValueError("TP2 must be further away than TP1")
        if not 0 <= self.tp1_close_pct < 100:
            raise ValueError("tp1_close_pct must be in [0, 100)")

    @property
    def breakeven_r(self) -> float:
        """Profit (in R) at which the stop moves to entry."""
        return self.tp1_r if self.breakeven_trigger == "TP1" else 2.0

    def to_dict(self) -> dict:
        return asdict(self)


# Default model: partial exit at TP1, stop to break even, rest at TP2.
MODEL_B = TPModel(name="B", tp1_r=2.0, tp2_r=4.0, tp1_close_pct=50, breakeven_trigger="TP1")
# Comparison model: single exit at 4R, stop to break even after 2R profit.
MODEL_A = TPModel(name="A", tp1_r=2.0, tp2_r=4.0, tp1_close_pct=0, breakeven_trigger="2R")

TP_MODELS = {"A": MODEL_A, "B": MODEL_B}


def tp_variant_grid() -> list[TPModel]:
    """The fixed, limited variant grid of brief 7.3. Do not extend it."""
    grid = []
    for tp1 in (1.5, 2.0):
        for tp2 in (3.0, 4.0):
            for pct in (0, 50):
                for be in ("TP1", "2R"):
                    name = f"tp1={tp1}_tp2={tp2}_pct={pct}_be={be}"
                    grid.append(TPModel(name, tp1, tp2, pct, be))  # type: ignore[arg-type]
    return grid


# ---------------------------------------------------------------------------
# Default rule parameters. Strategy cards may override them explicitly.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ManagementParams:
    entry_zone_atr: float = 0.25  # zone width in ATR (7.1)
    valid_for_candles: int = 3  # signal is cancelled after N candles (7.1)
    stop_atr: float = 1.5  # ATR stop distance (7.2)
    stop_buffer_atr: float = 0.1  # buffer beyond swing level for structural stop
    stop_method: Literal["atr", "structural", "wider"] = "wider"
    max_stop_pct: float = 0.08  # no signal if stop is further than 8% of price (7.2)
    max_leverage: float = 3.0  # (7.6)
    liq_stop_multiple: float = 2.0  # liquidation must be >= 2x stop distance away (7.6)
    maintenance_margin: float = 0.005  # conservative MMR estimate for liquidation estimate
    risk_per_trade: float = 0.01  # 1% of equity risked per trade (section 10)
    breakeven_buffer_pct: float = 0.0015  # covers fees + some funding when stop goes to entry


DEFAULT_PARAMS = ManagementParams()


def _sign(side: Side) -> int:
    return 1 if side == "long" else -1


# ---------------------------------------------------------------------------
# 7.1 Entry zone
# ---------------------------------------------------------------------------


def entry_zone(side: Side, close, atr, width_atr: float = DEFAULT_PARAMS.entry_zone_atr):
    """
    Entry zone between the signal candle close and close -/+ width_atr * ATR.
    Long: zone below close (we buy a small pullback). Short: zone above close.
    Returns (low, high, mid).
    """
    edge = close - _sign(side) * width_atr * atr
    low = np.minimum(close, edge)
    high = np.maximum(close, edge)
    mid = (low + high) / 2.0
    return low, high, mid


# ---------------------------------------------------------------------------
# 7.2 Stop
# ---------------------------------------------------------------------------


def stop_price(
    side: Side,
    entry_mid,
    atr,
    swing_level=None,
    params: ManagementParams = DEFAULT_PARAMS,
):
    """
    Stop level.
    - atr:        entry_mid -/+ stop_atr * ATR
    - structural: beyond the last swing low (long) / swing high (short) + buffer
    - wider:      the further of the two (gives the trade more room; default)
    """
    s = _sign(side)
    atr_stop = entry_mid - s * params.stop_atr * atr
    if params.stop_method == "atr" or swing_level is None:
        return atr_stop
    structural = swing_level - s * params.stop_buffer_atr * atr
    if params.stop_method == "structural":
        return structural
    # "wider": long -> lower of the two, short -> higher of the two
    return np.minimum(atr_stop, structural) if side == "long" else np.maximum(atr_stop, structural)


def stop_reason(side: Side, entry_mid, atr, swing_level, params: ManagementParams = DEFAULT_PARAMS) -> str:
    """Which rule produced the stop (for the explanation text)."""
    if params.stop_method == "atr" or swing_level is None:
        return "atr"
    if params.stop_method == "structural":
        return "below_swing_low" if side == "long" else "above_swing_high"
    s = _sign(side)
    atr_stop = entry_mid - s * params.stop_atr * atr
    structural = swing_level - s * params.stop_buffer_atr * atr
    structural_wider = structural < atr_stop if side == "long" else structural > atr_stop
    if structural_wider:
        return "below_swing_low" if side == "long" else "above_swing_high"
    return "atr"


def risk_r(entry_mid, stop):
    """Risk unit R = distance between entry zone middle and stop."""
    return np.abs(entry_mid - stop)


# ---------------------------------------------------------------------------
# 7.3 Targets
# ---------------------------------------------------------------------------


def targets(side: Side, entry_mid, stop, model: TPModel):
    """Returns (tp1, tp2) prices."""
    r = risk_r(entry_mid, stop)
    s = _sign(side)
    return entry_mid + s * model.tp1_r * r, entry_mid + s * model.tp2_r * r


# ---------------------------------------------------------------------------
# 7.5 Break even
# ---------------------------------------------------------------------------


def breakeven_stop(side: Side, entry_price: float, params: ManagementParams = DEFAULT_PARAMS) -> float:
    """Stop moved to entry plus a small buffer that covers fees and funding."""
    return entry_price * (1 + _sign(side) * params.breakeven_buffer_pct)


# ---------------------------------------------------------------------------
# 7.6 Leverage and liquidation
# ---------------------------------------------------------------------------


def liquidation_price_est(side: Side, entry: float, leverage: float, mmr: float) -> float:
    """
    Simplified isolated-margin liquidation estimate (ignores fees/funding,
    therefore slightly optimistic; the 2x safety rule compensates for that).
    """
    if side == "long":
        return entry * (1 - 1 / leverage + mmr)
    return entry * (1 + 1 / leverage - mmr)


def safe_leverage(side: Side, entry: float, stop: float, params: ManagementParams = DEFAULT_PARAMS) -> float | None:
    """
    Highest leverage (<= max_leverage, whole steps) for which the liquidation
    price is at least liq_stop_multiple * stop distance away from entry.
    Returns None when even 1x does not satisfy the rule.
    """
    stop_dist = abs(entry - stop)
    lev = float(int(params.max_leverage))
    while lev >= 1.0:
        liq = liquidation_price_est(side, entry, lev, params.maintenance_margin)
        if abs(entry - liq) >= params.liq_stop_multiple * stop_dist:
            return lev
        lev -= 1.0
    return None


# ---------------------------------------------------------------------------
# Section 10: position size from R
# ---------------------------------------------------------------------------


def position_notional(equity: float, entry: float, stop: float, params: ManagementParams = DEFAULT_PARAMS) -> float:
    """Notional size so that hitting the stop loses risk_per_trade of equity."""
    stop_pct = abs(entry - stop) / entry
    if stop_pct <= 0:
        return 0.0
    return equity * params.risk_per_trade / stop_pct


# ---------------------------------------------------------------------------
# Full plan for one signal
# ---------------------------------------------------------------------------


@dataclass
class TradePlan:
    side: Side
    zone_low: float
    zone_high: float
    entry: float  # zone middle = limit price used in backtest
    stop: float
    risk_r: float
    tp1: float
    tp2: float
    leverage: float
    liquidation_price_est: float
    stop_reason: str
    model: TPModel
    valid_for_candles: int


def build_plan(
    side: Side,
    close: float,
    atr: float,
    swing_level: float | None,
    model: TPModel,
    params: ManagementParams = DEFAULT_PARAMS,
) -> tuple[TradePlan | None, str]:
    """
    Builds the full trade plan for one signal, or returns (None, reason) if the
    rules say no signal may be produced (stop too far, liquidation too close).
    """
    low, high, mid = entry_zone(side, close, atr, params.entry_zone_atr)
    stop = float(stop_price(side, mid, atr, swing_level, params))
    if abs(mid - stop) / mid > params.max_stop_pct:
        return None, "stop_too_far"
    lev = safe_leverage(side, mid, stop, params)
    if lev is None:
        return None, "liquidation_too_close"
    tp1, tp2 = targets(side, mid, stop, model)
    plan = TradePlan(
        side=side,
        zone_low=float(low),
        zone_high=float(high),
        entry=float(mid),
        stop=stop,
        risk_r=float(risk_r(mid, stop)),
        tp1=float(tp1),
        tp2=float(tp2),
        leverage=lev,
        liquidation_price_est=liquidation_price_est(side, mid, lev, params.maintenance_margin),
        stop_reason=stop_reason(side, mid, atr, swing_level, params),
        model=model,
        valid_for_candles=params.valid_for_candles,
    )
    return plan, "ok"


# ---------------------------------------------------------------------------
# Reference simulator (used by tests, independent of Freqtrade)
# ---------------------------------------------------------------------------


def simulate_plan(plan: TradePlan, highs, lows) -> dict:
    """
    Walks candles AFTER the signal candle and returns the outcome in R
    (before costs). Pessimistic: when stop and a target are inside the same
    candle, the stop is assumed to be hit first.

    Returns {"status": "cancelled"|"stop"|"breakeven"|"tp2"|"open", "r": float}
    """
    s = _sign(plan.side)
    m = plan.model
    filled = False
    tp1_done = False
    be_active = False
    current_stop = plan.stop
    realized = 0.0
    remaining = 1.0
    for i, (h, lo) in enumerate(zip(highs, lows)):
        best, worst = (h, lo) if s == 1 else (lo, h)
        if not filled:
            if i >= plan.valid_for_candles:
                return {"status": "cancelled", "r": 0.0}
            hit_stop_first = (worst <= plan.stop) if s == 1 else (worst >= plan.stop)
            touched = lo <= plan.entry <= h
            if hit_stop_first and not touched:
                return {"status": "cancelled", "r": 0.0}
            if not touched:
                continue
            filled = True
        # stop first (pessimistic)
        stop_hit = (worst <= current_stop) if s == 1 else (worst >= current_stop)
        if stop_hit:
            r_at_stop = s * (current_stop - plan.entry) / plan.risk_r
            realized += remaining * r_at_stop
            return {"status": "breakeven" if be_active else "stop", "r": realized}
        move_r = s * (best - plan.entry) / plan.risk_r
        if not tp1_done and m.tp1_close_pct > 0 and move_r >= m.tp1_r:
            part = m.tp1_close_pct / 100
            realized += part * m.tp1_r
            remaining -= part
            tp1_done = True
        if not be_active and move_r >= m.breakeven_r:
            be_active = True
            current_stop = plan.entry
        if move_r >= m.tp2_r:
            realized += remaining * m.tp2_r
            return {"status": "tp2", "r": realized}
    return {"status": "open" if filled else "pending", "r": realized}
