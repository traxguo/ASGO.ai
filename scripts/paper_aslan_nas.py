"""
Paper tracking of Aslan's strategy on Nasdaq: AslanLiq2_1h WITH the daily bias filter, rules frozen as in
PR #53 / #54 (cards/aslan_liquidity.md, sections "Nasdaq testi" and "Kasa testi", holdout passed 2026-11-05).
No keys, no orders, no broker: signals are only logged and sent to Telegram (supervisor decision 2026-11-05).

Data: Yahoo Finance 1h bars of the Nasdaq-100 E-mini future (NQ=F, continuous front month), free, via
yfinance. Daily and 4h candles are built from these 1h bars on the 17:00 New York trading day, as in the
backtest. Differences to the backtest are listed in the card ("Kağıt takip").

Each run (hourly on GitHub Actions) replays the frozen rules over the last ~2 years of closed 1h candles
with the same code as the backtest (research/aslan_nasdaq/sim.py: signals_v2 + replay) and logs every
trade whose signal came after the tracking started. A logged trade is never changed afterwards.

    python scripts/paper_aslan_nas.py           # update forward/paper_aslan_nas/ and send Telegram messages
    python scripts/paper_aslan_nas.py --check   # fetch data and print the current state, save nothing
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "research" / "aslan_nasdaq"))
import sim  # noqa: E402

OUT_DIR = REPO / "forward" / "paper_aslan_nas"
SYMBOL = "NQ=F"
COST = sim.COST["NAS100"]  # same round-trip cost as the backtest
HEADER = "KÂĞIT Aslan Nasdaq (gerçek emir yok)"
FIELDS = ["sig_t", "side", "t_in", "entry", "stop", "target", "t_out", "exit", "gross_r", "net_r", "why"]


# ---------- data ----------

def fetch_1h() -> pd.DataFrame:
    import yfinance as yf

    d = yf.download(SYMBOL, period="730d", interval="1h", progress=False, auto_adjust=False)
    if d is None or d.empty:
        raise RuntimeError(f"no data from Yahoo for {SYMBOL}")
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    d = d.rename(columns=str.lower)[["open", "high", "low", "close"]].dropna()
    idx = pd.DatetimeIndex(d.index)
    d.index = idx.tz_localize("UTC") if idx.tz is None else idx.tz_convert("UTC")
    return d[~d.index.duplicated(keep="last")].sort_index().astype(float)


def closed_bars(h1: pd.DataFrame, now: datetime) -> pd.DataFrame:
    """Only 1h candles that have fully closed at `now` (Yahoo also returns the running hour)."""
    return h1[h1.index + pd.Timedelta(hours=1) <= pd.Timestamp(now)]


def frames_1h(h1: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "1h": h1.reset_index(names="date"),
        "4h": sim.session_bars(h1, 4, bar_minutes=60),
        "1d": sim.session_bars(h1, 24, bar_minutes=60),
    }


# ---------- tracking ----------

def _iso(ts) -> str:
    t = pd.Timestamp(ts)
    return (t.tz_convert("UTC") if t.tzinfo else t.tz_localize("UTC")).isoformat()


def _from_min(m: int) -> str:
    return _iso(pd.Timestamp(m * 60_000_000_000, tz="UTC"))


def _side_tr(side: str) -> str:
    return "LONG (alış)" if side == "long" else "SHORT (satış)"


def run_once(h1: pd.DataFrame, state: dict, now: datetime) -> list[str]:
    """Updates `state` from the closed candles; returns the Telegram lines for what is new."""
    msgs: list[str] = []
    if "started" not in state:
        msgs.append("Takip başladı: Nasdaq 1 saatlik Aslan kuralları (yön filtreli, 2R hedef), kurallar donduruldu.")
    started = pd.Timestamp(state.setdefault("started", now.isoformat()))
    bars = closed_bars(h1, now)
    if bars.empty:
        return msgs
    p = sim.signals_v2(frames_1h(bars), "1h", bias=True)
    r = sim.replay(p)
    trades = state.setdefault("trades", [])
    known = {t["sig_t"] for t in trades}

    # 1. closed trades, logged once and never changed
    for row in r[r["sig_t"] >= started].itertuples():
        key = _iso(row.sig_t)
        if key in known:
            continue
        net = row.gross_r - COST / row.stop_pct
        target = row.entry + (1 if row.side == "long" else -1) * 2.0 * abs(row.entry - row.stop)
        why = "hedef" if row.gross_r > 0 else "stop"
        trades.append({"sig_t": key, "side": row.side, "t_in": _iso(row.t_in), "entry": round(row.entry, 2),
                       "stop": round(row.stop, 2), "target": round(target, 2), "t_out": _iso(row.t_out),
                       "exit": round(row.exit, 2), "gross_r": round(row.gross_r, 3), "net_r": round(net, 3),
                       "why": why})
        known.add(key)
        total = sum(t["net_r"] for t in trades)
        msgs.append(f"KAPANDI {_side_tr(row.side)}: giriş {row.entry:.2f}, çıkış {row.exit:.2f} ({why}), "
                    f"{net:+.2f}R. Toplam {len(trades)} işlem, {total:+.2f}R")

    # 2. what is open after the last closed candle
    pos, order = r.attrs.get("open_pos"), r.attrs.get("open_order")
    now_open = None
    if pos is not None and pd.Timestamp(_from_min(pos["sig_t"])) >= started:
        now_open = {"status": "pozisyon", "side": pos["side"], "sig_t": _from_min(pos["sig_t"]),
                    "entry": round(pos["entry"], 2), "stop": round(pos["stop"], 2), "target": round(pos["tp"], 2)}
    elif order is not None and pd.Timestamp(_from_min(order["sig_t"])) >= started:
        now_open = {"status": "emir", "side": order["side"], "sig_t": _from_min(order["sig_t"]),
                    "entry": round(order["price"], 2), "stop": round(order["stop"], 2), "target": round(order["tp"], 2)}
    else:
        # 3. a signal on the last closed candle: the limit order starts with the next candle
        last = p.iloc[-1]
        sig_t = pd.Timestamp(last["date"])
        if sig_t >= started and pos is None and order is None:
            for side in ("long", "short"):
                if last[f"{side}_sig"]:
                    stop_pct = abs(last[f"{side}_entry"] - last[f"{side}_stop"]) / last[f"{side}_entry"]
                    if stop_pct >= sim.MIN_STOP_PCT:
                        now_open = {"status": "sinyal", "side": side, "sig_t": _iso(sig_t),
                                    "entry": round(float(last[f"{side}_entry"]), 2),
                                    "stop": round(float(last[f"{side}_stop"]), 2),
                                    "target": round(float(last[f"{side}_tp"]), 2)}
    prev = state.get("open")
    if now_open is not None and (prev is None or (prev["sig_t"], prev["status"]) != (now_open["sig_t"], now_open["status"])):
        o = now_open
        if o["status"] == "sinyal":
            msgs.append(f"YENİ SİNYAL {_side_tr(o['side'])}: limit giriş {o['entry']:.2f}, stop {o['stop']:.2f}, "
                        f"hedef {o['target']:.2f} (2R). Emir 2 saat geçerli; önce stop görülürse iptal.")
        elif o["status"] == "pozisyon":
            msgs.append(f"GİRİŞ DOLDU {_side_tr(o['side'])} @ {o['entry']:.2f}, stop {o['stop']:.2f}, hedef {o['target']:.2f}")
    if prev is not None and prev["status"] in ("sinyal", "emir") and (now_open is None or now_open["sig_t"] != prev["sig_t"]):
        if prev["sig_t"] not in known:
            msgs.append(f"İPTAL {_side_tr(prev['side'])} sinyali ({prev['sig_t'][:16]}): emir dolmadı.")
    state["open"] = now_open
    state["last_bar"] = _iso(bars.index[-1])
    return msgs


def save(state: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "state.json").write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    with (OUT_DIR / "trades.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(state.get("trades", []))


def notify(lines: list[str]) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not lines or not token:
        return
    from signals.dispatcher.telegram_client import TelegramClient, parse_chat_id

    text = HEADER + "\n" + "\n".join(lines)
    targets = [parse_chat_id(os.environ.get("TELEGRAM_CHAT_ID"))]
    group = os.environ.get("TELEGRAM_GROUP_ID", "").strip()
    if group.lstrip("-").isdigit() and int(group) < 0:  # the one group the owner chose (rule 7)
        targets.append(int(group))
    for chat in targets:
        try:
            TelegramClient(token, chat, timeout=20).send_message(text)
        except Exception as e:  # noqa: BLE001 - a message problem must not stop tracking
            print(f"telegram message not sent: {e}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fetch data and print, save nothing")
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    h1 = fetch_1h()
    print(f"{SYMBOL}: {len(h1)} 1h bars {h1.index[0]} -> {h1.index[-1]}, last close {h1['close'].iloc[-1]:.2f}")
    path = OUT_DIR / "state.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if a.check:
        state = {"started": (now - timedelta(days=60)).isoformat()}  # show the last 60 days as a dry check
    msgs = run_once(h1, state, now)
    print(f"trades {len(state['trades'])}, open {state.get('open')}")
    for m in msgs[-10:]:
        print("  " + m)
    if a.check:
        return
    save(state)
    notify(msgs)


if __name__ == "__main__":
    main()
