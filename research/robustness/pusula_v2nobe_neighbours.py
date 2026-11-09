"""
Queue item 32 (2026-11-09, research/queue/pusula_kuyruk.md): robustness
diagnostic of the PusulaV2NoBe baseline. Research only, no rule changes.

Ten one-parameter neighbours of PusulaV2NoBe, values fixed before the test
(about +-25%), everything else identical:
  - 4h breakout channel      20  -> 15 / 25
  - swing stop window        10  -> 8 / 12 candles
  - ATR stop multiplier      1.5 -> 1.25 / 1.75
  - daily fast EMA           20  -> 15 / 25  (score, "close above EMA" entry
                                              condition and EMA exit together;
                                              BTC's score uses the same value)
  - momentum                 90  -> 60 / 120 days (coin and BTC score)

PusulaV2NoBeNbBase is the unchanged baseline, so a single --strategy-list run
contains the baseline too. None of these classes is a candidate: the baseline
is not replaced by a neighbour, whatever the result (that would be data mining).

Freqtrade loads every .py in the strategy folder, so this module is not run
from research/robustness/ directly; put it (or a symlink to it) alone in a
folder and pass that folder as FT_STRATEGY_DIR:
  mkdir -p /tmp/nb && ln -sf $PWD/research/robustness/pusula_v2nobe_neighbours.py /tmp/nb/
  FT_STRATEGY_DIR=/tmp/nb FT_LOCAL=1 FT_OFFLINE=1 ./scripts/ft.sh backtesting \
      -c config/pairs_wide16.json --strategy-list PusulaV2NoBeNbBase PusulaV2NoBeNbChannel15 ...
"""

import sys
from dataclasses import replace
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from strategies.candidates.pusula import PusulaV2NoBe  # noqa: E402
from strategies.common import trade_management as tm  # noqa: E402


class PusulaV2NoBeNbBase(PusulaV2NoBe):
    """Unchanged baseline (control)."""


class PusulaV2NoBeNbChannel15(PusulaV2NoBe):
    channel = 15


class PusulaV2NoBeNbChannel25(PusulaV2NoBe):
    channel = 25


class PusulaV2NoBeNbSwing8(PusulaV2NoBe):
    swing_lookback = 8


class PusulaV2NoBeNbSwing12(PusulaV2NoBe):
    swing_lookback = 12


class PusulaV2NoBeNbAtr125(PusulaV2NoBe):
    mgmt = replace(tm.DEFAULT_PARAMS, stop_atr=1.25)


class PusulaV2NoBeNbAtr175(PusulaV2NoBe):
    mgmt = replace(tm.DEFAULT_PARAMS, stop_atr=1.75)


class PusulaV2NoBeNbEma15(PusulaV2NoBe):
    ema_fast = 15


class PusulaV2NoBeNbEma25(PusulaV2NoBe):
    ema_fast = 25


class PusulaV2NoBeNbMom60(PusulaV2NoBe):
    momentum_days = 60


class PusulaV2NoBeNbMom120(PusulaV2NoBe):
    momentum_days = 120


NEIGHBOURS = [
    PusulaV2NoBeNbChannel15, PusulaV2NoBeNbChannel25,
    PusulaV2NoBeNbSwing8, PusulaV2NoBeNbSwing12,
    PusulaV2NoBeNbAtr125, PusulaV2NoBeNbAtr175,
    PusulaV2NoBeNbEma15, PusulaV2NoBeNbEma25,
    PusulaV2NoBeNbMom60, PusulaV2NoBeNbMom120,
]
