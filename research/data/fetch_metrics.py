# Parallel fetcher for Binance USD-M daily "metrics" files (5m open interest, top-trader and taker long/short ratios)
# from data.binance.vision -> user_data/data/metrics/<COIN>-5m.feather
# Usage: python research/data/fetch_metrics.py <start YYYY-MM-DD> <end YYYY-MM-DD> COIN [COIN ...]
import sys,io,zipfile,urllib.request,os,pandas as pd
from concurrent.futures import ThreadPoolExecutor
s,e,coins=sys.argv[1],sys.argv[2],sys.argv[3:]
days=[d.strftime("%Y-%m-%d") for d in pd.date_range(s,e)]
B="https://data.binance.vision/data/futures/um/daily/metrics"
def get(c,d):
    try:
        z=zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(f"{B}/{c}USDT/{c}USDT-metrics-{d}.zip",timeout=60).read()))
        return c,pd.read_csv(z.open(z.namelist()[0]))
    except Exception: return c,None
os.makedirs("user_data/data/metrics",exist_ok=True)
with ThreadPoolExecutor(64) as ex: res=list(ex.map(lambda a:get(*a),[(c,d) for c in coins for d in days]))
for c in coins:
    parts=[x for k,x in res if k==c and x is not None]
    if not parts: print(c,"none");continue
    df=pd.concat(parts);df["date"]=pd.to_datetime(df.create_time,utc=True)
    df=df.drop(columns=["create_time","symbol"]).drop_duplicates("date").sort_values("date").reset_index(drop=True)
    df.to_feather(f"user_data/data/metrics/{c}-5m.feather");print(c,len(df),df.date.min(),df.date.max())
