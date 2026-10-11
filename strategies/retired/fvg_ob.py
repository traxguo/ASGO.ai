"""
fvg_ob: 15m market structure shift + order block + 3m fair value gap retest.
Strategy card: cards/fvg_ob.md (condition ids must match the card).
Rules fixed before the first test (2026-10-11).

Entry timeframe 3m; 15m candles are built inside the strategy from the 3m
candles (5 x 3m = 1 x 15m, incomplete groups dropped) and are only used from the
3m candle that closes the 15m candle, so there is no lookahead.

Long (short is the mirror, computed on negated prices):
  1. MSS: a 15m CLOSE above the last confirmed 15m swing high (fractal, 2 candles
     each side, confirmed after the 2 right candles). Each swing breaks once.
  2. origin = lowest-low 15m candle between that swing high and the MSS candle.
     Order block (OB) = the last red 15m candle at or before the origin (after the
     swing high). OB zone = its low..high.
  3. On 3m, the newest bullish FVG (low[i] > high[i-2]) whose three candles lie
     between the OB open and the MSS close and whose gap overlaps the OB zone, and
     whose entry level was not traded again before the signal.
  4. Entry = limit at the FVG 50% level (variant FvgObEdge: near edge = low[i]).
     Stop = OB low * (1 - 0.05%). Target = newest confirmed 15m swing high in the
     last 400 15m candles that price has not traded above since it formed.
     Trade only if (target - entry) / (entry - stop) >= 2.
  5. The limit lives 20 x 3m candles, is cancelled when a closed candle reached
     the target first, and fills only when (a) price trades through it by
     max(1 tick, 0.02%) and (b) the average volume of the closed pullback candles
     (3m candles after the highest high since the leg start, up to the candle before
     the fill candle; at least one) is below the average volume of the expansion
     candles (3m candles from just after the OB to the MSS close).
  6. Single target (resting limit, same trade-through rule, not on the fill
     candle), fixed stop, no break even. 1% risk per trade, leverage <= 10x with
     liquidation >= 2x the stop distance, after 3 losing trades in a row no new
     entries for 24 hours.

Rules (a) and (b) are applied in a small wrapper around
Backtesting._try_close_open_order that only acts on strategies with an
`fvg_fill_rule` attribute (every other strategy keeps Freqtrade's normal rule).
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
from strategies.common.freqtrade_mixin import SIDES, ManagedStrategy  # noqa: E402

FRACTAL_N = 2
HTF_GROUP = 5  # 3m candles per 15m candle
TP_LOOKBACK_15M = 400
STOP_BUFFER = 0.0005
MIN_RR = 2.0
VALID_CANDLES = 20
FILL_THROUGH_PCT = 0.0002
LOSS_STREAK = 3
HALT = timedelta(hours=24)
TICK_SIZE_MODE = 4  # ccxt.TICK_SIZE

SIGNAL_COLS = ("mss", "ob", "fvg", "rr_ok", "entry", "stop", "tp", "rr", "exp_vol", "leg_start",
               "swing", "ob_low", "ob_high", "fvg_low", "fvg_high")


# ------------------------------------------------------------------ 15m frame


def htf_frame(dates: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """First and last 3m row index of every complete 15m group (5 consecutive 3m candles)."""
    d = dates.astype("datetime64[ns]").astype(np.int64)
    step = 15 * 60 * 10**9
    bucket = d // step
    starts = np.flatnonzero(np.r_[True, bucket[1:] != bucket[:-1]])
    ends = np.r_[starts[1:], len(d)] - 1
    complete = (ends - starts + 1) == HTF_GROUP
    # consecutive 3m rows inside the group (no gaps)
    complete &= (d[ends] - d[starts]) == (HTF_GROUP - 1) * 3 * 60 * 10**9
    complete &= (d[starts] % step) == 0
    return starts[complete], ends[complete]


def _setups_one_side(o, h, lo, c, v, d_ns, entry_mode: str) -> dict[str, np.ndarray]:
    """Bullish logic on the given arrays (short side passes negated prices)."""
    n = len(c)
    out = {k: np.full(n, np.nan) for k in SIGNAL_COLS}
    for k in ("mss", "ob", "fvg", "rr_ok"):
        out[k] = np.zeros(n, dtype=bool)
    first, last = htf_frame(d_ns)
    if len(first) < 2 * FRACTAL_N + 2:
        return out
    H = np.array([h[a:b + 1].max() for a, b in zip(first, last)])
    L = np.array([lo[a:b + 1].min() for a, b in zip(first, last)])
    O = o[first]
    C = c[last]
    ph, _ = pivots(H, L, FRACTAL_N)
    # FVG candidates on 3m: gap between high[i-2] and low[i]
    gap_lo = np.full(n, np.nan)
    gap_hi = np.full(n, np.nan)
    if n >= 3:
        is_gap = lo[2:] > h[:-2]
        gap_lo[2:][is_gap] = h[:-2][is_gap]
        gap_hi[2:][is_gap] = lo[2:][is_gap]

    fh: list[int] = []
    used = -1
    nh = len(H)
    for k in range(nh):
        j = k - FRACTAL_N - 1  # confirmed by the close of 15m candle k-1
        if j >= 0 and ph[j]:
            fh.append(j)
        if not fh:
            continue
        sh = fh[-1]
        if sh == used or not C[k] > H[sh]:
            continue
        used = sh
        s = last[k]  # signal row: the 3m candle that closes the MSS 15m candle
        out["mss"][s] = True
        out["swing"][s] = H[sh]
        seg = L[sh + 1:k + 1]
        origin = sh + 1 + int(np.argmin(seg))
        ob = -1
        for i in range(origin, sh, -1):
            if C[i] < O[i]:
                ob = i
                break
        if ob < 0:
            continue
        out["ob"][s] = True
        ob_lo, ob_hi = L[ob], H[ob]
        out["ob_low"][s], out["ob_high"][s] = ob_lo, ob_hi
        leg0 = last[ob] + 1
        out["exp_vol"][s] = v[leg0:s + 1].mean()
        out["leg_start"][s] = d_ns[leg0].astype("datetime64[s]").astype(np.int64)  # seconds (exact in float64)
        # newest FVG inside [OB open, MSS close] overlapping the OB zone, not yet revisited
        entry = np.nan
        for i in range(s, first[ob] + 1, -1):
            gl, gh = gap_lo[i], gap_hi[i]
            if np.isnan(gl) or gl > ob_hi or gh < ob_lo:
                continue
            level = (gl + gh) / 2.0 if entry_mode == "mid" else gh
            if i < s and lo[i + 1:s + 1].min() <= level:
                continue
            entry = level
            out["fvg_low"][s], out["fvg_high"][s] = gl, gh
            break
        if np.isnan(entry):
            continue
        out["fvg"][s] = True
        # target: newest untaken confirmed swing high in the lookback window
        tp = np.nan
        for jj in reversed(fh):
            if jj < k - TP_LOOKBACK_15M:
                break
            if H[jj] > H[jj + 1:k + 1].max():
                tp = H[jj]
                break
        out["entry"][s] = entry
        out["tp"][s] = tp
        out["stop"][s] = ob_lo  # buffer applied by the caller (side dependent)
    return out


def find_setups(df: DataFrame, entry_mode: str = "mid") -> DataFrame:
    """Per 3m row: long_* and short_* setup columns (NaN / False where no setup)."""
    d_ns = pd.to_datetime(df["date"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]")
    o, h, lo, c, v = (df[x].to_numpy(float) for x in ("open", "high", "low", "close", "volume"))
    res = {}
    for side in SIDES:
        if side == "long":
            r = _setups_one_side(o, h, lo, c, v, d_ns, entry_mode)
        else:
            r = _setups_one_side(-o, -lo, -h, -c, v, d_ns, entry_mode)
            for col in ("entry", "stop", "tp", "swing"):
                r[col] = -r[col]
            r["ob_low"], r["ob_high"] = -r["ob_high"], -r["ob_low"]
            r["fvg_low"], r["fvg_high"] = -r["fvg_high"], -r["fvg_low"]
        sign = 1 if side == "long" else -1
        r["stop"] = r["stop"] * (1 - sign * STOP_BUFFER)
        risk = sign * (r["entry"] - r["stop"])
        reward = sign * (r["tp"] - r["entry"])
        with np.errstate(invalid="ignore", divide="ignore"):
            rr = np.where(risk > 0, reward / risk, np.nan)
        r["rr"] = rr
        r["rr_ok"] = r["fvg"] & (risk > 0) & (reward > 0) & (np.nan_to_num(rr, nan=0.0) >= MIN_RR)
        for col, arr in r.items():
            res[f"{side}_{col}"] = arr
    return DataFrame(res, index=df.index)


# ------------------------------------------------------------------ fill rule


def trade_through_buffer(price: float, tick: float, pct: float) -> float:
    return max(tick or 0.0, pct * price)


def limit_filled(order_side: str, price: float, low: float, high: float, buffer: float) -> bool:
    """A buy limit fills when the low trades below it by `buffer`; a sell limit when the high trades above."""
    if order_side == "buy":
        return low <= price - buffer
    return high >= price + buffer


def pullback_volume_ok(side: str, k: int, leg_start: int, high: np.ndarray, low: np.ndarray,
                       cumvol: np.ndarray, exp_vol: float) -> bool:
    """
    k = index of the candle being filled. Pullback candles = closed candles after the
    extreme (highest high for long, lowest low for short) of rows [leg_start, k-1],
    up to k-1. Needs at least one; their mean volume must be below exp_vol.
    """
    if k - 1 < leg_start:
        return False
    seg = high[leg_start:k] if side == "long" else -low[leg_start:k]
    ext = leg_start + len(seg) - 1 - int(np.argmax(seg[::-1]))  # last occurrence of the extreme
    count = (k - 1) - ext
    if count < 1:
        return False
    avg = (cumvol[k] - cumvol[ext + 1]) / count
    return bool(avg < exp_vol)


def loss_streak_halt_until(closed: list[tuple[datetime, float]]) -> datetime | None:
    """closed = [(close_date, profit_abs)] in close order. After LOSS_STREAK losses in a
    row the halt runs HALT from the last loss; the streak then starts again from zero."""
    streak = 0
    until = None
    for close_date, profit in closed:
        if profit < 0:
            streak += 1
            if streak >= LOSS_STREAK:
                until = close_date + HALT
                streak = 0
        else:
            streak = 0
    return until


def _install_fill_rule() -> None:
    try:
        from freqtrade.optimize import backtesting as bt
    except Exception:  # pragma: no cover
        return
    original = bt.Backtesting._try_close_open_order
    if getattr(original, "_asgo_fvg_fill", False):
        return

    def _try_close_open_order(self, order, trade, current_date, row):
        strat = self.strategy
        if order is None or not getattr(strat, "fvg_fill_rule", False):
            return original(self, order, trade, current_date, row)
        is_entry = order.ft_order_side == trade.entry_side
        if is_entry or order.ft_order_tag == "tp":
            tick = trade.price_precision if trade.precision_mode_price == TICK_SIZE_MODE else 0.0
            buf = trade_through_buffer(order.ft_price, tick, strat.fill_through_pct)
            if not limit_filled(order.ft_order_side, order.ft_price, row[bt.LOW_IDX], row[bt.HIGH_IDX], buf):
                return False
            if is_entry and not strat.entry_volume_ok(trade, current_date):
                return False
        return original(self, order, trade, current_date, row)

    _try_close_open_order._asgo_fvg_fill = True
    bt.Backtesting._try_close_open_order = _try_close_open_order


_install_fill_rule()


# ------------------------------------------------------------------ strategy


class FvgOb(ManagedStrategy):
    """Main version (the card decides on this one): limit at the FVG 50% level."""

    timeframe = "3m"
    startup_candle_count = 2400  # 480 x 15m: covers the 400-candle target lookback
    entry_mode = "mid"
    fvg_fill_rule = True
    fill_through_pct = FILL_THROUGH_PCT
    mgmt = tm.ManagementParams(
        entry_zone_atr=0.0,
        valid_for_candles=VALID_CANDLES,
        stop_method="structural",
        max_stop_pct=0.08,
        max_leverage=10.0,
        risk_per_trade=0.01,
    )

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._arrays: dict[str, dict] = {}

    # ---- indicators / signals

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        sig = find_setups(df, self.entry_mode)
        for col in sig.columns:
            df[col] = sig[col]
        vol = df["volume"].to_numpy(float)
        self._arrays[metadata["pair"]] = {
            "date": pd.to_datetime(df["date"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[s]").astype(np.int64),
            "high": df["high"].to_numpy(float),
            "low": df["low"].to_numpy(float),
            "cumvol": np.r_[0.0, np.cumsum(vol)],
        }
        return df

    def add_plan_columns(self, df: DataFrame) -> DataFrame:
        for side in SIDES:
            df[f"{side}_tp1"] = df[f"{side}_tp"]
            df[f"{side}_tp2"] = df[f"{side}_tp"]
            ok = df[f"{side}_rr_ok"].astype(bool)
            stop_pct = (df[f"{side}_entry"] - df[f"{side}_stop"]).abs() / df[f"{side}_entry"]
            df[f"{side}_plan_ok"] = ok & (stop_pct <= self.mgmt.max_stop_pct) & (stop_pct > 0)
        return df

    def signal_conditions(self, df: DataFrame):
        return {
            "long": {
                "mss_up_15m": df["long_mss"],
                "order_block": df["long_ob"],
                "fvg_in_ob": df["long_fvg"],
                "rr_ge_2": df["long_rr_ok"],
            },
            "short": {
                "mss_down_15m": df["short_mss"],
                "order_block": df["short_ob"],
                "fvg_in_ob": df["short_fvg"],
                "rr_ge_2": df["short_rr_ok"],
            },
        }

    # ---- plan

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
            "tp": float(row[f"{side}_tp"]),
            "tp1": float(row[f"{side}_tp"]),
            "tp2": float(row[f"{side}_tp"]),
            "exp_vol": float(row[f"{side}_exp_vol"]),
            "leg_start": int(row[f"{side}_leg_start"]),
        }
        trade.set_custom_data("plan", plan)
        return plan

    def entry_volume_ok(self, trade: Trade, current_date: datetime) -> bool:
        plan = self._plan_for_trade(trade)
        arr = self._arrays.get(trade.pair)
        if plan is None or arr is None:
            return False
        t = pd.Timestamp(current_date)
        t = (t.tz_convert(None) if t.tzinfo else t).value // 10**9
        k = int(np.searchsorted(arr["date"], t, side="right")) - 1
        ls = int(np.searchsorted(arr["date"], plan["leg_start"], side="left"))
        return pullback_volume_ok(plan["side"], k, ls, arr["high"], arr["low"], arr["cumvol"], plan["exp_vol"])

    # ---- callbacks

    def confirm_trade_entry(self, pair, order_type, amount, rate, time_in_force, current_time,
                            entry_tag, side, **kwargs) -> bool:
        closed = Trade.get_trades_proxy(is_open=False)
        rows = sorted(((t.close_date_utc, t.close_profit_abs or 0.0) for t in closed if t.close_date_utc),
                      key=lambda x: x[0])
        until = loss_streak_halt_until(rows)
        return not (until is not None and current_time < until)

    def check_entry_timeout(self, pair, trade, order, current_time, **kwargs) -> bool:
        """Cancel the pending entry once a closed candle has reached the target (target side first)."""
        plan = self._plan_for_trade(trade)
        last = self._last_row(pair)
        if plan is None or last is None:
            return False
        if last["date"] < self._signal_time_for_trade(trade) + timedelta(minutes=3):
            return False
        if trade.is_short:
            return bool(last["low"] <= plan["tp"])
        return bool(last["high"] >= plan["tp"])

    def custom_stoploss(self, pair, trade, current_time, current_rate, current_profit, after_fill, **kwargs):
        plan = self._plan_for_trade(trade)
        if plan is None:
            return None
        return stoploss_from_absolute(plan["stop"], current_rate, is_short=trade.is_short, leverage=trade.leverage)

    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, min_stake, max_stake, **kwargs):
        """Single target as a resting limit order, placed from the candle after the fill candle."""
        if trade.has_open_orders:
            return None
        entry = trade.select_filled_orders(trade.entry_side)
        if not entry:
            return None
        filled = entry[0].order_filled_utc
        if filled is not None and current_time < filled + timedelta(minutes=3):
            return None
        return -trade.stake_amount, "tp"

    def custom_exit_price(self, pair, trade, current_time, proposed_rate, current_profit, exit_tag, **kwargs) -> float:
        plan = self._plan_for_trade(trade)
        if plan is not None and exit_tag == "tp":
            return plan["tp"]
        return proposed_rate


class FvgObEdge(FvgOb):
    """Variant (declared on the card): limit at the near edge of the FVG."""

    entry_mode = "edge"


class FvgObLookahead(FvgOb):
    """
    Only for freqtrade lookahead-analysis (not a variant): that tool forces a 1e9 wallet,
    where the 1%-risk size exceeds the exchange limits and every entry is skipped.
    Same signals and orders; position size = Freqtrade's fixed stake, no loss-streak halt
    (lookahead-analysis disables protections too).
    """

    def custom_stake_amount(self, pair, current_time, current_rate, proposed_stake, min_stake, max_stake,
                            leverage, entry_tag, side, **kwargs) -> float:
        return proposed_stake

    def confirm_trade_entry(self, *args, **kwargs) -> bool:
        return True
