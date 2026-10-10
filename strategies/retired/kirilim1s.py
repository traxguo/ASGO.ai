"""
kirilim1s ("breakout 1h"): fast candidate 2, queue item 1b. Strategy card:
cards/kirilim1s.md (condition ids must match the card). Rules fixed before the
first test.

It is Pusula's rule set (strategies/candidates/pusula.py, PusulaBase) moved to
1h candles with a 24-candle (one day) channel and fixed Model B targets:

  daily regime : Pusula's score from the last CLOSED daily candle, +3 for longs,
                 -3 for shorts; BTC's score >= +1 for longs, <= -1 for shorts
  1h trigger   : first close above the previous 24-candle high (long) /
                 below the previous 24-candle low (short)
  management   : shared module (0.25 ATR entry zone, wider of 1.5 ATR /
                 10-candle swing stop, Model B 2R/4R, 3-candle validity, max 3x)

All of this is inherited; only the timeframe and channel length differ, so the
backtest, the signal and Pusula's tested regime code stay one and the same.

RETIRED 2026-10-10: development period 2020-2024 on 36 coins gave +0.06R per
trade after costs and funding, profit factor 1.04, max drawdown 48% and about
0 at double costs; only 0.6 trades a day. Reason on the card. Kept for the
record; do not use for signals.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.candidates.pusula import PusulaBase  # noqa: E402

CHANNEL_1H = 24  # one day of 1h candles


class Kirilim1s_B(PusulaBase):
    """Main version (the card decides on this one)."""

    timeframe = "1h"
    tp_model_name = "B"
    channel = CHANNEL_1H
    # 1h warm-up for ATR / channel; the daily data gets the same count of daily
    # candles, enough for EMA50 and the 90-day momentum (same as Nabiz).
    startup_candle_count = 400


class Kirilim1s12_B(Kirilim1s_B):
    """Diagnostic variant (declared on the card before testing): 12-candle channel."""

    channel = 12


class Kirilim1sNoBTC_B(Kirilim1s_B):
    """Diagnostic variant (declared on the card before testing): no BTC market filter."""

    use_market_filter = False
