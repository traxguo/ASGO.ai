"""
aslan_liquidity: Aslan's liquidity sweep strategy (ICT / smart money style).
Strategy card: cards/aslan_liquidity.md (condition ids below must match the card).

1. Liquidity levels from the 1d and 4h charts: swing highs / lows (a candle with
   2 lower highs / higher lows on each side) and the previous day high / low.
   A level is usable only after it is confirmed (no lookahead) and is used once.
2. Daily bias: bullish after a daily close above the last confirmed daily swing
   high, bearish after a daily close below the last confirmed daily swing low.
   Trades only in the bias direction.
3. Long: price takes a sell-side level (trades below a liquidity low). Within
   `setup_window` entry-timeframe candles, a reversal confirms with either
     - MSS : close above the last entry-timeframe swing high before the sweep low
     - iFVG: close above a bearish fair value gap formed since the sweep move
   Short is the mirror image.
4. Stop at the wick of the most extreme candle of the sweep. When that wick is
   longer than the candle body, the stop goes to the body end instead.
5. One target at 2R, no break even. Entry: limit at the signal candle close.
6. No new trade from 1h before to 1h after a high-impact US news event
   (FOMC, CPI, NFP; strategies/common/news_calendar.py).
"""

import heapq
import sys
from bisect import bisect_left
from datetime import timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import talib.abstract as ta  # noqa: E402
from freqtrade.exchange import timeframe_to_minutes  # noqa: E402
from pandas import DataFrame  # noqa: E402

from strategies.common import news_calendar  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402
from strategies.common.freqtrade_mixin import ManagedStrategy  # noqa: E402

# Single 2R target, no partial exit; break even would only trigger at 2R = target.
MODEL_ASLAN = tm.TPModel(name="ASLAN_2R", tp1_r=1.0, tp2_r=2.0, tp1_close_pct=0, breakeven_trigger="2R")

PIVOT_N = 2  # candles on each side of a swing point


# ---------------------------------------------------------------- building blocks


def pivots(high: np.ndarray, low: np.ndarray, n: int = PIVOT_N) -> tuple[np.ndarray, np.ndarray]:
    """Boolean arrays: swing high / swing low at index i (known only after candle i+n closes)."""
    size = len(high)
    ph = np.zeros(size, dtype=bool)
    pl = np.zeros(size, dtype=bool)
    for i in range(n, size - n):
        h, lo = high[i], low[i]
        if h > high[i - n:i].max() and h >= high[i + 1:i + n + 1].max():
            ph[i] = True
        if lo < low[i - n:i].min() and lo <= low[i + 1:i + n + 1].min():
            pl[i] = True
    return ph, pl


def htf_levels(htf: DataFrame, tf_minutes: int, prev_day: bool = False) -> DataFrame:
    """Liquidity levels of one higher timeframe: [avail (UTC ns), price, side 'high'|'low']."""
    h = htf["high"].to_numpy(float)
    lo = htf["low"].to_numpy(float)
    dates = pd.to_datetime(htf["date"], utc=True).reset_index(drop=True)
    ph, pl = pivots(h, lo)
    step = pd.Timedelta(minutes=tf_minutes)
    rows = []
    for i in np.flatnonzero(ph):
        if i + PIVOT_N < len(dates):
            rows.append((dates[i + PIVOT_N] + step, h[i], "high"))
    for i in np.flatnonzero(pl):
        if i + PIVOT_N < len(dates):
            rows.append((dates[i + PIVOT_N] + step, lo[i], "low"))
    if prev_day:
        for i in range(len(dates)):
            rows.append((dates[i] + step, h[i], "high"))
            rows.append((dates[i] + step, lo[i], "low"))
    out = DataFrame(rows, columns=["avail", "price", "side"])
    return out.sort_values("avail").reset_index(drop=True)


def daily_bias(daily: DataFrame) -> DataFrame:
    """Daily bias +1 / -1 / 0 with the time it becomes known: [avail, bias]."""
    h = daily["high"].to_numpy(float)
    lo = daily["low"].to_numpy(float)
    c = daily["close"].to_numpy(float)
    dates = pd.to_datetime(daily["date"], utc=True).reset_index(drop=True)
    ph, pl = pivots(h, lo)
    last_high = np.nan
    last_low = np.nan
    bias = 0
    out = np.zeros(len(c), dtype=int)
    for k in range(len(c)):
        j = k - PIVOT_N  # swing points confirmed by the close of candle k
        if j >= 0 and ph[j]:
            last_high = h[j]
        if j >= 0 and pl[j]:
            last_low = lo[j]
        if not np.isnan(last_high) and c[k] > last_high:
            bias = 1
        elif not np.isnan(last_low) and c[k] < last_low:
            bias = -1
        out[k] = bias
    avail = (dates + pd.Timedelta(days=1)).astype("datetime64[ns, UTC]")
    return DataFrame({"avail": avail, "bias": out})


def stop_from_candle(side: str, o: float, h: float, lo: float, c: float) -> float:
    """Wick of the extreme candle; body end when the wick is longer than the body."""
    body = abs(c - o)
    if side == "long":
        wick = min(o, c) - lo
        return min(o, c) if wick > body else lo
    wick = h - max(o, c)
    return max(o, c) if wick > body else h


def find_signals(
    df: DataFrame,
    levels: DataFrame,
    setup_window: int,
    fvg_lookback: int = 10,
) -> DataFrame:
    """
    Walks the entry-timeframe candles in order and returns, per candle, the
    sweep -> MSS / iFVG signals. Uses only data known at each candle's close.
    Columns: sweep_low_setup, sweep_high_setup, long_trigger, short_trigger
    ('mss' / 'ifvg' / ''), long_struct_stop, short_struct_stop.
    """
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    t_open = pd.to_datetime(df["date"], utc=True).to_numpy(dtype="datetime64[ns]")
    n = len(df)
    ph, pl = pivots(h, lo)

    lv_time = pd.to_datetime(levels["avail"], utc=True).dt.tz_localize(None).to_numpy(dtype="datetime64[ns]")
    lv_price = levels["price"].to_numpy(float)
    lv_side = levels["side"].to_numpy()

    long_trig = np.full(n, "", dtype=object)
    short_trig = np.full(n, "", dtype=object)
    long_stop = np.full(n, np.nan)
    short_stop = np.full(n, np.nan)
    in_long_setup = np.zeros(n, dtype=bool)
    in_short_setup = np.zeros(n, dtype=bool)

    lows_heap: list[float] = []  # max-heap (negated) of untaken sell-side levels
    highs_heap: list[float] = []  # min-heap of untaken buy-side levels
    ph_idx: list[int] = []
    pl_idx: list[int] = []
    li = 0
    # setup state per side: None or dict(start, ext)
    setup = {"long": None, "short": None}

    for k in range(n):
        while li < len(lv_time) and lv_time[li] <= t_open[k]:
            if lv_side[li] == "low":
                heapq.heappush(lows_heap, -lv_price[li])
            else:
                heapq.heappush(highs_heap, lv_price[li])
            li += 1
        j = k - PIVOT_N
        if j >= 0 and ph[j]:
            ph_idx.append(j)
        if j >= 0 and pl[j]:
            pl_idx.append(j)

        swept_low = False
        while lows_heap and -lows_heap[0] > lo[k]:
            heapq.heappop(lows_heap)
            swept_low = True
        swept_high = False
        while highs_heap and highs_heap[0] < h[k]:
            heapq.heappop(highs_heap)
            swept_high = True

        for side, swept in (("long", swept_low), ("short", swept_high)):
            st = setup[side]
            if st is not None and k - st["start"] > setup_window:
                st = setup[side] = None
            if swept:
                if st is None:
                    st = setup[side] = {"start": k, "ext": k}
                else:
                    st["start"] = k
            if st is None:
                continue
            e = st["ext"]
            if (side == "long" and lo[k] < lo[e]) or (side == "short" and h[k] > h[e]):
                st["ext"] = e = k
            (in_long_setup if side == "long" else in_short_setup)[k] = True

            trig = ""
            if side == "long":
                pos = bisect_left(ph_idx, e) - 1
                if pos >= 0 and c[k] > h[ph_idx[pos]]:
                    trig = "mss"
                else:
                    for f in range(max(2, st["start"] - fvg_lookback), k):
                        top = lo[f - 2]
                        if h[f] < top and c[k] > top and c[f + 1:k].max(initial=-np.inf) <= top:
                            trig = "ifvg"
                            break
                if trig:
                    long_trig[k] = trig
                    long_stop[k] = stop_from_candle("long", o[e], h[e], lo[e], c[e])
            else:
                pos = bisect_left(pl_idx, e) - 1
                if pos >= 0 and c[k] < lo[pl_idx[pos]]:
                    trig = "mss"
                else:
                    for f in range(max(2, st["start"] - fvg_lookback), k):
                        bottom = h[f - 2]
                        if lo[f] > bottom and c[k] < bottom and c[f + 1:k].min(initial=np.inf) >= bottom:
                            trig = "ifvg"
                            break
                if trig:
                    short_trig[k] = trig
                    short_stop[k] = stop_from_candle("short", o[e], h[e], lo[e], c[e])
            if trig:
                setup[side] = None  # one entry per sweep

    return DataFrame(
        {
            "sweep_low_setup": in_long_setup,
            "sweep_high_setup": in_short_setup,
            "long_trigger": long_trig,
            "short_trigger": short_trig,
            "long_struct_stop": long_stop,
            "short_struct_stop": short_stop,
        },
        index=df.index,
    )


# ---------------------------------------------------------------- strategies


class AslanLiqBase(ManagedStrategy):
    timeframe = "1h"
    setup_window = 12  # entry-timeframe candles = 12 hours
    startup_candle_count = 200  # also 200 daily / 4h candles for levels and bias
    news_before = timedelta(hours=1)
    news_after = timedelta(hours=1)
    use_news_filter = True
    mgmt = tm.ManagementParams(
        entry_zone_atr=0.0,  # limit at the signal candle close
        valid_for_candles=2,
        stop_method="structural",
        stop_buffer_atr=0.0,
        max_stop_pct=0.08,
        max_leverage=20.0,  # tight stops; liquidation stays >= 2x stop distance away
        risk_per_trade=0.03,  # Aslan: 3-5% of equity per trade
    )

    @property
    def tp_model(self) -> tm.TPModel:
        return MODEL_ASLAN

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        return [(p, tf) for p in pairs for tf in ("4h", "1d")]

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        df["atr"] = ta.ATR(df, timeperiod=14)
        d1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1d")
        h4 = self.dp.get_pair_dataframe(pair=pair, timeframe="4h")
        levels = pd.concat(
            [htf_levels(d1, 1440, prev_day=True), htf_levels(h4, 240)], ignore_index=True
        ).sort_values("avail", kind="stable")
        sig = find_signals(df, levels, self.setup_window)
        for col in sig.columns:
            df[col] = sig[col]

        # Daily bias known at this candle's close.
        bias = daily_bias(d1)
        close_time = (
            pd.to_datetime(df["date"], utc=True) + pd.Timedelta(minutes=timeframe_to_minutes(self.timeframe))
        ).astype("datetime64[ns, UTC]")
        merged = pd.merge_asof(
            pd.DataFrame({"t": close_time}).reset_index(), bias.rename(columns={"avail": "t"}), on="t", direction="backward"
        ).set_index("index")
        df["daily_bias"] = merged["bias"].fillna(0).astype(int)

        if self.use_news_filter:
            df["news_block"] = news_calendar.blocked(close_time, self.news_before, self.news_after)
        else:
            df["news_block"] = False
        return df

    def swing_levels(self, df: DataFrame):
        return {"long": df["long_struct_stop"], "short": df["short_struct_stop"]}

    def signal_conditions(self, df: DataFrame):
        stop_ok_long = df["long_struct_stop"] < df["close"]
        stop_ok_short = df["short_struct_stop"] > df["close"]
        return {
            "long": {
                "bias_up": df["daily_bias"] == 1,
                "liquidity_swept_low": df["long_trigger"] != "",
                "reversal_mss_or_ifvg": df["long_trigger"].isin(["mss", "ifvg"]) & stop_ok_long,
                "no_news": ~df["news_block"],
            },
            "short": {
                "bias_down": df["daily_bias"] == -1,
                "liquidity_swept_high": df["short_trigger"] != "",
                "reversal_mss_or_ifvg": df["short_trigger"].isin(["mss", "ifvg"]) & stop_ok_short,
                "no_news": ~df["news_block"],
            },
        }


class AslanLiq_1h(AslanLiqBase):
    timeframe = "1h"
    setup_window = 12


class AslanLiq_15m(AslanLiqBase):
    timeframe = "15m"
    setup_window = 48
    startup_candle_count = 800  # 800 x 15m; levels/bias get 800 daily / 4h candles of history


class AslanLiq_1h_NoNews(AslanLiq_1h):
    """Same as AslanLiq_1h without the news filter, to measure the filter's effect."""

    use_news_filter = False
