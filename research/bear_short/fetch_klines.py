# Klines (interval TF env, default 1h) for a list of Binance USDⓈ-M USDT perpetuals (delisted ones included), from data.binance.vision.
# Copy of research/xsec/fetch_klines_15m.py with a configurable interval (bear-short research, 2026-11-05).
# Output: user_data/data/pit{tf}/<COIN>_USDT_USDT-{tf}-futures.feather (date, open, high, low, close, volume),
# the same layout Freqtrade writes, so research/scans/wick_catcher_pit.py can read it. Not committed.
# Usage: TF=1h python research/bear_short/fetch_klines.py symbols.txt   (one symbol per line, e.g. BTCUSDT)
import io, os, re, sys, time, zipfile, urllib.request
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

tf = os.environ.get("TF", "1h")

LIST = f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/futures/um/monthly/klines/{{s}}/{tf}/"
FILE = f"https://data.binance.vision/data/futures/um/monthly/klines/{{s}}/{tf}/{{s}}-{tf}-{{m}}.zip"
LAST = os.environ.get("LAST", "2026-03")
OUT = f"user_data/data/pit{tf}/"
syms = open(sys.argv[1]).read().split()
os.makedirs(OUT, exist_ok=True)


def get(url):
    for i in range(5):
        try:
            return urllib.request.urlopen(url, timeout=60).read()
        except Exception:
            time.sleep(1 + 2 * i)
    return None


def months(s):
    x = (get(LIST.format(s=s)) or b"").decode()
    return sorted(m for m in set(re.findall(rf"{s}-{tf}-(\d{{4}}-\d{{2}})\.zip<", x)) if m <= LAST)


def one(sm):
    s, m = sm
    raw = get(FILE.format(s=s, m=m))
    if raw is None:
        print("missing", s, m, flush=True)
        return None
    z = zipfile.ZipFile(io.BytesIO(raw))
    df = pd.read_csv(z.open(z.namelist()[0]), header=None)
    if not str(df.iloc[0, 0]).isdigit():
        df = df.iloc[1:]
    df = df.iloc[:, :6].astype(float)
    df.columns = ["ts", "open", "high", "low", "close", "volume"]
    df["symbol"] = s
    return df


def save(s, parts):
    D = pd.concat(parts)
    D["date"] = pd.to_datetime(D.ts.astype("int64"), unit="ms", utc=True)
    D = D.drop(columns=["ts", "symbol"]).drop_duplicates("date").sort_values("date").reset_index(drop=True)
    D[["date", "open", "high", "low", "close", "volume"]].to_feather(OUT + f"{s[:-4]}_USDT_USDT-{tf}-futures.feather")


todo = [s for s in syms if not os.path.exists(OUT + f"{s[:-4]}_USDT_USDT-{tf}-futures.feather")]
with ThreadPoolExecutor(12) as ex:
    ms = list(ex.map(months, todo))
print(len(todo), "symbols,", sum(map(len, ms)), "monthly files", flush=True)
with ThreadPoolExecutor(16) as ex:
    for s, mm in zip(todo, ms):
        parts = [p for p in ex.map(one, [(s, m) for m in mm]) if p is not None]
        if parts:
            save(s, parts)
        print(s, len(parts), "months", flush=True)
