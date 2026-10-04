import json

import pytest

from signals.dispatcher import commands
from signals.dispatcher.bot import process_update
from signals.dispatcher.telegram_client import ConfigError, TelegramClient, parse_chat_id, parse_group_id

OWNER = 123456789


@pytest.fixture
def sample_signal_dict():
    from tests.test_schema import make_signal
    return make_signal().to_dict()


GROUP = -1001234567890


class FakeClient(TelegramClient):
    def __init__(self, group_id=None):
        super().__init__("1:abc", OWNER, group_id=group_id)
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


def test_configured_group_is_answered_others_are_not():
    c = FakeClient(group_id=GROUP)
    grp = {"message": {"chat": {"id": GROUP, "type": "supergroup"}, "text": "/btc@asgo_bot"}}
    other = {"message": {"chat": {"id": -100999, "type": "group"}, "text": "/btc"}}
    assert process_update(c, grp, responder=lambda t: "hi")
    assert not process_update(c, other, responder=lambda t: "hi")
    chatter = {"message": {"chat": {"id": GROUP, "type": "supergroup"}, "text": "btc düştü mü?"}}
    assert not process_update(c, chatter, responder=lambda t: "hi")
    assert [p["chat_id"] for _, p in c.sent] == [GROUP]
    with pytest.raises(PermissionError):
        c.send_message("x", chat_id=-100999)


def test_no_group_by_default():
    c = FakeClient()
    grp = {"message": {"chat": {"id": GROUP, "type": "supergroup"}, "text": "/btc"}}
    assert not process_update(c, grp, responder=lambda t: "hi")
    assert c.allowed_chats == (OWNER,)


def test_group_id_parsing():
    assert parse_group_id("") is None
    assert parse_group_id(str(GROUP)) == GROUP
    with pytest.raises(ConfigError):
        parse_group_id("12345")


def test_command_with_bot_suffix():
    assert commands.find_symbol("/eth@asgo_bot") == "ETH"
    assert "Seviye" in commands.handle("/durum@asgo_bot")


class FakeAI:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []

    def answer(self, question, facts):
        self.calls.append((question, facts))
        return self.reply


def test_ai_not_used_for_plain_commands(monkeypatch):
    monkeypatch.setattr(commands, "active_strategies", lambda: [])
    ai = FakeAI("selam")
    commands.handle("/btc", price_fetcher=no_price, ai=ai)
    commands.handle("btc'ye bak", price_fetcher=no_price, ai=ai)
    commands.handle("/durum", ai=ai)
    assert ai.calls == []


def test_ai_chat_free_text_and_coin_question(monkeypatch, tmp_path):
    monkeypatch.setattr(commands, "active_strategies", lambda: [])
    ai = FakeAI("Henüz test edilmiş strateji yok.")
    assert commands.handle("ne yaptın ne ettin", ai=ai) == "Henüz test edilmiş strateji yok."
    out = commands.handle("btc ne olur sence", price_fetcher=no_price, log_dir=tmp_path, ai=ai)
    assert out.startswith("🔎 BTC/USDT") and "💬 Henüz" in out
    assert "Seviye" in ai.calls[0][1]  # facts include project status
    assert commands.handle("/sor", ai=ai).startswith("Sorunu")


def test_ai_failure_falls_back_to_template(monkeypatch, tmp_path):
    monkeypatch.setattr(commands, "active_strategies", lambda: [])
    out = commands.handle("btc ne olur sence", price_fetcher=no_price, log_dir=tmp_path, ai=FakeAI(None))
    assert out.startswith("🔎 BTC/USDT") and "💬" not in out
    assert "Anlayamadım" in commands.handle("ne yaptın ne ettin", ai=None)


def test_grounding_guard():
    from signals.dispatcher.chat_ai import is_grounded
    facts = "Fiyat: 62345.1 (24s: +1.52%)\nSeviye: 0"
    assert is_grounded("BTC şu an 62345 civarında, seviye 0.", facts)
    assert not is_grounded("BTC 70000'e çıkar, stop 60000.", facts)


def test_group_replies_to_bot_are_answered():
    c = FakeClient(group_id=GROUP)
    reply = {"message": {"chat": {"id": GROUP, "type": "group"}, "text": "peki ne zaman?",
                         "reply_to_message": {"from": {"id": 555}}}}
    assert process_update(c, reply, responder=lambda t: "hi", bot_id=555)
    other_reply = {"message": {"chat": {"id": GROUP, "type": "group"}, "text": "aynen",
                               "reply_to_message": {"from": {"id": 999}}}}
    assert not process_update(c, other_reply, responder=lambda t: "hi", bot_id=555)
