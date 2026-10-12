"""
Sends one plain note to the owner's private Telegram chat (TELEGRAM_CHAT_ID) and, when TELEGRAM_GROUP_ID is set,
to the one group the owner chose (owner's request 2026-10-12: "Telegram gruptan yaz").
Used by .github/workflows/telegram_note.yml so Claude can tell the owner when research finds something
(owner's request 2026-10-12: "umut veren bir strateji bulursan Telegram'dan yaz").

    python scripts/telegram_note.py --text "Guo, umut veren bir strateji buldum..."
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from signals.dispatcher.telegram_client import TelegramClient  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--group-only", action="store_true", help="send only to the group (e.g. repeating an earlier note)")
    a = ap.parse_args()
    text = a.text.strip()[:1500]
    if not text:
        print("empty note; nothing sent")
        return 1
    client = TelegramClient.from_env()
    if not a.group_only:
        client.send_message(text)  # default chat = the owner's private chat
        print("note sent")
    if client.group_id is not None:  # the one group the owner chose (rule 7)
        client.send_message(text, client.group_id)
        print("note sent to the group")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
