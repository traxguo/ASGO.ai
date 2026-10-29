"""
PusulaV2 (the demo version) with a hard maximum holding time (owner's question 2026-10-21:
how short can the trades be without losing the edge?). Everything else is PusulaV2
(cards/pusula.md); a trade still open after N days is closed at market. Research
variants, not on the demo. Run like the demo: 16 coins, 4h, --max-open-trades 3.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.candidates.pusula import PusulaV2  # noqa: E402


class PusulaV2Max14(PusulaV2):
    max_hold_hours = 14 * 24

    def custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        if (current_time - trade.open_date_utc).total_seconds() >= self.max_hold_hours * 3600:
            return "max_hold"
        return None


class PusulaV2Max7(PusulaV2Max14):
    max_hold_hours = 7 * 24


class PusulaV2Max3(PusulaV2Max14):
    max_hold_hours = 3 * 24


class PusulaV2Max1(PusulaV2Max14):
    max_hold_hours = 24
