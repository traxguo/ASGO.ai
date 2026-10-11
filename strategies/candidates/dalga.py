"""
dalga ("wave"): Claude's fast candidate built from the lessons of the earlier
tests. Strategy card: cards/dalga.md (condition ids must match the card).
Rules fixed before the first test (2026-10-11).

It is PusulaV2NoBe (strategies/candidates/pusula.py) moved to 1h candles:
  daily regime : coin score >= +1 from the last CLOSED daily candle, long only
  1h trigger   : first close above the previous 24-candle high, daily close above EMA20
  exit         : daily close below daily EMA20, or BTC daily score <= -1; stop never moves
  sizing       : dynamic risk per trade (owner's request 2026-10-11, fixed before testing):
                 0.75% when the daily score is +3, 0.35% when it is +1; halved while
                 equity is 10% or more below its peak, quartered at 20% or more.
                 Run with --max-open-trades 8 (36 coins).
"""

import dataclasses
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.candidates.pusula import PusulaV2NoBe  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402


RISK_BY_SCORE = {3: 0.0075, 1: 0.0035}
DD_BRAKES = ((0.20, 0.25), (0.10, 0.5))  # (drawdown from peak, risk multiplier), deepest first


def dynamic_risk(score: float, equity: float, peak: float) -> float:
    """Risk fraction for a new trade from the daily score and the equity drawdown."""
    risk = RISK_BY_SCORE.get(int(score), 0.0) if score == score else 0.0
    dd = 1 - equity / peak if peak > 0 else 0.0
    for level, mult in DD_BRAKES:
        if dd >= level:
            return risk * mult
    return risk


class DalgaFixed(PusulaV2NoBe):
    """Diagnostic variant (declared on the card): fixed 0.5% risk. Run with --max-open-trades 8."""

    timeframe = "1h"
    channel = 24
    # 100 days of 1h candles; the daily data gets enough history for EMA50 / 90-day momentum
    startup_candle_count = 2400
    mgmt = tm.ManagementParams(risk_per_trade=0.005)


class Dalga(DalgaFixed):
    """Main version (the card decides on this one): dynamic risk. Run with --max-open-trades 8."""

    _peak = 0.0

    def custom_stake_amount(self, pair, current_time, current_rate, proposed_stake, min_stake, max_stake,
                            leverage, entry_tag, side, **kwargs) -> float:
        row = self._last_row(pair)
        if row is None:
            return 0.0
        equity = self.wallets.get_total_stake_amount()
        self._peak = max(self._peak, equity)
        risk = dynamic_risk(float(row["score_1d"]), equity, self._peak)
        if risk <= 0:
            return 0.0
        params = dataclasses.replace(self.mgmt, risk_per_trade=risk)
        notional = tm.position_notional(equity, float(row[f"{side}_entry"]), float(row[f"{side}_stop"]), params)
        stake = notional / leverage
        return 0.0 if stake > max_stake else stake
