"""
Records Bitget's current open interest and price for the 36-coin list into forward/oi/bitget_oi.csv.
Bitget only serves the current open interest (no history), so the Tasfiye research candidate (cards/tasfiye.md)
needs our own record before it can run live. Public data only, no keys, no orders. Run by the hourly
Dalga workflow; a failing coin is skipped and never stops the run.

    python scripts/record_oi.py
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAIRS_FILE = REPO / "config" / "pairs_all36.json"
OUT = REPO / "forward" / "oi" / "bitget_oi.csv"
FIELDS = ["time", "coin", "open_interest", "price"]


def snapshot(ex, pairs: list[str], now: datetime) -> list[dict]:
    rows = []
    for pair in pairs:
        try:
            oi = ex.fetch_open_interest(pair)
            amount = oi.get("openInterestAmount")
            if amount is None:
                amount = (oi.get("info") or {}).get("openInterestList", [{}])[0].get("size")
            price = ex.fetch_ticker(pair).get("last")
            if amount is None or price is None:
                raise ValueError("empty answer")
            rows.append({"time": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "coin": pair.split("/")[0],
                         "open_interest": float(amount), "price": float(price)})
        except Exception as e:  # noqa: BLE001 - one coin must not stop the others
            print(f"{pair}: open interest not recorded ({e})")
    return rows


def append(rows: list[dict], path: Path = OUT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def main() -> None:
    import ccxt

    ex = ccxt.bitget({"options": {"defaultType": "swap"}, "enableRateLimit": True})
    ex.load_markets()
    pairs = json.loads(PAIRS_FILE.read_text(encoding="utf-8"))["exchange"]["pair_whitelist"]
    rows = snapshot(ex, pairs, datetime.now(timezone.utc))
    append(rows)
    print(f"open interest recorded for {len(rows)}/{len(pairs)} coins")


if __name__ == "__main__":
    main()
