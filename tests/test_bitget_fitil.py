import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bitget_fitil as bf  # noqa: E402

H = datetime(2026, 10, 12, 10, 0, tzinfo=timezone.utc)
PAIR = "ETH/USDT:USDT"


class FakePub:
    """Public candles: a steady daily uptrend, hour opens at 100, BTC down `btc_drop` within the hour."""

    def __init__(self, btc_drop=0.0):
        self.btc_drop = btc_drop

    def fetch_ohlcv(self, pair, tf, since=None, limit=200):
        ms = {"1d": 86400000, "1h": 3600000, "1m": 60000}[tf]
        if tf == "1d":
            start = since
            return [[start + i * ms, 50 + i, 51 + i, 49 + i, 50.5 + i, 1] for i in range(min(limit, 200))]
        if tf == "1m":
            return [[since + i * ms, 100, 100, 100 * (1 - self.btc_drop), 100, 1] for i in range(30)]
        return [[since, 100.0, 101, 99, 100, 1]]


class FakeEx:
    def __init__(self, fill=0.0, status="open"):
        self.orders, self.cancelled, self.sold, self.fill, self.status = [], [], [], fill, status
        self.markets = {PAIR: {}, "BTC/USDT:USDT": {}}

    def fetch_order(self, oid, pair, params):
        return {"status": self.status, "filled": self.fill, "average": 95.0, "price": 95.0,
                "timestamp": int((H + timedelta(minutes=20)).timestamp() * 1000), "fee": {"cost": 0.01}}

    def cancel_order(self, oid, pair, params):
        self.cancelled.append(oid)

    def fetch_balance(self, params):
        return {"USDT": {"total": 1000.0, "free": 1000.0}}

    def price_to_precision(self, pair, p):
        return round(p, 4)

    def amount_to_precision(self, pair, a):
        return round(a, 3)

    def set_margin_mode(self, *a, **k):
        pass

    def set_leverage(self, *a, **k):
        pass

    def create_order(self, pair, kind, side, amount, price, params):
        (self.orders if side == "buy" else self.sold).append((pair, kind, amount, price))
        return {"id": f"o{len(self.orders)}"}

    def fetch_positions(self, pairs, params):
        return [{"symbol": PAIR, "contracts": 1.0}]

    def fetch_my_trades(self, pair, since=None, params=None):
        return [{"side": "sell", "amount": 1.0, "cost": 97.0, "fee": {"cost": 0.02}}]


def run(ex, pub, state, now, pairs=(PAIR,)):
    bf.OUT_DIR = Path(__import__("tempfile").mkdtemp())
    bf.run_once(ex, pub, state, now, bf.Log(), list(pairs))
    return state


def test_places_one_limit_per_hour_at_95_percent():
    ex, state = FakeEx(), {}
    run(ex, FakePub(), state, H + timedelta(minutes=2))
    run(ex, FakePub(), state, H + timedelta(minutes=17))
    assert len(ex.orders) == 1
    pair, kind, amount, price = ex.orders[0]
    assert (pair, kind, price) == (PAIR, "limit", 95.0) and amount == round(1000 * 0.99 / 5 / 95.0, 3)  # 0.99 = tradable balance ratio


def test_btc_crash_blocks_new_limits():
    ex = FakeEx()
    run(ex, FakePub(btc_drop=0.04), {}, H + timedelta(minutes=2))
    assert ex.orders == []


def test_unfilled_limit_is_cancelled_after_the_hour():
    ex, state = FakeEx(), {}
    run(ex, FakePub(), state, H + timedelta(minutes=2))
    run(ex, FakePub(), state, H + timedelta(minutes=62), pairs=())
    assert ex.cancelled == ["o1"] and list(state["trades"].values())[0]["status"] == "cancelled"


def test_fill_then_time_exit_after_three_hours():
    ex, state = FakeEx(), {}
    run(ex, FakePub(), state, H + timedelta(minutes=2))
    ex.fill, ex.status = ex.orders[0][2], "filled"
    run(ex, FakePub(), state, H + timedelta(minutes=32), pairs=())
    t = list(state["trades"].values())[0]
    assert t["status"] == "open" and ex.sold == []
    run(ex, FakePub(), state, H + timedelta(hours=3, minutes=25), pairs=())
    assert t["status"] == "closed" and t["exit_reason"] == "time_exit" and len(ex.sold) == 1


def test_fill_during_btc_crash_is_closed_at_once():
    ex, state = FakeEx(), {}
    run(ex, FakePub(), state, H + timedelta(minutes=2))
    ex.fill, ex.status = ex.orders[0][2], "filled"
    run(ex, FakePub(btc_drop=0.05), state, H + timedelta(minutes=32), pairs=())
    t = list(state["trades"].values())[0]
    assert t["status"] == "closed" and t["exit_reason"] == "btc_guard"


def test_daily_filter_needs_uptrend():
    up = pd.DataFrame({"close": [float(i) for i in range(1, 130)]})
    down = pd.DataFrame({"close": [float(i) for i in range(130, 1, -1)]})
    assert bf.daily_ok(up)[0] and not bf.daily_ok(down)[0]


class FakePubDown(FakePub):
    """Daily downtrend; hour opens at 100."""

    def fetch_ohlcv(self, pair, tf, since=None, limit=200):
        if tf == "1d":
            return [[since + i * 86400000, 300 - i, 301 - i, 299 - i, 299.5 - i, 1] for i in range(min(limit, 200))]
        return super().fetch_ohlcv(pair, tf, since, limit)


def test_downtrend_coin_gets_the_deeper_derin_fitil_limit():
    ex, state = FakeEx(), {}
    run(ex, FakePubDown(), state, H + timedelta(minutes=2))
    assert len(ex.orders) == 1 and ex.orders[0][3] == 92.0
    assert list(state["trades"].values())[0]["mode"] == "derin"


def test_depth_for_mixed_coin_places_nothing():
    # long-run uptrend (score +3) but the last close dipped under EMA20: neither rule applies
    mixed = pd.DataFrame({"close": [float(i) for i in range(1, 126)] + [110.0]})
    assert bf.depth_for(mixed)[0] is None
