"""
Lets the research simulator import the Aslan strategy modules on machines without
Freqtrade / TA-Lib (the GitHub runner). Only the pure signal functions are used;
the stubs below are never called.
"""

import sys
import types


def install() -> None:
    try:
        import freqtrade  # noqa: F401
        import talib  # noqa: F401
        return
    except ImportError:
        pass

    def mod(name: str, **attrs) -> None:
        m = types.ModuleType(name)
        m.__dict__.update(attrs)
        sys.modules[name] = m

    def tf_minutes(tf: str) -> int:
        return int(tf[:-1]) * {"m": 1, "h": 60, "d": 1440, "w": 10080}[tf[-1]]

    class _IStrategy:
        def __init__(self, config=None):
            pass

    mod("freqtrade")
    mod("freqtrade.exchange", timeframe_to_minutes=tf_minutes, timeframe_to_prev_date=lambda *a, **k: None)
    mod("freqtrade.persistence", Order=object, Trade=object)
    mod("freqtrade.strategy", IStrategy=_IStrategy, stoploss_from_absolute=lambda *a, **k: None)
    mod("talib")
    mod("talib.abstract", ATR=lambda *a, **k: None)
