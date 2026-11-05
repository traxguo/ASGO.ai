# Funding rates for every Binance USDⓈ-M USDT perpetual ever listed (delisted included), from data.binance.vision.
# Summed per UTC day -> user_data/data/xsec_all_funding_1d.feather (date, symbol, funding). Not committed.
# funding > 0 means longs pay shorts. Usage: python research/neutral/fetch_funding_daily.py user_data/data/all_usdt_syms.txt
import io, re, sys, time, zipfile, urllib.request
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

LIST = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/futures/um/monthly/fundingRate/{s}/"
FILE = "https://data.binance.vision/data/futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{m}.zip"
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
    return sorted(m for m in set(re.findall(rf"{s}-fundingRate-(\d{{4}}-\d{{2}})\.zip<", x)) if m <= LAST)


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
    df = df.iloc[:, [0, 2]].astype(float)
    df.columns = ["ts", "funding"]
    df["symbol"] = s
    return df


with ThreadPoolExecutor(12) as ex:
    ms = list(ex.map(months, syms))
jobs = [(s, m) for s, mm in zip(syms, ms) for m in mm]
print(len(jobs), "monthly files", flush=True)
with ThreadPoolExecutor(16) as ex:
    parts = [p for p in ex.map(one, jobs) if p is not None]
D = pd.concat(parts)
D["date"] = pd.to_datetime(D.ts.astype("int64"), unit="ms", utc=True).dt.floor("D")
D = D.drop_duplicates(["symbol", "ts"]).groupby(["date", "symbol"], as_index=False).funding.sum()
D.to_feather("user_data/data/xsec_all_funding_1d.feather")
print(D.symbol.nunique(), "symbols,", len(D), "rows")
