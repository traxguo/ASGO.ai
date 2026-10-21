"""
Dalga with a hard maximum holding time (owner's question 2026-10-21: how short can the
trades be without losing the edge?). Entries, stop, trend exit and sizing are exactly
Dalga's (cards/dalga.md); the only addition is: a trade still open after N days is
closed at market. Research variants, not on the demo. Run with --max-open-trades 8.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.candidates.dalga import Dalga  # noqa: E402


class DalgaMax7(Dalga):
    max_hold_hours = 7 * 24

    def custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        if (current_time - trade.open_date_utc).total_seconds() >= self.max_hold_hours * 3600:
            return "max_hold"
        return None


class DalgaMax5(DalgaMax7):
    max_hold_hours = 5 * 24


class DalgaMax3(DalgaMax7):
    max_hold_hours = 3 * 24


class DalgaMax2(DalgaMax7):
    max_hold_hours = 2 * 24


class DalgaMax1(DalgaMax7):
    max_hold_hours = 24
