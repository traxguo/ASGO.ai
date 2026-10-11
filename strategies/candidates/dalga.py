"""
dalga ("wave"): Claude's fast candidate built from the lessons of the earlier
tests. Strategy card: cards/dalga.md (condition ids must match the card).
Rules fixed before the first test (2026-10-11).

It is PusulaV2NoBe (strategies/candidates/pusula.py) moved to 1h candles:
  daily regime : coin score >= +1 from the last CLOSED daily candle, long only
  1h trigger   : first close above the previous 24-candle high, daily close above EMA20
  exit         : daily close below daily EMA20, or BTC daily score <= -1; stop never moves
  sizing       : 0.5% risk per trade, run with --max-open-trades 8 (36 coins)
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.candidates.pusula import PusulaV2NoBe  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402


class Dalga(PusulaV2NoBe):
    """Main version (the card decides on this one). Run with --max-open-trades 8."""

    timeframe = "1h"
    channel = 24
    # 100 days of 1h candles; the daily data gets enough history for EMA50 / 90-day momentum
    startup_candle_count = 2400
    mgmt = tm.ManagementParams(risk_per_trade=0.005)


class Dalga3(Dalga):
    """Diagnostic variant (declared on the card): 1% risk, run with --max-open-trades 3."""

    mgmt = tm.ManagementParams(risk_per_trade=0.01)
