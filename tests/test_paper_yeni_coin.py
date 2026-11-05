import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import paper_yeni_coin as py  # noqa: E402

DAY = 86_400_000
MS = lambda d: int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)  # noqa: E731


class Pub:
    """NEW/USDT listed on Bitget; daily candles from `start` with a given path of (open, high, low, close)."""

    def __init__(self, start: date, path, funding=0.0001):
        self.markets = {"NEW/USDT:USDT": {}, "BTC/USDT:USDT": {}}
        self.start, self.path, self.funding = MS(start), path, funding

    def fetch_ohlcv(self, pair, tf, since=None, limit=200):
        rows = [[self.start + i * DAY, *p, 1] for i, p in enumerate(self.path)]
        return [r for r in rows if r[0] >= since][:limit]

    def fetch_funding_rate_history(self, pair, since=None, limit=100):
        return [{"timestamp": self.start + i * DAY // 3, "fundingRate": self.funding} for i in range(60)]


def first_day(_s):
    return date(2026, 11, 10)


def boot():
    state = {}
    py.run_once(Pub(date(2026, 11, 11), []), state, datetime(2026, 11, 9, 6, tzinfo=timezone.utc), {"BTCUSDT"})
    assert state["known"] == ["BTCUSDT"] and "trades" in state
    return state


def test_first_run_only_records_history():
    boot()


def test_short_then_time_exit_after_14_days():
    state = boot()
    path = [(100, 105, 95, 98)] + [(98, 100, 80, 90)] * 13 + [(90, 92, 85, 88)] * 3
    pub = Pub(date(2026, 11, 11), path)
    msgs = py.run_once(pub, state, datetime(2026, 11, 11, 6, tzinfo=timezone.utc), {"BTCUSDT", "NEWUSDT"}, first_day)
    t = state["trades"][0]
    assert t["why"] == "open" and t["entry"] == 100 and abs(t["stop"] - 140) < 1e-9 and "KÂĞIT short" in msgs[0]
    assert t["notional"] == round(10_000 * 0.01 / 0.40, 2)
    py.run_once(pub, state, datetime(2026, 11, 24, 6, tzinfo=timezone.utc), {"BTCUSDT", "NEWUSDT"}, first_day)
    assert t["exit"] is None  # day 14 (2026-11-24) not closed yet
    py.run_once(pub, state, datetime(2026, 11, 25, 6, tzinfo=timezone.utc), {"BTCUSDT", "NEWUSDT"}, first_day)
    assert t["why"] == "time" and t["exit"] == 90 and t["exit_day"] == "2026-11-24"
    assert state["equity"] > py.START_EQUITY and t["funding_pct"] > 0


def test_stop_and_gap():
    state = boot()
    path = [(100, 105, 95, 98), (98, 150, 97, 120)]
    pub = Pub(date(2026, 11, 11), path)
    py.run_once(pub, state, datetime(2026, 11, 11, 6, tzinfo=timezone.utc), {"BTCUSDT", "NEWUSDT"}, first_day)
    py.run_once(pub, state, datetime(2026, 11, 13, 6, tzinfo=timezone.utc), {"BTCUSDT", "NEWUSDT"}, first_day)
    t = state["trades"][0]
    assert t["why"] == "stop" and abs(t["exit"] - 140 * 1.003) < 1e-9 and t["ret_pct"] < -40
    t2 = {"stop": 140.0, "entry_day": "2026-11-11"}
    py.manage(t2, [[MS(date(2026, 11, 11)), 100, 101, 99, 100], [MS(date(2026, 11, 12)), 160, 170, 150, 165]],
              date(2026, 11, 20))
    assert t2["why"] == "stop_gap" and abs(t2["exit"] - 160 * 1.003) < 1e-9


def test_not_on_bitget_is_skipped():
    state = boot()
    pub = Pub(date(2026, 11, 11), [(1, 1, 1, 1)])
    pub.markets = {"BTC/USDT:USDT": {}}
    msgs = py.run_once(pub, state, datetime(2026, 11, 11, 6, tzinfo=timezone.utc), {"BTCUSDT", "NEWUSDT"}, first_day)
    assert state["trades"][0]["note"] == "not on Bitget" and "atlandı" in msgs[0]


def test_waits_until_entry_day():
    state = boot()
    pub = Pub(date(2026, 11, 11), [(100, 101, 99, 100)])
    py.run_once(pub, state, datetime(2026, 11, 10, 20, tzinfo=timezone.utc), {"BTCUSDT", "NEWUSDT"}, first_day)
    assert state["trades"] == [] and state["pending"][0]["symbol"] == "NEWUSDT"


def test_bitget_pair_prefix():
    m = {"PEPE/USDT:USDT": {}, "1000SATS/USDT:USDT": {}}
    assert py.bitget_pair(m, "1000PEPEUSDT") == "PEPE/USDT:USDT"
    assert py.bitget_pair(m, "SATSUSDT") == "1000SATS/USDT:USDT"
    assert py.bitget_pair(m, "XYZUSDT") is None


# ---------- BTC-hedged variant (N7 M30 S30) ----------

class HPub:
    """NEW listed 2026-11-10 (Binance); Bitget daily candles from 11-11. BTC flat at 100 (or a given path)."""

    def __init__(self, path, btc=None, hours=None, vol=1000.0):
        self.markets = {"NEW/USDT:USDT": {}, "BTC/USDT:USDT": {}}
        self.start = MS(date(2026, 11, 11))
        self.path, self.btc, self.hours, self.vol = path, btc, hours or {}, vol

    def fetch_ohlcv(self, pair, tf, since=None, limit=200):
        if tf == "1h":
            return [r for r in self.hours.get(since, []) if r[0] >= since][:limit]
        if pair.startswith("BTC"):
            path = self.btc or [(100, 101, 99, 100)] * 60
            rows = [[MS(date(2026, 11, 1)) + i * DAY, *p, 1] for i, p in enumerate(path)]
        else:
            rows = [[self.start + i * DAY, *p, self.vol] for i, p in enumerate(self.path)]
        return [r for r in rows if r[0] >= since][:limit]

    def fetch_funding_rate_history(self, pair, since=None, limit=100):
        return []


def hboot():
    state = {}
    py.run_hedge(HPub([]), state, datetime(2026, 11, 9, 6, tzinfo=timezone.utc), {"BTCUSDT"}, first_day, lambda p: 0)
    return state


def run_h(pub, state, d, cut=0.0):
    return py.run_hedge(pub, state, datetime(d.year, d.month, d.day, 6, tzinfo=timezone.utc), {"BTCUSDT", "NEWUSDT"},
                        first_day, lambda p: cut)


def test_hedge_waits_a_week_then_shorts_and_buys_btc():
    state = hboot()
    path = [(100, 101, 99, 100)] * 7 + [(100, 110, 95, 98)] + [(98, 100, 80, 90)] * 40
    pub = HPub(path)
    run_h(pub, state, date(2026, 11, 17))
    assert state["trades"] == [] and state["pending"][0]["symbol"] == "NEWUSDT"
    msgs = run_h(pub, state, date(2026, 11, 18))  # listed 11-10 -> entry day 11-18
    t = state["trades"][0]
    assert t["why"] == "open" and t["entry"] == 100 and t["btc_entry"] == 100 and abs(t["stop"] - 130) < 1e-9
    assert t["notional"] == 500.0 and "long BTC" in msgs[0]
    run_h(pub, state, date(2026, 12, 17))
    assert t["exit"] is None  # day 30 = 12-17 not closed yet
    run_h(pub, state, date(2026, 12, 18))
    assert t["why"] == "time" and t["exit"] == 90 and t["exit_day"] == "2026-12-17"
    assert abs(t["coin_ret_pct"] - 10) < 1e-9 and t["btc_ret_pct"] == 0
    assert abs(state["equity"] - (10_000 + 500 * (0.10 - 0.004))) < 1e-6


def test_hedge_intraday_stop_uses_hour_fill():
    state = hboot()
    path = [(100, 101, 99, 100)] * 7 + [(100, 101, 99, 100), (100, 150, 99, 140)]
    d2 = MS(date(2026, 11, 19))
    hours = {d2: [[d2, 100, 110, 99, 105, 1], [d2 + 3_600_000, 128, 135, 120, 133, 1]]}
    pub = HPub(path, hours=hours)
    run_h(pub, state, date(2026, 11, 18))
    run_h(pub, state, date(2026, 11, 20))
    t = state["trades"][0]
    assert t["why"] == "stop" and t["exit_day"] == "2026-11-19" and abs(t["exit"] - 130 * 1.002) < 1e-9
    assert t["ret_pct"] < -10


def test_hedge_volume_filter_and_isolated_cap():
    state = hboot()
    path = [(100, 101, 99, 100)] * 8
    run_h(HPub(path, vol=1.0), state, date(2026, 11, 18), cut=1e9)
    assert state["trades"][0]["note"] == "not in top 100 by volume"
    t = {"entry": 1.0, "exit": 5.0, "btc_entry": 100.0, "notional": 100.0, "pair": "NEW/USDT:USDT",
         "entry_day": "2026-11-18", "exit_day": "2026-11-19"}
    py.hedge_close(HPub(path), t, 10_000)
    assert t["coin_ret_pct"] == -100.0
