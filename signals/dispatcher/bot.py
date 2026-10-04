"""
ASGO Telegram bot (long polling, no open ports needed).

    python -m signals.dispatcher.bot chatid   # after you message the bot: prints your chat id
    python -m signals.dispatcher.bot test     # sends one test message to your chat
    python -m signals.dispatcher.bot run      # keeps running, answers your commands

Token and chat id come from .env (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID).
Messages from any other chat are ignored and never answered.
"""

from __future__ import annotations

import logging
import os
import sys
import time

from signals.dispatcher.commands import handle
from signals.dispatcher.telegram_client import ConfigError, TelegramClient, load_env

log = logging.getLogger("asgo.bot")


def process_update(client: TelegramClient, update: dict, responder=handle) -> bool:
    """Answers one update. Returns True if it was answered."""
    msg = update.get("message") or {}
    chat = msg.get("chat") or {}
    if chat.get("id") != client.chat_id or chat.get("type") != "private":
        log.warning("ignored message from a chat that is not the owner's")
        return False
    text = msg.get("text")
    if not text:
        return False
    client.send_message(responder(text))
    return True


def run(client: TelegramClient) -> None:
    me = client.get_me()
    log.info("bot @%s started; answering only the owner's chat", me.get("username"))
    offset = None
    while True:
        try:
            for upd in client.get_updates(offset):
                offset = upd["update_id"] + 1
                try:
                    process_update(client, upd)
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
            seen[chat["id"]] = chat.get("first_name", "")
    if not seen:
        print("Henüz mesaj yok. Telegram'da botuna bir mesaj (ör. 'merhaba') at, sonra tekrar çalıştır.")
    for cid, name in seen.items():
        print(f"Chat ID: {cid}  ({name})  -> bunu .env içine TELEGRAM_CHAT_ID olarak yaz")


def main(argv: list[str]) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cmd = argv[1] if len(argv) > 1 else "run"
    try:
        if cmd == "chatid":
            print_chat_ids()
            return 0
        client = TelegramClient.from_env()
        if cmd == "test":
            client.send_message("✅ ASGO botu bağlandı. Bu bir deneme mesajıdır.\n\n/yardim yazarak komutları görebilirsin.")
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
