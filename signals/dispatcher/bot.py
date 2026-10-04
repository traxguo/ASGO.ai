"""
ASGO Telegram bot (long polling, no open ports needed).

    python -m signals.dispatcher.bot chatid   # after you message the bot: prints your chat id
    python -m signals.dispatcher.bot test     # sends one test message to your chat
    python -m signals.dispatcher.bot run      # keeps running, answers your commands

Token and chat id come from .env (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID).
Optional TELEGRAM_GROUP_ID: one group the owner chose; the bot answers there too.
Messages from any other chat are ignored and never answered.
"""

from __future__ import annotations

import logging
import os
import sys
import time

from signals.dispatcher.chat_ai import ChatAI
from signals.dispatcher.commands import handle
from signals.dispatcher.telegram_client import ConfigError, TelegramClient, load_env

log = logging.getLogger("asgo.bot")


def process_update(client: TelegramClient, update: dict, responder=handle, bot_id: int | None = None) -> bool:
    """Answers one update. Returns True if it was answered."""
    msg = update.get("message") or {}
    chat = msg.get("chat") or {}
    is_owner = chat.get("id") == client.chat_id and chat.get("type") == "private"
    is_group = (client.group_id is not None and chat.get("id") == client.group_id
                and chat.get("type") in ("group", "supergroup"))
    if not (is_owner or is_group):
        log.warning("ignored message from a chat that is not allowed")
        return False
    text = msg.get("text")
    if not text:
        return False
    replied_to = ((msg.get("reply_to_message") or {}).get("from") or {}).get("id")
    if is_group and not text.startswith("/") and (bot_id is None or replied_to != bot_id):
        return False  # in the group only /commands and replies to the bot are answered
    client.send_message(responder(text), chat_id=chat["id"])
    return True


def run(client: TelegramClient) -> None:
    me = client.get_me()
    ai = ChatAI.from_env()
    log.info("bot @%s started; answering only %s; AI chat %s", me.get("username"),
             client.allowed_chats, f"on ({ai.model})" if ai else "off")

    def responder(text: str) -> str:
        return handle(text, ai=ai)

    offset = None
    while True:
        try:
            for upd in client.get_updates(offset):
                offset = upd["update_id"] + 1
                try:
                    process_update(client, upd, responder, bot_id=me.get("id"))
                except Exception as e:  # one bad message must not stop the bot
                    log.error("could not answer: %s", e)
        except Exception as e:
            log.error("polling error: %s; retrying in 10s", e)
            time.sleep(10)


def print_chat_ids() -> None:
    load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    client = TelegramClient(token, chat_id=0, timeout=20)
    updates = client.get_updates(None, poll_seconds=0)
    seen = {}
    for u in updates:
        chat = (u.get("message") or {}).get("chat") or {}
        if chat.get("type") == "private":
            seen[chat["id"]] = (f"kişisel: {chat.get('first_name', '')}", "TELEGRAM_CHAT_ID")
        elif chat.get("type") in ("group", "supergroup"):
            seen[chat["id"]] = (f"grup: {chat.get('title', '')}", "TELEGRAM_GROUP_ID")
    if not seen:
        print("Henüz mesaj yok. Telegram'da botuna (veya gruba) /start yaz, sonra tekrar çalıştır.")
    for cid, (name, key) in seen.items():
        print(f"ID: {cid}  ({name})  -> bunu .env içine {key} olarak yaz")


def main(argv: list[str]) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cmd = argv[1] if len(argv) > 1 else "run"
    try:
        if cmd == "chatid":
            print_chat_ids()
            return 0
        client = TelegramClient.from_env()
        if cmd == "test":
            for cid in client.allowed_chats:
                client.send_message("✅ ASGO botu bağlandı. Bu bir deneme mesajıdır.\n\n/yardim yazarak komutları görebilirsin.", chat_id=cid)
            print("Deneme mesajı gönderildi.")
        elif cmd == "run":
            run(client)
        else:
            print(__doc__)
            return 2
    except ConfigError as e:
        print(f"Ayar hatası: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
