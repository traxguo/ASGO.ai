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


def fake_candles(up=True):
    def call(method, path, query=None, body=None, signed=True):
        assert path == "/api/v2/mix/market/candles" and signed is False
        n, day = int(query["limit"]), query["granularity"] == "1D"
        step = 86400000 if day else 3600000
        price = (lambda i: 50 + i) if up else (lambda i: 200 - i)
        return [[str(i * step), price(i), price(i) + 1, price(i) - 1, price(i), 1, 1] for i in range(n)][::-1]
    return call


def test_yorum_gives_facts_and_no_levels():
    text = tc.market_comment("eth", fake_candles(up=True), fng=lambda: "40/100 (korku)", ai=lambda f: None)
    assert text.startswith("ETH yorumu") and "+3/3" in text and "15 coinden 15" in text
    assert "Yükselen trend" in text and "korku" in text and "sinyal değildir" in text
    assert not any(w in text.lower() for w in ("stop", "hedef", "giriş"))


def test_yorum_downtrend_says_bots_wait():
    text = tc.market_comment("BTC", fake_candles(up=False), fng=lambda: None, ai=lambda f: None)
    assert "Düşüş trendi" in text and "15 coinden 0" in text


def test_yorum_uses_ai_text_when_available_and_keeps_facts():
    text = tc.market_comment("ETH", fake_candles(), fng=lambda: None, ai=lambda f: "Kısa yorum.")
    assert text.startswith("Kısa yorum.") and "ETH yorumu" in text


def test_yorum_without_coin_asks():
    assert "Hangi coin" in tc.run("/yorum", "", True, fake_candles())


def test_sor_without_key_says_so(monkeypatch):
    monkeypatch.delenv("AI_API_KEY", raising=False)
    assert "AI_API_KEY" in tc.run("/sor", "merhaba", sender_is_owner=False)


def test_sor_answers_and_drops_price_levels(monkeypatch):
    monkeypatch.setenv("AI_API_KEY", "k")
    assert tc.ask("merhaba", ai=lambda p: "Merhaba! Nasılsın?") == "Merhaba! Nasılsın?"
    assert "seviyesi vermediği" in tc.ask("btc ne olur", ai=lambda p: "BTC 68,500'e gider.")
    assert tc.ask("2025 nasıldı", ai=lambda p: "2025 zor bir yıldı.") == "2025 zor bir yıldı."
    assert "tekrar dene" in tc.ask("selam", ai=lambda p: None)
    assert tc.ask("", ai=lambda p: "x").startswith("Ne sormak")
