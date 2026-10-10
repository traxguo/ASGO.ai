import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("telegram_command", ROOT / "scripts" / "telegram_command.py")
tc = importlib.util.module_from_spec(spec)
sys.modules["telegram_command"] = tc
spec.loader.exec_module(tc)


class FakeResp:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body.encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_every_signed_request_carries_the_demo_header(monkeypatch):
    monkeypatch.setenv("BITGET_DEMO_API_KEY", "k")
    monkeypatch.setenv("BITGET_DEMO_API_SECRET", "s")
    monkeypatch.setenv("BITGET_DEMO_API_PASSPHRASE", "p")
    seen = []

    def opener(req, timeout):
        seen.append(req)
        return FakeResp(json.dumps({"code": "00000", "data": []}))

    tc.bitget("GET", "/api/v2/mix/account/accounts", {"productType": "USDT-FUTURES"}, opener=opener)
    tc.bitget("POST", "/api/v2/mix/order/close-positions", None, {"symbol": "NEARUSDT"}, opener=opener)
    for req in seen:
        assert req.get_header("Paptrading") == "1"
        assert req.get_header("Access-key") == "k"


def test_bitget_block_page_is_reported_readably():
    with pytest.raises(RuntimeError, match="Bitget: <html> blocked"):
        tc.bitget("GET", "/x", signed=False, opener=lambda req, timeout: FakeResp("<html> blocked </html>"))


def fake_call(routes, calls):
    def call(method, path, query=None, body=None, signed=True):
        calls.append((method, path, body))
        return routes[path]
    return call


def test_status_lists_balance_and_positions():
    calls = []
    call = fake_call({
        "/api/v2/mix/account/accounts": [{"marginCoin": "USDT", "accountEquity": "9999.5", "available": "9950",
                                          "unrealizedPL": "-0.5"}],
        "/api/v2/mix/position/all-position": [{"symbol": "NEARUSDT", "holdSide": "long", "total": "9",
                                               "openPriceAvg": "5.471", "markPrice": "5.46", "unrealizedPL": "-0.1"}],
    }, calls)
    text = tc.run("/durum", "", True, call)
    assert "9.999,50 USDT" in text
    assert "NEAR long: 9 adet, giriş 5.471" in text


def test_close_only_for_the_owner_and_only_open_positions():
    calls = []
    call = fake_call({"/api/v2/mix/position/all-position": [{"symbol": "NEARUSDT"}],
                      "/api/v2/mix/order/close-positions": {}}, calls)
    assert "sadece hesap sahibi" in tc.run("/kapat", "near", False, call)
    assert calls == []
    assert "açık demo işlemi yok" in tc.run("/kapat", "btc", True, call)
    assert "kapatıldı" in tc.run("/kapat", "near", True, call)
    assert calls[-1] == ("POST", "/api/v2/mix/order/close-positions", {"symbol": "NEARUSDT", "productType": "USDT-FUTURES"})


def test_errors_become_a_message():
    def call(*a, **k):
        raise RuntimeError("Bitget 40001: bad key")
    assert tc.run("/gecmis", "", True, call) == "Bir sorun oldu: Bitget 40001: bad key"


def test_price_and_symbols():
    call = fake_call({"/api/v2/mix/market/ticker": [{"symbol": "BTCUSDT", "lastPr": "83050", "change24h": "0.0052"}]}, [])
    assert tc.run("/fiyat", "btc", False, call).startswith("BTC: 83050 USDT (24 saat +0.52%)")
    assert tc.symbol_of("near") == "NEARUSDT"
    assert tc.symbol_of("BTCUSDT") == "BTCUSDT"
