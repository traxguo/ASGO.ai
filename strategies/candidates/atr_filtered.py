"""
ATR "is the market suitable?" filter (PROJECT_BRIEF strategy family 4) added to
the three base strategies. Strategy card: cards/atr_filtered.md.

One rule for all three, fixed before testing:
  vol_ok: ATR(14) / close is above its own median of the last 200 candles
          (the market is moving more than usual).
"""

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pandas import DataFrame  # noqa: E402


def _load(module: str, folder: str):
    """Import a sibling strategy file (Freqtrade loads files by path, not as a package)."""
    path = _REPO_ROOT / "strategies" / folder / f"{module}.py"
    spec = importlib.util.spec_from_file_location(f"asgo_{module}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_dc = _load("donchian_breakout", "candidates")
_rsi = _load("rsi_reversion", "candidates")
_tma = _load("trend_ma", "retired")

class ATRFilterMixin:
    vol_window = 200  # candles for the ATR% median (card: 100-300)

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        df = super().populate_indicators(df, metadata)
        df["atr_pct"] = df["atr"] / df["close"]
        df["atr_pct_median"] = df["atr_pct"].rolling(self.vol_window).median()
        return df

    def signal_conditions(self, df: DataFrame):
        conds = super().signal_conditions(df)
        vol_ok = df["atr_pct"] > df["atr_pct_median"]
        return {side: {**c, "vol_ok": vol_ok} for side, c in conds.items()}


class DonchianATR_B(ATRFilterMixin, _dc.DonchianBreakout_B):
    startup_candle_count = 500  # 200-candle median of a 14-period ATR


class DonchianATR_A(DonchianATR_B):
    tp_model_name = "A"


class RSIReversionATR_B(ATRFilterMixin, _rsi.RSIReversion_B):
    pass  # startup 1000 already covers the median window


class RSIReversionATR_A(RSIReversionATR_B):
    tp_model_name = "A"


class TrendMAATR_B(ATRFilterMixin, _tma.TrendMA_B):
    pass


class TrendMAATR_A(TrendMAATR_B):
    tp_model_name = "A"
