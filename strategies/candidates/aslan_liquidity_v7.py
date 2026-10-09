"""
aslan_liquidity v7 (Aslan, 2026-10-09 12:07, after reviewing audit charts 4 and 5):
  1. liquidity sweep (levels as in v3: 1h / 4h / 1d swings, previous day, sessions)
  2. MSS on 5m is required: a 5m candle closes beyond the last swing point
     (below the last swing low for a short), so the move has really turned
  3. only after that MSS: an FVG in the trade direction or an iFVG on 1m -> entry
     at the close of that 1m candle
Stop 0.1% beyond the sweep extreme, single 1R target, 4h trend filter, news filter.
Strategy card: cards/aslan_liquidity.md (section "v7").
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import talib.abstract as ta  # noqa: E402
from pandas import DataFrame  # noqa: E402

from strategies.candidates import aslan_liquidity_v3 as v3  # noqa: E402
from strategies.common import news_calendar  # noqa: E402

MSS_TF_MINUTES = 5


def mss_events(m5: DataFrame, levels: DataFrame, setup_window: int) -> DataFrame:
    """5m sweep -> MSS events: [avail (5m close), side, stop]."""
    sig = v3.find_signals_v3(m5, levels, setup_window, allow_break=False, stop_buffer_pct=0.001, mss_only=True)
    close_t = pd.to_datetime(m5["date"], utc=True) + pd.Timedelta(minutes=MSS_TF_MINUTES)
    rows = []
    for side in ("long", "short"):
        idx = np.flatnonzero((sig[f"{side}_trigger"] == "mss").to_numpy())
        for i in idx:
            rows.append((close_t.iloc[i], side, sig[f"{side}_struct_stop"].iloc[i]))
    ev = DataFrame(rows, columns=["avail", "side", "stop"])
    ev["avail"] = pd.to_datetime(ev["avail"], utc=True).astype("datetime64[ns, UTC]")
    return ev.sort_values("avail", kind="stable").reset_index(drop=True)


def find_entries_1m(df: DataFrame, events: DataFrame, window: int) -> DataFrame:
    """
    After each MSS (known at its 5m close), look on 1m for the first gap in the trade
    direction formed after the MSS ('fvg'), or a 1m gap against the trade formed after
    the MSS that a candle closes through ('ifvg'). Entry at that 1m close. The setup
    dies after `window` 1m candles or when price reaches the stop first.
    """
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    t_open = pd.to_datetime(df["date"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]")
    n = len(df)
    ev_t = pd.to_datetime(events["avail"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]")
    ev_side = events["side"].to_numpy()
    ev_stop = events["stop"].to_numpy(float)

    trig = {s: np.full(n, "", dtype=object) for s in ("long", "short")}
    stop = {s: np.full(n, np.nan) for s in ("long", "short")}
    setup = {"long": None, "short": None}  # dict(start, stop)
    ei = 0
    for k in range(n):
        while ei < len(ev_t) and ev_t[ei] <= t_open[k]:
            setup[ev_side[ei]] = {"start": k, "stop": ev_stop[ei]}  # newest MSS replaces an older one
            ei += 1
        for side in ("long", "short"):
            st = setup[side]
            if st is None:
                continue
            if k - st["start"] >= window or (lo[k] <= st["stop"] if side == "long" else h[k] >= st["stop"]):
                setup[side] = None
                continue
            s0 = st["start"]
            t = ""
            if side == "long":
                if k - 2 >= s0 and lo[k] > h[k - 2]:
                    t = "fvg"
                else:
                    for f in range(s0 + 2, k):
                        top = lo[f - 2]
                        if h[f] < top and c[k] > top and c[f + 1:k].max(initial=-np.inf) <= top:
                            t = "ifvg"
                            break
            else:
                if k - 2 >= s0 and h[k] < lo[k - 2]:
                    t = "fvg"
                else:
                    for f in range(s0 + 2, k):
                        bottom = h[f - 2]
                        if lo[f] > bottom and c[k] < bottom and c[f + 1:k].min(initial=np.inf) >= bottom:
                            t = "ifvg"
                            break
            if t:
                trig[side][k] = t
                stop[side][k] = st["stop"]
                setup[side] = None
    return DataFrame(
        {
            "long_trigger": trig["long"],
            "short_trigger": trig["short"],
            "long_struct_stop": stop["long"],
            "short_struct_stop": stop["short"],
        },
        index=df.index,
    )


class AslanLiq7_1m(v3.AslanLiq3Base):
    timeframe = "1m"
    mss_setup_window = 144  # 12 hours of 5m candles between sweep and MSS
    entry_window = 60  # 1 hour of 1m candles between MSS and the 1m gap
    startup_candle_count = 2400

    def informative_pairs(self):
        return [(p, tf) for p in self.dp.current_whitelist() for tf in ("5m", "1h", "4h", "1d")]

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        df["atr"] = ta.ATR(df, timeperiod=14)
        m5 = self.dp.get_pair_dataframe(pair=pair, timeframe="5m")
        h1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1h")
        h4 = self.dp.get_pair_dataframe(pair=pair, timeframe="4h")
        d1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1d")
        ev = mss_events(m5, v3.all_levels(h1, h4, d1), self.mss_setup_window)
        sig = find_entries_1m(df, ev, self.entry_window)
        for col in sig.columns:
            df[col] = sig[col]
        df["long_kind"] = np.where(df["long_trigger"] != "", "sweep", "")
        df["short_kind"] = np.where(df["short_trigger"] != "", "sweep", "")

        close_time = (pd.to_datetime(df["date"], utc=True) + pd.Timedelta(minutes=1)).astype("datetime64[ns, UTC]")
        base = pd.DataFrame({"avail": close_time}).reset_index()
        for tf, src, mins in (("4h", h4, 240), ("1h", h1, 60)):
            m = pd.merge_asof(base, v3.structure_trend(src, mins), on="avail", direction="backward").set_index("index")
            df[f"trend_{tf}"] = m["trend"].fillna(0).astype(int)
        df["news_block"] = news_calendar.blocked(close_time, self.news_before, self.news_after)
        return df

    def signal_conditions(self, df: DataFrame):
        return {
            "long": {
                "trend_up": self._trend_ok(df, 1),
                "sweep_then_mss_5m": df["long_kind"] != "",
                "fvg_or_ifvg_1m": df["long_trigger"].isin(["fvg", "ifvg"]) & (df["long_struct_stop"] < df["close"]),
                "no_news": ~df["news_block"],
            },
            "short": {
                "trend_down": self._trend_ok(df, -1),
                "sweep_then_mss_5m": df["short_kind"] != "",
                "fvg_or_ifvg_1m": df["short_trigger"].isin(["fvg", "ifvg"]) & (df["short_struct_stop"] > df["close"]),
                "no_news": ~df["news_block"],
            },
        }


# ---------------------------------------------------------------- v7 retest (Aslan's note on chart 3)
# Same sweep -> 5m MSS, but the entry waits for price to come back into the
# 5m gap the MSS candle left: limit order at the near edge of that gap
# (long: the gap top), valid for one hour, cancelled if the stop trades first.


def mss_gap_events(m5: DataFrame, levels: DataFrame, setup_window: int) -> DataFrame:
    """[avail, side, stop, edge]: the 5m FVG around the MSS candle and when it is known."""
    sig = v3.find_signals_v3(m5, levels, setup_window, allow_break=False, stop_buffer_pct=0.001, mss_only=True)
    h = m5["high"].to_numpy(float)
    lo = m5["low"].to_numpy(float)
    close_t = pd.to_datetime(m5["date"], utc=True) + pd.Timedelta(minutes=MSS_TF_MINUTES)
    n = len(m5)
    rows = []
    for side in ("long", "short"):
        for k in np.flatnonzero((sig[f"{side}_trigger"] == "mss").to_numpy()):
            stop = sig[f"{side}_struct_stop"].iloc[k]
            # gap with the MSS candle as the middle candle (known one candle later),
            # else a gap that the MSS candle itself completes
            for j in (k + 1, k):
                if j < 2 or j >= n:
                    continue
                if side == "long" and lo[j] > h[j - 2]:
                    rows.append((close_t.iloc[j], side, stop, lo[j]))
                    break
                if side == "short" and h[j] < lo[j - 2]:
                    rows.append((close_t.iloc[j], side, stop, h[j]))
                    break
    ev = DataFrame(rows, columns=["avail", "side", "stop", "edge"])
    ev["avail"] = pd.to_datetime(ev["avail"], utc=True).astype("datetime64[ns, UTC]")
    return ev.sort_values("avail", kind="stable").reset_index(drop=True)


class AslanLiq7_1m_Retest(AslanLiq7_1m):
    mgmt = v3.tm.ManagementParams(
        entry_zone_atr=0.0,
        valid_for_candles=60,  # the limit order waits one hour for the retest
        stop_method="structural",
        stop_buffer_atr=0.0,
        max_stop_pct=0.08,
        max_leverage=20.0,
        risk_per_trade=0.01,
    )

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_indicators(df, metadata)
        pair = metadata["pair"]
        m5 = self.dp.get_pair_dataframe(pair=pair, timeframe="5m")
        h1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1h")
        h4 = self.dp.get_pair_dataframe(pair=pair, timeframe="4h")
        d1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1d")
        ev = mss_gap_events(m5, v3.all_levels(h1, h4, d1), self.mss_setup_window)
        close_time = (pd.to_datetime(df["date"], utc=True) + pd.Timedelta(minutes=1)).astype("datetime64[ns, UTC]")
        for side in ("long", "short"):
            e = ev[ev["side"] == side].set_index("avail")
            e = e[~e.index.duplicated(keep="last")]
            df[f"{side}_trigger"] = np.where(close_time.isin(e.index), "retest", "")
            df[f"{side}_struct_stop"] = close_time.map(e["stop"]).to_numpy()
            df[f"{side}_edge"] = close_time.map(e["edge"]).to_numpy()
            df[f"{side}_kind"] = np.where(df[f"{side}_trigger"] != "", "sweep", "")
        return df

    def add_plan_columns(self, df: DataFrame) -> DataFrame:
        df = super().add_plan_columns(df)
        for side in ("long", "short"):
            has = df[f"{side}_edge"].notna()
            entry = df[f"{side}_edge"].where(has, df[f"{side}_entry"])
            stop = df[f"{side}_stop"]
            tp1, tp2 = v3.tm.targets(side, entry, stop, self.tp_model)
            df[f"{side}_entry"] = entry
            df[f"{side}_tp1"] = tp1
            df[f"{side}_tp2"] = tp2
            stop_pct = np.abs(entry - stop) / entry
            df[f"{side}_plan_ok"] = (stop_pct <= self.mgmt.max_stop_pct) & (stop_pct > 0)
        return df

    def signal_conditions(self, df: DataFrame):
        return {
            "long": {
                "trend_up": self._trend_ok(df, 1),
                "sweep_then_mss_5m_gap": df["long_trigger"] == "retest",
                "gap_below_price": (df["long_edge"] < df["close"]) & (df["long_struct_stop"] < df["long_edge"]),
                "no_news": ~df["news_block"],
            },
            "short": {
                "trend_down": self._trend_ok(df, -1),
                "sweep_then_mss_5m_gap": df["short_trigger"] == "retest",
                "gap_above_price": (df["short_edge"] > df["close"]) & (df["short_struct_stop"] > df["short_edge"]),
                "no_news": ~df["news_block"],
            },
        }
