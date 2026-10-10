#!/usr/bin/env python3
"""
Fallback downloader: Binance public data archive (data.binance.vision).

Use this only when `freqtrade download-data` cannot reach the Binance futures
API (PROJECT_BRIEF section 2). It downloads monthly archives of
  - futures klines (OHLCV)
  - mark price klines
  - funding rate history
for USD-M perpetuals and stores them in Freqtrade's feather format, so the
backtest reads them exactly like data from download-data.

The current (unfinished) month is not in the monthly archive. With
--current-month the candles (klines + mark) of the current month are added from
the daily archives up to yesterday. Funding has no daily archive, so the current
month has no funding data until the month is over (results for those days are
provisional).

Usage:
  python research/data/fetch_binance_vision.py --pairs BTC/USDT:USDT ETH/USDT:USDT \
      --timeframes 1h 4h --start 2019-09 [--datadir user_data/data/binance]
"""

from __future__ import annotations

import argparse
import io
import urllib.error
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
from freqtrade.data.history import get_datahandler
from freqtrade.enums import CandleType

BASE = "https://data.binance.vision/data/futures/um/monthly"
DAILY_BASE = "https://data.binance.vision/data/futures/um/daily"
KLINE_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
              "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]


def symbol_of(pair: str) -> str:
    return pair.split(":")[0].replace("/", "")


def months(start: str, end: date) -> list[str]:
    last_full = (pd.Timestamp(end).to_period("M") - 1)
    return [str(p) for p in pd.period_range(pd.Period(start, "M"), last_full, freq="M")]


CACHE_DIR = Path("user_data/data/binance_vision_raw")  # raw zips, reused on re-runs


def fetch_zip_csv(url: str) -> bytes | None:
    cached = CACHE_DIR / url.split("/um/", 1)[-1].split("/", 1)[-1]
    missing = cached.with_suffix(".missing")
    if missing.exists():
        return None
    if cached.exists():
        raw = cached.read_bytes()
    else:
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                raw = r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                missing.parent.mkdir(parents=True, exist_ok=True)
                missing.touch()
                return None  # month not available (coin not listed yet)
            raise
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        return z.read(z.namelist()[0])


def parse_klines(csv: bytes) -> pd.DataFrame:
    """Older archive files have no header row, newer ones do; handle both."""
    first = csv.split(b"\n", 1)[0]
    has_header = not first[:1].isdigit()
    df = pd.read_csv(io.BytesIO(csv), header=0 if has_header else None)
    df = df.iloc[:, :6]
    df.columns = KLINE_COLS[:6]
    df["date"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True)
    return df[["date", "open", "high", "low", "close", "volume"]].astype(
        {"open": float, "high": float, "low": float, "close": float, "volume": float})


def parse_funding(csv: bytes) -> pd.DataFrame:
    """Columns: calc_time, funding_interval_hours, last_funding_rate."""
    df = pd.read_csv(io.BytesIO(csv))
    time_col = df.columns[0]
    rate_col = df.columns[-1]
    out = pd.DataFrame({
        "date": pd.to_datetime(df[time_col].astype("int64"), unit="ms", utc=True).dt.floor("h"),
        "funding_rate": df[rate_col].astype(float),
    })
    return out


def collect(urls: list[str], parser) -> pd.DataFrame:
    parts = []
    for u in urls:
        csv = fetch_zip_csv(u)
        if csv is not None:
            parts.append(parser(csv))
    if not parts:
        return pd.DataFrame()
    df = pd.concat(parts).drop_duplicates("date").sort_values("date").reset_index(drop=True)
    return df


def missing_days(df: pd.DataFrame, timeframe: str) -> list[str]:
    """Calendar days with at least one missing candle between first and last candle."""
    if df.empty:
        return []
    full = pd.date_range(df["date"].min(), df["date"].max(), freq=pd.Timedelta(timeframe))
    gaps = full.difference(pd.DatetimeIndex(df["date"]))
    return sorted({d.strftime("%Y-%m-%d") for d in gaps})


def fill_from_daily(df: pd.DataFrame, kind: str, sym: str, tf: str) -> pd.DataFrame:
    """Some monthly archives are truncated (e.g. SOL/XRP Feb+Mar 2022); the daily
    archives for the same days are complete. Top up only the missing days."""
    days = missing_days(df, tf)
    if not days:
        return df
    extra = collect([f"{DAILY_BASE}/{kind}/{sym}/{tf}/{sym}-{tf}-{d}.zip" for d in days], parse_klines)
    if extra.empty:
        return df
    return pd.concat([df, extra]).drop_duplicates("date").sort_values("date").reset_index(drop=True)


def add_current_month(df: pd.DataFrame, kind: str, sym: str, tf: str) -> pd.DataFrame:
    """Candles of the current month, day by day from the daily archive, up to yesterday."""
    today = date.today()
    days = [date(today.year, today.month, d).isoformat() for d in range(1, today.day)]
    extra = collect([f"{DAILY_BASE}/{kind}/{sym}/{tf}/{sym}-{tf}-{d}.zip" for d in days], parse_klines)
    if extra.empty:
        return df
    return pd.concat([df, extra]).drop_duplicates("date").sort_values("date").reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", required=True)
    ap.add_argument("--timeframes", nargs="+", default=["1h", "4h"])
    ap.add_argument("--start", default="2019-09", help="first month, YYYY-MM")
    ap.add_argument("--datadir", default="user_data/data/binance")
    ap.add_argument("--current-month", action="store_true",
                    help="also add the current month's candles from the daily archives (up to yesterday)")
    a = ap.parse_args()

    Path(a.datadir).mkdir(parents=True, exist_ok=True)
    dh = get_datahandler(Path(a.datadir), "feather")
    ms = months(a.start, date.today())
    for pair in a.pairs:
        sym = symbol_of(pair)
        for tf in a.timeframes:
            df = collect([f"{BASE}/klines/{sym}/{tf}/{sym}-{tf}-{m}.zip" for m in ms], parse_klines)
            df = fill_from_daily(df, "klines", sym, tf)
            if a.current_month:
                df = add_current_month(df, "klines", sym, tf)
            print(f"{pair} {tf} futures: {len(df)} candles")
            if not df.empty:
                dh.ohlcv_store(pair, tf, df, CandleType.FUTURES)
        mark = collect([f"{BASE}/markPriceKlines/{sym}/1h/{sym}-1h-{m}.zip" for m in ms], parse_klines)
        mark = fill_from_daily(mark, "markPriceKlines", sym, "1h")
        if a.current_month:
            mark = add_current_month(mark, "markPriceKlines", sym, "1h")
        print(f"{pair} 1h mark: {len(mark)} candles")
        if not mark.empty:
            dh.ohlcv_store(pair, "1h", mark, CandleType.MARK)
        fr = collect([f"{BASE}/fundingRate/{sym}/{sym}-fundingRate-{m}.zip" for m in ms], parse_funding)
        print(f"{pair} funding: {len(fr)} rows")
        if not fr.empty:
            dh.ohlcv_store(pair, "1h", fr, CandleType.FUNDING_RATE)


if __name__ == "__main__":
    main()
