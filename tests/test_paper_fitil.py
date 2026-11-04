import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import paper_fitil as pf  # noqa: E402

H = datetime(2026, 10, 17, 10, 0, tzinfo=timezone.utc)
MS = lambda t: int(t.timestamp() * 1000)  # noqa: E731


class Pub:
    """Daily uptrend for every coin; ETH dips 6% in the second 15m candle of 10:00, BTC calm."""

    def __init__(self, btc_low=99.5):
        self.btc_low = btc_low

    def fetch_ohlcv(self, pair, tf, since=None, limit=200):
        if tf == "1d":
            return [[since + i * 86400000, 50 + i, 51 + i, 49 + i, 50.5 + i, 1] for i in range(min(limit, 200))]
        rows = []
        for i in range(limit):
            t = since + i * 900000
            low = 99.5
            if pair.startswith("ETH") and t == MS(H + timedelta(minutes=15)):
                low = 94.0
            if pair.startswith("BTC") and t == MS(H + timedelta(minutes=15)):
                low = self.btc_low
            rows.append([t, 100.0, 100.5, low, 100.2, 1])
        return rows


def test_fill_then_exit_after_three_hours():
    state, pairs = {"done_until": H.isoformat()}, ["ETH/USDT:USDT", "SOL/USDT:USDT"]
    msgs = pf.run_once(Pub(), state, H + timedelta(hours=1, minutes=5), pairs)
    assert len(state["trades"]) == 1 and "ETH" in msgs[0]
    t = state["trades"][0]
    assert t["entry"] == 95.0 and t["mode"] == "fitil" and t["exit"] is None
    pf.run_once(Pub(), state, H + timedelta(hours=3, minutes=20), pairs)
    assert t["exit"] is None  # fill candle 10:15 -> exit at the close of the 13:15 candle (13:30)
    pf.run_once(Pub(), state, H + timedelta(hours=3, minutes=31), pairs)
    assert t["exit"] == 100.2 and abs(t["ret_pct"] - round((100.2 / 95 - 1 - pf.COST) * 100, 3)) < 1e-9
    assert state["equity"] > pf.START_EQUITY


def test_btc_guard_skips_the_fill():
    state = {"done_until": H.isoformat()}
    pf.run_once(Pub(btc_low=96.0), state, H + timedelta(hours=1, minutes=5), ["ETH/USDT:USDT"])
    assert state["trades"] == []


def test_open_hour_is_not_judged_yet():
    state = {"done_until": H.isoformat()}
    pf.run_once(Pub(), state, H + timedelta(minutes=50), ["ETH/USDT:USDT"])
    assert state["trades"] == [] and state["done_until"] == H.isoformat()


class _Pub15:
    def __init__(self, rows):
        self.rows = rows

    def fetch_ohlcv(self, pair, tf, since=None, limit=200):
        return [[since + i * 900000, *r, 1] for i, r in enumerate(self.rows)][:limit]


def test_derin_stop_exits_at_the_stop_or_a_gap_open():
    from datetime import datetime, timedelta, timezone
    import paper_fitil as pf
    fill = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)
    t = {"pair": "X/USDT:USDT", "mode": "derin", "fill_time": fill.isoformat(), "entry": 100.0}
    now = fill + timedelta(hours=4)
    # o, h, l, c: fill candle ok, then a dip through 96
    assert pf.deep_stop(_Pub15([[100, 101, 99, 100], [100, 100, 95, 97]]), t, now)[1] == 96.0
    # gap: the next candle opens at 94 under the stop
    assert pf.deep_stop(_Pub15([[100, 101, 99, 100], [94, 95, 93, 94]]), t, now)[1] == 94.0
    # fill candle already closes under the stop
    assert pf.deep_stop(_Pub15([[100, 101, 95, 95.5]]), t, now)[1] == 95.5
    assert pf.deep_stop(_Pub15([[100, 101, 99, 100], [100, 101, 97, 98]]), t, now) is None
