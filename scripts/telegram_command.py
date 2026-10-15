"""
Answers one Telegram command about the Bitget DEMO account (play money).

Bitget blocks requests from Cloudflare's servers, so the Cloudflare bot (telegram_worker/)
only checks who is asking and then starts .github/workflows/telegram_command.yml, which runs
this script on a GitHub runner (Bitget answers there) and sends the reply to Telegram.

Every signed Bitget request carries the demo header (paptrading: 1); there is no live path.
Standard library only, so the workflow starts fast.

    python scripts/telegram_command.py --cmd /durum --chat 123 --sender 123
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from signals.dispatcher.telegram_client import TelegramClient  # noqa: E402

BITGET = "https://api.bitget.com"
PRODUCT = "USDT-FUTURES"


def demo_headers(key: str, secret: str, passphrase: str, method: str, request_path: str, body: str) -> dict:
    ts = str(int(time.time() * 1000))
    sign = base64.b64encode(hmac.new(secret.encode(), (ts + method + request_path + body).encode(),
                                     hashlib.sha256).digest()).decode()
    headers = {
        "ACCESS-KEY": key, "ACCESS-SIGN": sign, "ACCESS-TIMESTAMP": ts, "ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json", "locale": "en-US",
        "paptrading": "1",  # demo account only; never removed
    }
    if headers.get("paptrading") != "1":
        raise RuntimeError("STOP: request without the demo header")
    return headers


def bitget(method: str, path: str, query: dict | None = None, body: dict | None = None, signed: bool = True,
           opener=urllib.request.urlopen):
    qs = urllib.parse.urlencode(query or {})
    request_path = path + (f"?{qs}" if qs else "")
    body_text = json.dumps(body, separators=(",", ":")) if body else ""
    headers = {"Content-Type": "application/json"}
    if signed:
        headers = demo_headers(os.environ["BITGET_DEMO_API_KEY"], os.environ["BITGET_DEMO_API_SECRET"],
                               os.environ["BITGET_DEMO_API_PASSPHRASE"], method, request_path, body_text)
    req = urllib.request.Request(BITGET + request_path, data=body_text.encode() or None, headers=headers,
                                 method=method)
    try:
        with opener(req, timeout=20) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
    try:
        data = json.loads(raw)
    except ValueError:
        raise RuntimeError(f"Bitget: {' '.join(raw.split())[:150]}") from None
    if data.get("code") != "00000":
        raise RuntimeError(f"Bitget {data.get('code')}: {data.get('msg')}")
    return data.get("data")


def num(x, d: int = 2) -> str:
    """Turkish number format: 9.999,50"""
    s = f"{float(x or 0):,.{d}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def coin(symbol: str) -> str:
    return re.sub(r"USDT$", "", symbol)


def symbol_of(word: str) -> str:
    return re.sub(r"USDT$", "", re.sub(r"[^A-Z0-9]", "", (word or "").upper())) + "USDT"


def status(call=bitget) -> str:
    accounts = call("GET", "/api/v2/mix/account/accounts", {"productType": PRODUCT}) or []
    usdt = next((a for a in accounts if a.get("marginCoin") == "USDT"), {})
    positions = call("GET", "/api/v2/mix/position/all-position", {"productType": PRODUCT, "marginCoin": "USDT"}) or []
    lines = [f"Bakiye: {num(usdt.get('accountEquity'))} USDT (kullanılabilir {num(usdt.get('available'))})",
             f"Açık kâr/zarar: {num(usdt.get('unrealizedPL'))} USDT", ""]
    if not positions:
        lines.append("Açık işlem yok.")
    for p in positions:
        lines.append(f"• {coin(p['symbol'])} {p.get('holdSide')}: {p.get('total')} adet, giriş {p.get('openPriceAvg')}, "
                     f"şimdi {p.get('markPrice')}, kâr/zarar {num(p.get('unrealizedPL'))} USDT")
    return "\n".join(lines)


def history(call=bitget) -> str:
    data = call("GET", "/api/v2/mix/position/history-position", {"productType": PRODUCT, "limit": "10"}) or {}
    items = data.get("list") or []
    if not items:
        return "Henüz kapanmış işlem yok."
    lines = ["Son kapanan işlemler:"]
    for p in items:
        ms = int(p.get("utime") or p.get("uTime") or p.get("ctime") or 0)
        day = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        net = p.get("netProfit") if p.get("netProfit") is not None else p.get("pnl")
        lines.append(f"• {day} {coin(p['symbol'])} {p.get('holdSide')}: giriş {p.get('openAvgPrice')}, "
                     f"çıkış {p.get('closeAvgPrice')}, net {num(net)} USDT")
    return "\n".join(lines)


def price(word: str, call=bitget) -> str:
    if not word:
        return "Hangi coin? Örnek: /fiyat BTC"
    try:
        data = call("GET", "/api/v2/mix/market/ticker", {"symbol": symbol_of(word), "productType": PRODUCT},
                    signed=False)
    except RuntimeError:
        data = None
    if not data:
        return f"{word.upper()} bulunamadı."
    t = data[0]
    change = float(t.get("change24h") or 0) * 100
    return (f"{coin(t['symbol'])}: {t.get('lastPr')} USDT (24 saat {'+' if change >= 0 else ''}{change:.2f}%). "
            "Bilgi amaçlıdır, sinyal değildir.")


def close(word: str, call=bitget) -> str:
    if not word:
        return "Hangi coin? Örnek: /kapat NEAR"
    symbol = symbol_of(word)
    positions = call("GET", "/api/v2/mix/position/all-position", {"productType": PRODUCT, "marginCoin": "USDT"}) or []
    if not any(p.get("symbol") == symbol for p in positions):
        return f"{coin(symbol)} için açık demo işlemi yok."
    call("POST", "/api/v2/mix/order/close-positions", None, {"symbol": symbol, "productType": PRODUCT})
    return f"{coin(symbol)} demo işlemi piyasa fiyatından kapatıldı. /durum ile kontrol edebilirsin."


# ------------------------------------------------------------------ /yorum: market comment
# Facts only from live public candles and the same daily-trend score the demo bots use
# (scripts/bitget_fitil.py daily_ok). Never a level, target or buy/sell call.
DEMO_COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "LINK", "LTC", "DOT", "AVAX", "TRX", "BCH",
              "UNI", "NEAR"]
FNG_TR = {"Extreme Fear": "aşırı korku", "Fear": "korku", "Neutral": "nötr", "Greed": "açgözlülük",
          "Extreme Greed": "aşırı açgözlülük"}


def closes(word: str, granularity: str, limit: int, call=bitget) -> list[list[float]]:
    rows = call("GET", "/api/v2/mix/market/candles", {"symbol": symbol_of(word), "productType": PRODUCT,
                                                     "granularity": granularity, "limit": str(limit)},
                signed=False) or []
    return sorted([[float(v) for v in r[:5]] for r in rows], key=lambda r: r[0])


def ema(values: list[float], span: int) -> float:
    k, e = 2 / (span + 1), values[0]
    for v in values[1:]:
        e = v * k + e * (1 - k)
    return e


def trend(daily: list[list[float]]) -> tuple[int, bool] | None:
    """Score -3..+3 and 'close above EMA20' on the last CLOSED day (the running day is dropped)."""
    c = [r[4] for r in daily[:-1]]
    if len(c) < 91:
        return None
    e20, e50 = ema(c, 20), ema(c, 50)
    sign = lambda x: (x > 0) - (x < 0)  # noqa: E731
    return sign(c[-1] - e50) + sign(e20 - e50) + sign(c[-1] / c[-91] - 1), c[-1] > e20


def fear_greed(opener=urllib.request.urlopen) -> str | None:
    try:
        with opener(urllib.request.Request("https://api.alternative.me/fng/?limit=1"), timeout=10) as resp:
            d = json.loads(resp.read().decode())["data"][0]
        return f"{d['value']}/100 ({FNG_TR.get(d['value_classification'], d['value_classification'])})"
    except Exception:
        return None


def pct(a: float, b: float) -> str:
    x = (a / b - 1) * 100
    return f"{'+' if x >= 0 else ''}{x:.1f}%"


def comment_facts(word: str, call=bitget, fng=fear_greed) -> str:
    daily = closes(word, "1D", 120, call)
    hourly = closes(word, "1H", 25, call)
    if len(daily) < 10 or len(hourly) < 25:
        return f"{word.upper()} için yeterli veri yok."
    last = hourly[-1][4]
    lo, hi = min(r[3] for r in hourly[-24:]), max(r[2] for r in hourly[-24:])
    where = (last - lo) / (hi - lo) * 100 if hi > lo else 50
    t = trend(daily)
    up = 0
    for c in DEMO_COINS:
        try:
            ct = trend(closes(c, "1D", 120, call))
        except RuntimeError:
            ct = None
        up += bool(ct and ct[0] >= 1 and ct[1])
    name = coin(symbol_of(word))
    lines = [f"{name} yorumu (Bitget, şimdi)",
             f"Fiyat {last:g} USDT: 24 saatte {pct(last, hourly[-25][4])}, 7 günde {pct(last, daily[-8][4])}.",
             f"Son 24 saat aralığı {lo:g} - {hi:g}; fiyat bu aralığın %{where:.0f} seviyesinde."]
    if t is None:
        lines.append("Günlük trend: yeterli geçmiş yok.")
        verdict = "Bu coin için trend ölçülemiyor."
    else:
        score, above = t
        lines.append(f"Günlük trend puanı {score:+d}/3, fiyat 20 günlük ortalamanın {'üstünde' if above else 'altında'}.")
        if score >= 1 and above:
            verdict = "Yükselen trend. Botlarımız bu coinde sert düşüşlerde alım fırsatı arar."
        elif score <= -1 and not above:
            verdict = "Düşüş trendi. Botlarımız bu coinde alım yapmaz, beklemede."
        else:
            verdict = "Kararsız, net yön yok. Botlarımız trend netleşene kadar bekler."
    lines.append(f"Piyasa geneli: botların izlediği 15 coinden {up} tanesi yükselen trendde.")
    f = fng()
    if f:
        lines.append(f"Korku-açgözlülük endeksi: {f}.")
    lines += ["", f"Özet: {verdict}"]
    return "\n".join(lines)


def ai_rewrite(facts: str, opener=urllib.request.urlopen) -> str | None:
    """Optional: turn the facts into a short natural comment with Gemini (AI_API_KEY). No levels, ever."""
    key = os.environ.get("AI_API_KEY")
    if not key:
        return None
    prompt = ("Aşağıdaki kripto piyasa verilerini sade Türkçe ile 3-4 cümlelik bir yorum olarak anlat. "
              "Sadece verilen bilgileri kullan, yeni rakam uydurma. Fiyat hedefi, giriş, stop veya al/sat "
              "tavsiyesi verme. Son cümle olarak 'Bilgi amaçlıdır, sinyal değildir.' yaz.\n\n" + facts)
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        data=body, headers={"Content-Type": "application/json", "x-goog-api-key": key}, method="POST")
    try:
        with opener(req, timeout=25) as resp:
            out = json.loads(resp.read().decode())
        return out["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return None


def market_comment(word: str, call=bitget, fng=fear_greed, ai=ai_rewrite) -> str:
    if not word:
        return "Hangi coin? Örnek: /yorum ETH"
    try:
        facts = comment_facts(word, call, fng)
    except RuntimeError:
        return f"{word.upper()} bulunamadı."
    if "yorumu" not in facts:  # not enough data: say so as is
        return facts
    text = ai(facts)
    return f"{text}\n\n---\n{facts}" if text else f"{facts}\n\nBilgi amaçlıdır, sinyal değildir."


def run(cmd: str, arg: str, sender_is_owner: bool, call=bitget) -> str:
    cmd = cmd.lower().split("@")[0]
    try:
        if cmd == "/durum":
            return status(call)
        if cmd == "/gecmis":
            return history(call)
        if cmd == "/fiyat":
            return price(arg, call)
        if cmd == "/yorum":
            return market_comment(arg, call)
        if cmd == "/kapat":
            if not sender_is_owner:
                return "İşlem kapatmayı sadece hesap sahibi yapabilir."
            return close(arg, call)
        return "Bu komutu tanımıyorum. /yardim yaz."
    except Exception as e:  # report, never crash silently
        return f"Bir sorun oldu: {str(e)[:200]}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmd", required=True)
    ap.add_argument("--arg", default="")
    ap.add_argument("--chat", required=True)
    ap.add_argument("--sender", required=True)
    a = ap.parse_args()
    tg = TelegramClient.from_env()
    chat = int(a.chat)
    if chat not in tg.allowed_chats:  # the worker already checks; this is the second lock
        print("chat not allowed; nothing sent")
        return 1
    text = run(a.cmd, a.arg.strip(), sender_is_owner=int(a.sender) == tg.chat_id)
    tg.send_message(text, chat_id=chat)
    print("answered", a.cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
