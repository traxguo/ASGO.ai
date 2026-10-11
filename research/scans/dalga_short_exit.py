# Dalga entries with short exits: fixed target T (R) + time stop H hours, 1h candles, stop first.
import json,glob,zipfile,sys,re,numpy as np,pandas as pd
z=sorted(glob.glob(sys.argv[1]+"/*.zip"))[-1]
with zipfile.ZipFile(z) as f:
    n=[n for n in f.namelist() if n.endswith(".json") and "config" not in n and "meta" not in n][0]; d=json.load(f.open(n))
t=d["strategy"]["Dalga"]["trades"]
cache={}
def px(pair):
    if pair not in cache:
        p=pair.split("/")[0]; df=pd.read_feather(f"user_data/data/binance/futures/{p}_USDT_USDT-1h-futures.feather").set_index("date"); cache[pair]=df
    return cache[pair]
res={}
for x in t:
    stop=float(re.search(r"stop=([0-9.eE+-]+)",x["enter_tag"]).group(1)); e=x["open_rate"]; risk=e-stop
    if risk<=0: continue
    df=px(x["pair"]); od=pd.Timestamp(x["open_date"])
    w=df[df.index>=od.floor("h")].iloc[:49]
    cost=0.002*e/risk
    for T in (1.0,1.5,2.0,3.0):
        for H in (4,8,12,24,48):
            r=None
            for k,(i,row) in enumerate(w.iterrows()):
                if k>=H: r=(row.open-e)/risk; break
                if row.low<=stop: r=-1; break
                if row.high>=e+T*risk: r=T; break
            if r is None: r=(w.close.iloc[-1]-e)/risk
            res.setdefault((T,H),[]).append(r-cost)
print("T\\H "+" ".join(f"{h:>6}" for h in (4,8,12,24,48)))
for T in (1.0,1.5,2.0,3.0):
    print(f"{T:<4}"+" ".join(f"{np.mean(res[(T,H)]):6.2f}" for H in (4,8,12,24,48)))
