#!/usr/bin/env python3
"""
Runs Pusula on a Binance DEMO TRADING account (demo.binance.com, play money).

Owner decision 2026-10-10 (docs/decisions.md): the strategy may place orders on
the Binance demo account so the owner can follow it there. Real-money trading
stays forbidden. Guards, all checked before Freqtrade starts:
  - only config/demo.json may have dry_run false, and only with
    exchange.demo_trading true (scripts/safety_check.py)
  - keys come from .env (BINANCE_DEMO_API_KEY / BINANCE_DEMO_API_SECRET), never
    from a config file
  - after ccxt is created, every Binance API url must point to a demo-* host,
    otherwise the bot stops before any private request
Demo keys do not work on the real exchange and real keys do not work on the
demo hosts, so a mix-up fails instead of trading real money.

Usage (from the repo folder, on a computer that can reach Binance):
  py scripts/demo_freqtrade.py            # Windows
  python3 scripts/demo_freqtrade.py       # Linux / macOS
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

STRATEGY = "PusulaV2"
DEMO_CONFIG = "config/demo.json"


def load_env(path: Path = REPO / ".env") -> None:
    """Reads KEY=value lines from .env into os.environ. Existing non-empty values win; a
    later non-empty line beats an earlier empty one (the template has empty lines)."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if value and not os.environ.get(key):
            os.environ[key] = value


def api_hosts(urls: dict) -> set[str]:
    """All hosts in a ccxt `urls['api']` dict (values may be nested dicts)."""
    hosts: set[str] = set()
    for v in urls.values():
        if isinstance(v, dict):
            hosts |= api_hosts(v)
        elif isinstance(v, str):
            hosts.add(urlparse(v).hostname or "")
    return hosts


def assert_demo_hosts(api) -> None:
    hosts = api_hosts(api.urls.get("api", {}))
    bad = sorted(h for h in hosts if not h.startswith("demo-"))
    if not hosts or bad:
        raise SystemExit(f"STOP: Binance API is not in demo mode (non-demo hosts: {bad}). No order was sent.")


def preflight() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("safety_check", REPO / "scripts" / "safety_check.py")
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
    errors: list[str] = []
    sc.check_configs(errors)  # the git secret scan needs git; the ZIP download has no git
    if errors:
        print("SAFETY CHECK FAILED - stopping.")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(1)

    load_env()
    key = os.environ.get("BINANCE_DEMO_API_KEY", "").strip()
    secret = os.environ.get("BINANCE_DEMO_API_SECRET", "").strip()
    if not key or not secret:
        raise SystemExit("STOP: BINANCE_DEMO_API_KEY / BINANCE_DEMO_API_SECRET are empty in .env "
                         "(steps: docs/demo_kurulum.md).")
    # Freqtrade reads FREQTRADE__SECTION__KEY environment variables over the config files.
    os.environ["FREQTRADE__EXCHANGE__KEY"] = key
    os.environ["FREQTRADE__EXCHANGE__SECRET"] = secret
    if len(os.environ.get("FREQTRADE_API_JWT_SECRET", "").strip()) < 32:
        import secrets  # the web screen only needs some random secret; a new one per start is fine
        os.environ["FREQTRADE_API_JWT_SECRET"] = secrets.token_hex(32)
    for env_name, cfg_name in (("USERNAME", "USERNAME"), ("PASSWORD", "PASSWORD"), ("JWT_SECRET", "JWT_SECRET_KEY")):
        value = os.environ.get(f"FREQTRADE_API_{env_name}", "").strip()
        if not value:
            raise SystemExit(f"STOP: FREQTRADE_API_{env_name} is empty in .env (needed for the web screen, "
                             "steps: docs/demo_kurulum.md).")
        os.environ[f"FREQTRADE__API_SERVER__{cfg_name}"] = value


def main() -> None:
    preflight()

    from unittest import mock

    from freqtrade.exchange.binance import Binance
    from freqtrade.exchange.exchange import Exchange
    from freqtrade.main import main as ft_main

    original_init = Exchange._init_ccxt

    def init_demo_only(self, exchange_config, sync, ccxt_kwargs):
        api = original_init(self, exchange_config, sync, ccxt_kwargs)
        assert_demo_hosts(api)
        return api

    # Freqtrade turns Binance demo trading off by default because the demo account
    # is a separate market (own order book), not a copy of the live market.
    ft_has = {**Binance._ft_has, "supports_demo_trading": True}
    with mock.patch.object(Binance, "_ft_has", ft_has), \
            mock.patch.object(Exchange, "_init_ccxt", init_demo_only):
        os.chdir(REPO)
        ft_main(["trade", "-c", "config/base.json", "-c", DEMO_CONFIG,
                 "--strategy", STRATEGY, "--strategy-path", "strategies/candidates",
                 "--userdir", "user_data", "--db-url", "sqlite:///user_data/demo_trades.sqlite"])


if __name__ == "__main__":
    main()
