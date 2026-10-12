# BTC lead-lag scan: after a sharp BTC hour, do lagging altcoins catch up in the next 1-3h?
# Signal at close of hour t: |BTC r_t| >= X%, alt r_t has same sign but < half of BTC's move.
# Trade alt in BTC's direction from open t+1, hold H hours. Cost 0.2% round trip. Dev vs validation.
import sys,json,numpy as np,pandas as pd
pf=sys.argv[1]
pl=[p.split("/")[0] for p in json.load(open(pf))["exchange"]["pair_whitelist"] if not p.startswith("BTC/")]
B="user_data/data/binance/futures/"
bt=pd.read_feather(B+"BTC_USDT_USDT-1h-futures.feather").set_index("date")
br=(bt.close/bt.open-1)
res=[]
for p in pl:
    try: h=pd.read_feather(B+f"{p}_USDT_USDT-1h-futures.feather").set_index("date")
    except FileNotFoundError: continue
    r=h.close/h.open-1;b=br.reindex(h.index)
    for H in (1,2,3):
        fwd=h.close.shift(-H)/h.open.shift(-1)-1
        for X in (0.01,0.015,0.02):
            for side in (1,-1):
                s=(side*b>=X)&(side*r<side*b/2)
                f=(side*fwd[s]).dropna()*100-0.2
                per=np.where(f.index<"2025-01-01","dev",np.where(f.index<"2026-04-01","val","x"))
                for k in ("dev","val"):
                    v=f[per==k]
                    res.append((H,X,side,k,len(v),v.sum()))
R=pd.DataFrame(res,columns=["H","X","side","per","n","sum"]).groupby(["H","X","side","per"]).sum()
R["mean%"]=R["sum"]/R["n"];print(R["mean%"].unstack().join(R["n"].unstack(),rsuffix="_n").round(3).to_string())
