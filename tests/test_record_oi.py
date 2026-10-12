import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import record_oi  # noqa: E402


class FakeExchange:
    def fetch_open_interest(self, pair):
        if pair.startswith("BAD"):
            raise RuntimeError("not listed")
        return {"openInterestAmount": 123.5}

    def fetch_ticker(self, pair):
        return {"last": 2.5}


def test_snapshot_skips_failing_coin_and_appends_csv(tmp_path):
    now = datetime(2026, 10, 12, 9, 25, tzinfo=timezone.utc)
    rows = record_oi.snapshot(FakeExchange(), ["BTC/USDT:USDT", "BAD/USDT:USDT"], now)
    assert rows == [{"time": "2026-10-12T09:25:00Z", "coin": "BTC", "open_interest": 123.5, "price": 2.5}]
    out = tmp_path / "oi.csv"
    record_oi.append(rows, out)
    record_oi.append(rows, out)
    lines = out.read_text().splitlines()
    assert lines[0] == "time,coin,open_interest,price" and len(lines) == 3
