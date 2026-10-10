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


def test_demo_exchange_refuses_demo_coin_products_without_header():
    # ccxt leaves the header off for the old S-USDT demo products; the guard must stop that
    ex = bd.demo_exchange("k", "s", "p")
    with pytest.raises(SystemExit):
        ex.sign("v2/mix/order/place-order", ["private", "mix"], "POST", {"productType": "SUSDT-FUTURES"})


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
