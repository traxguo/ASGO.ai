import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")
pytest.importorskip("talib")

from strategies.candidates import pusula  # noqa: E402


def daily(closes, start="2021-01-01"):
    closes = np.asarray(closes, dtype=float)
    return pd.DataFrame({
        "date": pd.date_range(start, periods=len(closes), freq="1D", tz="UTC"),
        "open": closes, "high": closes * 1.01, "low": closes * 0.99, "close": closes, "volume": 1.0,
    })


def test_steady_rise_is_up_and_steady_fall_is_down():
    up = pusula.regime_score(daily(np.linspace(100, 300, 200)))
    down = pusula.regime_score(daily(np.linspace(300, 100, 200)))
    assert up.iloc[-1] == 3 and pusula.regime_label(up.iloc[-1]) == "up"
    assert down.iloc[-1] == -3 and pusula.regime_label(down.iloc[-1]) == "down"


def test_no_score_before_enough_history():
    s = pusula.regime_score(daily(np.linspace(100, 300, 200)))
    assert s.iloc[: pusula.MOMENTUM_DAYS].isna().all()
    assert pusula.regime_label(s.iloc[0]) == "unknown"


def test_rise_then_sharp_drop_is_mixed():
    # long rise, then a drop below EMA50 while the 90-day return is still positive
    closes = np.concatenate([np.linspace(100, 300, 180), np.linspace(300, 220, 10)])
    s = pusula.regime_score(daily(closes))
    assert pusula.regime_label(s.iloc[-1]) == "mixed"


def test_score_uses_only_past_data():
    closes = np.concatenate([np.linspace(100, 300, 150), np.linspace(300, 50, 50)])
    full = pusula.regime_score(daily(closes))
    cut = pusula.regime_score(daily(closes[:160]))
    pd.testing.assert_series_equal(full.iloc[:160], cut, check_names=False)


def test_market_score_joined_by_date():
    coin = daily(np.linspace(100, 300, 200))
    btc = daily(np.linspace(300, 100, 200))
    frame = pusula.daily_regime_frame(coin, btc)
    assert frame["score"].iloc[-1] == 3 and frame["mkt_score"].iloc[-1] == -3


def _row(score, mkt, close=100.0):
    return {"close": close, "atr": 2.0, "dc_upper": 102.0, "dc_lower": 95.0, "swing_low": 97.0, "swing_high": 103.0,
            "score_1d": score, "mkt_score_1d": mkt, "ema_slow_1d": 90.0, "mom_1d": 0.25}


def test_commentary_gives_long_plan_in_uptrend():
    v = pusula.commentary(_row(3, 2), "ETH/USDT:USDT")
    assert v["side"] == "long" and v["trigger"] == 102.0
    p = v["plan"]
    assert p["stop"] < p["zone_low"] < p["zone_high"] <= 102.0 < p["tp1"] < p["tp2"]
    assert "LONG tetiği" in v["text"]


def test_commentary_no_trade_when_mixed_or_market_disagrees():
    assert pusula.commentary(_row(1, 2), "ETH/USDT:USDT")["side"] is None
    assert pusula.commentary(_row(-3, 1), "ETH/USDT:USDT")["side"] is None
    assert pusula.commentary(_row(-3, -2), "ETH/USDT:USDT")["side"] == "short"


def test_kalabalik_funding_rank_uses_only_past_prints():
    from strategies.candidates import kalabalik as k
    n = k.LOOKBACK_PRINTS + 50
    rates = np.linspace(-0.0001, 0.0003, n)
    f = pd.DataFrame({"date": pd.date_range("2021-01-01", periods=n, freq="8h", tz="UTC"), "funding_rate": rates})
    full = k.funding_features(f)
    cut = k.funding_features(f.iloc[: n - 20])
    pd.testing.assert_frame_equal(full.iloc[: n - 20], cut)
    assert full["pct_rank"].iloc[-1] == 1.0  # rising rates: newest is the highest of the past year


def test_v2_no_be_keeps_planned_stop_after_2r():
    """PusulaV2NoBe: the stop stays at the planned level even after a 2R+ move; the baseline moves it to entry."""
    from types import SimpleNamespace

    plan = {"side": "long", "entry": 100.0, "stop": 90.0, "tp1": 120.0, "tp2": 140.0}
    trade = SimpleNamespace(is_short=False, leverage=1.0, open_rate=100.0, max_rate=125.0, min_rate=99.0,
                            nr_of_successful_exits=0)
    rate = 124.0

    def stop_level(cls):
        strat = cls.__new__(cls)
        strat._plan_for_trade = lambda t: plan
        sl = strat.custom_stoploss("X/USDT:USDT", trade, None, rate, 0.24, False)
        return rate * (1 - sl)  # stoploss_from_absolute returns the distance below the rate for longs

    assert issubclass(pusula.PusulaV2NoBe, pusula.PusulaV2NoBtcScore1)
    assert stop_level(pusula.PusulaV2NoBe) == pytest.approx(90.0)
    assert stop_level(pusula.PusulaV2NoBtcScore1) > 100.0


def test_v2_no_be_ema50_exits_on_ema50_not_ema20():
    """PusulaV2NoBeEma50: close between EMA50 and EMA20 keeps the long; below EMA50 or BTC turn closes it."""
    tf = pusula.REGIME_TF
    df = pd.DataFrame({
        f"close_{tf}": [105.0, 95.0, 105.0, 110.0],
        f"ema_fast_{tf}": [110.0, 110.0, 100.0, 100.0],
        f"ema_slow_{tf}": [100.0, 100.0, 100.0, 100.0],
        f"mkt_score_{tf}": [1, 1, 1, -1],
    })

    def exits(cls):
        strat = cls.__new__(cls)
        out = strat.populate_exit_trend(df.copy(), {"pair": "X/USDT:USDT"})
        return out.get("exit_long", pd.Series(np.nan, index=df.index)).fillna(0).astype(int).tolist()

    assert issubclass(pusula.PusulaV2NoBeEma50, pusula.PusulaV2NoBe)
    assert exits(pusula.PusulaV2NoBe) == [1, 1, 0, 1]
    assert exits(pusula.PusulaV2NoBeEma50) == [0, 1, 0, 1]


def test_v2_no_be_no_btc_exit_keeps_only_ema20_exit():
    """PusulaV2NoBeNoBtcExit: BTC score <= -1 no longer closes the long; daily close below EMA20 still does."""
    tf = pusula.REGIME_TF
    df = pd.DataFrame({
        f"close_{tf}": [105.0, 95.0, 105.0, 95.0],
        f"ema_fast_{tf}": [100.0, 100.0, 100.0, 100.0],
        f"ema_slow_{tf}": [100.0, 100.0, 100.0, 100.0],
        f"mkt_score_{tf}": [1, 1, -1, -3],
    })

    def exits(cls):
        strat = cls.__new__(cls)
        out = strat.populate_exit_trend(df.copy(), {"pair": "X/USDT:USDT"})
        return out.get("exit_long", pd.Series(np.nan, index=df.index)).fillna(0).astype(int).tolist()

    assert issubclass(pusula.PusulaV2NoBeNoBtcExit, pusula.PusulaV2NoBe)
    assert exits(pusula.PusulaV2NoBe) == [0, 1, 1, 1]
    assert exits(pusula.PusulaV2NoBeNoBtcExit) == [0, 1, 0, 1]


def test_v2_no_be_no_reentry_one_trade_per_daily_long_regime():
    """PusulaV2NoBeNoReentry: no second trade on a coin in the same daily long regime; after a score below +1 it is allowed."""
    from types import SimpleNamespace

    cls = pusula.PusulaV2NoBeNoReentry
    days = pd.date_range("2022-01-01", periods=8, freq="1D", tz="UTC")
    scores = pd.DataFrame({"date": days, "score": [1, 3, 3, 1, -1, 1, 3, 3]})
    strat = cls.__new__(cls)
    strat._daily_scores = lambda pair: scores
    # last trade: signal candle 2022-01-02 16:00 (sees dailies closed by 20:00), opened 20:00, closed 2022-01-04
    last = SimpleNamespace(open_date_utc=pd.Timestamp("2022-01-02 21:00", tz="UTC"),
                           close_date_utc=pd.Timestamp("2022-01-04", tz="UTC"))
    strat._closed_trades = lambda pair: [last]

    def allowed(when):
        return strat.confirm_trade_entry("X/USDT:USDT", "limit", 1.0, 1.0, "GTC", pd.Timestamp(when, tz="UTC"),
                                         "long", "long")

    assert not allowed("2022-01-05 00:00")  # dailies of 01-02..01-04 closed: +3, +3, +1 -> same regime
    assert allowed("2022-01-06 00:00")  # 01-05 daily (-1) closed: the regime left long
    assert allowed("2022-01-08 04:00")
    strat._closed_trades = lambda pair: []
    assert allowed("2022-01-05 00:00")  # no earlier trade on the coin
    assert issubclass(cls, pusula.PusulaV2NoBe)


def test_v2_no_be_rank_prefers_strongest_90d_return_when_slots_are_short():
    """PusulaV2NoBeRank: more same-candle signals than free slots -> only the highest 90-day returns may enter."""
    from datetime import datetime, timezone
    from types import SimpleNamespace

    cls = pusula.PusulaV2NoBeRank
    sig = pd.Timestamp("2022-03-01 04:00", tz="UTC")  # last closed 4h candle at 08:00
    strat = cls.__new__(cls)
    strat._signal_book = {"A": {sig: 0.10}, "B": {sig: 0.50}, "C": {sig: 0.30}, "D": {sig - pd.Timedelta(hours=4): 9.0}}
    strat._whitelist = lambda: ["A", "B", "C", "D", "E"]
    strat._max_open = lambda: 3
    open_trades = [SimpleNamespace(pair="E", close_date_utc=None)]
    strat._trades = lambda is_open: open_trades if is_open else []
    now = datetime(2022, 3, 1, 9, 0, tzinfo=timezone.utc)  # a 1h detail candle inside the 08:00 candle

    def allowed(pair):
        return strat.confirm_trade_entry(pair, "limit", 1.0, 1.0, "GTC", now, "long", "long")

    assert strat.rank_candidates(now) == (["B", "C", "A"], 2)  # D's signal is an older candle; E is busy
    assert allowed("B") and allowed("C") and not allowed("A")
    open_trades.clear()  # three free slots: no collision, everybody may enter
    assert allowed("A")
    probe = pusula.PusulaV2NoBeRankProbe.__new__(pusula.PusulaV2NoBeRankProbe)
    probe.__dict__.update(strat.__dict__)
    open_trades.append(SimpleNamespace(pair="E", close_date_utc=None))
    assert probe.confirm_trade_entry("A", "limit", 1.0, 1.0, "GTC", now, "long", "long")  # probe = baseline order
    assert issubclass(cls, pusula.PusulaV2NoBe)


def test_v2_no_be_weekly_uses_only_closed_monday_weeks():
    """PusulaV2NoBeWeekly: weeks start Monday 00:00 UTC, running weeks are dropped, a week is seen only after it closes."""
    start = "2021-01-01"  # a Friday: the first (partial) week is dropped
    closes = np.arange(1, 501, dtype=float) + 100
    d = daily(closes, start=start)
    w = pusula.weekly_from_daily(d)
    assert (w["date"].dt.dayofweek == 0).all() and w["date"].iloc[0] == pd.Timestamp("2021-01-04", tz="UTC")
    last_day = d["date"].iloc[-1]
    assert w["date"].iloc[-1] + pd.Timedelta(days=7) <= last_day + pd.Timedelta(days=1)  # no running week
    sunday = d.loc[d["date"] == pd.Timestamp("2021-01-10", tz="UTC"), "close"].iloc[0]
    assert w["close"].iloc[0] == sunday

    h4 = pd.DataFrame({"date": pd.date_range("2021-06-01", "2022-04-01", freq="4h", tz="UTC")})
    h4["close"] = 1.0
    out = pusula.add_weekly_regime(h4, d, d, "4h")
    tf = pusula.WEEKLY_TF

    def seen_close(when):
        return out.loc[out["date"] == pd.Timestamp(when, tz="UTC"), f"close_{tf}"].iloc[0]

    def day_close(when):
        return d.loc[d["date"] == pd.Timestamp(when, tz="UTC"), "close"].iloc[0]

    # Week Mon 2021-12-06 .. Sun 12-12 closes Mon 12-13 00:00 = close of the 4h candle starting Sun 20:00.
    assert seen_close("2021-12-12 20:00") == day_close("2021-12-12")
    assert seen_close("2021-12-12 16:00") == day_close("2021-12-05")  # that week still running: previous week
    assert seen_close("2021-12-09 08:00") == day_close("2021-12-05")

    # Cutting the daily data mid-week does not change any score already visible (no lookahead).
    cut = pusula.add_weekly_regime(h4, d[d["date"] <= pd.Timestamp("2022-01-12", tz="UTC")], d, "4h")
    upto = out["date"] <= pd.Timestamp("2022-01-09 20:00", tz="UTC")
    pd.testing.assert_series_equal(out.loc[upto, f"score_{tf}"], cut.loc[upto, f"score_{tf}"])
    assert out[f"score_{tf}"].dropna().iloc[-1] == 3  # steady rise -> +3 on the weekly chart too
    assert issubclass(pusula.PusulaV2NoBeWeekly, pusula.PusulaV2NoBe)


def test_v2_no_be_weekly_btc_exit_on_weekly_score():
    """PusulaV2NoBeWeekly: BTC-turn exit reads the weekly BTC score; the daily EMA20 exit is unchanged."""
    df = pd.DataFrame({
        "close_1d": [105.0, 95.0, 105.0, 105.0],
        "ema_fast_1d": [100.0, 100.0, 100.0, 100.0],
        "ema_slow_1d": [100.0, 100.0, 100.0, 100.0],
        "mkt_score_1d": [-1, 1, -1, 1],
        "mkt_score_1w": [1, 1, 1, -1],
    })
    strat = pusula.PusulaV2NoBeWeekly.__new__(pusula.PusulaV2NoBeWeekly)
    out = strat.populate_exit_trend(df.copy(), {"pair": "X/USDT:USDT"})
    assert out["exit_long"].fillna(0).astype(int).tolist() == [0, 1, 0, 1]


def test_v2_no_be_5_slots_keep_total_open_risk_of_3_slots():
    from strategies.common import trade_management as tm

    base, five = pusula.PusulaV2NoBe, pusula.PusulaV2NoBe5
    assert five.max_open_trades == 5
    assert five.mgmt.risk_per_trade == pytest.approx(base.mgmt.risk_per_trade * 3 / 5)
    assert 5 * five.mgmt.risk_per_trade == pytest.approx(3 * base.mgmt.risk_per_trade)
    # only the risk changes; every other management rule is the baseline's
    assert {k: v for k, v in vars(five.mgmt).items() if k != "risk_per_trade"} == \
        {k: v for k, v in vars(base.mgmt).items() if k != "risk_per_trade"}
    # a stop-out loses 0.6% of equity: notional scales with the risk
    n_base = tm.position_notional(10_000, 100.0, 95.0, base.mgmt)
    n_five = tm.position_notional(10_000, 100.0, 95.0, five.mgmt)
    assert n_five * 0.05 == pytest.approx(60.0) and n_five == pytest.approx(n_base * 0.6)
    assert five.custom_stoploss is base.custom_stoploss


def test_v2_no_be_no_breakout_enters_on_every_trend_candle_with_same_stop():
    """PusulaV2NoBeNoBreakout: only the 4h breakout condition is dropped; stop/plan columns are the baseline's."""
    tf = pusula.REGIME_TF
    n = 8
    close = [100.0, 101.0, 102.0, 101.5, 101.0, 100.5, 101.0, 102.0]
    df = pd.DataFrame({
        "close": close,
        "high": [c + 0.5 for c in close],
        "low": [c - 0.5 for c in close],
        "atr": [1.0] * n,
        "swing_low": [99.0] * n,
        "swing_high": [103.0] * n,
        # previous 20-candle high: only candle 2 breaks it
        "dc_upper": [101.0, 101.5, 101.5, 102.5, 102.5, 102.5, 102.5, 102.5],
        "dc_lower": [90.0] * n,
        f"score_{tf}": [1, 1, 1, 1, 1, -1, 1, 3],
        f"close_{tf}": [105.0, 105.0, 105.0, 105.0, 95.0, 105.0, 105.0, 105.0],
        f"ema_fast_{tf}": [100.0] * n,
        f"mkt_score_{tf}": [1] * n,
    })

    def entries(cls):
        strat = cls.__new__(cls)
        strat.mgmt = cls.mgmt
        out = strat.populate_entry_trend(df.copy(), {"pair": "X/USDT:USDT"})
        return out, out.get("enter_long", pd.Series(np.nan, index=df.index)).fillna(0).astype(int).tolist()

    base_df, base = entries(pusula.PusulaV2NoBe)
    nb_df, nb = entries(pusula.PusulaV2NoBeNoBreakout)
    assert issubclass(pusula.PusulaV2NoBeNoBreakout, pusula.PusulaV2NoBe)
    assert base == [0, 0, 1, 0, 0, 0, 0, 0]
    # score >= +1 and daily close above EMA20 -> signal, breakout or not
    assert nb == [1, 1, 1, 1, 0, 0, 1, 1]
    pd.testing.assert_series_equal(base_df["long_stop"], nb_df["long_stop"])
    pd.testing.assert_series_equal(base_df["long_entry"], nb_df["long_entry"])
    assert pusula.PusulaV2NoBeNoBreakout.custom_stoploss is pusula.PusulaV2NoBe.custom_stoploss
    assert pusula.PusulaV2NoBeNoBreakout.populate_exit_trend is pusula.PusulaV2NoBe.populate_exit_trend


def test_v2_no_be_atr_stop_uses_only_1_5_atr_stop():
    """PusulaV2NoBeAtrStop: stop = entry_mid - 1.5 ATR, the swing low is ignored; entries unchanged."""
    tf = pusula.REGIME_TF
    n = 4
    close = [100.0, 101.0, 102.0, 103.0]
    df = pd.DataFrame({
        "close": close,
        "high": [c + 0.5 for c in close],
        "low": [c - 0.5 for c in close],
        "atr": [1.0] * n,
        # candle 2: swing stop (95.9) wider than ATR stop -> baseline uses swing, new class ATR
        # candle 3: swing stop above ATR stop -> both use the ATR stop
        "swing_low": [99.0, 99.0, 96.0, 102.5],
        "swing_high": [104.0] * n,
        "dc_upper": [101.0, 101.5, 101.5, 102.5],
        "dc_lower": [90.0] * n,
        f"score_{tf}": [1] * n,
        f"close_{tf}": [105.0] * n,
        f"ema_fast_{tf}": [100.0] * n,
        f"mkt_score_{tf}": [1] * n,
    })

    def run(cls):
        strat = cls.__new__(cls)
        strat.mgmt = cls.mgmt
        return strat.populate_entry_trend(df.copy(), {"pair": "X/USDT:USDT"})

    base, atr = run(pusula.PusulaV2NoBe), run(pusula.PusulaV2NoBeAtrStop)
    assert issubclass(pusula.PusulaV2NoBeAtrStop, pusula.PusulaV2NoBe)
    assert pusula.PusulaV2NoBe.mgmt.stop_method == "wider"
    assert pusula.PusulaV2NoBeAtrStop.mgmt.stop_method == "atr"
    mid = df["close"] - 0.125 * df["atr"]
    np.testing.assert_allclose(atr["long_stop"], mid - 1.5 * df["atr"])
    assert base["long_stop"].iloc[2] == pytest.approx(96.0 - 0.1)
    assert base["long_stop"].iloc[3] == pytest.approx(atr["long_stop"].iloc[3])
    pd.testing.assert_series_equal(base["long_entry"], atr["long_entry"])
    pd.testing.assert_series_equal(base["enter_long"].fillna(0), atr["enter_long"].fillna(0))
    assert pusula.PusulaV2NoBeAtrStop.custom_stoploss is pusula.PusulaV2NoBe.custom_stoploss
    assert pusula.PusulaV2NoBeAtrStop.populate_exit_trend is pusula.PusulaV2NoBe.populate_exit_trend
