"""
ams_liquidity_mss: "Algorithmic liquidity + MSS strategy (V27)", a fully mechanical
rule set the owner received from Gemini on 2026-10-09 after the Aslan tests.
Strategy card: cards/ams_liquidity_mss.md.

All on 15m candles, times in UTC (Turkey = UTC+3):
1. Fractal = 2 candles on each side (pivots(n=2)).
   Liquidity levels only:
   - Asian session high / low: highest fractal high / lowest fractal low of
     00:00-08:00 Turkey time (21:00-05:00 UTC), usable after the window and confirmation
   - previous day high / low (UTC day)
   - equal highs / lows: two fractals within 100 candles, less than 0.05% apart
2. Sweep: a candle trades through the level and that candle or the next one closes
   back inside. Two closes beyond the level in a row = break: the level is dropped.
3. MSS: a 15m close beyond the last fractal on the other side formed before the
   sweep extreme (close, not a wick).
4. Entry: the most recent FVG formed inside the sweep -> MSS leg that no later wick
   has touched. Limit order at the far edge of the gap (short: low of the first
   candle, long: high of the first candle), valid for `valid_for_candles` candles,
   cancelled if the stop trades first.
5. Stop 0.1% beyond the sweep extreme. TP1 1.5R (close 50%, stop to entry), TP2 3R.
6. Filters: sweep and MSS only in the killzones (London 10:00-12:00, New York
   15:30-18:00 Turkey time); 1h close above EMA200 -> longs only (sweeps of lows),
   below -> shorts only; no signal from 2.5h before a high-impact US release (the
   order lifetime plus 30 minutes) until 15 minutes after it.
"""

import sys
from datetime import timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import talib.abstract as ta  # noqa: E402
from pandas import DataFrame  # noqa: E402

from strategies.candidates.aslan_liquidity import pivots  # noqa: E402
from strategies.common import news_calendar  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402
from strategies.common.freqtrade_mixin import ManagedStrategy  # noqa: E402

TF = pd.Timedelta(minutes=15)
FRACTAL_N = 2
EQ_LOOKBACK = 100
EQ_TOLERANCE = 0.0005
LEVEL_MAX_AGE = pd.Timedelta(days=1)
STOP_BUFFER = 0.001
# Killzones in UTC minutes of the day: London 07:00-09:00, New York 12:30-15:00.
KILLZONES_UTC = ((7 * 60, 9 * 60), (12 * 60 + 30, 15 * 60))
MODEL_V27 = tm.TPModel(name="V27_1.5R_3R", tp1_r=1.5, tp2_r=3.0, tp1_close_pct=50, breakeven_trigger="TP1")


def in_killzone(dates: pd.Series) -> np.ndarray:
    d = pd.to_datetime(dates, utc=True)
    minute = (d.dt.hour * 60 + d.dt.minute).to_numpy()
    out = np.zeros(len(d), dtype=bool)
    for a, b in KILLZONES_UTC:
        out |= (minute >= a) & (minute < b)
    return out


def liquidity_levels(df: DataFrame, d1: DataFrame) -> DataFrame:
    """[avail, price, side, kind] from 15m candles and daily candles."""
    h = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    dates = pd.to_datetime(df["date"], utc=True).reset_index(drop=True)
    ph, pl = pivots(h, lo, FRACTAL_N)
    rows = []

    # Asian session (21:00-05:00 UTC): extreme fractal inside the window
    shifted = dates + pd.Timedelta(hours=3)  # Turkey time
    asia = (shifted.dt.hour < 8).to_numpy()
    day = shifted.dt.floor("D").to_numpy()
    for side, mask, values, pick in (("high", ph, h, np.argmax), ("low", pl, lo, np.argmin)):
        idx = np.flatnonzero(mask & asia)
        if len(idx) == 0:
            continue
        frame = pd.DataFrame({"i": idx, "day": day[idx], "v": values[idx]})
        for d, g in frame.groupby("day"):
            j = int(g["i"].iloc[pick(g["v"].to_numpy())])
            window_end = pd.Timestamp(d).tz_convert("UTC") + pd.Timedelta(hours=5)  # 08:00 Turkey
            avail = max(window_end, dates[j] + TF * (FRACTAL_N + 1))
            rows.append((avail, values[j], side, "asia"))

    # previous day high / low
    dd = pd.to_datetime(d1["date"], utc=True)
    for t, hi, low in zip(dd, d1["high"].to_numpy(float), d1["low"].to_numpy(float)):
        rows.append((t + pd.Timedelta(days=1), hi, "high", "pdh"))
        rows.append((t + pd.Timedelta(days=1), low, "low", "pdl"))

    # equal highs / lows
    for side, mask, values in (("high", ph, h), ("low", pl, lo)):
        idx = np.flatnonzero(mask)
        for a, j in enumerate(idx):
            for i in idx[max(0, a - 20):a][::-1]:
                if j - i > EQ_LOOKBACK:
                    break
                if abs(values[j] - values[i]) / values[i] < EQ_TOLERANCE:
                    price = max(values[i], values[j]) if side == "high" else min(values[i], values[j])
                    rows.append((dates[j] + TF * (FRACTAL_N + 1), price, side, "eq"))
                    break
    out = DataFrame(rows, columns=["avail", "price", "side", "kind"])
    out["avail"] = pd.to_datetime(out["avail"], utc=True).astype("datetime64[ns, UTC]")
    return out.sort_values("avail", kind="stable").reset_index(drop=True)


def find_signals(df: DataFrame, levels: DataFrame) -> DataFrame:
    """Per 15m candle: MSS signal with the limit entry (edge), stop and level kind."""
    h = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    t_open = pd.to_datetime(df["date"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]")
    n = len(df)
    kz = in_killzone(df["date"])
    ph, pl = pivots(h, lo, FRACTAL_N)
    lv_t = pd.to_datetime(levels["avail"], utc=True).dt.tz_convert(None).to_numpy(dtype="datetime64[ns]")
    lv_p = levels["price"].to_numpy(float)
    lv_s = levels["side"].to_numpy()
    lv_k = levels["kind"].to_numpy()
    max_age = np.timedelta64(LEVEL_MAX_AGE)

    out = {
        f"{s}_{col}": (np.full(n, np.nan) if col in ("edge", "struct_stop") else np.full(n, "", dtype=object))
        for s in ("long", "short")
        for col in ("trigger", "edge", "struct_stop", "kind")
    }
    active: list[list] = []  # [avail, price, side, kind, pending_break_candle]
    setup = {"long": None, "short": None}  # dict(sweep, ext, kind)
    fh: list[int] = []  # confirmed fractal highs / lows (candle index)
    fl: list[int] = []
    li = 0
    for k in range(n):
        while li < len(lv_t) and lv_t[li] <= t_open[k]:
            active.append([lv_t[li], lv_p[li], lv_s[li], lv_k[li], -1])
            li += 1
        j = k - FRACTAL_N - 1  # fractal confirmed by the close of candle k - 1
        if j >= 0 and ph[j]:
            fh.append(j)
        if j >= 0 and pl[j]:
            fl.append(j)

        # 1) sweeps / breaks of the levels
        keep = []
        for lv in active:
            t0, p, side, kind, pend = lv
            if t_open[k] - t0 > max_age:
                continue
            if side == "high":
                beyond = c[k] > p
                touched = h[k] > p
                trade = "short"
            else:
                beyond = c[k] < p
                touched = lo[k] < p
                trade = "long"
            if pend >= 0:  # traded through and closed beyond on the previous candle
                if beyond:
                    continue  # two closes beyond: break, level dropped
                if kz[k] and kz[pend]:
                    setup[trade] = {"sweep": pend, "ext": pend, "kind": kind}
                continue  # level used
            if touched:
                if beyond:
                    lv[4] = k
                    keep.append(lv)
                    continue
                if kz[k]:
                    setup[trade] = {"sweep": k, "ext": k, "kind": kind}
                continue
            keep.append(lv)
        active = keep[-300:]

        # 2) MSS, then the FVG of the leg
        for side in ("long", "short"):
            st = setup[side]
            if st is None:
                continue
            if not kz[k]:
                setup[side] = None  # MSS must come inside the same killzone
                continue
            e = st["ext"]
            if (side == "long" and lo[k] < lo[e]) or (side == "short" and h[k] > h[e]):
                st["ext"] = e = k
            idx = fh if side == "long" else fl
            ref = [i for i in idx[-10:] if i < e]
            if not ref:
                continue
            r = ref[-1]
            mss = c[k] > h[r] if side == "long" else c[k] < lo[r]
            if not mss:
                continue
            setup[side] = None
            edge = np.nan
            for i in range(k, e + 1, -1):  # newest gap first, all three candles inside the leg
                if i - 2 < e:
                    break
                if side == "long" and lo[i] > h[i - 2]:
                    top, bottom = lo[i], h[i - 2]
                    if (lo[i + 1:k + 1] > top).all():
                        edge = bottom
                        break
                if side == "short" and h[i] < lo[i - 2]:
                    bottom, top = h[i], lo[i - 2]
                    if (h[i + 1:k + 1] < bottom).all():
                        edge = top
                        break
            if np.isnan(edge):
                continue
            out[f"{side}_trigger"][k] = "mss_fvg"
            out[f"{side}_edge"][k] = edge
            out[f"{side}_struct_stop"][k] = lo[e] * (1 - STOP_BUFFER) if side == "long" else h[e] * (1 + STOP_BUFFER)
            out[f"{side}_kind"][k] = st["kind"]
    return DataFrame(out, index=df.index)


class AMSLiquidityMSS(ManagedStrategy):
    timeframe = "15m"
    startup_candle_count = 800
    news_before = timedelta(hours=2, minutes=30)
    news_after = timedelta(minutes=15)
    mgmt = tm.ManagementParams(
        entry_zone_atr=0.0,
        valid_for_candles=8,  # the limit order waits two hours for the retest
        stop_method="structural",
        stop_buffer_atr=0.0,
        max_stop_pct=0.08,
        max_leverage=20.0,
        risk_per_trade=0.01,
    )

    @property
    def tp_model(self) -> tm.TPModel:
        return MODEL_V27

    def informative_pairs(self):
        return [(p, tf) for p in self.dp.current_whitelist() for tf in ("1h", "1d")]

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        df["atr"] = ta.ATR(df, timeperiod=14)
        h1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1h")
        d1 = self.dp.get_pair_dataframe(pair=pair, timeframe="1d")
        sig = find_signals(df, liquidity_levels(df, d1))
        for col in sig.columns:
            df[col] = sig[col]
        close_time = (pd.to_datetime(df["date"], utc=True) + TF).astype("datetime64[ns, UTC]")
        ema = pd.DataFrame(
            {
                "avail": (pd.to_datetime(h1["date"], utc=True) + pd.Timedelta(hours=1)).astype("datetime64[ns, UTC]"),
                "above": (h1["close"] > ta.EMA(h1, timeperiod=200)).astype(int) - (h1["close"] < ta.EMA(h1, timeperiod=200)).astype(int),
            }
        )
        m = pd.merge_asof(pd.DataFrame({"avail": close_time}).reset_index(), ema, on="avail").set_index("index")
        df["ema_side"] = m["above"].fillna(0).astype(int)
        df["news_block"] = news_calendar.blocked(close_time, self.news_before, self.news_after)
        return df

    def swing_levels(self, df: DataFrame):
        return {"long": df["long_struct_stop"], "short": df["short_struct_stop"]}

    def add_plan_columns(self, df: DataFrame) -> DataFrame:
        df = super().add_plan_columns(df)
        for side in ("long", "short"):
            entry = df[f"{side}_edge"].where(df[f"{side}_edge"].notna(), df[f"{side}_entry"])
            stop = df[f"{side}_stop"]
            tp1, tp2 = tm.targets(side, entry, stop, self.tp_model)
            df[f"{side}_entry"], df[f"{side}_tp1"], df[f"{side}_tp2"] = entry, tp1, tp2
            stop_pct = np.abs(entry - stop) / entry
            df[f"{side}_plan_ok"] = (stop_pct <= self.mgmt.max_stop_pct) & (stop_pct > 0)
        return df

    def signal_conditions(self, df: DataFrame):
        return {
            "long": {
                "ema200_1h_above": df["ema_side"] == 1,
                "sweep_low_then_mss_in_killzone": df["long_trigger"] == "mss_fvg",
                "fvg_below_price": (df["long_edge"] < df["close"]) & (df["long_struct_stop"] < df["long_edge"]),
                "no_news": ~df["news_block"],
            },
            "short": {
                "ema200_1h_below": df["ema_side"] == -1,
                "sweep_high_then_mss_in_killzone": df["short_trigger"] == "mss_fvg",
                "fvg_above_price": (df["short_edge"] > df["close"]) & (df["short_struct_stop"] > df["short_edge"]),
                "no_news": ~df["news_block"],
            },
        }

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_entry_trend(df, metadata)
        for side in ("long", "short"):
            m = df.get(f"enter_{side}", pd.Series(0, index=df.index)).fillna(0) == 1
            df.loc[m, "enter_tag"] = df.loc[m, "enter_tag"] + " kind=" + df.loc[m, f"{side}_kind"]
        return df
