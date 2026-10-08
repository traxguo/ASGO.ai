"""
Runs a Freqtrade command (backtesting, lookahead-analysis, ...) with a static
Binance USD-M market list instead of loading it from the Binance API.

Needed where the API is unreachable (the cloud environment gets HTTP 451) but
the data itself came from data.binance.vision. Normally called through
`FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh ...`, so the safety check still runs.

Tick sizes / lot steps are Binance USD-M values as of 2026-10 (not verifiable
from the API here); they only affect price/amount rounding.

Usage: python scripts/offline_freqtrade.py <freqtrade command> <normal args>
"""

import sys
from unittest import mock

from freqtrade.exchange.exchange import Exchange
from freqtrade.main import main as ft_main

# base -> (price tick, amount step)
SYMBOLS = {
    "BTC": (0.1, 0.001),
    "ETH": (0.01, 0.001),
    "SOL": (0.001, 1),
    "XRP": (0.0001, 0.1),
    "BNB": (0.01, 0.01),
    "DOGE": (0.00001, 1),
    "ADA": (0.0001, 1),
}


def _market(base: str, tick: float, step: float) -> dict:
    return {
        "id": f"{base}USDT",
        "symbol": f"{base}/USDT:USDT",
        "base": base,
        "quote": "USDT",
        "settle": "USDT",
        "baseId": base,
        "quoteId": "USDT",
        "settleId": "USDT",
        "type": "swap",
        "spot": False,
        "margin": False,
        "swap": True,
        "future": False,
        "option": False,
        "active": True,
        "contract": True,
        "linear": True,
        "inverse": False,
        "contractSize": 1.0,
        "precision": {"amount": step, "price": tick},
        "limits": {
            "amount": {"min": step, "max": 10_000_000},
            "price": {"min": tick, "max": None},
            "cost": {"min": 5, "max": None},
            "leverage": {"min": 1, "max": 125},
        },
        "info": {},
    }


MARKETS = {m["symbol"]: m for m in (_market(b, *v) for b, v in SYMBOLS.items())}


async def _fake_reload(self, reload=False):
    self._api_async.set_markets(MARKETS)


if __name__ == "__main__":
    with mock.patch.object(Exchange, "_api_reload_markets", _fake_reload):
        ft_main(sys.argv[1:])
