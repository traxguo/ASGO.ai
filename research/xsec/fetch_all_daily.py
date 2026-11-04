# Daily klines for EVERY Binance USDⓈ-M USDT perpetual ever listed (delisted ones included), from data.binance.vision.
# Used to check survivorship bias of the cross-sectional scans: our pair lists only hold coins that still trade today.
# Output: user_data/data/xsec_all_1d.feather (date, symbol, close, quote_volume). Not committed.
import io, re, sys, time, zipfile, urllib.request
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

LIST = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/futures/um/monthly/klines/{s}/1d/"
FILE = "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1d/{s}-1d-{m}.zip"
LAST = "2026-03"
syms = open(sys.argv[1]).read().split()


def get(url):
    for i in range(5):
        try:
            return urllib.request.urlopen(url, timeout=30).read()
        except Exception:
            time.sleep(1 + 2 * i)
    return None


def months(s):
    x = (get(LIST.format(s=s)) or b"").decode()
    return sorted(m for m in set(re.findall(rf"{s}-1d-(\d{{4}}-\d{{2}})\.zip<", x)) if m <= LAST)


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
    df = df.iloc[:, [0, 4, 7]].astype(float)
    df.columns = ["ts", "close", "quote_volume"]
    df["symbol"] = s
    return df


with ThreadPoolExecutor(12) as ex:
    ms = list(ex.map(months, syms))
jobs = [(s, m) for s, mm in zip(syms, ms) for m in mm]
print(len(jobs), "monthly files", flush=True)
with ThreadPoolExecutor(16) as ex:
    parts = [p for p in ex.map(one, jobs) if p is not None]
D = pd.concat(parts)
D["date"] = pd.to_datetime(D.ts.astype("int64"), unit="ms", utc=True)
D = D.drop(columns="ts").drop_duplicates(["symbol", "date"]).reset_index(drop=True)
D.to_feather("user_data/data/xsec_all_1d.feather")
print(D.symbol.nunique(), "symbols,", len(D), "rows")
