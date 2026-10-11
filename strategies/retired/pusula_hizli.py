"""
pusula_hizli ("fast compass"): a faster Pusula. Strategy card: cards/pusula_hizli.md
(condition ids below must match the card). Rules fixed before the first test.

Same building blocks as Pusula (strategies/candidates/pusula.py, not modified):
  - daily regime score (-3 .. +3) from the last CLOSED daily candle, for the coin and BTC
  - 4h trigger: first close above the previous 20-candle high (long) / below the low (short)

Differences, to get short and frequent trades:
  - looser regime: coin score >= +2 for longs, <= -2 for shorts (Pusula: +3 / -3);
    BTC on the same side (score >= +1 / <= -1), as in Pusula.
    NOTE: the score is always odd, so +-2 equals +-3; the correction round uses
    +-1 (two of three signs), see PusulaHizli1_B and the card
  - fixed exits from the shared module: Model B (half at 2R + stop to break even, rest at 4R),
    no daily trend exit
  - max 5 open trades (set on the command line, --max-open-trades 5)

The shared module has no time stop, so none is used.

RETIRED 2026-10-10: development period 2020-2024 on 36 coins, max 5 open:
PusulaHizli1_B 599 trades (0.34 a day), +0.09R, PF 1.07, max drawdown 46%;
the +-3 version (= PusulaHizli_B) 524 trades, +0.23R, drawdown 25.9%.
Neither reached the trade frequency target or the thresholds. Reason on the
card. Kept for the record; do not use for signals.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pandas import DataFrame  # noqa: E402

from strategies.candidates.pusula import REGIME_TF, PusulaBase  # noqa: E402


class PusulaHizli_B(PusulaBase):
    """Main version (the card decides on this one): regime threshold +-2, Model B."""

    tp_model_name = "B"
    regime_min = 2

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        score = df[f"score_{REGIME_TF}"]
        conds["long"]["regime_up"] = score >= self.regime_min
        conds["short"]["regime_down"] = score <= -self.regime_min
        return conds


class PusulaHizli3_B(PusulaHizli_B):
    """Variant 1 (declared on the card before testing): Pusula's strict regime threshold +-3."""

    regime_min = 3


class PusulaHizli1_B(PusulaHizli_B):
    """
    Correction round (card section "Düzeltme turu"): the score is a sum of three
    +-1 signs, so it is odd (-3, -1, +1, +3) and ">= +2" turned out identical to
    "== +3". The card's intent, "two of three signs", is score >= +1 / <= -1.
    This is the main version from the correction round on.
    """

    regime_min = 1
