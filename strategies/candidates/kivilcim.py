"""
kivilcim ("spark"): short-hold TRIAL bot for the Bitget demo (owner's request 2026-10-11:
see a bot take ~3 trades a day and close them within a few hours). Card: cards/kivilcim.md.

Its rule had NO positive test: research/scans/short_trade_grid.py (S2_pullback, tp 1.5 ATR,
sl 1.5 ATR, 3h) gave about -0.08R per trade on 2020-2024 and -0.12R on 2025-01..2026-03
after costs. It runs on the demo only to collect live fills; it is not a strategy candidate.

  regime : coin daily score == +3 from the last CLOSED daily candle (same score as Pusula/Dalga)
  trigger: 1h RSI(14) below 35 on the candle that just closed (pullback inside a strong trend)
  entry  : market order right after the 1h candle closes
  stop   : entry - 1.5 * ATR(14, 1h);  take profit: entry + 1.5 * ATR(14, 1h)
  time   : closed at market 3 hours after the fill if neither was hit
  size   : 0.2% of equity risked per trade, at most 2 open trades and 3 new trades per UTC day

Plain class (no Freqtrade backtest); scripts/bitget_demo.py calls the populate_* methods.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.common import trade_management as tm  # noqa: E402

RSI_LEN = 14
RSI_MAX = 35.0
ATR_LEN = 14
STOP_ATR = 1.5
TP_ATR = 1.5


def daily_score(daily: pd.DataFrame) -> pd.Series:
    """Score -3..+3 of each CLOSED daily candle, indexed by that candle's date."""
    d = daily.set_index("date")["close"]
    e20 = d.ewm(span=20, adjust=False).mean()
    e50 = d.ewm(span=50, adjust=False).mean()
    return np.sign(d - e50) + np.sign(e20 - e50) + np.sign(d / d.shift(90) - 1)


class _TpModel:
    breakeven_r = float("inf")  # stop never moves


class Kivilcim:
    timeframe = "1h"
    mgmt = tm.ManagementParams(risk_per_trade=0.002, stop_method="atr", stop_atr=STOP_ATR)
    tp_model = _TpModel()

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.dp = None

    def populate_indicators(self, df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        df = df.copy()
        prev_close = df["close"].shift()
        tr = pd.concat([df["high"] - df["low"], (df["high"] - prev_close).abs(),
                        (df["low"] - prev_close).abs()], axis=1).max(axis=1)
        df["atr"] = tr.rolling(ATR_LEN).mean()
        diff = df["close"].diff()
        up = diff.clip(lower=0).ewm(alpha=1 / RSI_LEN).mean()
        down = (-diff.clip(upper=0)).ewm(alpha=1 / RSI_LEN).mean()
        df["rsi"] = 100 - 100 / (1 + up / down)
        score = daily_score(self.dp.get_pair_dataframe(metadata["pair"], "1d"))
        # a 1h candle of day D sees the score of day D-1 (the last closed daily candle)
        day_before = df["date"].dt.floor("D") - pd.Timedelta(days=1)
        df["score_1d"] = score.reindex(pd.DatetimeIndex(day_before)).to_numpy()
        return df

    def populate_entry_trend(self, df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        df["enter_long"] = ((df["score_1d"] == 3) & (df["rsi"] < RSI_MAX) & df["atr"].notna()).astype(int)
        df["long_entry"] = df["close"]
        df["long_stop"] = df["close"] - STOP_ATR * df["atr"]
        df["long_tp"] = df["close"] + TP_ATR * df["atr"]
        return df

    def populate_exit_trend(self, df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        df["exit_long"] = 0  # exits are the stop, the take profit and the 3h clock
        return df
