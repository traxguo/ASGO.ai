"""
Probe for the Akis idea (journal 2026-10-11): can Bitget's public futures data
stand in for the Binance archive "metrics" (open interest, long/short ratio,
taker buy/sell ratio)? Prints what each Bitget endpoint returns and, for the
overlapping hours, the correlation with Binance's archive for the same coin.

Public endpoints only, no keys. Runs on GitHub Actions (the cloud sandbox cannot
reach Bitget): python research/live/bitget_metrics_probe.py
"""

import io
import json
import urllib.request
import zipfile
from datetime import date, timedelta

import pandas as pd

BITGET = "https://api.bitget.com/api/v2/mix/market/"
COINS = ["BTC", "ETH", "SOL"]


def get(url: str):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "asgo-probe"}), timeout=30) as r:
        return json.loads(r.read())


def bitget(endpoint: str, coin: str, period: str = "1h"):
    url = f"{BITGET}{endpoint}?symbol={coin}USDT&productType=usdt-futures&period={period}"
    try:
        data = get(url).get("data")
    except Exception as e:  # report and continue
        return None, str(e)
    return data, None


def binance_metrics(coin: str, days: int = 6) -> pd.DataFrame:
    parts = []
    for i in range(2, days + 2):
        d = date.today() - timedelta(days=i)
        url = f"https://data.binance.vision/data/futures/um/daily/metrics/{coin}USDT/{coin}USDT-metrics-{d}.zip"
        try:
            with urllib.request.urlopen(url, timeout=30) as r, zipfile.ZipFile(io.BytesIO(r.read())) as z:
                parts.append(pd.read_csv(z.open(z.namelist()[0])))
        except Exception as e:
            print(f"binance {coin} {d}: {e}")
    if not parts:
        return pd.DataFrame()
    m = pd.concat(parts)
    m["t"] = pd.to_datetime(m["create_time"], utc=True)
    return m.set_index("t").sort_index()


def frame(rows, ts_key="ts") -> pd.DataFrame:
    if not rows or not isinstance(rows, list) or not isinstance(rows[0], dict):
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["t"] = pd.to_datetime(pd.to_numeric(df[ts_key]), unit="ms", utc=True)
    return df.set_index("t").sort_index().apply(pd.to_numeric, errors="coerce")


for coin in COINS:
    print(f"===== {coin}")
    got = {}
    for ep in ("account-long-short", "long-short", "taker-buy-sell", "position-long-short", "open-interest"):
        data, err = bitget(ep, coin)
        if err:
            print(f"{ep}: ERROR {err}")
            continue
        sample = data[:1] + data[-1:] if isinstance(data, list) else data
        print(f"{ep}: {len(data) if isinstance(data, list) else 'object'} rows, sample {json.dumps(sample)[:300]}")
        got[ep] = frame(data) if isinstance(data, list) else pd.DataFrame()
    b = binance_metrics(coin)
    if b.empty:
        continue
    bh = b.resample("1h").last()
    taker_b = pd.to_numeric(b["sum_taker_long_short_vol_ratio"], errors="coerce").resample("1h").mean()
    for ep, df in got.items():
        if df.empty:
            continue
        for col in df.columns:
            j = pd.concat([df[col].rename("bitget"),
                           pd.to_numeric(bh["count_long_short_ratio"], errors="coerce").rename("binance_ls"),
                           taker_b.rename("binance_taker")], axis=1).dropna()
            if len(j) >= 20:
                print(f"  {ep}.{col}: {len(j)} common hours, corr with binance L/S {j.bitget.corr(j.binance_ls):+.2f}, "
                      f"with binance taker {j.bitget.corr(j.binance_taker):+.2f}")
