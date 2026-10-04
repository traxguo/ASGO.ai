import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "fbv", Path(__file__).resolve().parents[1] / "research" / "data" / "fetch_binance_vision.py"
)
fbv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fbv)

ROW = b"1704067200000,42000.1,42100,41900,42050,123.4,1704070799999,5000000,1000,60,2500000,0\n"


def test_klines_without_header():
    df = fbv.parse_klines(ROW)
    assert len(df) == 1 and df["close"].iloc[0] == 42050
    assert str(df["date"].iloc[0]) == "2024-01-01 00:00:00+00:00"


def test_klines_with_header():
    header = b"open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
    df = fbv.parse_klines(header + ROW)
    assert len(df) == 1 and df["open"].iloc[0] == 42000.1


def test_funding():
    csv = b"calc_time,funding_interval_hours,last_funding_rate\n1704067200005,8,0.00010000\n"
    df = fbv.parse_funding(csv)
    assert df["funding_rate"].iloc[0] == 0.0001
    assert str(df["date"].iloc[0]) == "2024-01-01 00:00:00+00:00"


def test_symbol():
    assert fbv.symbol_of("BTC/USDT:USDT") == "BTCUSDT"
