#!/usr/bin/env python3
"""
Runs PusulaV2 on a Bitget DEMO account (play money) from a scheduled GitHub
Actions job, so it works without the owner's computer.

Owner decisions: 2026-10-10 demo trading allowed, real money still forbidden;
2026-10-10 Bitget demo on GitHub's free runners (Binance and Bybit demo block
GitHub's US servers). See docs/decisions.md.

One run = one pass after a 4h candle closes. The job keeps no process alive, so
everything a later run needs is either on the exchange (orders, positions, the
stop order) or in forward/bitget_demo/state.json, which the workflow commits.

Same rules as the backtest:
  - signals, entry price, stop and the exit rule come from the PusulaV2 class
    itself (strategies/candidates/pusula.py), run on Bitget's live candles
  - entry: limit order at the middle of the entry zone, with the stop attached
    on the exchange, so a filled entry is protected at once
  - the entry order is cancelled after 3 candles, or when a closed candle
    touched the stop before it filled
  - stop moves to break even (+0.15%) once price went 2R in favour (checked on
    1h highs, like the backtest's 1h detail), at most 4h late
  - exit: daily close below daily EMA20 or BTC score <= -1 (exit_long column)
  - 1% of equity risked per trade, leverage from the liquidation rule, max 3 trades
Differences, written down so the analysis can account for them: exits are
market orders (the backtest assumes limit at the close), and the break-even
move can lag up to one 4h candle.

Safety: every signed request must carry Bitget's demo header (PAPTRADING: 1),
otherwise the run stops before sending it. Demo keys only work on the demo
account, so a real key fails instead of trading real money.

Usage:
  python scripts/bitget_demo.py --check   # no keys: fetch data, print signals
  python scripts/bitget_demo.py           # needs BITGET_DEMO_API_KEY / _SECRET / _PASSPHRASE
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "strategies" / "candidates"))

import pandas as pd  # noqa: E402

STRATEGY = "PusulaV2"
TF, DAILY_TF, DETAIL_TF = "4h", "1d", "1h"
TF_HOURS = 4
MAX_OPEN_TRADES = 3
TRADABLE_BALANCE_RATIO = 0.99  # same as config/base.json
CANDLES_4H = 300
CANDLES_1D = 400
PAIRS_FILE = REPO / "config" / "pairs_wide16.json"
OUT_DIR = REPO / "forward" / "bitget_demo"
STATE_FILE = OUT_DIR / "state.json"
TRADES_FILE = OUT_DIR / "trades.csv"
EVENTS_FILE = OUT_DIR / "events.csv"
PRODUCT = {"productType": "USDT-FUTURES"}
TRADE_FIELDS = ["pair", "signal_time", "plan_entry", "plan_stop", "fill_time", "fill_price", "amount",
                "leverage", "exit_time", "exit_price", "exit_reason", "breakeven_moved", "pnl_usdt",
                "fees_usdt", "funding_usdt", "r"]


# ------------------------------------------------------------------ exchange


def assert_demo_request(request: dict) -> None:
    """Stops before any signed request that would not go to the demo account."""
    headers = request.get("headers") or {}
    if "ACCESS-KEY" in headers and str(headers.get("PAPTRADING")) != "1":
        raise SystemExit("STOP: a signed Bitget request without the demo header (PAPTRADING: 1). No order was sent.")


def demo_exchange(key: str, secret: str, passphrase: str):
    import ccxt

    ex = ccxt.bitget({"options": {"defaultType": "swap"}, "enableRateLimit": True})
    ex.apiKey, ex.secret, ex.password = key, secret, passphrase
    ex.set_sandbox_mode(True)
    original_sign = ex.sign

    def sign_demo_only(*args, **kwargs):
        request = original_sign(*args, **kwargs)
        assert_demo_request(request)
        return request

    ex.sign = sign_demo_only
    return ex


def public_exchange():
    """No keys: live market candles, the same market the backtests used."""
    import ccxt

    return ccxt.bitget({"options": {"defaultType": "swap"}, "enableRateLimit": True})


def last_closed_open(now: datetime, hours: int) -> datetime:
    """Open time of the last fully closed candle of `hours` length (UTC-aligned)."""
    step = hours * 3600
    ts = int(now.timestamp()) // step * step - step
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def fetch_candles(ex, pair: str, tf: str, count: int, now: datetime) -> pd.DataFrame:
    hours = {"1h": 1, "4h": 4, "1d": 24}[tf]
    last_open = last_closed_open(now, hours)
    since = int((last_open - timedelta(hours=hours * (count - 1))).timestamp() * 1000)
    rows: list = []
    cursor = since
    while True:
        batch = ex.fetch_ohlcv(pair, tf, since=cursor, limit=200)
        batch = [b for b in batch if b[0] >= cursor]
        if not batch:
            break
        rows.extend(batch)
        cursor = batch[-1][0] + hours * 3600 * 1000
        if cursor > last_open.timestamp() * 1000:
            break
    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"]).drop_duplicates("date")
    df["date"] = pd.to_datetime(df["date"], unit="ms", utc=True)
    df = df[df["date"] <= last_open]  # drop the candle that is still forming
    return df.sort_values("date").reset_index(drop=True)


# ------------------------------------------------------------------ strategy


class _Provider:
    def __init__(self, candles: dict):
        self.candles = candles

    def get_pair_dataframe(self, pair, timeframe):
        return self.candles[(pair, timeframe)].copy()

    def current_whitelist(self):
        return sorted({p for p, tf in self.candles if tf == TF})


def make_strategy():
    import pusula

    strategy = getattr(pusula, STRATEGY)({"timeframe": TF, "stake_currency": "USDT", "dry_run": True,
                                          "trading_mode": "futures", "margin_mode": "isolated"})
    return strategy


def analyze(candles: dict, pairs: list[str]) -> dict[str, pd.DataFrame]:
    """Runs the strategy's own populate_* methods, exactly like Freqtrade does."""
    strategy = make_strategy()
    strategy.dp = _Provider(candles)
    out = {}
    for pair in pairs:
        if (pair, TF) not in candles or candles[(pair, TF)].empty:
            continue
        meta = {"pair": pair}
        df = strategy.populate_indicators(candles[(pair, TF)].copy(), meta)
        df = strategy.populate_entry_trend(df, meta)
        df = strategy.populate_exit_trend(df, meta)
        out[pair] = df
    return out


def signal_plan(df: pd.DataFrame, signal_time: datetime) -> dict | None:
    """The long plan on the given closed candle, or None when it has no entry signal."""
    rows = df.loc[df["date"] == pd.Timestamp(signal_time)]
    if rows.empty:
        return None
    row = rows.iloc[-1]
    if row.get("enter_long") != 1:
        return None
    return {"entry": float(row["long_entry"]), "stop": float(row["long_stop"]),
            "signal_time": signal_time.isoformat()}


def exit_signal(df: pd.DataFrame, signal_time: datetime) -> bool:
    rows = df.loc[df["date"] == pd.Timestamp(signal_time)]
    return (not rows.empty) and rows.iloc[-1].get("exit_long") == 1


# ------------------------------------------------------------------ records


def load_state(path: Path = STATE_FILE) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"trades": {}}


def save_state(state: dict, path: Path = STATE_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_csv(path: Path, fields: list[str], row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.is_file()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)


class Recorder:
    def __init__(self, out_dir: Path = OUT_DIR):
        self.out_dir = out_dir
        self.events: list[str] = []

    def event(self, now: datetime, pair: str, what: str, detail: str = "") -> None:
        self.events.append(f"{pair}: {what} {detail}".strip())
        print(f"{now:%Y-%m-%d %H:%M} {pair}: {what} {detail}")
        append_csv(self.out_dir / EVENTS_FILE.name, ["time", "pair", "event", "detail"],
                   {"time": now.isoformat(), "pair": pair, "event": what, "detail": detail})

    def trade(self, row: dict) -> None:
        append_csv(self.out_dir / TRADES_FILE.name, TRADE_FIELDS, row)


# ------------------------------------------------------------------ one pass


def client_id(pair: str, signal_time: datetime) -> str:
    return f"pv2{pair.split('/')[0].lower()}{signal_time:%Y%m%d%H}"


def position_size(ex, pair: str) -> float:
    for p in ex.fetch_positions([pair], PRODUCT):
        if p.get("symbol") == pair and float(p.get("contracts") or 0) > 0:
            return float(p["contracts"])
    return 0.0


def close_fills(ex, pair: str, since: datetime, side: str) -> tuple[float, float, float]:
    """(average price, amount, fees) of our fills on one side since `since`."""
    trades = ex.fetch_my_trades(pair, since=int(since.timestamp() * 1000), params=PRODUCT)
    picked = [t for t in trades if t.get("side") == side]
    amount = sum(float(t["amount"]) for t in picked)
    cost = sum(float(t["cost"]) for t in picked)
    fees = sum(float((t.get("fee") or {}).get("cost") or 0) for t in picked)
    return (cost / amount if amount else float("nan")), amount, fees


def funding_paid(ex, pair: str, since: datetime) -> float:
    try:
        rows = ex.fetch_funding_history(pair, since=int(since.timestamp() * 1000), params=PRODUCT)
        return sum(float(r.get("amount") or 0) for r in rows)
    except Exception as e:  # not every account type reports it; the report says so
        print(f"{pair}: funding history not available ({e})")
        return float("nan")


def finish_trade(ex, rec: Recorder, now: datetime, cid: str, t: dict, reason: str) -> None:
    fill_time = datetime.fromisoformat(t["fill_time"])
    exit_price, _, exit_fees = close_fills(ex, t["pair"], fill_time, "sell")
    funding = funding_paid(ex, t["pair"], fill_time)
    fees = float(t.get("entry_fees") or 0) + exit_fees
    pnl = (exit_price - t["fill_price"]) * t["amount"] - fees + (0 if funding != funding else funding)
    risk = t["amount"] * abs(t["fill_price"] - t["plan_stop"])
    t.update(status="closed", exit_time=now.isoformat(), exit_price=exit_price, exit_reason=reason,
             pnl_usdt=round(pnl, 4), fees_usdt=round(fees, 4), funding_usdt=funding,
             r=round(pnl / risk, 3) if risk > 0 else None)
    rec.trade({"pair": t["pair"], "plan_entry": t["plan_entry"], "plan_stop": t["plan_stop"], **t})
    rec.event(now, t["pair"], "closed", f"{reason} r={t['r']}")


def stop_orders(ex, pair: str) -> list[dict]:
    orders = ex.fetch_open_orders(pair, params={**PRODUCT, "trigger": True, "planType": "profit_loss"})
    return [o for o in orders if o.get("stopLossPrice") or o.get("triggerPrice")]


def move_stop(ex, pair: str, amount: float, new_stop: float) -> None:
    """New stop first, then remove the old ones, so the position is never unprotected."""
    old = stop_orders(ex, pair)
    ex.create_order(pair, "market", "sell", amount, None,
                    {**PRODUCT, "stopLossPrice": new_stop, "marginMode": "isolated"})
    for o in old:
        ex.cancel_order(o["id"], pair, {**PRODUCT, "trigger": True, "planType": "profit_loss"})


def demo_balance(balance: dict) -> tuple[float, float]:
    """(usable equity, free margin). The demo account may report its play money as SUSDT."""
    for coin in ("USDT", "SUSDT"):
        total = float((balance.get(coin) or {}).get("total") or 0)
        if total > 0:
            return total * TRADABLE_BALANCE_RATIO, float((balance.get(coin) or {}).get("free") or 0)
    return 0.0, 0.0


def check_demo_key(ex) -> None:
    """Bitget answers 40099 when a real-account key is used with the demo header."""
    try:
        ex.fetch_balance({"type": "swap", **PRODUCT})
    except Exception as e:
        if "40099" in str(e):
            raise SystemExit("STOP: this API key is not a Bitget DEMO key (40099 exchange environment is "
                             "incorrect). Nothing was traded. Create the key in Demo mode "
                             "(docs/bitget_demo_kurulum.md).")
        raise


def run_once(ex, pub, analyzed: dict, state: dict, now: datetime, rec: Recorder) -> None:
    from strategies.common import trade_management as tm

    strategy = make_strategy()
    mgmt, model = strategy.mgmt, strategy.tp_model
    signal_time = last_closed_open(now, TF_HOURS)
    trades = state.setdefault("trades", {})

    # 1. pending entries: filled, cancelled, or still waiting
    for cid, t in trades.items():
        if t["status"] != "pending":
            continue
        order = ex.fetch_order(t["order_id"], t["pair"], PRODUCT)
        filled = float(order.get("filled") or 0)
        sig = datetime.fromisoformat(t["signal_time"])
        expired = now >= sig + timedelta(hours=TF_HOURS * (1 + mgmt.valid_for_candles))
        df = analyzed.get(t["pair"])
        after = df[df["date"] > pd.Timestamp(sig)] if df is not None else pd.DataFrame()
        touched_stop = (not after.empty) and float(after["low"].min()) <= t["plan_stop"]
        if order.get("status") == "open" and filled == 0 and (expired or touched_stop):
            ex.cancel_order(t["order_id"], t["pair"], PRODUCT)
            t["status"] = "cancelled"
            rec.event(now, t["pair"], "entry cancelled", "stop touched first" if touched_stop else "3 candles passed")
            continue
        if order.get("status") == "open" and filled > 0 and (expired or touched_stop):
            ex.cancel_order(t["order_id"], t["pair"], PRODUCT)  # keep the filled part, like Freqtrade
        if filled > 0:
            fill_time = datetime.fromtimestamp((order.get("lastTradeTimestamp") or order["timestamp"]) / 1000,
                                               tz=timezone.utc)
            t.update(status="open", fill_price=float(order.get("average") or order["price"]), amount=filled,
                     fill_time=fill_time.isoformat(), entry_fees=float((order.get("fee") or {}).get("cost") or 0))
            rec.event(now, t["pair"], "entry filled", f"{filled} @ {t['fill_price']}")
        elif order.get("status") in ("canceled", "cancelled", "rejected", "expired"):
            t["status"] = "cancelled"
            rec.event(now, t["pair"], "entry cancelled", f"by exchange ({order.get('status')})")

    # 2. open trades: stopped out, exit signal, break-even move
    for cid, t in trades.items():
        if t["status"] != "open":
            continue
        pair = t["pair"]
        if position_size(ex, pair) == 0:
            finish_trade(ex, rec, now, cid, t, "stop_breakeven" if t.get("breakeven_moved") else "stop")
            continue
        df = analyzed.get(pair)
        if df is not None and exit_signal(df, signal_time):
            for o in stop_orders(ex, pair):
                ex.cancel_order(o["id"], pair, {**PRODUCT, "trigger": True, "planType": "profit_loss"})
            ex.create_order(pair, "market", "sell", t["amount"], None,
                            {**PRODUCT, "reduceOnly": True, "marginMode": "isolated"})
            finish_trade(ex, rec, now, cid, t, "exit_signal")
            continue
        if not t.get("breakeven_moved"):
            fill_time = datetime.fromisoformat(t["fill_time"])
            hours_open = int((now - fill_time).total_seconds() // 3600) + 2
            detail = fetch_candles(pub, pair, DETAIL_TF, hours_open, now)
            best = float(detail.loc[detail["date"] >= pd.Timestamp(fill_time).floor("h"), "high"].max())
            risk = abs(t["plan_entry"] - t["plan_stop"])
            if risk > 0 and (best - t["fill_price"]) / risk >= model.breakeven_r:
                be = tm.breakeven_stop("long", t["fill_price"], mgmt)
                move_stop(ex, pair, t["amount"], be)
                t["breakeven_moved"] = True
                rec.event(now, pair, "stop moved to break even", f"{be:.6g}")

    # 3. new signals on the candle that just closed
    active = [t for t in trades.values() if t["status"] in ("pending", "open")]
    busy_pairs = {t["pair"] for t in active}
    slots = MAX_OPEN_TRADES - len(active)
    if slots <= 0:
        return
    balance = ex.fetch_balance({"type": "swap", **PRODUCT})
    equity, free = demo_balance(balance)
    print(f"demo balance: equity {equity:.2f}, free {free:.2f}")
    if equity <= 0:
        rec.event(now, "-", "no demo balance found", "neither USDT nor SUSDT in the futures account")
        return
    for pair, df in analyzed.items():
        if slots <= 0:
            break
        plan = signal_plan(df, signal_time)
        if plan is None or pair in busy_pairs:
            continue
        cid = client_id(pair, signal_time)
        if cid in trades:
            continue
        lev = tm.safe_leverage("long", plan["entry"], plan["stop"], mgmt) or 1.0
        notional = tm.position_notional(equity, plan["entry"], plan["stop"], mgmt)
        if notional / lev > free:
            rec.event(now, pair, "signal skipped", "not enough free margin for a full 1R position")
            continue
        amount = float(ex.amount_to_precision(pair, notional / plan["entry"]))
        if amount <= 0:
            rec.event(now, pair, "signal skipped", "size below the exchange minimum")
            continue
        try:
            ex.set_margin_mode("isolated", pair, PRODUCT)
        except Exception as e:  # already isolated
            print(f"{pair}: margin mode unchanged ({e})")
        try:
            ex.set_leverage(lev, pair, {**PRODUCT, "marginMode": "isolated"})
        except Exception:  # some account modes want the position side as well
            ex.set_leverage(lev, pair, {**PRODUCT, "marginMode": "isolated", "holdSide": "long"})
        order = ex.create_order(pair, "limit", "buy", amount, plan["entry"],
                                {**PRODUCT, "marginMode": "isolated", "clientOrderId": cid,
                                 "stopLoss": {"triggerPrice": plan["stop"]}})
        trades[cid] = {"pair": pair, "status": "pending", "order_id": order["id"],
                       "signal_time": plan["signal_time"], "plan_entry": plan["entry"],
                       "plan_stop": plan["stop"], "leverage": lev, "breakeven_moved": False}
        busy_pairs.add(pair)
        slots -= 1
        rec.event(now, pair, "entry order placed",
                  f"{amount} @ {plan['entry']:.6g}, stop {plan['stop']:.6g}, {lev:g}x")


# ------------------------------------------------------------------ main


def pairs() -> list[str]:
    return json.loads(PAIRS_FILE.read_text(encoding="utf-8"))["exchange"]["pair_whitelist"]


def load_all(pub, pair_list: list[str], now: datetime) -> dict:
    import pusula

    candles = {}
    for pair in sorted(set(pair_list) | {pusula.MARKET_PAIR}):
        try:
            candles[(pair, TF)] = fetch_candles(pub, pair, TF, CANDLES_4H, now)
            candles[(pair, DAILY_TF)] = fetch_candles(pub, pair, DAILY_TF, CANDLES_1D, now)
        except Exception as e:  # a missing coin must not stop the others
            print(f"{pair}: no data ({e})")
    return candles


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--check", action="store_true", help="no keys: fetch data and print the last candle's signals")
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    pair_list = pairs()
    pub = public_exchange()
    analyzed = analyze(load_all(pub, pair_list, now), pair_list)
    signal_time = last_closed_open(now, TF_HOURS)
    print(f"last closed 4h candle: {signal_time:%Y-%m-%d %H:%M} UTC, pairs analysed: {len(analyzed)}/{len(pair_list)}")
    for pair, df in analyzed.items():
        last = df.iloc[-1]
        print(f"  {pair:16} close {last['close']:<12.6g} score_1d {last.get('score_1d')}  "
              f"mkt {last.get('mkt_score_1d')}  enter {last.get('enter_long') == 1}  exit {last.get('exit_long') == 1}")
    if a.check:
        if len(analyzed) < len(pair_list) or any(df.empty or df.iloc[-1]["date"] != pd.Timestamp(signal_time)
                                                 for df in analyzed.values()):
            raise SystemExit("CHECK FAILED: some pairs have no data or stale candles.")
        print("check ok")
        return

    key, secret, phrase = (os.environ.get(f"BITGET_DEMO_API_{n}", "").strip() for n in ("KEY", "SECRET", "PASSPHRASE"))
    if not (key and secret and phrase):
        raise SystemExit("STOP: BITGET_DEMO_API_KEY / _SECRET / _PASSPHRASE are not set "
                         "(GitHub: Settings > Secrets and variables > Actions; steps: docs/bitget_demo_kurulum.md).")
    ex = demo_exchange(key, secret, phrase)
    ex.load_markets()
    check_demo_key(ex)
    try:
        ex.set_position_mode(False, None, PRODUCT)  # one-way, like the backtest
    except Exception as e:  # fails while positions are open; then it is already set
        print(f"position mode unchanged ({e})")
    state = load_state()
    before = json.dumps(state, sort_keys=True)
    run_once(ex, pub, analyzed, state, now, Recorder())
    if json.dumps(state, sort_keys=True) != before:  # the workflow commits only real changes
        save_state(state)


if __name__ == "__main__":
    main()
