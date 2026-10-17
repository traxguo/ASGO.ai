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
