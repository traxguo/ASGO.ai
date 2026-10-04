"""
Minimal Telegram Bot API client (standard library only).

The client is locked to ONE chat id: the project owner's personal chat
(PROJECT_BRIEF rule 7). Sending to any other chat raises an error, and
incoming messages from other chats are dropped by the bot.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://api.telegram.org"
REPO = Path(__file__).resolve().parents[2]


class ConfigError(RuntimeError):
    pass


def load_env(path: Path = REPO / ".env") -> None:
    """Reads KEY=value lines from .env into os.environ (existing values win)."""
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_chat_id(raw: str | None) -> int:
    raw = (raw or "").strip()
    if not raw:
        raise ConfigError("TELEGRAM_CHAT_ID is empty in .env")
    try:
        chat_id = int(raw)
    except ValueError as e:
        raise ConfigError("TELEGRAM_CHAT_ID must be a number") from e
    # Personal chats have positive ids; groups and channels are negative.
    if chat_id <= 0:
        raise ConfigError("TELEGRAM_CHAT_ID must be a personal chat (positive number), not a group or channel")
    return chat_id


class TelegramClient:
    def __init__(self, token: str, chat_id: int, timeout: float = 70.0):
        if not token or ":" not in token:
            raise ConfigError("TELEGRAM_BOT_TOKEN is missing or malformed in .env")
        self._token = token
        self.chat_id = chat_id
        self.timeout = timeout

    @classmethod
    def from_env(cls) -> "TelegramClient":
        load_env()
        return cls(os.environ.get("TELEGRAM_BOT_TOKEN", "").strip(),
                   parse_chat_id(os.environ.get("TELEGRAM_CHAT_ID")))

    def _call(self, method: str, params: dict) -> dict:
        url = f"{API_BASE}/bot{self._token}/{method}"
        data = urllib.parse.urlencode(params).encode()
        try:
            with urllib.request.urlopen(url, data=data, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            # Never include the URL: it contains the token.
            try:
                desc = json.loads(e.read().decode()).get("description", "")
            except Exception:
                desc = ""
            raise RuntimeError(f"Telegram {method} failed: HTTP {e.code} {desc}") from None
        except urllib.error.URLError as e:
            raise RuntimeError(f"Telegram {method} failed: {e.reason}") from None
        if not body.get("ok"):
            raise RuntimeError(f"Telegram {method} failed: {body.get('description', '')}")
        return body["result"]

    def get_me(self) -> dict:
        return self._call("getMe", {})

    def send_message(self, text: str, chat_id: int | None = None) -> dict:
        target = self.chat_id if chat_id is None else chat_id
        if target != self.chat_id:
            raise PermissionError("messages may only go to the owner's personal chat")
        return self._call("sendMessage", {
            "chat_id": target,
            "text": text,
            "disable_web_page_preview": "true",
        })

    def get_updates(self, offset: int | None, poll_seconds: int = 50) -> list[dict]:
        params = {"timeout": poll_seconds, "allowed_updates": json.dumps(["message"])}
        if offset is not None:
            params["offset"] = offset
        return self._call("getUpdates", params)
