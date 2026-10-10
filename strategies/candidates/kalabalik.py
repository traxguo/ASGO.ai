"""
kalabalik: trade against the crowded side when funding is extreme and price turns.
Strategy card: cards/kalabalik.md (condition ids below must match the card).

Funding (8h prints) is read from the funding-rate data file of the pair. A 4h
candle only sees prints with a time <= the candle's open time (announced before
the candle), so there is no lookahead.
  funding_24h : mean of the last 3 prints
  pct_rank    : rank of funding_24h among the previous 365 days of values (0..1)
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import talib.abstract as ta  # noqa: E402
from pandas import DataFrame, Series  # noqa: E402

from strategies.common.freqtrade_mixin import ManagedStrategy  # noqa: E402

FUNDING_PRINTS = 3
LOOKBACK_PRINTS = 3 * 365
EXTREME = 0.05
CHANNEL = 10


def first_true(cond: Series) -> Series:
    return cond & ~cond.shift(1, fill_value=False)


def funding_features(funding: DataFrame) -> DataFrame:
    """funding: columns date, funding_rate (one row per 8h print). Past-only features per print."""
    f = funding[["date", "funding_rate"]].sort_values("date").reset_index(drop=True)
    f["funding_24h"] = f["funding_rate"].rolling(FUNDING_PRINTS).mean()
    prev = f["funding_24h"].shift(1)
    # share of the previous LOOKBACK_PRINTS values that are below the current one
    f["pct_rank"] = [
        np.nan if i < LOOKBACK_PRINTS or np.isnan(v) else float((prev.iloc[i - LOOKBACK_PRINTS:i] < v).mean())
        for i, v in enumerate(f["funding_24h"].to_numpy())
    ]
    return f[["date", "funding_24h", "pct_rank"]]


def attach_funding(df: DataFrame, feats: DataFrame) -> DataFrame:
    """As-of join: each candle gets the newest print whose time <= the candle open time."""
    out = pd.merge_asof(df.sort_values("date"), feats.sort_values("date"), on="date", direction="backward")
    return out


class Kalabalik_B(ManagedStrategy):
    timeframe = "4h"
    tp_model_name = "B"
    swing_lookback = 10
    startup_candle_count = 400
    datadir = _REPO_ROOT / "user_data" / "data" / "binance" / "futures"

    def _funding(self, pair: str) -> DataFrame:
        path = self.datadir / f"{pair.replace('/', '_').replace(':', '_')}-1h-funding_rate.feather"
        return pd.read_feather(path)

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df["atr"] = ta.ATR(df, timeperiod=14)
        df["swing_low"] = df["low"].rolling(self.swing_lookback).min()
        df["swing_high"] = df["high"].rolling(self.swing_lookback).max()
        df["high10"] = df["high"].rolling(CHANNEL).max().shift(1)
        df["low10"] = df["low"].rolling(CHANNEL).min().shift(1)
        feats = funding_features(self._funding(metadata["pair"]))
        index = df.index
        df = attach_funding(df.reset_index(drop=True), feats)
        df.index = index
        return df

    def swing_levels(self, df: DataFrame):
        return {"long": df["swing_low"], "short": df["swing_high"]}

    def signal_conditions(self, df: DataFrame):
        rank, f24 = df["pct_rank"], df["funding_24h"]
        return {
            "long": {
                "crowded_short": rank <= EXTREME,
                "turn_up": first_true(df["close"] > df["high10"]),
            },
            "short": {
                "crowded_long": (rank >= 1 - EXTREME) & (f24 > 0),
                "turn_down": first_true(df["close"] < df["low10"]),
            },
        }
