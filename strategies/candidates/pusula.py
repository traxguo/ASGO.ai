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
from freqtrade.exchange import timeframe_to_minutes, timeframe_to_prev_date  # noqa: E402
from freqtrade.strategy import merge_informative_pair, stoploss_from_absolute  # noqa: E402
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


class PusulaV2Vol(PusulaV2):
    """
    Improvement round 3a (2026-10-10, fixed before testing): long breakout only
    when the breakout 4h candle's volume is at least 1.5x the average volume of
    the previous 20 candles.
    """

    volume_mult = 1.5

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_indicators(df, metadata)
        df["vol_avg20"] = df["volume"].rolling(20).mean().shift(1)
        return df

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["long"]["volume_confirm"] = df["volume"] >= self.volume_mult * df["vol_avg20"]
        return conds


class PusulaV2Time(PusulaV2):
    """
    Improvement round 3b (2026-10-10, fixed before testing): time stop. A long
    that has never been 1R in profit after 10 days is closed. Winners last about
    14 days on average, losers about 4; a trade going nowhere for 10 days ties up
    one of the 3 slots.
    """

    time_stop_days = 10
    time_stop_min_r = 1.0

    def custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        if (current_time - trade.open_date_utc).days < self.time_stop_days:
            return None
        plan = self._plan_for_trade(trade)
        if plan is None:
            return None
        risk = abs(plan["entry"] - plan["stop"])
        if risk <= 0:
            return None
        best_r = ((trade.max_rate or trade.open_rate) - trade.open_rate) / risk
        if best_r < self.time_stop_min_r:
            return "time_stop"
        return None


class PusulaV2NoBtcFilter(PusulaV2):
    """
    Removal round 1 (2026-10-10, research/queue/pusula_kuyruk.md item 2): PusulaV2
    without the BTC entry filter (no "BTC score >= +1" condition for longs).
    BTC daily data is still loaded, because the accepted BTC-turn exit (round 2a)
    still uses it; only the entry condition is dropped.
    """

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["long"].pop("market_up", None)
        return conds


class PusulaV2NoBtcScore1(PusulaV2NoBtcFilter):
    """
    Removal round 2 (2026-10-11, research/queue/pusula_kuyruk.md item 2): the
    accepted round-1 version with a looser daily regime threshold for longs:
    coin score >= +1 instead of +3. The score can only be -3, -1, +1 or +3, so
    "+2" in the queue means +1 in practice. Nothing else changes.
    """

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["long"]["regime_up"] = df[f"score_{REGIME_TF}"] >= 1
        return conds


class PusulaV2NoBe(PusulaV2NoBtcScore1):
    """
    Removal round 3 (2026-10-11, research/queue/pusula_kuyruk.md item 2): the
    accepted round-2 version without the "stop to break even at 2R" rule. The
    planned stop never moves; the trade ends at that stop, the daily EMA20 exit
    or the BTC-turn exit. Entries and everything else are unchanged.
    """

    def custom_stoploss(self, pair, trade, current_time, current_rate, current_profit, after_fill, **kwargs):
        plan = self._plan_for_trade(trade)
        if plan is None:
            return None
        return stoploss_from_absolute(plan["stop"], current_rate, is_short=trade.is_short, leverage=trade.leverage)



class PusulaV2NoBeEma50(PusulaV2NoBe):
    """
    Removal round 4 (2026-10-12, research/queue/pusula_kuyruk.md item 2): the
    accepted round-3 version with a slower trend exit: a long is closed when the
    last closed daily close is below the daily EMA(50) instead of the EMA(20)
    (short mirror: above EMA50). The BTC-turn exit, the fixed stop and the entry
    conditions are unchanged. Note: Freqtrade ignores an entry on a candle that
    also has an exit signal, so as before no trade opens while the exit rule is
    already true (here: daily close below EMA50).
    """

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        close_1d, ema_slow = df[f"close_{REGIME_TF}"], df[f"ema_slow_{REGIME_TF}"]
        df.loc[close_1d < ema_slow, "exit_long"] = 1
        df.loc[close_1d > ema_slow, "exit_short"] = 1
        df.loc[df[f"mkt_score_{REGIME_TF}"] <= -1, "exit_long"] = 1  # BTC-turn exit (round 2a), unchanged
        return df


class PusulaV2NoBeNoBtcExit(PusulaV2NoBe):
    """
    Removal round 5 (2026-10-13, research/queue/pusula_kuyruk.md item 2): the
    accepted round-3 version without the BTC-turn exit (round 2a: close longs
    when the last closed daily BTC score is -1 or lower). The daily EMA20 trend
    exit and the fixed stop stay. Side effect: Freqtrade ignores an entry on a
    candle that also has an exit signal, so until now no long could open while
    the BTC score was <= -1; the BTC entry filter was already removed in round 1,
    so without this exit longs can now open while BTC's score is <= -1.
    """

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        # Skip PusulaTrendLongBtcExit's override: only the EMA20 trend exit remains.
        return super(PusulaTrendLongBtcExit, self).populate_exit_trend(df, metadata)


class PusulaV2NoBeNoReentry(PusulaV2NoBe):
    """
    Queue item 6 (2026-10-17, research/queue/pusula_kuyruk.md), fixed before testing.

    What PusulaV2NoBe already does: after a trade on a coin closes (stop or
    EMA20/BTC exit), it may open a new long on that coin on the next FRESH
    breakout candle (first 4h close above the previous 20-candle high after a
    candle that was not above it) whenever all entry conditions hold again.
    There is no cooldown or per-trend limit, and no adding while a trade is open
    (one trade per pair, adjust_trade_position places no orders). So "re-entry on
    a second breakout while the trend lasts" is already in the baseline.

    This variant is the stricter alternative that actually differs: at most one
    trade per coin per daily long regime. A regime run is an unbroken stretch of
    4h candles where the last closed daily score of the coin is >= +1. After a
    trade closes, a new long on the same coin is refused until the score has been
    <= -1 at least once and a new run has started. Everything else unchanged.
    """

    # Implementation note: the check reads the coin's own daily candles, not the
    # analysed 4h frame, because in backtesting that frame only holds the last
    # 1000 candles (~166 days) and a regime run can last longer.

    def _closed_trades(self, pair: str):
        from freqtrade.persistence import Trade

        return Trade.get_trades_proxy(pair=pair, is_open=False)

    def _daily_scores(self, pair: str) -> DataFrame:
        daily = self.dp.get_pair_dataframe(pair=pair, timeframe=REGIME_TF)
        return pd.DataFrame({"date": daily["date"], "score": regime_score(daily, self.ema_fast, self.ema_slow,
                                                                          self.momentum_days)})

    def regime_left_long_since(self, pair: str, since, now) -> bool:
        """True if a daily candle that closed after `since` and by `now` had a score below +1."""
        d = self._daily_scores(pair)
        closes = d["date"] + pd.Timedelta(days=1)
        window = d.loc[(closes > since) & (closes <= now), "score"]
        return bool((window < 1).any())

    def confirm_trade_entry(self, pair, order_type, amount, rate, time_in_force, current_time, entry_tag, side,
                            **kwargs) -> bool:
        closed = [t for t in self._closed_trades(pair) if t.close_date_utc is not None]
        if not closed:
            return True
        last = max(closed, key=lambda t: t.close_date_utc)
        # What the last trade's signal saw: daily candles closed by the end of its signal candle.
        last_seen = self._signal_time_for_trade(last) + pd.Timedelta(minutes=timeframe_to_minutes(self.timeframe))
        # Same daily long regime as the last closed trade -> no second trade on this coin.
        return self.regime_left_long_since(pair, last_seen, current_time)


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


class PusulaV2NoBeRank(PusulaV2NoBe):
    """
    Queue item 7 (2026-10-18, research/queue/pusula_kuyruk.md), fixed before testing.

    Coin selection when signals collide. PusulaV2NoBe takes same-candle entry
    signals in Freqtrade's pair order (pairs with open trades first, then the
    whitelist order) until the 3 slots are full. This variant ranks them instead:

    - Candidates at a moment: every whitelist pair with a valid long signal on
      the last closed 4h candle (all entry conditions true and no exit signal on
      that candle, exactly what Freqtrade would act on), no open trade or pending
      entry order on that pair, and no trade on that pair that closed during the
      current 4h candle (Freqtrade skips such a pair for that candle).
    - Free slots = max_open_trades - open trades (pending entry orders count).
    - If candidates > free slots, only the `free` candidates with the highest
      90-day return (last closed daily close / daily close 90 days earlier - 1,
      the `mom` column of the regime) may enter; ties go to whitelist order.
      Otherwise nothing changes. Everything else is PusulaV2NoBe.

    The check runs in confirm_trade_entry, so it is evaluated whenever Freqtrade
    would open a trade (also on 1h detail candles when a slot frees mid-candle).
    It reads a book of signal candles filled in populate_exit_trend; it only looks
    up the candle that has just closed, never a later one.
    """

    rank_enabled = True  # False = baseline behaviour, used by the collision probe below

    def _book(self) -> dict:
        if not hasattr(self, "_signal_book"):
            self._signal_book = {}
        return self._signal_book

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_exit_trend(df, metadata)
        enter = df.get("enter_long", pd.Series(0, index=df.index)).fillna(0) == 1
        exit_ = df.get("exit_long", pd.Series(0, index=df.index)).fillna(0) == 1
        valid = enter & ~exit_
        self._book()[metadata["pair"]] = dict(zip(df.loc[valid, "date"], df.loc[valid, f"mom_{REGIME_TF}"]))
        return df

    def _whitelist(self) -> list:
        return list(self.dp.current_whitelist())

    def _trades(self, is_open: bool):
        from freqtrade.persistence import Trade

        return Trade.get_trades_proxy(is_open=is_open)

    def _max_open(self) -> int:
        return int(self.config.get("max_open_trades", self.max_open_trades))

    def rank_candidates(self, current_time):
        """(ordered candidate pairs, free slots) at current_time, from data closed by then."""
        candle = timeframe_to_prev_date(self.timeframe, current_time)  # current 4h candle start
        signal_time = candle - pd.Timedelta(minutes=timeframe_to_minutes(self.timeframe))
        open_trades = list(self._trades(True))
        busy = {t.pair for t in open_trades}
        busy |= {t.pair for t in self._trades(False) if t.close_date_utc is not None and t.close_date_utc >= candle}
        book = self._book()
        cands = []
        for i, pair in enumerate(self._whitelist()):
            mom = book.get(pair, {}).get(signal_time)
            if mom is None or pair in busy:
                continue
            cands.append((-(mom if pd.notna(mom) else -np.inf), i, pair))
        cands.sort()
        free = self._max_open() - len(open_trades)
        return [c[2] for c in cands], free

    def confirm_trade_entry(self, pair, order_type, amount, rate, time_in_force, current_time, entry_tag, side,
                            **kwargs) -> bool:
        if side != "long":
            return True
        ranked, free = self.rank_candidates(current_time)
        if len(ranked) > free:
            self._log_collision(pair, current_time, ranked, free)
            if self.rank_enabled:
                return pair in ranked[:max(free, 0)] or pair not in ranked
        return True

    def _log_collision(self, pair, current_time, ranked, free):
        import json
        import os

        path = os.environ.get("PUSULA_COLLISION_LOG")
        if not path:
            return
        rec = {"strategy": self.__class__.__name__, "time": str(current_time), "pair": pair, "free": free,
               "candidates": ranked, "allowed": ranked[:max(free, 0)]}
        with open(path, "a") as f:
            f.write(json.dumps(rec) + "\n")


class PusulaV2NoBeRankProbe(PusulaV2NoBeRank):
    """Diagnostic only (queue item 7): PusulaV2NoBe behaviour (no ranking), logs signal collisions."""

    rank_enabled = False


# ---------------------------------------------------------------------------
# Queue item 10 (2026-10-19): the regime read from the weekly chart.
# ---------------------------------------------------------------------------

WEEKLY_TF = "1w"
WEEKLY_MOMENTUM_WEEKS = 13  # 91 days, the weekly equivalent of the 90-day momentum window


def weekly_from_daily(daily: DataFrame) -> DataFrame:
    """
    Weekly candles built from daily candles. A week starts Monday 00:00 UTC
    (`date` = that Monday) and closes the next Monday 00:00 UTC. Only full weeks
    (all 7 daily candles present) are kept, so a running week never appears.
    """
    d = daily[["date", "open", "high", "low", "close", "volume"]].copy()
    day = d["date"].dt.floor("D")
    d["week"] = day - pd.to_timedelta(day.dt.dayofweek, unit="D")
    g = d.groupby("week", sort=True)
    w = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                      "close": g["close"].last(), "volume": g["volume"].sum(), "days": g["date"].count()})
    w = w[w["days"] == 7].drop(columns="days").reset_index().rename(columns={"week": "date"})
    return w


def add_weekly_regime(df: DataFrame, daily: DataFrame, market_daily: DataFrame | None, timeframe: str,
                      fast: int = EMA_FAST, slow: int = EMA_SLOW, mom_weeks: int = WEEKLY_MOMENTUM_WEEKS) -> DataFrame:
    """
    Adds the weekly regime columns (`score_1w`, `mkt_score_1w`, `close_1w`, ...)
    to a 4h frame. merge_informative_pair shifts each week to its close, so a 4h
    candle only sees weeks that closed by the end of that candle (no lookahead).
    """
    weekly = weekly_from_daily(daily)
    market_weekly = None if market_daily is None else weekly_from_daily(market_daily)
    regime = daily_regime_frame(weekly, market_weekly, fast, slow, mom_weeks)
    return merge_informative_pair(df, regime, timeframe, WEEKLY_TF, ffill=True)


class PusulaV2NoBeWeekly(PusulaV2NoBe):
    """
    Queue item 10 (2026-10-19, research/queue/pusula_kuyruk.md), fixed before testing.

    PusulaV2NoBe with the regime read from the weekly chart. Weekly candles are
    built from the daily candles (Monday 00:00 UTC week start, only fully closed
    weeks). Same score formula on weekly candles: weekly close vs weekly EMA(50),
    weekly EMA(20) vs weekly EMA(50), 13-week return (= 91 days) sign.

    - Entry: coin's last closed WEEKLY score >= +1 (instead of the daily score),
      plus the unchanged 4h breakout and the unchanged "daily close above daily
      EMA20" condition.
    - Exits: the BTC-turn exit used BTC's daily regime score; it now uses BTC's
      last closed WEEKLY score <= -1. The daily EMA20 trend exit (not a regime
      score) and the fixed planned stop are unchanged.
    """

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_indicators(df, metadata)
        daily = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=REGIME_TF)
        market = self.dp.get_pair_dataframe(pair=MARKET_PAIR, timeframe=REGIME_TF)
        return add_weekly_regime(df, daily, market, self.timeframe, self.ema_fast, self.ema_slow)

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["long"]["regime_up"] = df[f"score_{WEEKLY_TF}"] >= 1
        return conds

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        # Daily EMA20 trend exit unchanged (PusulaTrend); BTC-turn exit on the weekly score.
        df = super(PusulaTrendLongBtcExit, self).populate_exit_trend(df, metadata)
        df.loc[df[f"mkt_score_{WEEKLY_TF}"] <= -1, "exit_long"] = 1
        return df


class PusulaV2NoBe5(PusulaV2NoBe):
    """
    Queue item 11 (2026-10-20, research/queue/pusula_kuyruk.md), fixed before testing.

    PusulaV2NoBe with more, smaller slots. The baseline risks 1% of equity per
    trade (a stop-out loses 1% of total equity) with at most 3 open trades, so
    at most 3% of equity is at risk at once. This version runs with at most 5
    open trades (run with --max-open-trades 5) and risks 1% * 3 / 5 = 0.6% of
    equity per trade, so the total open risk stays at most 3%. Position size
    is still set from the stop distance (custom_stake_amount); leverage cap,
    entries, stop and exits are unchanged.
    """

    max_open_trades = 5
    from dataclasses import replace as _replace

    from strategies.common import trade_management as _tm
    mgmt = _replace(_tm.DEFAULT_PARAMS, risk_per_trade=0.01 * 3 / 5)


class PusulaV2NoBeNoBreakout(PusulaV2NoBe):
    """
    Queue item 12 (2026-10-21, research/queue/pusula_kuyruk.md), removal test,
    fixed before testing.

    PusulaV2NoBe without the 4h breakout trigger ("breakout_up": first 4h close
    above the previous 20-candle high). The remaining long conditions are
    unchanged: last closed daily score >= +1 ("regime_up"), last closed daily
    close above the daily EMA(20) ("daily_above_ema20") and the shared plan
    check (stop distance within the limit). As before, no entry while an exit
    signal is true (daily close below EMA20 or BTC daily score <= -1).

    So the entry signal is on EVERY 4h candle where these hold, not only the
    first one: the first 4h candle after the conditions become true, and, while
    they stay true, any later 4h candle when the coin has no open trade (e.g.
    right after a stop-out, or when a slot frees up). One trade per coin, no
    adding (unchanged).

    Stop and 1R: unchanged. The stop never depended on the breakout level: it is
    the wider of entry_mid - 1.5 ATR and the 10-candle swing low (shared module),
    entry_mid = signal close - half the 0.25 ATR entry zone, all from the signal
    candle. So 1R means the same thing as in the baseline. Exits unchanged
    (fixed stop, daily EMA20 exit, BTC-turn exit).
    """

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["long"].pop("breakout_up", None)
        return conds


class PusulaV2NoBeAtrStop(PusulaV2NoBe):
    """
    Queue item 14 (2026-10-23, research/queue/pusula_kuyruk.md), removal test,
    fixed before testing.

    PusulaV2NoBe without the structural (swing-low) part of the stop. The
    baseline stop is the wider of entry_mid - 1.5 ATR and the 10-candle swing
    low - 0.1 ATR buffer; here it is only entry_mid - 1.5 ATR (shared module
    stop_method="atr"), entry_mid = signal close - 0.125 ATR, all from the
    signal candle. The stop never moves (as in the baseline).

    Consequences (same shared rules, nothing else changed):
    - The stop is never further than the baseline stop, so 1R (stop distance)
      is the same or smaller and the position (1% equity risk) the same or
      larger; leverage is still the highest safe step up to 3x.
    - The plan check (stop distance <= 8% of price) uses this stop, so a signal
      the baseline skipped only because its swing stop was > 8% away can now
      be taken. A trade is skipped when its margin does not fit the free
      balance (unchanged rule).
    Entries and exits (daily EMA20 exit, BTC-turn exit) are unchanged.
    """

    from dataclasses import replace as _replace

    from strategies.common import trade_management as _tm
    mgmt = _replace(_tm.DEFAULT_PARAMS, stop_method="atr")


MATURE_TREND_DAYS = 11


def trend_age(daily: DataFrame) -> Series:
    """Per daily candle: how many consecutive daily candles, ending with this one, have score >= +1."""
    up = (regime_score(daily) >= 1).astype(int)
    run_id = (up == 0).cumsum()
    return up.groupby(run_id).cumsum()


def add_trend_age(df: DataFrame, daily: DataFrame, timeframe_inf: str = REGIME_TF) -> DataFrame:
    """
    Add f"trend_age_{tf}" to a frame already merged with merge_informative_pair:
    the age of the daily candle that row already sees (f"date_{tf}" = last CLOSED
    daily candle), so no lookahead. Rows before any closed daily candle get NaN.
    """
    age = pd.Series(trend_age(daily).to_numpy(), index=pd.DatetimeIndex(daily["date"]))
    df[f"trend_age_{timeframe_inf}"] = df[f"date_{timeframe_inf}"].map(age)
    return df


class PusulaV2NoBeMature(PusulaV2NoBe):
    """
    Queue item 15 (2026-10-24, research/queue/pusula_kuyruk.md), addition test,
    fixed before testing.

    PusulaV2NoBe with one extra long-entry condition ("trend_mature"): the coin's
    daily regime score has been >= +1 for at least 11 consecutive CLOSED daily
    candles, counted up to and including the last daily candle that closed at
    or before the signal 4h candle's close (= the entry candle's open). Same
    definition as research/robustness/pusula_trend_age.py (queue item 13). The
    threshold 11 comes from item 13's buckets fixed before that test (0-10 days
    was the weak group); no sweep. Everything else is unchanged.
    """

    mature_days = MATURE_TREND_DAYS

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_indicators(df, metadata)
        daily = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=REGIME_TF)
        return add_trend_age(df, daily, REGIME_TF)

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        conds["long"]["trend_mature"] = df[f"trend_age_{REGIME_TF}"] >= self.mature_days
        return conds


DD_BRAKE_THRESHOLD = 0.15  # drawdown from the running peak that switches the brake on
DD_BRAKE_RISK = 0.005  # risk per trade while the brake is on (baseline 1%)


def dd_brake_risk(closed_balances, current_equity: float, base_risk: float = 0.01,
                  brake_risk: float = DD_BRAKE_RISK, threshold: float = DD_BRAKE_THRESHOLD) -> float:
    """
    Risk per trade under the drawdown brake.

    closed_balances: the account balance after each closed trade so far, starting
    with the starting balance (closed-trade equity curve, nothing unrealized).
    current_equity: today's closed-trade balance. The running peak is the highest
    of these; if current_equity is >= `threshold` below that peak, return
    brake_risk, else base_risk.
    """
    peak = max([float(b) for b in closed_balances] + [float(current_equity)])
    if peak <= 0:
        return base_risk
    drawdown = 1.0 - float(current_equity) / peak
    return brake_risk if drawdown >= threshold - 1e-12 else base_risk


class PusulaV2NoBeDdBrake(PusulaV2NoBe):
    """
    Queue item 16 (2026-10-25, research/queue/pusula_kuyruk.md), risk rule,
    fixed before testing.

    PusulaV2NoBe with an account drawdown brake. Equity measure: the closed-trade
    balance (starting balance + realized profit of closed trades, funding and
    costs included) - the same number the baseline sizes positions from
    (wallets.get_total_stake_amount() in futures backtest/dry-run). Open trades'
    unrealized profit is ignored, so only what is known at entry time is used.

    At each entry: peak = highest closed-trade balance so far (starting balance
    and the balance after every trade closed before this entry). If the current
    closed-trade balance is 15% or more below that peak, the new trade risks
    0.5% of equity; otherwise 1% (baseline). Thresholds fixed, no sweep.
    Position size from the stop distance as before; entries, stop, leverage cap,
    exits unchanged. The "skip if margin does not fit" rule is unchanged.
    """

    dd_brake_threshold = DD_BRAKE_THRESHOLD
    dd_brake_risk = DD_BRAKE_RISK

    def _closed_balances(self) -> list[float]:
        from freqtrade.persistence import Trade

        start = float(self.wallets.get_starting_balance())
        closed = [t for t in Trade.get_trades_proxy(is_open=False) if t.close_date is not None]
        closed.sort(key=lambda t: t.close_date)
        balances, bal = [start], start
        for t in closed:
            bal += float(t.close_profit_abs or 0.0)
            balances.append(bal)
        return balances

    def custom_stake_amount(self, pair, current_time, current_rate, proposed_stake, min_stake, max_stake, leverage, entry_tag, side, **kwargs) -> float:
        from dataclasses import replace

        from strategies.common import trade_management as tm

        row = self._last_row(pair)
        if row is None:
            return 0.0
        equity = self.wallets.get_total_stake_amount()
        risk = dd_brake_risk(self._closed_balances(), equity, self.mgmt.risk_per_trade,
                             self.dd_brake_risk, self.dd_brake_threshold)
        params = replace(self.mgmt, risk_per_trade=risk)
        notional = tm.position_notional(equity, float(row[f"{side}_entry"]), float(row[f"{side}_stop"]), params)
        stake = notional / leverage
        if stake > max_stake:
            return 0.0
        return stake
