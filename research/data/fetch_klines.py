# Parallel monthly kline fetcher from data.binance.vision (USD-M futures) -> user_data/data/binance/futures/<COIN>_USDT_USDT-<tf>-futures.feather
# Usage: python research/data/fetch_klines.py <pairs.json> <tf> <YYYY-MM start> <YYYY-MM end>
import sys,json,io,zipfile,urllib.request,pandas as pd
from concurrent.futures import ThreadPoolExecutor
pf,tf,s,e=sys.argv[1:5]
coins=[p.split("/")[0] for p in json.load(open(pf))["exchange"]["pair_whitelist"]]
months=[m.strftime("%Y-%m") for m in pd.period_range(s,e,freq="M")]
B="https://data.binance.vision/data/futures/um/monthly/klines"
def get(c,m):
    u=f"{B}/{c}USDT/{tf}/{c}USDT-{tf}-{m}.zip"
    try:
        z=zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(u,timeout=60).read()))
        df=pd.read_csv(z.open(z.namelist()[0]),header=None,usecols=range(6))
        df=df[pd.to_numeric(df[0],errors="coerce").notna()].astype(float)
        return c,df
    except Exception: return c,None
with ThreadPoolExecutor(48) as ex: res=list(ex.map(lambda a:get(*a),[(c,m) for c in coins for m in months]))
for c in coins:
    parts=[d for k,d in res if k==c and d is not None]
    if not parts: print(c,"none");continue
    d=pd.concat(parts);d.columns=["date","open","high","low","close","volume"]
    d["date"]=pd.to_datetime(d.date.astype("int64"),unit="ms",utc=True)
    d=d.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    d.to_feather(f"user_data/data/binance/futures/{c}_USDT_USDT-{tf}-futures.feather")
print("done",len(coins))
