"""
Hourly collector for the Akis idea (journal 2026-10-11, research/scans/oi_flow_scan.py).

Bitget only serves the last ~30 hours of its long/short and taker buy/sell data
and only the current open interest, while Akis needs 30 days of history for its
z-scores. So a scheduled job stores one row per coin and hour, from public
endpoints (no keys):
  forward/akis_metrics/<COIN>.csv: ts, open_interest, long_short_account,
                                   taker_buy, taker_sell
Rows already stored are not written again. Usage: python research/live/collect_bitget_metrics.py
"""

import csv
import json
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "forward" / "akis_metrics"
COINS = "BTC ETH SOL XRP BNB DOGE ADA LINK AVAX LTC DOT TRX".split()
BASE = "https://api.bitget.com/api/v2/mix/market/"
FIELDS = ["ts", "open_interest", "long_short_account", "taker_buy", "taker_sell"]


def get(endpoint: str, coin: str, extra: str = "") -> object:
    url = f"{BASE}{endpoint}?symbol={coin}USDT&productType=usdt-futures{extra}"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "asgo-akis"}), timeout=30) as r:
        return json.loads(r.read())["data"]


def collect(coin: str) -> int:
    path = OUT / f"{coin}.csv"
    seen = set()
    if path.is_file():
        with path.open(encoding="utf-8") as f:
            seen = {row["ts"] for row in csv.DictReader(f)}
    ls = {r["ts"]: r for r in get("account-long-short", coin, "&period=1h")}
    tk = {r["ts"]: r for r in get("taker-buy-sell", coin, "&period=1h")}
    oi = get("open-interest", coin)
    oi_now = oi["openInterestList"][0]["size"]
    rows = []
    latest = max(ls) if ls else None
    for ts in sorted(set(ls) & set(tk)):
        if ts in seen:
            continue
        rows.append({"ts": ts, "long_short_account": ls[ts]["longShortAccountRatio"],
                     "taker_buy": tk[ts]["buyVolume"], "taker_sell": tk[ts]["sellVolume"],
                     # open interest has no history: only the newest hour gets the snapshot taken now
                     "open_interest": oi_now if ts == latest else ""})
    if rows:
        OUT.mkdir(parents=True, exist_ok=True)
        new = not path.is_file()
        with path.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if new:
                w.writeheader()
            w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    for c in COINS:
        try:
            print(f"{c}: {collect(c)} new rows")
        except Exception as e:  # one coin must not stop the others
            print(f"{c}: failed ({e})")
