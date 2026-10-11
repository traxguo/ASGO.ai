"""
Freqtrade lookahead-analysis for strategies whose limit entry fills after the order
candle (e.g. fvg_ob). The stock tool cuts the data one candle after the ORDER, so a
limit that fills later is missing in the cut run and is reported as "biased". Here the
entry check data ends two candles after the entry FILL instead (one candle is not
enough: the last candle of a backtest is not processed). Everything else is the stock
tool. Run from the repo root after scripts/safety_check.py, with the usual arguments:

  python3 scripts/safety_check.py && python research/robustness/lookahead_limit_fill.py \
      lookahead-analysis -c config/base.json -c config/pairs_level1.json --userdir user_data \
      --strategy-path strategies/candidates --strategy FvgObLookahead --allow-limit-orders ...
"""

import sys
from datetime import timedelta
from unittest import mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import offline_freqtrade as off
from freqtrade.exchange.exchange import Exchange
from freqtrade.exchange import timeframe_to_minutes
from freqtrade.optimize.analysis import lookahead as la
import pandas as pd

orig = la.LookaheadAnalysis.fill_entry_and_exit_varHolders


def patched(self, result_row):
    orig(self, result_row)
    ev = self.entry_varHolders[-1]
    fill = None
    for o in result_row["orders"]:
        if o["ft_is_entry"]:
            fill = pd.Timestamp(o["order_filled_timestamp"], unit="ms", tz="UTC")
            break
    if fill is not None and fill > result_row["open_date"]:
        ev.to_dt = fill.to_pydatetime() + timedelta(minutes=2 * timeframe_to_minutes(self.full_varHolder.timeframe))
        self.prepare_data(ev, [result_row["pair"]])


la.LookaheadAnalysis.fill_entry_and_exit_varHolders = patched
with mock.patch.object(Exchange, "_api_reload_markets", off._fake_reload):
    from freqtrade.main import main
    main(sys.argv[1:])
