"""
Sends one plain note to the owner's PRIVATE Telegram chat (TELEGRAM_CHAT_ID), never to the group.
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
    text = ap.parse_args().text.strip()[:1500]
    if not text:
        print("empty note; nothing sent")
        return 1
    TelegramClient.from_env().send_message(text)  # default chat = the owner's private chat
    print("note sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
