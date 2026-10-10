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


def regime_score(daily: DataFrame, fast: int = EMA_FAST, slow: int = EMA_SLOW, mom_days: int = MOMENTUM_DAYS) -> Series:
    """-3 .. +3 trend score per daily candle, from that candle's data and older only."""
    close = daily["close"]
    ema_fast = close.ewm(span=fast, adjust=False, min_periods=fast).mean()
    ema_slow = close.ewm(span=slow, adjust=False, min_periods=slow).mean()
    momentum = close / close.shift(mom_days) - 1
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


def daily_regime_frame(daily: DataFrame, market_daily: DataFrame | None, fast: int = EMA_FAST,
                       slow: int = EMA_SLOW, mom_days: int = MOMENTUM_DAYS) -> DataFrame:
    """Daily frame with the coin's score, its EMAs and the market (BTC) score, joined on date."""
    out = daily[["date", "close"]].copy()
    close = out["close"]
    out["ema_fast"] = close.ewm(span=fast, adjust=False, min_periods=fast).mean()
    out["ema_slow"] = close.ewm(span=slow, adjust=False, min_periods=slow).mean()
    out["mom"] = close / close.shift(mom_days) - 1
    out["score"] = regime_score(daily, fast, slow, mom_days)
    if market_daily is None:
        out["mkt_score"] = out["score"]
        out["mkt_mom"] = out["mom"]
    else:
        mclose = market_daily["close"]
        mkt = pd.DataFrame({"date": market_daily["date"],
                            "mkt_score": regime_score(market_daily, fast, slow, mom_days),
                            "mkt_mom": mclose / mclose.shift(mom_days) - 1})
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
    ema_fast = EMA_FAST
    ema_slow = EMA_SLOW
    momentum_days = MOMENTUM_DAYS
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
        regime = daily_regime_frame(daily, market, self.ema_fast, self.ema_slow, self.momentum_days)
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


class PusulaTrend(PusulaBase):
    """
    Round 2 (fixed before testing, card section "2. tur"): same entries, but no
    fixed take-profit. The trade is held until the daily trend breaks:
      long  exit: last closed daily close below daily EMA(20)
      short exit: last closed daily close above daily EMA(20)
    The planned stop stays; it moves to break even once price has gone 2R in
    favour (Model A break-even rule). Entries are skipped when the exit rule is
    already true, so a trade is never opened only to be closed on the next candle.
    """

    tp_model_name = "A"  # only its break-even rule is used (2R); no TP orders are placed
    use_exit_signal = True

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        close_1d, ema_fast = df[f"close_{REGIME_TF}"], df[f"ema_fast_{REGIME_TF}"]
        conds["long"]["daily_above_ema20"] = close_1d > ema_fast
        conds["short"]["daily_below_ema20"] = close_1d < ema_fast
        return conds

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        close_1d, ema_fast = df[f"close_{REGIME_TF}"], df[f"ema_fast_{REGIME_TF}"]
        df.loc[close_1d < ema_fast, "exit_long"] = 1
        df.loc[close_1d > ema_fast, "exit_short"] = 1
        return df

    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, min_stake, max_stake, **kwargs):
        return None  # no TP orders: the exit comes from the daily trend rule or the stop


class PusulaTrendRS(PusulaTrend):
    """
    Improvement round 1 (2026-10-10, research/queue/pusula_kuyruk.md): shorts only
    when the coin is weaker than Bitcoin over the momentum window (coin 90-day
    return below BTC's). Longs unchanged. On BTC itself the two are equal, so BTC
    is never shorted. Judged against PusulaTrend on the old 16 and the new 20 coins.
    """

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["short"]["weaker_than_btc"] = df[f"mom_{REGIME_TF}"] < df[f"mkt_mom_{REGIME_TF}"]
        return conds


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
    """Turkish number format: 79.535,1 (dot for thousands, comma for decimals)."""
    x = float(x)
    if abs(x) >= 1000:
        text = f"{x:,.1f}"
    elif abs(x) >= 1:
        text = f"{x:,.4g}" if abs(x) < 100 else f"{x:,.2f}"
    else:
        text = f"{x:.4g}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def trigger_plan(side: str, trigger: float, atr: float, swing: float, mgmt, model) -> dict:
    """Plan if the trigger candle closed exactly at the trigger level (shared rules)."""
    from strategies.common import trade_management as tm

    low, high, mid = tm.entry_zone(side, trigger, atr, mgmt.entry_zone_atr)
    stop = tm.stop_price(side, mid, atr, swing, mgmt)
    tp1, tp2 = tm.targets(side, mid, stop, model)
    return {"zone_low": float(low), "zone_high": float(high), "stop": float(stop), "tp1": float(tp1), "tp2": float(tp2)}


def commentary(row, pair: str, mgmt=None, model=None, market_filter: bool = True, trend_exit: bool = False,
               long_only: bool = False) -> dict:
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
    daily_close = row.get(f"close_{REGIME_TF}", row["close"])
    lines.append(f"Son günlük kapanış {_fmt(daily_close)}, günlük 50 ortalama {_fmt(row[f'ema_slow_{REGIME_TF}'])}, "
                 f"90 günlük değişim %{row[f'mom_{REGIME_TF}'] * 100:.0f}. Son 4 saatlik kapanış {_fmt(row['close'])}.")
    if market_filter and not pd.isna(mkt):
        lines.append(f"Bitcoin puanı {int(mkt):+d}/3.")

    side = {"up": "long", "down": "short"}.get(regime)
    if not market_filter:
        market_ok = True
    elif pd.isna(mkt):
        market_ok = False
    else:
        market_ok = (side == "long" and mkt >= 1) or (side == "short" and mkt <= -1)
    if side == "short" and long_only:
        lines.append("İşlem önermiyorum: düşüş trendinde bekliyorum (short tarafı testlerde kâr getirmedi).")
    elif side is None:
        lines.append("İşlem önermiyorum: trend yönü belli değil. "
                     f"Long için puanın +3, short için -3 olması gerekir.")
    elif not market_ok:
        lines.append(f"{'Long' if side == 'long' else 'Short'} önermiyorum: Bitcoin aynı tarafta değil.")
    elif trend_exit and side == "long" and row.get(f"close_{REGIME_TF}", np.inf) <= row.get(f"ema_fast_{REGIME_TF}", -np.inf):
        lines.append("Şimdilik long yok: günlük kapanış 20 günlük ortalamanın "
                     f"({_fmt(row[f'ema_fast_{REGIME_TF}'])}) altında. Üstüne çıkınca tetik devreye girer.")
    elif trend_exit and side == "short" and row.get(f"close_{REGIME_TF}", -np.inf) >= row.get(f"ema_fast_{REGIME_TF}", np.inf):
        lines.append("Şimdilik short yok: günlük kapanış 20 günlük ortalamanın "
                     f"({_fmt(row[f'ema_fast_{REGIME_TF}'])}) üstünde.")
    else:
        trigger = row["dc_upper"] if side == "long" else row["dc_lower"]
        swing = row["swing_low"] if side == "long" else row["swing_high"]
        plan = trigger_plan(side, float(trigger), float(row["atr"]), float(swing), mgmt, model)
        view.update(side=side, plan=plan, trigger=float(trigger))
        word = "üstünde" if side == "long" else "altında"
        if trend_exit:
            exit_text = ("hedef yok: günlük kapanış 20 günlük ortalamanın altına inince çıkılır, "
                         "fiyat 2R lehte gidince stop girişe çekilir")
        else:
            exit_text = f"TP1 {_fmt(plan['tp1'])}, TP2 {_fmt(plan['tp2'])}"
        lines.append(
            f"{side.upper()} tetiği {_fmt(trigger)}: 4 saatlik mum bunun {word} kapanırsa "
            f"giriş {_fmt(plan['zone_low'])} - {_fmt(plan['zone_high'])}, stop {_fmt(plan['stop'])}, "
            f"{exit_text} (yaklaşık; kesin rakamlar kırılım mumunun kapanışından)."
        )
        lines.append(f"{'Short' if side == 'long' else 'Long'} yok: trende karşı işlem açmıyorum.")
    view["text"] = "\n".join(lines)
    return view


class PusulaTrendLong(PusulaTrend):
    """
    Added AFTER the round 2 result (post-hoc, see card): PusulaTrend without
    shorts. Round 1 and 2 both showed no short edge in 2020-2024.
    """

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["short"] = {}
        return conds


class PusulaTrendLongBtcExit(PusulaTrendLong):
    """
    Improvement round 2a (2026-10-10): also close longs when the market turns,
    i.e. the last closed daily BTC regime score is -1 or lower (the same level
    that would allow shorts). Entries are unchanged.
    """

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_exit_trend(df, metadata)
        df.loc[df[f"mkt_score_{REGIME_TF}"] <= -1, "exit_long"] = 1
        return df


class PusulaTrendLongRS(PusulaTrendLong):
    """
    Improvement round 2b (2026-10-10): long only when the coin is at least as
    strong as Bitcoin over the momentum window (coin 90-day return >= BTC's).
    BTC itself always passes. Exits unchanged.
    """

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["long"]["stronger_than_btc"] = df[f"mom_{REGIME_TF}"] >= df[f"mkt_mom_{REGIME_TF}"]
        return conds


class PusulaV2(PusulaTrendLongBtcExit):
    """
    Collects the improvements accepted in the background rounds (better on both
    the old 16 and the new 20 coins). Accepted so far: round 2a (BTC-turn exit).
    The frozen PusulaTrendLong in the paper test is not changed.
    """


class TwoSpeedExitMixin:
    """
    Round 3 (fixed before testing, card section "3. tur"): two-speed exit.
    Once the trade has been at least `fast_exit_after_r` in profit at any time,
    it is also closed when a 4h candle closes beyond the opposite 20-candle
    channel (long: below the previous 20-candle low). The slow daily EMA20 exit
    stays as before. Aim: give back less of a big open profit.
    """

    fast_exit_after_r = 4.0

    def custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        plan = self._plan_for_trade(trade)
        last = self._last_row(pair)
        if plan is None or last is None:
            return None
        risk = abs(plan["entry"] - plan["stop"])
        if risk <= 0:
            return None
        if trade.is_short:
            best_r = (trade.open_rate - (trade.min_rate or trade.open_rate)) / risk
            broke = last["close"] > last["dc_upper"]
        else:
            best_r = ((trade.max_rate or trade.open_rate) - trade.open_rate) / risk
            broke = last["close"] < last["dc_lower"]
        if best_r >= self.fast_exit_after_r and broke:
            return "fast_exit_4h"
        return None


class PusulaTrend2(TwoSpeedExitMixin, PusulaTrend):
    pass


class PusulaTrendLong2(TwoSpeedExitMixin, PusulaTrendLong):
    pass


class PusulaTrendLongClose(PusulaTrendLong):
    """Round 3 test: limit entry at the breakout candle close (no 0.25 ATR pullback), so fast breakouts are not missed."""

    from strategies.common import trade_management as _tm
    mgmt = _tm.ManagementParams(entry_zone_atr=0.0)


class PusulaTrendLongBE1(PusulaTrendLong):
    """Round 3 test: stop moves to break even after 1R in favour instead of 2R."""

    @property
    def tp_model(self):
        from strategies.common import trade_management as tm
        return tm.TPModel(name="BE1", tp1_r=1.0, tp2_r=1.0, tp1_close_pct=0, breakeven_trigger="TP1")


# ---------------------------------------------------------------------------
# Round 4 stress tests (not candidates): same rules under worse conditions.
# ---------------------------------------------------------------------------


class PusulaTrendLongLate(PusulaTrendLong):
    """Stress test: every signal is acted on one 4h candle late (plan from that later candle)."""

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        return {side: {k: v.shift(1, fill_value=False) for k, v in c.items()} for side, c in conds.items()}


class PusulaTrendLong1h(PusulaTrendLong):
    """Stress test: the same rules with 1h candles for the breakout, stop and plan."""

    timeframe = "1h"
    startup_candle_count = 2400  # 100 days of 1h candles; the daily data gets enough history too


class PusulaTrendLongStrictBTC(PusulaTrendLong):
    """Round 4 test: longs only when BTC is also in a strong uptrend (score +3), against long losing streaks after a market top."""

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["long"]["market_up"] = df[f"mkt_score_{REGIME_TF}"] >= 3
        return conds
