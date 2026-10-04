import json

import pytest

from signals.dispatcher import commands
from signals.dispatcher.bot import process_update
from signals.dispatcher.telegram_client import ConfigError, TelegramClient, parse_chat_id

OWNER = 123456789


@pytest.fixture
def sample_signal_dict():
    from tests.test_schema import make_signal
    return make_signal().to_dict()


class FakeClient(TelegramClient):
    def __init__(self):
        super().__init__("1:abc", OWNER)
        self.sent = []

    def _call(self, method, params):
        self.sent.append((method, params))
        return {}


def no_price(_symbol):
    return None


@pytest.mark.parametrize("text,symbol", [
    ("btc", "BTC"), ("/btc", "BTC"), ("btc'ye bak", "BTC"), ("BTC ye bak", "BTC"),
    ("ethere bak", "ETH"), ("/bak eth", "ETH"), ("solanaya bak", "SOL"), ("doge", "DOGE"),
])
def test_find_symbol(text, symbol):
    assert commands.find_symbol(text) == symbol


def test_find_symbol_none():
    assert commands.find_symbol("merhaba nasılsın") is None


def test_pair_report_without_active_strategy_gives_no_levels(tmp_path, monkeypatch):
    monkeypatch.setattr(commands, "active_strategies", lambda: [])
    out = commands.handle("btc'ye bak", price_fetcher=no_price, log_dir=tmp_path)
    assert "aktif) strateji yok" in out
    assert "Stop" not in out


def test_pair_report_shows_logged_signal_as_is(tmp_path, monkeypatch, sample_signal_dict):
    monkeypatch.setattr(commands, "active_strategies", lambda: ["trend_ma"])
    (tmp_path / "s.json").write_text(json.dumps(sample_signal_dict))
    out = commands.handle("/eth", price_fetcher=lambda s: {"price": 3400.0, "change_pct": 1.5},
                          log_dir=tmp_path)
    assert "3400" in out and "sinyal değil" in out
    assert f"Stop: {sample_signal_dict['stop']:g}" in out


def test_help_and_status():
    assert "/durum" in commands.handle("/yardim")
    assert "Seviye" in commands.handle("/durum")


def test_send_only_to_owner():
    c = FakeClient()
    with pytest.raises(PermissionError):
        c.send_message("x", chat_id=999)
    c.send_message("x")
    assert c.sent[0][1]["chat_id"] == OWNER


def test_other_chats_are_ignored():
    c = FakeClient()
    stranger = {"message": {"chat": {"id": 42, "type": "private"}, "text": "btc"}}
    group = {"message": {"chat": {"id": OWNER, "type": "group"}, "text": "btc"}}
    assert not process_update(c, stranger, responder=lambda t: "hi")
    assert not process_update(c, group, responder=lambda t: "hi")
    assert c.sent == []
    owner = {"message": {"chat": {"id": OWNER, "type": "private"}, "text": "btc"}}
    assert process_update(c, owner, responder=lambda t: "hi")


@pytest.mark.parametrize("raw", ["", "abc", "-100123", "0"])
def test_chat_id_must_be_personal(raw):
    with pytest.raises(ConfigError):
        parse_chat_id(raw)


def test_env_file_with_bom(tmp_path, monkeypatch):
    from signals.dispatcher.telegram_client import load_env
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    env = tmp_path / ".env"
    env.write_bytes("﻿TELEGRAM_CHAT_ID=123\n".encode("utf-8"))
    load_env(env)
    import os
    assert os.environ["TELEGRAM_CHAT_ID"] == "123"
