"""
aslan_liquidity v3: Aslan's rules as corrected on 2026-10-09.
Strategy card: cards/aslan_liquidity.md (section "v3"). Building blocks
(pivots, levels, stop rule, news filter) come from aslan_liquidity.py.

Changes against v1/v2:
1. Liquidity levels: swing highs / lows of 1h, 4h and 1d, previous day high /
   low, and the high / low of each trading session (UTC: Asia 00-07,
   London 07-13, New York 13-21). A session level is usable after the session ends.
2. Two setups when price trades through a level:
   - sweep  : the candle closes back inside (wick only) -> trade the reversal
              (low swept -> long, high swept -> short)
   - break  : a candle closes beyond the level -> trade in the break direction
              (low broken -> short, high broken -> long). A sweep that is later
              closed through within the setup window turns into a break.
   Entry confirmation is the same for both: MSS or iFVG on the entry timeframe
   (15m or 5m) in the trade direction, within `setup_window` candles.
3. Trend ("daily bias") from market structure: a timeframe is up when its last
   confirmed swing high and swing low are higher than the previous ones (HH + HL),
   down on LH + LL, otherwise neutral. Trades only in the trend direction
   (4h trend by default; variants: 4h and 1h both, or no filter).
4. Target 1R (single target), stop at the wick with the 175% wick cap.
"""

import heapq
import sys
from bisect import bisect_left
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import talib.abstract as ta  # noqa: E402
from freqtrade.exchange import timeframe_to_minutes  # noqa: E402
from pandas import DataFrame  # noqa: E402

from strategies.candidates.aslan_liquidity import (  # noqa: E402
    PIVOT_N,
    AslanLiqBase,
    htf_levels,
    pivots,
    stop_from_candle,
)
from strategies.common import news_calendar  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402

MODEL_1R = tm.TPModel(name="ASLAN_1R", tp1_r=1.0, tp2_r=1.0, tp1_close_pct=0, breakeven_trigger="2R")

SESSIONS_UTC = {"asia": (0, 7), "london": (7, 13), "newyork": (13, 21)}
WICK_CAP = 1.75


def session_levels(h1: DataFrame) -> DataFrame:
    """High / low of each session from 1h candles: [avail, price, side]."""
    d = h1.copy()
    d["date"] = pd.to_datetime(d["date"], utc=True)
    hour = d["date"].dt.hour
    rows = []
    for name, (a, b) in SESSIONS_UTC.items():
        part = d[(hour >= a) & (hour < b)]
        g = part.groupby(part["date"].dt.floor("D"))
        agg = g.agg(high=("high", "max"), low=("low", "min"), n=("high", "size"))
        agg = agg[agg["n"] == b - a]  # complete sessions only
        avail = agg.index + pd.Timedelta(hours=b)
        rows.append(DataFrame({"avail": avail, "price": agg["high"].to_numpy(), "side": "high"}))
        rows.append(DataFrame({"avail": avail, "price": agg["low"].to_numpy(), "side": "low"}))
    return pd.concat(rows, ignore_index=True)


def all_levels(h1: DataFrame, h4: DataFrame, d1: DataFrame) -> DataFrame:
    lv = pd.concat(
        [
            htf_levels(d1, 1440, prev_day=True),
            htf_levels(h4, 240),
            htf_levels(h1, 60),
            session_levels(h1),
        ],
        ignore_index=True,
    )
    lv["avail"] = pd.to_datetime(lv["avail"], utc=True).astype("datetime64[ns, UTC]")
    return lv.sort_values("avail", kind="stable").reset_index(drop=True)


def structure_trend(htf: DataFrame, tf_minutes: int) -> DataFrame:
    """+1 (HH+HL) / -1 (LH+LL) / 0, known at each HTF candle close: [avail, trend]."""
    h = htf["high"].to_numpy(float)
    lo = htf["low"].to_numpy(float)
    dates = pd.to_datetime(htf["date"], utc=True).reset_index(drop=True)
    ph, pl = pivots(h, lo)
    highs: list[float] = []
    lows: list[float] = []
    out = np.zeros(len(h), dtype=int)
    for k in range(len(h)):
        j = k - PIVOT_N
        if j >= 0 and ph[j]:
            highs.append(h[j])
        if j >= 0 and pl[j]:
            lows.append(lo[j])
        if len(highs) >= 2 and len(lows) >= 2:
            if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
                out[k] = 1
            elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                out[k] = -1
    avail = (dates + pd.Timedelta(minutes=tf_minutes)).astype("datetime64[ns, UTC]")
    return DataFrame({"avail": avail, "trend": out})


def _confirm(side, k, e, start, o, h, lo, c, ph_idx, pl_idx, fvg_lookback, post_sweep=False):
    """MSS or iFVG in the trade direction at candle k ('' if none).
    post_sweep=True (v6): the inverted gap must have formed at or after the sweep candle,
    and a new FVG in the trade direction formed after the sweep also confirms ('fvg')."""
    if post_sweep:
        fvg_lookback = -2  # first gap candle f - 2 >= start
        if k - 2 >= start and ((side == "long" and lo[k] > h[k - 2]) or (side == "short" and h[k] < lo[k - 2])):
            return "fvg"
    if side == "long":
        pos = bisect_left(ph_idx, e) - 1
        if pos >= 0 and c[k] > h[ph_idx[pos]]:
            return "mss"
        for f in range(max(2, start - fvg_lookback), k):
            top = lo[f - 2]
            if h[f] < top and c[k] > top and c[f + 1:k].max(initial=-np.inf) <= top:
                return "ifvg"
        return ""
    pos = bisect_left(pl_idx, e) - 1
    if pos >= 0 and c[k] < lo[pl_idx[pos]]:
        return "mss"
    for f in range(max(2, start - fvg_lookback), k):
        bottom = h[f - 2]
        if lo[f] > bottom and c[k] < bottom and c[f + 1:k].min(initial=np.inf) >= bottom:
            return "ifvg"
    return ""


def _ob_confirm(side, k, e, o, c, h, lo):
    """Order block: close beyond the last opposite candle at or before the extreme (v5)."""
    for j in range(e, max(-1, e - 20), -1):
        if side == "long" and c[j] < o[j]:
            return c[k] > h[j]
        if side == "short" and c[j] > o[j]:
            return c[k] < lo[j]
    return False


def find_signals_v3(
    df: DataFrame,
    levels: DataFrame,
    setup_window: int,
    fvg_lookback: int = 10,
    allow_break: bool = True,
    use_ob: bool = False,
    stop_buffer_pct: float | None = None,
    post_sweep: bool = False,
) -> DataFrame:
    """
    v5 options: allow_break=False trades sweeps (reversals) only; use_ob=True also
    accepts an order block break as confirmation; stop_buffer_pct puts the stop at
    the sweep extreme plus this buffer instead of the wick-cap rule.

    Per entry-timeframe candle: long_trigger / short_trigger ('mss' / 'ifvg' / ''),
    long_kind / short_kind ('sweep' / 'break'), and the structural stop.
    Uses only data known at each candle's close.
    """
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    t_open = pd.to_datetime(df["date"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]")
    n = len(df)
    ph, pl = pivots(h, lo)
    lv_time = pd.to_datetime(levels["avail"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]")
    lv_price = levels["price"].to_numpy(float)
    lv_side = levels["side"].to_numpy()

    trig = {"long": np.full(n, "", dtype=object), "short": np.full(n, "", dtype=object)}
    kind = {"long": np.full(n, "", dtype=object), "short": np.full(n, "", dtype=object)}
    stop = {"long": np.full(n, np.nan), "short": np.full(n, np.nan)}
    # audit trail of each signal: swept level, candle that took it, extreme candle
    lvl = {"long": np.full(n, np.nan), "short": np.full(n, np.nan)}
    at = {"long": np.full(n, -1), "short": np.full(n, -1)}
    ext = {"long": np.full(n, -1), "short": np.full(n, -1)}

    lows_heap: list[float] = []
    highs_heap: list[float] = []
    ph_idx: list[int] = []
    pl_idx: list[int] = []
    li = 0
    # one open setup per trade direction: dict(start, ext, kind, level)
    setup: dict[str, dict | None] = {"long": None, "short": None}

    def open_setup(side, k, kd, level):
        if kd == "break" and not allow_break:
            return
        setup[side] = {"start": k, "ext": k, "kind": kd, "level": level}

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

        for side in ("long", "short"):
            st = setup[side]
            if st is not None and k - st["start"] > setup_window:
                setup[side] = None

        # a swept level closed through later: the sweep becomes a break
        st = setup["long"]
        if st is not None and st["kind"] == "sweep" and c[k] < st["level"]:
            setup["long"] = None
            open_setup("short", k, "break", st["level"])
        st = setup["short"]
        if st is not None and st["kind"] == "sweep" and c[k] > st["level"]:
            setup["short"] = None
            open_setup("long", k, "break", st["level"])

        taken_low = None
        while lows_heap and -lows_heap[0] > lo[k]:
            p = -heapq.heappop(lows_heap)
            taken_low = p if taken_low is None else taken_low
        if taken_low is not None:
            if c[k] < taken_low:
                open_setup("short", k, "break", taken_low)
            else:
                open_setup("long", k, "sweep", taken_low)
        taken_high = None
        while highs_heap and highs_heap[0] < h[k]:
            p = heapq.heappop(highs_heap)
            taken_high = p if taken_high is None else taken_high
        if taken_high is not None:
            if c[k] > taken_high:
                open_setup("long", k, "break", taken_high)
            else:
                open_setup("short", k, "sweep", taken_high)

        for side in ("long", "short"):
            st = setup[side]
            if st is None:
                continue
            e = st["ext"]
            if (side == "long" and lo[k] < lo[e]) or (side == "short" and h[k] > h[e]):
                st["ext"] = e = k
            t = _confirm(side, k, e, st["start"], o, h, lo, c, ph_idx, pl_idx, fvg_lookback, post_sweep)
            if not t and use_ob and _ob_confirm(side, k, e, o, c, h, lo):
                t = "ob"
            if t:
                trig[side][k] = t
                kind[side][k] = st["kind"]
                lvl[side][k], at[side][k], ext[side][k] = st["level"], st["start"], e
                if stop_buffer_pct is None:
                    stop[side][k] = stop_from_candle(side, o[e], h[e], lo[e], c[e], WICK_CAP)
                elif side == "long":
                    stop[side][k] = lo[e] * (1 - stop_buffer_pct)
                else:
                    stop[side][k] = h[e] * (1 + stop_buffer_pct)
                setup[side] = None

    return DataFrame(
        {
            "long_trigger": trig["long"],
            "short_trigger": trig["short"],
            "long_kind": kind["long"],
            "short_kind": kind["short"],
            "long_struct_stop": stop["long"],
            "short_struct_stop": stop["short"],
            "long_level": lvl["long"],
            "short_level": lvl["short"],
            "long_setup_at": at["long"],
            "short_setup_at": at["short"],
            "long_ext_at": ext["long"],
            "short_ext_at": ext["short"],
        },
        index=df.index,
    )


class AslanLiq3Base(AslanLiqBase):
    timeframe = "15m"
    setup_window = 48  # 12 hours of 15m candles
    startup_candle_count = 800
    trend_filter = "4h"  # "4h", "4h+1h" or "none"
    allow_break = True
    use_ob = False
    stop_buffer_pct: float | None = None
    post_sweep = False
    mgmt = tm.ManagementParams(
        entry_zone_atr=0.0,
        valid_for_candles=2,
        stop_method="structural",
        stop_buffer_atr=0.0,
        max_stop_pct=0.08,
        max_leverage=20.0,
        risk_per_trade=0.01,  # Aslan trades 3-5%; 1% keeps the test account alive for the whole period
    )

    @property
    def tp_model(self) -> tm.TPModel:
        return MODEL_1R

    def informative_pairs(self):
        return [(p, tf) for p in self.dp.current_whitelist() for tf in ("1h", "4h", "1d")]

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        df["atr"] = ta.ATR(df, timeperiod=14)
        h1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1h")
        h4 = self.dp.get_pair_dataframe(pair=pair, timeframe="4h")
        d1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1d")
        sig = find_signals_v3(
            df,
            all_levels(h1, h4, d1),
            self.setup_window,
            allow_break=self.allow_break,
            use_ob=self.use_ob,
            stop_buffer_pct=self.stop_buffer_pct,
            post_sweep=self.post_sweep,
        )
        for col in sig.columns:
            df[col] = sig[col]

        close_time = (
            pd.to_datetime(df["date"], utc=True) + pd.Timedelta(minutes=timeframe_to_minutes(self.timeframe))
        ).astype("datetime64[ns, UTC]")
        base = pd.DataFrame({"avail": close_time}).reset_index()
        for tf, mins in (("4h", 240), ("1h", 60)):
            src = h4 if tf == "4h" else h1
            m = pd.merge_asof(base, structure_trend(src, mins), on="avail", direction="backward").set_index("index")
            df[f"trend_{tf}"] = m["trend"].fillna(0).astype(int)
        df["news_block"] = news_calendar.blocked(close_time, self.news_before, self.news_after)
        return df

    def _trend_ok(self, df: DataFrame, sign: int) -> pd.Series:
        if self.trend_filter == "none":
            return pd.Series(True, index=df.index)
        ok = df["trend_4h"] == sign
        if self.trend_filter == "4h+1h":
            ok &= df["trend_1h"] == sign
        return ok

    def signal_conditions(self, df: DataFrame):
        return {
            "long": {
                "trend_up": self._trend_ok(df, 1),
                "liquidity_taken": df["long_kind"] != "",
                "reversal_mss_or_ifvg": df["long_trigger"].isin(["mss", "ifvg", "fvg"]) & (df["long_struct_stop"] < df["close"]),
                "no_news": ~df["news_block"],
            },
            "short": {
                "trend_down": self._trend_ok(df, -1),
                "liquidity_taken": df["short_kind"] != "",
                "reversal_mss_or_ifvg": df["short_trigger"].isin(["mss", "ifvg", "fvg"]) & (df["short_struct_stop"] > df["close"]),
                "no_news": ~df["news_block"],
            },
        }

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_entry_trend(df, metadata)
        for side in ("long", "short"):
            m = df.get(f"enter_{side}", pd.Series(0, index=df.index)).fillna(0) == 1
            df.loc[m, "enter_tag"] = df.loc[m, "enter_tag"] + " kind=" + df.loc[m, f"{side}_kind"]
        return df


class AslanLiq3_15m(AslanLiq3Base):
    timeframe = "15m"
    setup_window = 48


class AslanLiq3_5m(AslanLiq3Base):
    timeframe = "5m"
    setup_window = 144  # 12 hours of 5m candles
    startup_candle_count = 2400


class AslanLiq3_15m_Trend2(AslanLiq3_15m):
    trend_filter = "4h+1h"


class AslanLiq3_15m_NoTrend(AslanLiq3_15m):
    trend_filter = "none"


class AslanLiq3_5m_Trend2(AslanLiq3_5m):
    trend_filter = "4h+1h"


class AslanLiq3_5m_NoTrend(AslanLiq3_5m):
    trend_filter = "none"


# ---------------------------------------------------------------- v5 (Aslan, 2026-10-09 10:05)
# Sweeps only (reversal), confirmation on 5m / 15m by order block, iFVG or MSS,
# stop a little (0.1%) beyond the high / low that took the liquidity.


class AslanLiq5_15m(AslanLiq3_15m):
    allow_break = False
    use_ob = True
    stop_buffer_pct = 0.001


class AslanLiq5_5m(AslanLiq3_5m):
    allow_break = False
    use_ob = True
    stop_buffer_pct = 0.001


# ---------------------------------------------------------------- v6 (Aslan, 2026-10-09 10:58)
# Confirmation only from what forms after the sweep: a new FVG in the trade
# direction, an iFVG whose gap formed after the sweep, or an MSS. Entry chart
# 5m or 1m. No order block. Stop 0.1% beyond the sweep extreme, 1R target.


class AslanLiq6_5m(AslanLiq3_5m):
    allow_break = False
    stop_buffer_pct = 0.001
    post_sweep = True


class AslanLiq6_1m(AslanLiq6_5m):
    timeframe = "1m"
    setup_window = 720  # 12 hours of 1m candles
    startup_candle_count = 2400  # freqtrade allows at most ~2500 1m candles
