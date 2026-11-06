"""
Paper tracking of the BTC/ETH time-series momentum line, rules frozen with no changes (cards/btc_eth_trend.md).
The pre-registered test (results/2026-11-06_btc_eth_trend) did NOT pass its bar (the short side lost in dev);
the supervisor decided on 2026-11-06 to paper-track one config only: N120 sma, vol target 20%.
No keys, no orders: target positions and a paper equity are only logged and sent to Telegram.

Rules (same code as the research: research/tsmom/tsmom.py, `signals` + `run` are imported, not copied):
  signal    close vs SMA(120), decided at the daily close (UTC), held over the next day
  size      0.20 / (30-day realised vol, daily log returns x sqrt(365)), at most 3x per half of capital
  book      BTC + ETH, half of the capital each, rebalanced to the target at every daily close
  costs     0.1% of traded notional, real funding paid / received by position side

Data: Binance USDⓈ-M public API (fapi, no key) daily klines + funding history. If Binance refuses the runner
(HTTP 451 / any error), Bitget public USDT-FUTURES daily (UTC) candles + funding history are used instead;
the source of each logged day is written in daily.csv.

The paper account starts at 10,000 USDT at the first run: it opens the target at the last closed daily candle,
then every later run books the days that have closed since (price P&L + funding - cost) and logs them once.

    python scripts/paper_btc_eth_trend.py           # update forward/paper_btc_eth_trend/ and send Telegram
    python scripts/paper_btc_eth_trend.py --check   # fetch data and print the current target, save nothing
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "research" / "tsmom"))
import tsmom as T  # noqa: E402

OUT_DIR = REPO / "forward" / "paper_btc_eth_trend"
LOOKBACK, KIND, VOL_TARGET = 120, "sma", 0.20  # frozen config "N120_sma_vt20"
ASSETS = T.ASSETS  # ["BTC", "ETH"]
BASE_USDT = 10_000.0
HISTORY_DAYS = 400  # SMA(120) and 30-day vol need ~150 closed days; more is kept as margin
HEADER = "KÂĞIT BTC/ETH Trend (gerçek emir yok)"
FIELDS = ["date", "source", "w_BTC", "w_ETH", "close_BTC", "close_ETH", "ret_BTC", "ret_ETH",
          "price_pct", "funding_pct", "cost_pct", "pnl_pct", "equity"]
DAY = pd.Timedelta(days=1)


# ---------- data ----------

def _get(url: str, params: dict) -> object:
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers={"User-Agent": "asgo-paper"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def binance_daily(asset: str, limit: int = HISTORY_DAYS) -> pd.Series:
    rows = _get("https://fapi.binance.com/fapi/v1/klines", {"symbol": f"{asset}USDT", "interval": "1d", "limit": limit})
    idx = pd.to_datetime([int(r[0]) for r in rows], unit="ms", utc=True)
    return pd.Series([float(r[4]) for r in rows], index=idx, name=asset)


def binance_funding(asset: str) -> pd.Series:
    rows = _get("https://fapi.binance.com/fapi/v1/fundingRate", {"symbol": f"{asset}USDT", "limit": 1000})
    ts = pd.to_datetime([int(r["fundingTime"]) for r in rows], unit="ms", utc=True)
    return pd.Series([float(r["fundingRate"]) for r in rows], index=ts)


def _bitget(path: str, params: dict) -> list:
    out = _get("https://api.bitget.com" + path, {"symbol": params.pop("symbol"), "productType": "USDT-FUTURES", **params})
    if str(out.get("code")) != "00000":
        raise RuntimeError(f"bitget {path}: {out.get('code')} {out.get('msg')}")
    return out.get("data") or []


def bitget_daily(asset: str, limit: int = HISTORY_DAYS) -> pd.Series:
    rows = _bitget("/api/v2/mix/market/candles", {"symbol": f"{asset}USDT", "granularity": "1Dutc", "limit": limit})
    idx = pd.to_datetime([int(r[0]) for r in rows], unit="ms", utc=True)
    return pd.Series([float(r[4]) for r in rows], index=idx, name=asset).sort_index()


def bitget_funding(asset: str, pages: int = 3) -> pd.Series:
    rows: list = []
    for page in range(1, pages + 1):
        got = _bitget("/api/v2/mix/market/history-fund-rate",
                      {"symbol": f"{asset}USDT", "pageSize": 100, "pageNo": page})
        rows += got
        if len(got) < 100:
            break
    ts = pd.to_datetime([int(r["fundingTime"]) for r in rows], unit="ms", utc=True)
    return pd.Series([float(r["fundingRate"]) for r in rows], index=ts)


def fetch(now: datetime) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Closed daily closes and daily funding for BTC + ETH; Binance first, Bitget if Binance refuses."""
    try:
        closes = {a: binance_daily(a) for a in ASSETS}
        events = {a: binance_funding(a) for a in ASSETS}
        source = "binance"
    except (urllib.error.URLError, OSError, ValueError, KeyError) as e:
        code = getattr(e, "code", None)
        print(f"binance not usable ({code or e}); using bitget public data")
        closes = {a: bitget_daily(a) for a in ASSETS}
        events = {a: bitget_funding(a) for a in ASSETS}
        source = "bitget"
    px = closed_days(pd.DataFrame(closes), now)
    return px, daily_funding(events, px.index), source


def closed_days(px: pd.DataFrame, now: datetime) -> pd.DataFrame:
    """Only daily candles that have closed at `now` (the API also returns the running day), gaps forward-filled
    as in research/tsmom/tsmom.py:load_prices."""
    px = px[~px.index.duplicated(keep="last")].sort_index()
    px = px[px.index + DAY <= pd.Timestamp(now)].dropna(how="all")
    full = pd.date_range(px.index.min(), px.index.max(), freq="D", tz="UTC")
    return px.reindex(full).ffill()


def daily_funding(events: dict[str, pd.Series], index: pd.DatetimeIndex) -> pd.DataFrame:
    """Funding of the position held over day t = events in (t 00:00, t+1 00:00], as in tsmom.load_funding."""
    out = {}
    for a, f in events.items():
        f = f.copy()
        f.index = f.index.round("h")
        f = f[~f.index.duplicated()].sort_index()
        day = (f.index - pd.Timedelta(seconds=1)).floor("D")
        out[a] = f.groupby(day).sum()
    return pd.DataFrame(out).reindex(index).fillna(0.0)


# ---------- rules (imported from the research code) ----------

def evaluate(px: pd.DataFrame, fund: pd.DataFrame) -> tuple[dict, pd.Series]:
    """Run the research code on the closed days plus one placeholder day. The weight `run` gives for day t uses
    closes up to t-1 only, so the placeholder row's weight is the target decided at the last real close.
    Returns (res for the real days, target weights to hold over the next day)."""
    nxt = px.index[-1] + DAY
    px_x = pd.concat([px, px.iloc[[-1]].set_axis([nxt])])
    fund_x = pd.concat([fund, pd.DataFrame(0.0, index=[nxt], columns=fund.columns)])
    res = T.run(px_x, fund_x, LOOKBACK, KIND, VOL_TARGET)
    if not bool(res["valid"].iloc[-1]):
        raise RuntimeError("not enough closed days for SMA(120) + 30-day vol")
    target = res["w"].iloc[-1]
    real = {k: (v.iloc[:-1] if hasattr(v, "iloc") else v) for k, v in res.items()}
    return real, target


# ---------- tracking ----------

def _side(w: float) -> str:
    return "LONG" if w > 0 else ("SHORT" if w < 0 else "YOK")


def _lev(w: float) -> float:
    return abs(w) * 2  # leverage on its own half of capital


def run_once(px: pd.DataFrame, fund: pd.DataFrame, source: str, state: dict, now: datetime) -> tuple[list[str], list[dict]]:
    """Update `state` with the days closed since the last run; return (Telegram lines, new daily rows)."""
    res, target = evaluate(px, fund)
    last = px.index[-1]
    rows: list[dict] = []
    if "started" not in state:
        state.update({"name": "BTC/ETH Trend (N120 sma, %20 vol)", "started": now.isoformat(),
                      "start_close": last.date().isoformat(), "base_usdt": BASE_USDT, "equity": BASE_USDT,
                      "peak": BASE_USDT, "max_dd_pct": 0.0, "last_day": last.date().isoformat(),
                      "curve": [{"t": (last + DAY).isoformat(), "eq": BASE_USDT}]})
    else:
        first_hold = pd.Timestamp(state["start_close"], tz="UTC") + DAY
        done = pd.Timestamp(state["last_day"], tz="UTC")
        for d in px.index[(px.index > done) & (px.index >= first_hold)]:
            w = res["w"].loc[d]
            price = float(res["contrib"].loc[d].sum() - res["pnl_f"].loc[d].sum() - res["pnl_c"].loc[d].sum())
            funding = float(res["pnl_f"].loc[d].sum())
            # the paper account opened from flat at the start close: its first cost is the full entry
            cost = -T.COST * float(w.abs().sum()) if d == first_hold else float(res["pnl_c"].loc[d].sum())
            pnl = price + funding + cost
            state["equity"] = state["equity"] * (1 + pnl)
            state["peak"] = max(state["peak"], state["equity"])
            state["max_dd_pct"] = max(state["max_dd_pct"], (1 - state["equity"] / state["peak"]) * 100)
            r = px.pct_change().loc[d]
            rows.append({"date": d.date().isoformat(), "source": source,
                         **{f"w_{a}": round(float(w[a]), 4) for a in ASSETS},
                         **{f"close_{a}": float(px.loc[d, a]) for a in ASSETS},
                         **{f"ret_{a}": round(float(r[a]), 6) for a in ASSETS},
                         "price_pct": round(price * 100, 4), "funding_pct": round(funding * 100, 4),
                         "cost_pct": round(cost * 100, 4), "pnl_pct": round(pnl * 100, 4),
                         "equity": round(state["equity"], 2)})
            state["curve"].append({"t": (d + DAY).isoformat(), "eq": round(state["equity"], 2)})
            state["last_day"] = d.date().isoformat()

    prev = state.get("target") or {}
    new_target = {a: round(float(target[a]), 4) for a in ASSETS}
    changed = [a for a in ASSETS if np.sign(prev.get(a, 0.0)) != np.sign(new_target[a])]
    state["target"] = new_target
    state["target_for"] = (last + DAY).date().isoformat()
    state["source"] = source
    state["return_pct"] = round((state["equity"] / state["base_usdt"] - 1) * 100, 3)
    state["equity"] = round(state["equity"], 2)
    state["days"] = len(state["curve"]) - 1

    today = pd.Timestamp(now).date().isoformat()
    monday = pd.Timestamp(now).weekday() == 0 and state.get("last_note") != today
    msgs: list[str] = []
    if changed or monday:
        if not prev:
            msgs.append("Takip başladı: N120 SMA, %20 hedef oynaklık, kurallar donduruldu (ön kayıtlı çıtayı geçmedi).")
        elif changed:
            msgs.append("YÖN DEĞİŞTİ: " + ", ".join(f"{a} {_side(prev.get(a, 0))} → {_side(new_target[a])}" for a in changed))
        else:
            msgs.append("Haftalık durum")
        for a in ASSETS:
            msgs.append(f"{a}: {_side(new_target[a])} {_lev(new_target[a]):.2f}x (kendi yarısında), kapanış {px[a].iloc[-1]:,.2f}")
        msgs.append(f"Kasa {state['equity']:,.0f} USDT ({state['return_pct']:+.2f}%), {state['days']} gün, "
                    f"en büyük düşüş %{state['max_dd_pct']:.1f}")
        state["last_note"] = today
    return msgs, rows


def save(state: dict, rows: list[dict], out_dir: Path = OUT_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "state.json").write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    path = out_dir / "daily.csv"
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def notify(lines: list[str], header: str = HEADER) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not lines or not token:
        return
    from signals.dispatcher.telegram_client import TelegramClient, parse_chat_id

    text = header + "\n" + "\n".join(lines)
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
    px, fund, source = fetch(now)
    print(f"{source}: {len(px)} closed days {px.index[0].date()} -> {px.index[-1].date()}, "
          + ", ".join(f"{c} {px[c].iloc[-1]:,.2f}" for c in ASSETS))
    path = OUT_DIR / "state.json"
    state = {} if a.check or not path.exists() else json.loads(path.read_text(encoding="utf-8"))
    msgs, rows = run_once(px, fund, source, state, now)
    print(f"target for {state['target_for']}: {state['target']}, equity {state['equity']} ({len(rows)} new days)")
    for m in msgs:
        print("  " + m)
    if a.check:
        return
    save(state, rows)
    notify(msgs)


if __name__ == "__main__":
    main()
