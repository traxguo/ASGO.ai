"""
pusula ("compass"): Claude's own core strategy, designed from everything the
Level 1 and Aslan tests taught. Strategy card: cards/pusula.md (condition ids
below must match the card).

Two layers, both fixed before the first test:

1. Daily regime, for every coin at every moment (also used for the commentary):
     a) last closed daily close above / below daily EMA(50)
     b) daily EMA(20) above / below daily EMA(50)
     c) 90-day return above / below zero (time-series momentum)
   score = sum of the three signs (-3 .. +3)
     +3 -> "up" (strong uptrend), -3 -> "down" (strong downtrend), else "mixed".
   The market (BTC) must agree: BTC's own score >= +1 for longs, <= -1 for shorts.

2. 4h trigger in the regime's direction only:
     long : first 4h close above the previous 20-candle high
     short: first 4h close below the previous 20-candle low
   In a "mixed" regime there is no trade (commentary only).

Trade management: shared module (entry zone, wider of 1.5 ATR / swing stop,
Model B 2R/4R, 3-candle validity, max 3x).

merge_informative_pair shifts the daily data so a 4h candle only sees daily
candles that had already closed (no lookahead).
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import talib.abstract as ta  # noqa: E402
from freqtrade.strategy import merge_informative_pair  # noqa: E402
from pandas import DataFrame, Series  # noqa: E402

from strategies.common.freqtrade_mixin import ManagedStrategy  # noqa: E402

REGIME_TF = "1d"
MARKET_PAIR = "BTC/USDT:USDT"
EMA_FAST = 20
EMA_SLOW = 50
MOMENTUM_DAYS = 90
CHANNEL = 20


def first_true(cond: Series) -> Series:
    """True only on the first candle of a run of True values."""
    return cond & ~cond.shift(1, fill_value=False)


def regime_score(daily: DataFrame) -> Series:
    """-3 .. +3 trend score per daily candle, from that candle's data and older only."""
    close = daily["close"]
    ema_fast = close.ewm(span=EMA_FAST, adjust=False, min_periods=EMA_FAST).mean()
    ema_slow = close.ewm(span=EMA_SLOW, adjust=False, min_periods=EMA_SLOW).mean()
    momentum = close / close.shift(MOMENTUM_DAYS) - 1
    parts = [np.sign(close - ema_slow), np.sign(ema_fast - ema_slow), np.sign(momentum)]
    score = sum(parts)
    # Not enough history yet -> no regime (no trade, no commentary verdict).
    ready = ema_slow.notna() & momentum.notna()
    return score.where(ready)


def regime_label(score) -> str:
    if score is None or pd.isna(score):
        return "unknown"
    if score >= 3:
        return "up"
    if score <= -3:
        return "down"
    return "mixed"


def daily_regime_frame(daily: DataFrame, market_daily: DataFrame | None) -> DataFrame:
    """Daily frame with the coin's score, its EMAs and the market (BTC) score, joined on date."""
    out = daily[["date", "close"]].copy()
    close = out["close"]
    out["ema_fast"] = close.ewm(span=EMA_FAST, adjust=False, min_periods=EMA_FAST).mean()
    out["ema_slow"] = close.ewm(span=EMA_SLOW, adjust=False, min_periods=EMA_SLOW).mean()
    out["mom"] = close / close.shift(MOMENTUM_DAYS) - 1
    out["score"] = regime_score(daily)
    if market_daily is None:
        out["mkt_score"] = out["score"]
    else:
        mkt = pd.DataFrame({"date": market_daily["date"], "mkt_score": regime_score(market_daily)})
        out = out.merge(mkt, on="date", how="left")
    return out


class PusulaBase(ManagedStrategy):
    timeframe = "4h"
    tp_model_name = "B"
    swing_lookback = 10
    # 4h warm-up; the daily data gets the same count of daily candles, enough for
    # EMA50 and the 90-day momentum.
    startup_candle_count = 400
    channel = CHANNEL
    use_market_filter = True

    def informative_pairs(self):
        pairs = [(pair, REGIME_TF) for pair in self.dp.current_whitelist()]
        if self.use_market_filter and (MARKET_PAIR, REGIME_TF) not in pairs:
            pairs.append((MARKET_PAIR, REGIME_TF))
        return pairs

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df["atr"] = ta.ATR(df, timeperiod=14)
        df["swing_low"] = df["low"].rolling(self.swing_lookback).min()
        df["swing_high"] = df["high"].rolling(self.swing_lookback).max()
        df["dc_upper"] = df["high"].rolling(self.channel).max().shift(1)
        df["dc_lower"] = df["low"].rolling(self.channel).min().shift(1)

        daily = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=REGIME_TF)
        market = None
        if self.use_market_filter:
            market = self.dp.get_pair_dataframe(pair=MARKET_PAIR, timeframe=REGIME_TF)
        regime = daily_regime_frame(daily, market)
        return merge_informative_pair(df, regime, self.timeframe, REGIME_TF, ffill=True)

    def swing_levels(self, df: DataFrame):
        return {"long": df["swing_low"], "short": df["swing_high"]}

    def signal_conditions(self, df: DataFrame):
        score = df[f"score_{REGIME_TF}"]
        mkt = df[f"mkt_score_{REGIME_TF}"]
        long_c = {
            "regime_up": score >= 3,
            "breakout_up": first_true(df["close"] > df["dc_upper"]),
        }
        short_c = {
            "regime_down": score <= -3,
            "breakout_down": first_true(df["close"] < df["dc_lower"]),
        }
        if self.use_market_filter:
            long_c["market_up"] = mkt >= 1
            short_c["market_down"] = mkt <= -1
        return {"long": long_c, "short": short_c}


class Pusula_B(PusulaBase):
    """Core strategy."""


class PusulaNoBTC_B(PusulaBase):
    """Ablation: same rules without the market (BTC) filter."""

    use_market_filter = False


# ---------------------------------------------------------------------------
# Commentary: a view for any coin at any moment (same rules as the strategy).
# ---------------------------------------------------------------------------

REGIME_TEXT = {
    "up": "güçlü yükseliş",
    "down": "güçlü düşüş",
    "mixed": "kararsız",
    "unknown": "yeterli geçmiş veri yok",
}


def _fmt(x: float) -> str:
    return f"{x:,.6g}".replace(",", ".") if abs(x) >= 1000 else f"{x:.6g}"


def trigger_plan(side: str, trigger: float, atr: float, swing: float, mgmt, model) -> dict:
    """Plan if the trigger candle closed exactly at the trigger level (shared rules)."""
    from strategies.common import trade_management as tm

    low, high, mid = tm.entry_zone(side, trigger, atr, mgmt.entry_zone_atr)
    stop = tm.stop_price(side, mid, atr, swing, mgmt)
    tp1, tp2 = tm.targets(side, mid, stop, model)
    return {"zone_low": float(low), "zone_high": float(high), "stop": float(stop), "tp1": float(tp1), "tp2": float(tp2)}


def commentary(row, pair: str, mgmt=None, model=None, market_filter: bool = True) -> dict:
    """
    View for one coin from the last analysed 4h row: regime, market, the trigger
    level for the allowed side and the plan it would produce. Never invents a
    level: every number comes from the strategy's own columns and rules.
    """
    from strategies.common import trade_management as tm

    mgmt = mgmt or tm.DEFAULT_PARAMS
    model = model or tm.MODEL_B
    score = row.get(f"score_{REGIME_TF}")
    mkt = row.get(f"mkt_score_{REGIME_TF}")
    regime = regime_label(score)
    view = {"pair": pair, "regime": regime, "score": score, "market_score": mkt, "side": None, "plan": None}
    coin = pair.split("/")[0]
    lines = [f"{coin} (4s): {REGIME_TEXT[regime]}" + ("" if pd.isna(score) else f" ({int(score):+d}/3).")]
    if regime == "unknown":
        view["text"] = lines[0]
        return view
    lines.append(f"Fiyat {_fmt(row['close'])}. Günlük 50 ortalama {_fmt(row[f'ema_slow_{REGIME_TF}'])}, "
                 f"90 günlük değişim %{row[f'mom_{REGIME_TF}'] * 100:.0f}.")
    if market_filter and not pd.isna(mkt):
        lines.append(f"Bitcoin puanı {int(mkt):+d}/3.")

    side = {"up": "long", "down": "short"}.get(regime)
    if not market_filter:
        market_ok = True
    elif pd.isna(mkt):
        market_ok = False
    else:
        market_ok = (side == "long" and mkt >= 1) or (side == "short" and mkt <= -1)
    if side is None:
        lines.append("İşlem önermiyorum: trend yönü belli değil. "
                     f"Long için puanın +3, short için -3 olması gerekir.")
    elif not market_ok:
        lines.append(f"{'Long' if side == 'long' else 'Short'} önermiyorum: Bitcoin aynı tarafta değil.")
    else:
        trigger = row["dc_upper"] if side == "long" else row["dc_lower"]
        swing = row["swing_low"] if side == "long" else row["swing_high"]
        plan = trigger_plan(side, float(trigger), float(row["atr"]), float(swing), mgmt, model)
        view.update(side=side, plan=plan, trigger=float(trigger))
        word = "üstünde" if side == "long" else "altında"
        lines.append(
            f"{side.upper()} tetiği {_fmt(trigger)}: 4 saatlik mum bunun {word} kapanırsa "
            f"giriş {_fmt(plan['zone_low'])} - {_fmt(plan['zone_high'])}, stop {_fmt(plan['stop'])}, "
            f"TP1 {_fmt(plan['tp1'])}, TP2 {_fmt(plan['tp2'])} (yaklaşık; kesin rakamlar kırılım mumunun kapanışından)."
        )
        lines.append(f"{'Short' if side == 'long' else 'Long'} yok: trende karşı işlem açmıyorum.")
    view["text"] = "\n".join(lines)
    return view
