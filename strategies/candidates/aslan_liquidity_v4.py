"""
aslan_liquidity v4: pullback into a point of interest, then mini structure
break + engulfing candle (from the video checklist the owner sent, 2026-10-09):
  1- daily bias   2- trend   3- FVG / iFVG / liquidity / order block   4- mini structure point + engulf
Strategy card: cards/aslan_liquidity.md (section "v4").

1. Daily bias: 1d market structure (HH+HL up, LH+LL down; structure_trend).
2. Trend: 4h market structure in the same direction.
3. Points of interest (POI) from the 1h chart, usable after the candle that
   completes them closes:
   - FVG     : bullish gap low[i] > high[i-2] -> zone [high[i-2], low[i]]
   - OB      : order block = the last bearish candle (i-1 or i-2) before that
               bullish gap -> zone [its low, its high]
   - iFVG    : a bearish gap that a later 1h candle closes above -> zone of that gap
   Bearish zones are the mirror image. A zone is dropped after a close beyond
   it (long zone: close below its bottom) or after 5 days; it is used once.
4. Entry: price touches the zone, then within `setup_window` entry-timeframe
   candles an engulfing candle in the trade direction closes beyond the last
   mini swing point (1 candle each side). Entry at that close.
   Stop at the extreme since the touch (wick cap 175%). Target 1R (2R variant).
Liquidity sweeps (item 3) were tested in v1-v3 and are not repeated here.
"""

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

from strategies.candidates.aslan_liquidity import pivots, stop_from_candle  # noqa: E402
from strategies.candidates.aslan_liquidity_v3 import MODEL_1R, WICK_CAP, AslanLiq3Base, structure_trend  # noqa: E402
from strategies.common import news_calendar  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402

MODEL_2R = tm.TPModel(name="ASLAN_2R_SINGLE", tp1_r=2.0, tp2_r=2.0, tp1_close_pct=0, breakeven_trigger="2R")
ZONE_MAX_AGE = pd.Timedelta(days=5)


def poi_zones(h1: DataFrame) -> DataFrame:
    """FVG, order block and iFVG zones from 1h candles: [avail, bottom, top, side, kind]."""
    o = h1["open"].to_numpy(float)
    h = h1["high"].to_numpy(float)
    lo = h1["low"].to_numpy(float)
    c = h1["close"].to_numpy(float)
    close_t = (pd.to_datetime(h1["date"], utc=True) + pd.Timedelta(hours=1)).reset_index(drop=True)
    rows = []
    open_bear_gaps: list[tuple[float, float]] = []  # (bottom, top) waiting for inversion
    open_bull_gaps: list[tuple[float, float]] = []
    for i in range(2, len(h)):
        t = close_t[i]
        # inversions first: gaps formed earlier, closed through by this candle
        still = []
        for b, tp in open_bear_gaps:
            if c[i] > tp:
                rows.append((t, b, tp, "long", "ifvg"))
            else:
                still.append((b, tp))
        open_bear_gaps = still[-20:]
        still = []
        for b, tp in open_bull_gaps:
            if c[i] < b:
                rows.append((t, b, tp, "short", "ifvg"))
            else:
                still.append((b, tp))
        open_bull_gaps = still[-20:]

        if lo[i] > h[i - 2]:  # bullish FVG
            rows.append((t, h[i - 2], lo[i], "long", "fvg"))
            open_bull_gaps.append((h[i - 2], lo[i]))
            for j in (i - 1, i - 2):
                if c[j] < o[j]:
                    rows.append((t, lo[j], h[j], "long", "ob"))
                    break
        if h[i] < lo[i - 2]:  # bearish FVG
            rows.append((t, h[i], lo[i - 2], "short", "fvg"))
            open_bear_gaps.append((h[i], lo[i - 2]))
            for j in (i - 1, i - 2):
                if c[j] > o[j]:
                    rows.append((t, lo[j], h[j], "short", "ob"))
                    break
    z = DataFrame(rows, columns=["avail", "bottom", "top", "side", "kind"])
    z["avail"] = pd.to_datetime(z["avail"], utc=True).astype("datetime64[ns, UTC]")
    return z.sort_values("avail", kind="stable").reset_index(drop=True)


def find_signals_v4(df: DataFrame, zones: DataFrame, setup_window: int) -> DataFrame:
    """Per entry-timeframe candle: long/short trigger ('engulf' or ''), POI kind, stop."""
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    t_open = pd.to_datetime(df["date"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]")
    n = len(df)
    mph, mpl = pivots(h, lo, n=1)  # mini structure points

    z_t = pd.to_datetime(zones["avail"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]")
    z_b = zones["bottom"].to_numpy(float)
    z_tp = zones["top"].to_numpy(float)
    z_side = zones["side"].to_numpy()
    z_kind = zones["kind"].to_numpy()
    max_age = np.timedelta64(ZONE_MAX_AGE)

    trig = {s: np.full(n, "", dtype=object) for s in ("long", "short")}
    kind = {s: np.full(n, "", dtype=object) for s in ("long", "short")}
    stop = {s: np.full(n, np.nan) for s in ("long", "short")}
    active = {"long": [], "short": []}  # [avail, bottom, top, kind]
    setup = {"long": None, "short": None}
    mph_idx: list[int] = []
    mpl_idx: list[int] = []
    zi = 0

    for k in range(n):
        while zi < len(z_t) and z_t[zi] <= t_open[k]:
            active[z_side[zi]].append([z_t[zi], z_b[zi], z_tp[zi], z_kind[zi]])
            zi += 1
        if k >= 1 and mph[k - 1]:
            mph_idx.append(k - 1)
        if k >= 1 and mpl[k - 1]:
            mpl_idx.append(k - 1)

        for side in ("long", "short"):
            st = setup[side]
            if st is not None and k - st["start"] > setup_window:
                setup[side] = None
            keep = []
            touched = None
            for z in active[side]:
                if t_open[k] - z[0] > max_age:
                    continue
                if side == "long":
                    if c[k] < z[1]:
                        continue  # closed below the zone: invalid
                    if lo[k] <= z[2]:
                        touched = z
                        continue  # used
                else:
                    if c[k] > z[2]:
                        continue
                    if h[k] >= z[1]:
                        touched = z
                        continue
                keep.append(z)
            active[side] = keep[-200:]
            if touched is not None and setup[side] is None:
                setup[side] = {"start": k, "ext": k, "kind": touched[3]}

            st = setup[side]
            if st is None:
                continue
            e = st["ext"]
            if (side == "long" and lo[k] < lo[e]) or (side == "short" and h[k] > h[e]):
                st["ext"] = e = k
            if k == 0:
                continue
            if side == "long":
                engulf = c[k] > o[k] and c[k - 1] < o[k - 1] and c[k] >= o[k - 1] and o[k] <= c[k - 1]
                pos = bisect_left(mph_idx, k - 1)  # mini highs confirmed before this candle
                broke = pos > 0 and c[k] > h[mph_idx[pos - 1]]
            else:
                engulf = c[k] < o[k] and c[k - 1] > o[k - 1] and c[k] <= o[k - 1] and o[k] >= c[k - 1]
                pos = bisect_left(mpl_idx, k - 1)
                broke = pos > 0 and c[k] < lo[mpl_idx[pos - 1]]
            if engulf and broke:
                trig[side][k] = "engulf"
                kind[side][k] = st["kind"]
                stop[side][k] = stop_from_candle(side, o[e], h[e], lo[e], c[e], WICK_CAP)
                setup[side] = None

    return DataFrame(
        {
            "long_trigger": trig["long"],
            "short_trigger": trig["short"],
            "long_kind": kind["long"],
            "short_kind": kind["short"],
            "long_struct_stop": stop["long"],
            "short_struct_stop": stop["short"],
        },
        index=df.index,
    )


class AslanLiq4Base(AslanLiq3Base):
    timeframe = "5m"
    setup_window = 36  # 3 hours of 5m candles
    startup_candle_count = 2400
    target_model = MODEL_1R

    @property
    def tp_model(self) -> tm.TPModel:
        return self.target_model

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        df["atr"] = ta.ATR(df, timeperiod=14)
        h1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1h")
        h4 = self.dp.get_pair_dataframe(pair=pair, timeframe="4h")
        d1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1d")
        sig = find_signals_v4(df, poi_zones(h1), self.setup_window)
        for col in sig.columns:
            df[col] = sig[col]
        close_time = (
            pd.to_datetime(df["date"], utc=True) + pd.Timedelta(minutes=timeframe_to_minutes(self.timeframe))
        ).astype("datetime64[ns, UTC]")
        base = pd.DataFrame({"avail": close_time}).reset_index()
        for name, src, mins in (("trend_1d", d1, 1440), ("trend_4h", h4, 240)):
            m = pd.merge_asof(base, structure_trend(src, mins), on="avail", direction="backward").set_index("index")
            df[name] = m["trend"].fillna(0).astype(int)
        df["news_block"] = news_calendar.blocked(close_time, self.news_before, self.news_after)
        return df

    def signal_conditions(self, df: DataFrame):
        return {
            "long": {
                "bias_up": df["trend_1d"] == 1,
                "trend_up": df["trend_4h"] == 1,
                "poi_touched": df["long_kind"] != "",
                "mini_structure_engulf": (df["long_trigger"] == "engulf") & (df["long_struct_stop"] < df["close"]),
                "no_news": ~df["news_block"],
            },
            "short": {
                "bias_down": df["trend_1d"] == -1,
                "trend_down": df["trend_4h"] == -1,
                "poi_touched": df["short_kind"] != "",
                "mini_structure_engulf": (df["short_trigger"] == "engulf") & (df["short_struct_stop"] > df["close"]),
                "no_news": ~df["news_block"],
            },
        }


class AslanLiq4_5m(AslanLiq4Base):
    timeframe = "5m"
    setup_window = 36


class AslanLiq4_5m_2R(AslanLiq4_5m):
    target_model = MODEL_2R


class AslanLiq4_15m(AslanLiq4Base):
    timeframe = "15m"
    setup_window = 12
    startup_candle_count = 800


class AslanLiq4_15m_2R(AslanLiq4_15m):
    target_model = MODEL_2R
