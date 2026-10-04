"""
Runs `freqtrade backtesting` without internet by feeding Freqtrade a static
market list instead of downloading it from Binance.

ONLY for pipeline smoke tests in environments where Binance is blocked.
Real research runs use the normal command (scripts/ft.sh backtesting ...).

Usage: python tests/smoke/offline_backtest.py <freqtrade command> <normal args>
   e.g. python tests/smoke/offline_backtest.py backtesting -c config/base.json ...
"""

import sys
from unittest import mock

from freqtrade.exchange.exchange import Exchange
from freqtrade.main import main as ft_main

SYMBOLS = ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE"]


def _market(base: str) -> dict:
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
        "precision": {"amount": 0.001, "price": 0.0001},
        "limits": {
            "amount": {"min": 0.001, "max": 1_000_000},
            "price": {"min": 0.0001, "max": None},
            "cost": {"min": 5, "max": None},
            "leverage": {"min": 1, "max": 125},
        },
        "info": {},
    }


MARKETS = {m["symbol"]: m for m in (_market(b) for b in SYMBOLS)}


async def _fake_reload(self, reload=False):
    self._api_async.set_markets(MARKETS)


if __name__ == "__main__":
    with mock.patch.object(Exchange, "_api_reload_markets", _fake_reload):
        ft_main(sys.argv[1:])
