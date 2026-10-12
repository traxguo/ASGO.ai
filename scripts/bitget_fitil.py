"""
Runs Fitil Avcisi (cards/fitil_avcisi.md) on the Bitget DEMO account (play money, PAPTRADING header on every
signed request, same guard as scripts/bitget_demo.py). Started every 15 minutes by the Cloudflare clock.

Each run:
1. pending buy limits: filled -> open trade (closed at once if BTC fell >= 3% in that hour, the tested guard);
   not filled after one hour, or BTC already down >= 3% -> cancelled
2. open trades: market close 3 hours after the fill (no stop, as tested)
3. first run of a new hour: for coins in a daily uptrend (score >= +1 and close > EMA20, last closed day),
   a buy limit at 95% of the hour's open price, one per coin, each sized equity / 5

    python scripts/bitget_fitil.py          # trade (needs BITGET_DEMO_API_* secrets)
    python scripts/bitget_fitil.py --check  # no keys: print today's eligible coins and the limit prices
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bitget_demo as bd  # noqa: E402  (exchange helpers and the demo-only guard)

REPO = Path(__file__).resolve().parents[1]
PAIRS_FILE = REPO / "config" / "pairs_all36.json"
OUT_DIR = REPO / "forward" / "bitget_fitil"
STATE_FILE = OUT_DIR / "state.json"
OTHER_STATE_FILES = [REPO / "forward" / "bitget_demo" / "state.json",
                     REPO / "forward" / "bitget_demo_dalga" / "state.json"]
DEPTH = 0.05          # limit this far under the hour's open
HOLD_HOURS = 3
BTC_GUARD = 0.03      # skip when BTC is down this much from the hour's open
MAX_OPEN = 5          # each trade gets equity / MAX_OPEN
LEVERAGE = 3          # margin only; total exposure stays about 1x equity
MIN_SCORE = 1
BTC = "BTC/USDT:USDT"
TRADE_FIELDS = ["pair", "hour", "limit_price", "fill_time", "fill_price", "amount", "exit_time", "exit_price",
                "exit_reason", "pnl_usdt", "fees_usdt", "ret_pct"]


def daily_ok(daily: pd.DataFrame) -> tuple[bool, float]:
    """Daily uptrend on the last CLOSED day: score >= MIN_SCORE and close above EMA20 (as in the scan)."""
    c = daily["close"].astype(float).reset_index(drop=True)
    if len(c) < 91:
        return False, float("nan")
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    score = float(np.sign(c.iloc[-1] - e50.iloc[-1]) + np.sign(e20.iloc[-1] - e50.iloc[-1])
                  + np.sign(c.iloc[-1] / c.iloc[-91] - 1))
    return score >= MIN_SCORE and c.iloc[-1] > e20.iloc[-1], score


def hour_open_price(pub, pair: str, hour: datetime) -> float | None:
    rows = pub.fetch_ohlcv(pair, "1h", since=int(hour.timestamp() * 1000), limit=2)
    for r in rows:
        if r[0] == int(hour.timestamp() * 1000):
            return float(r[1])
    return None


def btc_drop(pub, hour: datetime, now: datetime) -> float:
    """How far BTC has fallen from the hour's open (0.03 = -3%), using 1m lows up to now."""
    rows = pub.fetch_ohlcv(BTC, "1m", since=int(hour.timestamp() * 1000), limit=200)
    rows = [r for r in rows if hour.timestamp() * 1000 <= r[0] <= now.timestamp() * 1000]
    if not rows:
        return 0.0
    return 1 - min(float(r[3]) for r in rows) / float(rows[0][1])


def busy_elsewhere() -> set[str]:
    out = set()
    for path in OTHER_STATE_FILES:
        if path.is_file():
            for t in json.loads(path.read_text(encoding="utf-8")).get("trades", {}).values():
                if t.get("status") in ("pending", "open"):
                    out.add(t["pair"])
    return out


class Log:
    def __init__(self):
        self.lines: list[str] = []

    def event(self, now: datetime, pair: str, what: str, detail: str = "", tell: bool = False) -> None:
        print(f"{now:%Y-%m-%d %H:%M} {pair}: {what} {detail}")
        bd.append_csv(OUT_DIR / "events.csv", ["time", "pair", "event", "detail"],
                      {"time": now.isoformat(), "pair": pair, "event": what, "detail": detail})
        if tell:
            self.lines.append(f"• {pair.split('/')[0]}: {detail}")


def close_trade(ex, log: Log, now: datetime, t: dict, reason: str) -> None:
    pair = t["pair"]
    if bd.position_size(ex, pair) > 0:
        ex.create_order(pair, "market", "sell", t["amount"], None,
                        {**bd.PRODUCT, "reduceOnly": True, "marginMode": "isolated"})
    fill_time = datetime.fromisoformat(t["fill_time"])
    price, _, fees = bd.close_fills(ex, pair, fill_time, "sell")
    fees += float(t.get("entry_fees") or 0)
    pnl = (price - t["fill_price"]) * t["amount"] - fees if price == price else float("nan")
    ret = pnl / (t["fill_price"] * t["amount"]) * 100 if pnl == pnl else float("nan")
    t.update(status="closed", exit_time=now.isoformat(), exit_price=price, exit_reason=reason,
             pnl_usdt=round(pnl, 4), fees_usdt=round(fees, 4), ret_pct=round(ret, 3))
    bd.append_csv(OUT_DIR / "trades.csv", TRADE_FIELDS, t)
    tr = {"time_exit": "3 saat doldu, satıldı", "btc_guard": "BTC de çakıldı, hemen satıldı",
          "over_limit": "5 işlem sınırı doluydu, hemen satıldı"}[reason]
    log.event(now, pair, "closed", f"{tr}, sonuç %{ret:+.2f}", tell=True)


def run_once(ex, pub, state: dict, now: datetime, log: Log, pairs: list[str]) -> None:
    trades = state.setdefault("trades", {})
    hour = now.replace(minute=0, second=0, microsecond=0)

    # 1. pending limits
    drops: dict = {}
    for cid, t in trades.items():
        if t["status"] != "pending":
            continue
        h = datetime.fromisoformat(t["hour"])
        if h not in drops:
            drops[h] = btc_drop(pub, h, min(now, h + timedelta(hours=1)))
        order = ex.fetch_order(t["order_id"], t["pair"], bd.PRODUCT)
        filled = float(order.get("filled") or 0)
        if order.get("status") == "open" and (now >= h + timedelta(hours=1) or drops[h] >= BTC_GUARD):
            ex.cancel_order(t["order_id"], t["pair"], bd.PRODUCT)
            if filled == 0:
                t["status"] = "cancelled"
                log.event(now, t["pair"], "limit cancelled", "BTC guard" if drops[h] >= BTC_GUARD else "hour over")
                continue
        if filled > 0:
            ft = datetime.fromtimestamp((order.get("lastTradeTimestamp") or order["timestamp"]) / 1000, tz=timezone.utc)
            t.update(status="open", amount=filled, fill_time=ft.isoformat(),
                     fill_price=float(order.get("average") or order["price"]),
                     entry_fees=float((order.get("fee") or {}).get("cost") or 0))
            log.event(now, t["pair"], "filled", f"panik fitili yakalandı, {filled} adet @ {t['fill_price']:.6g}",
                      tell=True)
            if drops[h] >= BTC_GUARD:
                close_trade(ex, log, now, t, "btc_guard")
        elif order.get("status") in ("canceled", "cancelled", "rejected", "expired"):
            t["status"] = "cancelled"
            log.event(now, t["pair"], "limit cancelled", f"by exchange ({order.get('status')})")

    # 2. open trades: over the cap (fills beyond MAX_OPEN, latest first) or time exit
    opened = sorted((t for t in trades.values() if t["status"] == "open"), key=lambda t: t["fill_time"])
    for t in opened[MAX_OPEN:]:
        close_trade(ex, log, now, t, "over_limit")
    for t in opened[:MAX_OPEN]:
        if now >= datetime.fromisoformat(t["fill_time"]) + timedelta(hours=HOLD_HOURS):
            close_trade(ex, log, now, t, "time_exit")

    # 3. new limits, once per hour
    if state.get("last_hour") == hour.isoformat():
        return
    state["last_hour"] = hour.isoformat()
    if btc_drop(pub, hour, now) >= BTC_GUARD:
        log.event(now, "-", "no new limits", "BTC already down 3% this hour")
        return
    equity, free = bd.demo_balance(ex.fetch_balance({"type": "swap", **bd.PRODUCT}))
    if equity <= 0:
        log.event(now, "-", "no demo balance found")
        return
    busy = {t["pair"] for t in trades.values() if t["status"] in ("pending", "open")} | busy_elsewhere()
    for pair in pairs:
        if pair in busy or not bd.listed(ex, pair):
            continue
        ok, score = daily_ok(bd.fetch_candles(pub, pair, "1d", 120, now))
        if not ok:
            continue
        ref = hour_open_price(pub, pair, hour)
        if ref is None:
            continue
        price = float(ex.price_to_precision(pair, ref * (1 - DEPTH)))
        amount = float(ex.amount_to_precision(pair, equity / MAX_OPEN / price))
        if amount <= 0 or equity / MAX_OPEN / LEVERAGE > free:
            log.event(now, pair, "limit skipped", "size or margin")
            continue
        try:
            ex.set_margin_mode("isolated", pair, bd.PRODUCT)
        except Exception as e:  # already isolated
            print(f"{pair}: margin mode unchanged ({e})")
        try:
            ex.set_leverage(LEVERAGE, pair, {**bd.PRODUCT, "marginMode": "isolated"})
        except Exception:
            ex.set_leverage(LEVERAGE, pair, {**bd.PRODUCT, "marginMode": "isolated", "holdSide": "long"})
        cid = f"fit{pair.split('/')[0].lower()}{hour:%Y%m%d%H}"
        order = ex.create_order(pair, "limit", "buy", amount, price,
                                {**bd.PRODUCT, "marginMode": "isolated", "clientOrderId": cid})
        trades[cid] = {"pair": pair, "status": "pending", "order_id": order["id"], "hour": hour.isoformat(),
                       "limit_price": price}
        free -= equity / MAX_OPEN / LEVERAGE
        log.event(now, pair, "limit placed", f"{amount} @ {price:.6g} (hour open {ref:.6g}, score {score:+.0f})")


def notify(lines: list[str]) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not lines or not token:
        return
    from signals.dispatcher.telegram_client import TelegramClient, parse_chat_id

    text = "Bitget demo (Fitil Avcısı)\n" + "\n".join(lines)
    targets = [parse_chat_id(os.environ.get("TELEGRAM_CHAT_ID"))]
    group = os.environ.get("TELEGRAM_GROUP_ID", "").strip()
    if group.lstrip("-").isdigit() and int(group) < 0:  # the one group the owner chose (rule 7)
        targets.append(int(group))
    for chat in targets:
        try:
            TelegramClient(token, chat, timeout=20).send_message(text)
        except Exception as e:  # noqa: BLE001 - a message problem must not stop trading
            print(f"telegram message not sent: {e}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="no keys: print eligible coins and limit prices")
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    pairs = json.loads(PAIRS_FILE.read_text(encoding="utf-8"))["exchange"]["pair_whitelist"]
    pub = bd.public_exchange()
    if a.check:
        hour = now.replace(minute=0, second=0, microsecond=0)
        print(f"BTC drop this hour: {btc_drop(pub, hour, now):.2%}")
        n = 0
        for pair in pairs:
            ok, score = daily_ok(bd.fetch_candles(pub, pair, "1d", 120, now))
            ref = hour_open_price(pub, pair, hour)
            n += ok
            print(f"  {pair:16} score {score:+.0f}  eligible {ok}  limit {ref * (1 - DEPTH) if ref else float('nan'):.6g}")
        print(f"check ok: {n} eligible coins")
        return
    key, secret, phrase = (os.environ.get(f"BITGET_DEMO_API_{n}", "").strip() for n in ("KEY", "SECRET", "PASSPHRASE"))
    if not (key and secret and phrase):
        raise SystemExit("STOP: BITGET_DEMO_API_KEY / _SECRET / _PASSPHRASE are not set.")
    ex = bd.demo_exchange(key, secret, phrase)
    ex.load_markets()
    bd.check_demo_key(ex)
    ex = bd.choose_demo_product(ex, pairs)
    state = bd.load_state(STATE_FILE)
    log = Log()
    run_once(ex, pub, state, now, log, pairs)
    notify(log.lines)
    bd.save_state(state, STATE_FILE)


if __name__ == "__main__":
    main()
