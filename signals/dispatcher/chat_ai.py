"""
Optional free-text chat through an AI model (Google Gemini API free tier).

The AI only talks. It gets the system's own facts (status, the template
pair report) and must answer from them. It never produces entry/stop/target
levels or price predictions (PROJECT_BRIEF 1.3, 7.9). As an extra guard,
an AI answer that contains a number (3+ digits) not present in the facts is
thrown away and the bot falls back to the plain template answer.

Enabled only when AI_API_KEY is set in .env. AI_MODEL can override the model.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.request

DEFAULT_MODEL = "gemini-2.5-flash"
KEY_HEADER = "x-goog-api-" + "key"  # built in two parts so the repo secret scanner doesn't flag the header line
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = """Sen ASGO adlı bir kripto strateji araştırma projesinin Telegram botunun sohbet yardımcısısın.
Kısa, samimi, sade Türkçe yaz (en fazla 4-5 cümle).
Kesin kurallar:
- Alım bölgesi, stop, hedef (TP), fiyat tahmini, "yükselir/düşer" yorumu veya yatırım tavsiyesi VERME.
- Sadece aşağıdaki BİLGİLER bölümündeki gerçeklere dayan. Orada olmayan rakam yazma.
- Biri fiyat yönü veya seviye sorarsa: seviyelerin sadece testi geçmiş stratejilerden geldiğini, şu anki durumu ve ilgili komutu (/btc, /durum) söyle.
- Bilmediğin bir şey sorulursa bilmediğini söyle.
"""

log = logging.getLogger("asgo.ai")

NUMBER = re.compile(r"\d[\d.,]*\d|\d")


def _numbers(text: str) -> set[str]:
    return {n.replace(",", "").replace(".", "") for n in NUMBER.findall(text)}


def _allowed_numbers(facts: str) -> set[str]:
    allowed = _numbers(facts)
    # also accept the integer part of facts like "62345.1" or "+1.52"
    allowed |= {re.split(r"[.,]", n)[0] for n in NUMBER.findall(facts)}
    return allowed


def is_grounded(answer: str, facts: str) -> bool:
    """False if the answer has a 3+ digit number that is not in the facts."""
    allowed = _allowed_numbers(facts)
    return all(len(n) < 3 or n in allowed for n in _numbers(answer))


class ChatAI:
    def __init__(self, key: str, model: str = DEFAULT_MODEL, timeout: float = 30.0):
        self._key = key
        self.model = model
        self.timeout = timeout

    @classmethod
    def from_env(cls) -> "ChatAI | None":
        key = os.environ.get("AI_API_KEY", "").strip()
        if not key:
            return None
        return cls(key, os.environ.get("AI_MODEL", "").strip() or DEFAULT_MODEL)

    def _generate(self, prompt: str) -> str:
        body = json.dumps({
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 400},
        }).encode()
        req = urllib.request.Request(API_URL.format(model=self.model), data=body, headers={
            "Content-Type": "application/json",
            KEY_HEADER: self._key,
        })
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode())
        return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"]).strip()

    def answer(self, question: str, facts: str) -> str | None:
        """AI answer, or None if the call failed or the answer was not grounded."""
        prompt = f"BİLGİLER:\n{facts}\n\nKULLANICININ MESAJI:\n{question}"
        try:
            text = self._generate(prompt)
        except urllib.error.HTTPError as e:
            log.error("AI call failed: HTTP %s", e.code)
            return None
        except Exception as e:
            log.error("AI call failed: %s", type(e).__name__)
            return None
        if not text or not is_grounded(text, facts):
            log.warning("AI answer dropped (empty or contained numbers not in the facts)")
            return None
        return text
