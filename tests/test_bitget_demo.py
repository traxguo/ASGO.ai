from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")
pytest.importorskip("talib")
pytest.importorskip("ccxt")

from scripts import bitget_demo as bd  # noqa: E402

PAIR = "ETH/USDT:USDT"
NOW = datetime(2026, 10, 12, 4, 7, tzinfo=timezone.utc)  # 7 minutes after the 00:00 candle closed
SIGNAL = datetime(2026, 10, 12, 0, 0, tzinfo=timezone.utc)


# ------------------------------------------------------------------ safety


def test_signed_request_without_demo_header_is_stopped():
    with pytest.raises(SystemExit):
        bd.assert_demo_request({"headers": {"ACCESS-KEY": "k"}})
    bd.assert_demo_request({"headers": {"ACCESS-KEY": "k", "PAPTRADING": "1"}})
    bd.assert_demo_request({"headers": {}})  # public request, no key


def test_demo_exchange_signs_with_demo_header():
    ex = bd.demo_exchange("k", "s", "p")
    req = ex.sign("v2/mix/order/place-order", ["private", "mix"], "POST", {"productType": "USDT-FUTURES"})
    assert req["headers"]["PAPTRADING"] == "1"


# ------------------------------------------------------------------ candles


def test_last_closed_candle():
    assert bd.last_closed_open(NOW, 4) == SIGNAL
    assert bd.last_closed_open(NOW, 24) == datetime(2026, 10, 11, tzinfo=timezone.utc)


class CandleSource:
    """fetch_ohlcv with a 200-row page limit, like Bitget."""

    def __init__(self, hours):
        self.step = hours * 3600 * 1000

    def fetch_ohlcv(self, pair, tf, since=None, limit=200):
        end = int(NOW.timestamp() * 1000)
        rows = []
        t = since
        while t <= end and len(rows) < limit:
            rows.append([t, 1.0, 2.0, 0.5, 1.5, 10.0])
            t += self.step
        return rows


def test_fetch_candles_pages_and_drops_forming_candle():
    df = bd.fetch_candles(CandleSource(4), PAIR, "4h", 300, NOW)
    assert len(df) == 300
    assert df["date"].iloc[-1] == pd.Timestamp(SIGNAL)
    assert df["date"].diff().dropna().eq(pd.Timedelta(hours=4)).all()


# ------------------------------------------------------------------ strategy


def synthetic(pair_seed, periods, freq, end):
    rng = np.random.default_rng(pair_seed)
    steps = rng.normal(0.002, 0.02, periods)
    close = 100 * np.exp(np.cumsum(steps))
    dates = pd.date_range(end=end, periods=periods, freq=freq, tz="UTC")
    return pd.DataFrame({"date": dates, "open": close, "high": close * 1.01, "low": close * 0.99,
                         "close": close, "volume": 1.0})


def candles(n4, n1):
    out = {}
    for seed, pair in enumerate([PAIR, "BTC/USDT:USDT"]):
        out[(pair, "4h")] = synthetic(seed, 3000, "4h", pd.Timestamp(SIGNAL)).tail(n4).reset_index(drop=True)
        out[(pair, "1d")] = synthetic(seed + 10, 900, "1D", pd.Timestamp("2026-10-11")).tail(n1).reset_index(drop=True)
    return out


def test_runner_history_gives_same_levels_as_long_history():
    """The runner fetches 300 4h + 400 daily candles; levels on recent candles must match a long history."""
    full = bd.analyze(candles(3000, 900), [PAIR])[PAIR].tail(30).reset_index(drop=True)
    short = bd.analyze(candles(bd.CANDLES_4H, bd.CANDLES_1D), [PAIR])[PAIR].tail(30).reset_index(drop=True)
    for col in ("long_entry", "long_stop", "score_1d", "mkt_score_1d"):
        np.testing.assert_allclose(full[col], short[col], rtol=1e-6)
    for col in ("enter_long", "exit_long"):
        assert full[col].fillna(0).tolist() == short[col].fillna(0).tolist()


# ------------------------------------------------------------------ one pass


class FakeExchange:
    def __init__(self, equity=10_000.0):
        self.equity = equity
        self.orders = {}
        self.positions = {}
        self.trigger_orders = []
        self.my_trades = []
        self.calls = []

    def amount_to_precision(self, pair, amount):
        return f"{amount:.3f}"

    def fetch_balance(self, params=None):
        return {"USDT": {"total": self.equity, "free": self.equity}}

    def set_margin_mode(self, *a, **k):
        self.calls.append(("margin", a))

    def set_leverage(self, lev, pair, params=None):
        self.calls.append(("leverage", lev, pair))

    def create_order(self, pair, type_, side, amount, price=None, params=None):
        params = params or {}
        self.calls.append(("create", pair, type_, side, amount, price, params))
        oid = f"o{len(self.calls)}"
        if "stopLossPrice" in params:
            self.trigger_orders.append({"id": oid, "symbol": pair, "stopLossPrice": params["stopLossPrice"]})
        elif type_ == "market":
            self.positions[pair] = 0.0
            self.my_trades.append({"side": side, "amount": amount, "cost": amount * 110.0, "fee": {"cost": 1.0}})
        else:
            self.orders[oid] = {"id": oid, "status": "open", "filled": 0.0, "price": price, "average": None,
                                "timestamp": int(NOW.timestamp() * 1000), "amount": amount}
        return {"id": oid}

    def fetch_order(self, oid, pair, params=None):
        return self.orders[oid]

    def cancel_order(self, oid, pair, params=None):
        self.calls.append(("cancel", oid))
        if oid in self.orders:
            self.orders[oid]["status"] = "canceled"
        self.trigger_orders = [o for o in self.trigger_orders if o["id"] != oid]

    def fetch_positions(self, pairs, params=None):
        return [{"symbol": p, "contracts": s} for p, s in self.positions.items()]

    def fetch_open_orders(self, pair, params=None):
        return [o for o in self.trigger_orders if o["symbol"] == pair]

    def fetch_my_trades(self, pair, since=None, params=None):
        return self.my_trades

    def fetch_funding_history(self, pair, since=None, params=None):
        return [{"amount": -0.5}]

    def fill(self, oid, price, when):
        o = self.orders[oid]
        o.update(status="closed", filled=o["amount"], average=price,
                 lastTradeTimestamp=int(when.timestamp() * 1000), fee={"cost": 1.0})


def frame(rows):
    """Analysed 4h frame: rows of (date, low, high, enter_long, exit_long)."""
    df = pd.DataFrame(rows, columns=["date", "low", "high", "enter_long", "exit_long"])
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df["long_entry"], df["long_stop"] = 100.0, 95.0
    return df


class Detail:
    def __init__(self, high):
        self.high = high

    def fetch_ohlcv(self, pair, tf, since=None, limit=200):
        return [[since, 100.0, self.high, 99.0, 100.0, 1.0]]


def test_signal_places_limit_entry_with_stop_on_exchange(tmp_path):
    ex, state = FakeExchange(), {"trades": {}}
    analyzed = {PAIR: frame([(SIGNAL, 99, 101, 1, 0)])}
    bd.run_once(ex, None, analyzed, state, NOW, bd.Recorder(tmp_path))
    create = [c for c in ex.calls if c[0] == "create"][0]
    _, pair, type_, side, amount, price, params = create
    assert (pair, type_, side, price) == (PAIR, "limit", "buy", 100.0)
    assert params["stopLoss"] == {"triggerPrice": 95.0}
    assert params["clientOrderId"] == bd.client_id(PAIR, SIGNAL)
    # 1% of 0.99 * equity lost at the stop: 99 USDT over a 5 USDT stop distance
    assert float(amount) == pytest.approx(19.8, abs=1e-3)
    (t,) = state["trades"].values()
    assert t["status"] == "pending" and t["plan_stop"] == 95.0


def test_entry_cancelled_when_stop_touched_before_fill(tmp_path):
    ex, state = FakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: frame([(SIGNAL, 99, 101, 1, 0)])}, state, NOW, bd.Recorder(tmp_path))
    later = NOW + timedelta(hours=4)
    analyzed = {PAIR: frame([(SIGNAL, 99, 101, 1, 0), (SIGNAL + timedelta(hours=4), 94, 99, 0, 0)])}
    bd.run_once(ex, None, analyzed, state, later, bd.Recorder(tmp_path))
    (t,) = state["trades"].values()
    assert t["status"] == "cancelled"


def test_entry_cancelled_after_three_candles(tmp_path):
    ex, state = FakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: frame([(SIGNAL, 99, 101, 1, 0)])}, state, NOW, bd.Recorder(tmp_path))
    rows = [(SIGNAL, 99, 101, 1, 0)] + [(SIGNAL + timedelta(hours=4 * i), 101, 103, 0, 0) for i in (1, 2, 3)]
    bd.run_once(ex, None, {PAIR: frame(rows)}, state, NOW + timedelta(hours=8), bd.Recorder(tmp_path))
    assert next(iter(state["trades"].values()))["status"] == "pending"
    bd.run_once(ex, None, {PAIR: frame(rows)}, state, NOW + timedelta(hours=12), bd.Recorder(tmp_path))
    assert next(iter(state["trades"].values()))["status"] == "cancelled"


def test_fill_then_break_even_then_exit_signal(tmp_path):
    ex, state = FakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: frame([(SIGNAL, 99, 101, 1, 0)])}, state, NOW, bd.Recorder(tmp_path))
    (oid,) = ex.orders
    ex.fill(oid, 100.0, NOW + timedelta(minutes=30))
    ex.positions[PAIR] = ex.orders[oid]["amount"]
    ex.trigger_orders.append({"id": "preset", "symbol": PAIR, "stopLossPrice": 95.0})

    t1 = NOW + timedelta(hours=4)
    rows = [(SIGNAL, 99, 101, 1, 0), (SIGNAL + timedelta(hours=4), 100, 111, 0, 0)]
    bd.run_once(ex, Detail(high=111.0), {PAIR: frame(rows)}, state, t1, bd.Recorder(tmp_path))
    (t,) = state["trades"].values()
    assert t["status"] == "open" and t["breakeven_moved"]
    assert [o["stopLossPrice"] for o in ex.trigger_orders] == [pytest.approx(100.15)]

    t2 = t1 + timedelta(hours=4)
    rows.append((SIGNAL + timedelta(hours=8), 105, 112, 0, 1))
    bd.run_once(ex, Detail(high=112.0), {PAIR: frame(rows)}, state, t2, bd.Recorder(tmp_path))
    assert t["status"] == "closed" and t["exit_reason"] == "exit_signal"
    assert ex.trigger_orders == []
    # +10 per coin on 19.8 coins, minus 2 USDT fees, minus 0.5 funding, over 5 * 19.8 risk
    assert t["r"] == pytest.approx((10 * 19.8 - 2 - 0.5) / (5 * 19.8), abs=1e-3)
    assert (tmp_path / "trades.csv").is_file()


def test_stop_out_detected_when_position_is_gone(tmp_path):
    ex, state = FakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: frame([(SIGNAL, 99, 101, 1, 0)])}, state, NOW, bd.Recorder(tmp_path))
    (oid,) = ex.orders
    ex.fill(oid, 100.0, NOW + timedelta(minutes=30))
    ex.positions[PAIR] = 0.0
    ex.my_trades = [{"side": "sell", "amount": 19.8, "cost": 19.8 * 95.0, "fee": {"cost": 1.0}}]
    bd.run_once(ex, None, {PAIR: frame([(SIGNAL, 99, 101, 1, 0)])}, state, NOW + timedelta(hours=4),
                bd.Recorder(tmp_path))
    (t,) = state["trades"].values()
    assert t["status"] == "closed" and t["exit_reason"] == "stop"
    assert t["r"] == pytest.approx(-1.0 - 2.5 / 99, abs=1e-3)


def test_no_more_than_three_trades(tmp_path):
    ex, state = FakeExchange(), {"trades": {}}
    pairs = ["A/USDT:USDT", "B/USDT:USDT", "C/USDT:USDT", "D/USDT:USDT"]
    analyzed = {p: frame([(SIGNAL, 99, 101, 1, 0)]) for p in pairs}
    bd.run_once(ex, None, analyzed, state, NOW, bd.Recorder(tmp_path))
    assert sorted(t["pair"] for t in state["trades"].values()) == pairs[:3]


def test_demo_balance_accepts_susdt():
    assert bd.demo_balance({"SUSDT": {"total": 3000.0, "free": 2500.0}}) == (3000.0 * 0.99, 2500.0)
    assert bd.demo_balance({"USDT": {"total": 0}, "SUSDT": {"total": 0}}) == (0.0, 0.0)


def test_real_key_is_reported_clearly():
    class Live:
        def fetch_balance(self, params=None):
            raise RuntimeError('bitget {"code":"40099","msg":"exchange environment is incorrect"}')

    with pytest.raises(SystemExit, match="not a Bitget DEMO key"):
        bd.check_demo_key(Live())


def test_play_money_requests_also_carry_demo_header():
    ex = bd.demo_exchange("k", "s", "p")
    req = ex.sign("v2/mix/order/place-order", ["private", "mix"], "POST",
                  {"productType": "SUSDT-FUTURES", "symbol": "SBTCSUSDT"})
    assert req["headers"]["PAPTRADING"] == "1"


def test_symbol_map_translates_both_ways(tmp_path):
    ex = FakeExchange()
    mapped = bd.SymbolMap(ex, {PAIR: "SETH/SUSDT:SUSDT"})
    mapped.create_order(PAIR, "limit", "buy", 1.0, 100.0, {})
    assert ex.calls[-1][1] == "SETH/SUSDT:SUSDT"
    ex.positions["SETH/SUSDT:SUSDT"] = 2.0
    assert bd.position_size(mapped, PAIR) == 2.0
    assert bd.demo_symbols({"SETH/SUSDT:SUSDT": {}}, [PAIR, "XLM/USDT:USDT"]) == {PAIR: "SETH/SUSDT:SUSDT"}


def test_unlisted_demo_coin_is_skipped(tmp_path):
    ex, state = FakeExchange(), {"trades": {}}
    mapped = bd.SymbolMap(ex, {})
    bd.run_once(mapped, None, {PAIR: frame([(SIGNAL, 99, 101, 1, 0)])}, state, NOW, bd.Recorder(tmp_path))
    assert state["trades"] == {}


def test_demo_exchange_uses_classic_futures_account():
    ex = bd.demo_exchange("k", "s", "p")
    uta, _ = ex.handle_uta_and_params({}, "fetchBalance", False)
    assert uta is False


def test_smoke_test_opens_tiny_long_with_stop_off_the_strategy_books(tmp_path):
    ex = FakeExchange()
    ex.markets = {"SUI/USDT:USDT": {}}
    ex.fetch_ticker = lambda pair: {"last": 2.5}
    ex.market = lambda pair: {"limits": {"amount": {"min": 1.0}}}
    ex.price_to_precision = lambda pair, price: f"{price:.4f}"
    rec = bd.Recorder(tmp_path)
    bd.smoke_test(ex, ["BTC/USDT:USDT"], NOW, rec)
    create = [c for c in ex.calls if c[0] == "create"][0]
    assert create[1:4] == ("SUI/USDT:USDT", "market", "buy")
    assert create[4] == 20.0                                    # 50 USDT / 2.5
    assert create[6]["stopLoss"]["triggerPrice"] == 2.375       # 5% under
    assert not (tmp_path / bd.TRADES_FILE.name).exists()        # not a Pusula trade
    assert "smoke test opened" in (tmp_path / bd.EVENTS_FILE.name).read_text()


def test_smoke_test_never_uses_a_pusula_coin():
    ex = FakeExchange()
    ex.markets = {"SUI/USDT:USDT": {}}
    with pytest.raises(SystemExit):
        bd.smoke_test(ex, ["SUI/USDT:USDT"], NOW, None)


def test_telegram_message_only_for_trade_events(monkeypatch):
    sent = []

    class FakeClient:
        def __init__(self, token, chat_id, timeout=0):
            self.chat_id = chat_id

        def send_message(self, text):
            sent.append(text)

    import signals.dispatcher.telegram_client as tc
    monkeypatch.setattr(tc, "TelegramClient", FakeClient)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "1:x")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    bd.notify_telegram(["BTC/USDT:USDT: signal skipped size below the exchange minimum", "-: no demo balance found"])
    assert sent == []
    bd.notify_telegram(["ETH/USDT:USDT: entry order placed limit 2500 stop 2400"])
    assert sent == ["Bitget demo (Pusula)\n• ETH: Giriş emri kondu limit 2500 stop 2400"]


def test_telegram_problem_never_stops_the_run(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "1:x")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-5")  # a group id: refused, but only printed
    bd.notify_telegram(["ETH/USDT:USDT: closed +1.2R"])


# ------------------------------------------------------------------ second bot (Dalga)


NOW_1H = SIGNAL + timedelta(hours=1, minutes=7)  # 7 minutes after the 00:00 1h candle closed


@pytest.fixture
def dalga_bot(monkeypatch, tmp_path):
    monkeypatch.setattr(bd, "BOT", bd.BOTS["dalga"])
    monkeypatch.setattr(bd, "OTHER_STATE_FILES", [tmp_path / "other_state.json"])
    return tmp_path / "other_state.json"


def dalga_frame(score, exit_long=0):
    df = frame([(SIGNAL, 99, 101, 1, exit_long)])
    df["score_1d"] = score
    return df


@pytest.mark.parametrize("score,risk", [(3, 0.0075), (1, 0.0035)])
def test_dalga_risk_follows_trend_strength(dalga_bot, tmp_path, score, risk):
    ex, state = FakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: dalga_frame(score)}, state, NOW_1H, bd.Recorder(tmp_path))
    amount = float([c for c in ex.calls if c[0] == "create"][0][4])
    assert amount == pytest.approx(9900 * risk / 5, abs=1e-3)
    assert next(iter(state["trades"])).startswith("dlg")


def test_dalga_risk_halves_in_drawdown(dalga_bot, tmp_path):
    ex, state = FakeExchange(), {"trades": {}, "equity_peak": 12_000.0}  # 9900 is 17.5% below the peak
    bd.run_once(ex, None, {PAIR: dalga_frame(3)}, state, NOW_1H, bd.Recorder(tmp_path))
    amount = float([c for c in ex.calls if c[0] == "create"][0][4])
    assert amount == pytest.approx(9900 * 0.0075 * 0.5 / 5, abs=1e-3)
    assert state["equity_peak"] == 12_000.0


def test_coin_held_by_the_other_bot_is_skipped(dalga_bot, tmp_path):
    dalga_bot.write_text('{"trades": {"x": {"pair": "%s", "status": "open"}}}' % PAIR)
    ex, state = FakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: dalga_frame(3)}, state, NOW_1H, bd.Recorder(tmp_path))
    assert state["trades"] == {} and not [c for c in ex.calls if c[0] == "create"]


def test_no_entry_when_exit_rule_is_already_true(dalga_bot, tmp_path):
    ex, state = FakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: dalga_frame(3, exit_long=1)}, state, NOW_1H, bd.Recorder(tmp_path))
    assert state["trades"] == {}


def test_dalga_never_moves_stop_to_break_even(dalga_bot, tmp_path):
    ex, state = FakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: dalga_frame(3)}, state, NOW_1H, bd.Recorder(tmp_path))
    (oid,) = ex.orders
    ex.fill(oid, 100.0, NOW_1H + timedelta(minutes=30))
    ex.positions[PAIR] = ex.orders[oid]["amount"]
    df = pd.concat([dalga_frame(3), frame([(SIGNAL + timedelta(hours=1), 100, 120, 0, 0)])], ignore_index=True)
    bd.run_once(ex, Detail(high=120.0), {PAIR: df}, state, NOW_1H + timedelta(hours=1), bd.Recorder(tmp_path))
    (t,) = state["trades"].values()
    assert t["status"] == "open" and not t["breakeven_moved"]


# ------------------------------------------------------------------ third bot (Kivilcim, trial)


class MarketFakeExchange(FakeExchange):
    """Market buys fill at once at 100; a position appears."""

    def price_to_precision(self, pair, price):
        return f"{price:.4f}"

    def create_order(self, pair, type_, side, amount, price=None, params=None):
        if type_ == "market" and side == "buy":
            params = params or {}
            self.calls.append(("create", pair, type_, side, amount, price, params))
            oid = f"o{len(self.calls)}"
            self.orders[oid] = {"id": oid, "status": "closed", "filled": float(amount), "average": 100.0,
                                "price": None, "timestamp": int(NOW_1H.timestamp() * 1000),
                                "lastTradeTimestamp": int(NOW_1H.timestamp() * 1000), "fee": {"cost": 0.5},
                                "amount": float(amount)}
            self.positions[pair] = float(amount)
            return {"id": oid}
        return super().create_order(pair, type_, side, amount, price, params)


@pytest.fixture
def kivilcim_bot(monkeypatch, tmp_path):
    monkeypatch.setattr(bd, "BOT", bd.BOTS["kivilcim"])
    monkeypatch.setattr(bd, "OTHER_STATE_FILES", [tmp_path / "other_state.json"])


def kivilcim_frame():
    df = frame([(SIGNAL, 99, 101, 1, 0)])
    df["long_stop"], df["long_tp"], df["score_1d"] = 97.0, 103.0, 3
    return df


def test_kivilcim_enters_at_market_with_stop_and_take_profit(kivilcim_bot, tmp_path):
    ex, state, rec = MarketFakeExchange(), {"trades": {}}, bd.Recorder(tmp_path)
    bd.run_once(ex, None, {PAIR: kivilcim_frame()}, state, NOW_1H, rec)
    (create,) = [c for c in ex.calls if c[0] == "create"]
    assert create[2] == "market" and create[6]["stopLoss"]["triggerPrice"] == 97.0
    assert create[6]["takeProfit"]["triggerPrice"] == 103.0
    (t,) = state["trades"].values()
    assert t["status"] == "open" and t["fill_price"] == 100.0 and t["plan_tp"] == 103.0
    assert float(create[4]) == pytest.approx(9900 * 0.002 / 3, abs=1e-3)  # 0.2% risk, stop 3 away
    assert any("entry filled" in e for e in rec.events)


def test_kivilcim_closes_after_three_hours(kivilcim_bot, tmp_path):
    ex, state = MarketFakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: kivilcim_frame()}, state, NOW_1H, bd.Recorder(tmp_path))
    later = NOW_1H + timedelta(hours=2, minutes=50)
    bd.run_once(ex, None, {PAIR: kivilcim_frame()}, state, later, bd.Recorder(tmp_path))
    assert next(iter(state["trades"].values()))["status"] == "open"
    bd.run_once(ex, None, {PAIR: kivilcim_frame()}, state, NOW_1H + timedelta(hours=3, minutes=5),
                bd.Recorder(tmp_path))
    t = next(iter(state["trades"].values()))
    assert t["status"] == "closed" and t["exit_reason"] == "time_exit"
    assert [c for c in ex.calls if c[0] == "create"][-1][2:4] == ("market", "sell")


def test_kivilcim_take_profit_is_named(kivilcim_bot, tmp_path):
    ex, state = MarketFakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: kivilcim_frame()}, state, NOW_1H, bd.Recorder(tmp_path))
    ex.positions[PAIR] = 0.0  # the exchange's take profit closed it
    ex.my_trades = [{"side": "sell", "amount": 1.0, "cost": 103.0, "fee": {"cost": 0.1}}]
    bd.run_once(ex, None, {PAIR: kivilcim_frame()}, state, NOW_1H + timedelta(hours=1), bd.Recorder(tmp_path))
    assert next(iter(state["trades"].values()))["exit_reason"] == "take_profit"


def test_kivilcim_skips_stale_signal_and_caps_daily_entries(kivilcim_bot, tmp_path):
    ex, state = MarketFakeExchange(), {"trades": {}}
    bd.run_once(ex, None, {PAIR: kivilcim_frame()}, state, NOW_1H + timedelta(minutes=45), bd.Recorder(tmp_path))
    assert state["trades"] == {}
    day = f"{NOW_1H:%Y-%m-%d}"
    state = {"trades": {f"k{i}": {"pair": f"X{i}/USDT:USDT", "status": "closed", "signal_time": day + "T00:00:00",
                                  "fill_time": day + "T00:10:00"} for i in range(3)}}
    bd.run_once(ex, None, {PAIR: kivilcim_frame()}, state, NOW_1H, bd.Recorder(tmp_path))
    assert len(state["trades"]) == 3


def test_kivilcim_signal_uses_yesterdays_daily_score():
    import kivilcim

    days = pd.date_range("2026-01-01", periods=120, freq="D", tz="UTC")
    daily = pd.DataFrame({"date": days, "open": 1.0, "high": 1.0, "low": 1.0,
                          "close": [100 + i for i in range(120)], "volume": 1.0})  # steady uptrend: score +3
    hours = pd.date_range(days[-1], periods=48, freq="h", tz="UTC")
    close = [200 - i * 0.5 for i in range(48)]  # falling hours: RSI low
    h = pd.DataFrame({"date": hours, "open": close, "high": [c + 0.2 for c in close],
                      "low": [c - 0.2 for c in close], "close": close, "volume": 1.0})
    s = kivilcim.Kivilcim()
    s.dp = bd._Provider({(PAIR, "1d"): daily, (PAIR, "1h"): h})
    df = s.populate_exit_trend(s.populate_entry_trend(s.populate_indicators(h, {"pair": PAIR}), {}), {})
    last = df.iloc[-1]
    assert last["score_1d"] == 3 and last["enter_long"] == 1
    assert last["long_stop"] < last["close"] < last["long_tp"]
    # the first day's hours see the score of the day before the last daily candle
    assert df.iloc[0]["score_1d"] == 3


def test_telegram_also_goes_to_the_chosen_group_with_turkish_exit_reason(monkeypatch):
    sent = []

    class FakeClient:
        def __init__(self, token, chat_id, timeout=0):
            self.chat_id = chat_id

        def send_message(self, text):
            sent.append((self.chat_id, text))

    import signals.dispatcher.telegram_client as tc
    monkeypatch.setattr(tc, "TelegramClient", FakeClient)
    monkeypatch.setattr(bd, "BOT", bd.BOTS["kivilcim"])
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "1:x")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    monkeypatch.setenv("TELEGRAM_GROUP_ID", "-100123")
    bd.notify_telegram(["SOL/USDT:USDT: closed take_profit r=0.95"])
    text = "Bitget demo (Kıvılcım - DENEME)\n• SOL: İşlem kapandı kâr alındı r=0.95"
    assert sent == [(42, text), (-100123, text)]
