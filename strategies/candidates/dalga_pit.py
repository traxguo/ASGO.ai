"""
Dalga on a point-in-time universe (survivorship check, 2026-11-03).

Our pair lists hold coins that still trade today, which can flatter a strategy. Here the universe is chosen
the way a live bot could have chosen it: each January, the 36 most traded USDT perpetuals by 90-day average
quote volume up to Dec 31 (2020: as of 2020-03-31, the archive starts in 2020-01). A coin may only open a
trade in a year it is on that year's list; open trades are managed as usual. Rules otherwise identical to Dalga.
Run with --max-open-trades 8 on config/pairs_top36_yearly_union.json.
"""

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.candidates.dalga import Dalga  # noqa: E402

YEARLY = {int(y): {s[:-4] for s in v}
          for y, v in json.load(open(_REPO_ROOT / "research" / "xsec" / "top36_yearly.json")).items()}


class DalgaPIT(Dalga):
    def confirm_trade_entry(self, pair, order_type, amount, rate, time_in_force, current_time, entry_tag, side,
                            **kwargs) -> bool:
        return pair.split("/")[0] in YEARLY.get(current_time.year, set())
