"""
Answers the owner's Telegram commands ("btc'ye bak", "/eth", "/durum" ...).

Rule (PROJECT_BRIEF 1.3 and 13): the bot never invents levels or reasons.
A pair query only reports:
  - which active (tested) strategies watch the pair,
  - the last logged signal for that pair (signals/log/), exactly as logged,
  - the current market price and 24h change, labelled as information only.
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from typing import Callable

from signals.schema import LOG_DIR, Signal

REPO = Path(__file__).resolve().parents[2]
ACTIVE_DIR = REPO / "strategies" / "active"
PAIRS_FILE = REPO / "config" / "pairs_level1.json"
ROADMAP = REPO / "docs" / "roadmap.md"

# Spoken / Turkish-suffixed names -> base symbol. Longest match wins.
ALIASES = {
    "btc": "BTC", "bitcoin": "BTC",
    "eth": "ETH", "ether": "ETH", "ethereum": "ETH",
    "sol": "SOL", "solana": "SOL",
    "xrp": "XRP", "ripple": "XRP",
    "bnb": "BNB",
    "doge": "DOGE", "dogecoin": "DOGE",
}

HELP = (
    "Merhaba, ben ASGO botu. Sadece sana cevap veririm.\n\n"
    "Komutlar:\n"
    "• btc / eth / sol ... (ya da \"btc'ye bak\"): o coin için test edilmiş stratejilerin "
    "şu an ne dediği + güncel fiyat\n"
    "• /durum: projenin hangi seviyede olduğu, kaç strateji aktif\n"
    "• /liste: takip edilen coinler\n"
    "• /yardim: bu mesaj\n\n"
    "Not: Bot kendi kafasına göre alım/stop/hedef seviyesi söylemez. Seviyeler sadece "
    "testi geçmiş stratejilerden gelir."
)

PriceFetcher = Callable[[str], "dict | None"]


def binance_price(symbol: str) -> dict | None:
    """Last price and 24h change from Binance USDⓈ-M public endpoint. None on any error."""
    url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}USDT"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            d = json.loads(resp.read().decode())
        return {"price": float(d["lastPrice"]), "change_pct": float(d["priceChangePercent"])}
    except Exception:
        return None


def known_pairs() -> list[str]:
    try:
        return json.loads(PAIRS_FILE.read_text(encoding="utf-8"))["exchange"]["pair_whitelist"]
    except Exception:
        return []


def active_strategies() -> list[str]:
    if not ACTIVE_DIR.is_dir():
        return []
    return sorted(p.stem for p in ACTIVE_DIR.glob("*.py") if not p.name.startswith("_"))


def current_level() -> str:
    try:
        m = re.search(r"Şu anki seviye:\s*([^*(]+)", ROADMAP.read_text(encoding="utf-8"))
        return m.group(1).strip() if m else "?"
    except Exception:
        return "?"


def find_symbol(text: str) -> str | None:
    words = re.findall(r"[a-zçğıöşü0-9]+", text.lower().replace("'", " ").replace("’", " "))
    pair_bases = {p.split("/")[0].lower(): p.split("/")[0] for p in known_pairs()}
    names = {**pair_bases, **ALIASES}
    for w in words:
        # "ethere", "btcye", "solanaya" -> longest alias the word starts with
        for name in sorted(names, key=len, reverse=True):
            if w == name or (w.startswith(name) and len(name) >= 3):
                return names[name]
    return None


def last_signal(symbol: str, log_dir: Path = LOG_DIR) -> Signal | None:
    best = None
    for path in log_dir.glob("*.json"):
        try:
            sig = Signal.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
        if sig.pair.split("/")[0] == symbol and (best is None or sig.timestamp > best.timestamp):
            best = sig
    return best


def format_signal_short(sig: Signal) -> str:
    zone = f"{sig.entry_zone.high:g} - {sig.entry_zone.low:g}"
    side = "LONG" if sig.side == "long" else "SHORT"
    tps = " | ".join(f"{t.level}: {t.price:g} ({t.R:g}R)" for t in sig.targets)
    return (f"{sig.timestamp} · {sig.strategy} · {side} ({sig.timeframe})\n"
            f"Bölge: {zone} | Stop: {sig.stop:g}\n{tps}\nDurum: {sig.status}")


def pair_report(symbol: str, price_fetcher: PriceFetcher = binance_price,
                log_dir: Path = LOG_DIR) -> str:
    lines = [f"🔎 {symbol}/USDT"]
    p = price_fetcher(symbol)
    if p:
        lines.append(f"Fiyat: {p['price']:g} (24s: {p['change_pct']:+.2f}%) · sadece bilgi, sinyal değil")
    else:
        lines.append("Fiyat: şu an alınamadı.")

    actives = active_strategies()
    tracked = any(pr.split("/")[0] == symbol for pr in known_pairs())
    if not actives:
        lines.append("\nHenüz testi geçmiş (aktif) strateji yok, o yüzden alım/stop/hedef "
                     "seviyesi veremem. İlk strateji testi geçince burada görünecek.")
    elif not tracked:
        lines.append(f"\n{symbol} takip listesinde değil; aktif stratejiler bu coine bakmıyor.")
    else:
        lines.append("\nBakan aktif stratejiler: " + ", ".join(actives))

    sig = last_signal(symbol, log_dir)
    if sig:
        lines.append("\nSon sinyal (kayıttan, olduğu gibi):\n" + format_signal_short(sig))
    elif actives and tracked:
        lines.append("Şu an bu coin için açık bir sinyal yok; koşullar oluşmamış.")
    return "\n".join(lines)


def status_report() -> str:
    actives = active_strategies()
    return (f"📊 Durum\nSeviye: {current_level()}\n"
            f"Aktif strateji: {len(actives)}" + (f" ({', '.join(actives)})" if actives else "") +
            "\nSinyal gönderimi: " + ("açık" if actives else "kapalı (testi geçen strateji yok)"))


def handle(text: str, price_fetcher: PriceFetcher = binance_price, log_dir: Path = LOG_DIR) -> str:
    t = (text or "").strip()
    cmd = t.lower().split()[0].split("@")[0] if t else ""
    if cmd in ("/start", "/yardim", "/yardım", "/help", "yardim", "yardım"):
        return HELP
    if cmd in ("/durum", "durum", "/status"):
        return status_report()
    if cmd in ("/liste", "liste"):
        pairs = known_pairs()
        return "Takip edilen coinler: " + (", ".join(p.split("/")[0] for p in pairs) or "yok")
    symbol = find_symbol(t)
    if symbol:
        return pair_report(symbol, price_fetcher, log_dir)
    return "Anlayamadım. Örnek: \"btc'ye bak\", \"/eth\", \"/durum\". Tüm komutlar için /yardim."
