"""
Generates SYNTHETIC futures data (random walk with trending regimes) in
Freqtrade's format. Used ONLY to check that the pipeline runs end to end when
real Binance data cannot be downloaded. Results on this data mean nothing.

Usage: python tests/smoke/make_synthetic_data.py <datadir>
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from freqtrade.data.history import get_datahandler
from freqtrade.enums import CandleType

PAIRS = {"BTC/USDT:USDT": 30000.0, "ETH/USDT:USDT": 2000.0}


def make_1h(start_price: float, seed: int, n: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # regime drift switches every ~500 hours
    drift = np.repeat(rng.normal(0, 0.0006, n // 500 + 1), 500)[:n]
    rets = drift + rng.normal(0, 0.008, n)
    close = start_price * np.exp(np.cumsum(rets))
    open_ = np.concatenate([[start_price], close[:-1]])
    wick = np.abs(rng.normal(0, 0.004, n))
    high = np.maximum(open_, close) * (1 + wick)
    low = np.minimum(open_, close) * (1 - wick)
    date = pd.date_range("2022-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame({"date": date, "open": open_, "high": high, "low": low,
                         "close": close, "volume": rng.uniform(100, 1000, n)})


def main(datadir: str) -> None:
    Path(datadir).mkdir(parents=True, exist_ok=True)
    dh = get_datahandler(Path(datadir), "feather")
    n = 24 * 365 * 2
    for i, (pair, price) in enumerate(PAIRS.items()):
        h1 = make_1h(price, seed=i, n=n)
        dh.ohlcv_store(pair, "1h", h1, CandleType.FUTURES)
        h4 = (h1.set_index("date").resample("4h")
              .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
              .reset_index())
        dh.ohlcv_store(pair, "4h", h4, CandleType.FUTURES)
        dh.ohlcv_store(pair, "1h", h1, CandleType.MARK)
        fr = h1.loc[h1["date"].dt.hour % 8 == 0, ["date"]].copy()  # funding every 8h
        fr["funding_rate"] = 0.0001
        dh.ohlcv_store(pair, "1h", fr, CandleType.FUNDING_RATE)
    print(f"synthetic data written to {datadir}")


if __name__ == "__main__":
    main(sys.argv[1])
