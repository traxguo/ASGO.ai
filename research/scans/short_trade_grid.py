# Short-hold (<=3h) event engine on 1h bars, 81 coins. Signals at bar close, entry next open.
# Exits: TP k*ATR, SL m*ATR, time stop T hours (exit at close of bar T). TP+SL same bar -> SL (conservative).
# PnL in R (risk = m*ATR) net of 0.2% round-trip cost. One open trade per coin.
import sys,json,numpy as np,pandas as pd
pf,start,end=sys.argv[1],sys.argv[2],sys.argv[3]
pl=[p.split("/")[0] for p in json.load(open(pf))["exchange"]["pair_whitelist"]]
SIG=("S1_break24","S2_pullback","S3_expansion","S4_capit")
GRID=[(3.0,1.5,3),(2.0,1.5,3),(1.5,1.5,3)]
res={(s,g):[] for s in SIG for g in GRID}
for p in pl:
    try:
        h=pd.read_feather(f"user_data/data/binance/futures/{p}_USDT_USDT-1h-futures.feather").set_index("date")
        d=pd.read_feather(f"user_data/data/binance/futures/{p}_USDT_USDT-1d-futures.feather").set_index("date").close
    except FileNotFoundError: continue
    e20,e50=d.ewm(span=20,adjust=False).mean(),d.ewm(span=50,adjust=False).mean()
    sc=(np.sign(d-e50)+np.sign(e20-e50)+np.sign(d/d.shift(90)-1)).shift(1)
    score=sc.reindex(h.index.floor("D")).values
    o,hi,lo,c=h.open.values,h.high.values,h.low.values,h.close.values
    tr=np.maximum(hi-lo,np.maximum(abs(hi-np.r_[np.nan,c[:-1]]),abs(lo-np.r_[np.nan,c[:-1]])))
    atr=pd.Series(tr).rolling(14).mean().values
    hh24=pd.Series(hi).rolling(24).max().shift(1).values
    dl=np.diff(c,prepend=np.nan);up=pd.Series(np.where(dl>0,dl,0)).ewm(alpha=1/14).mean();dn=pd.Series(np.where(dl<0,-dl,0)).ewm(alpha=1/14).mean()
    rsi=(100-100/(1+up/dn)).values
    r3=(c-np.r_[[np.nan]*3,c[:-3]])
    rng=hi-lo; pos=(c-lo)/np.where(rng>0,rng,np.nan)
    inwin=(h.index>=start)&(h.index<end)
    sigs={"S1_break24":(score==3)&(c>hh24),
          "S2_pullback":(score==3)&(rsi<35),
          "S3_expansion":(score>=1)&(rng>2*np.r_[np.nan,atr[:-1]])&(pos>0.8),
          "S4_capit":(score>=1)&(r3<-3*atr)}
    n=len(c)
    for s,m in sigs.items():
        idx=np.where(m&inwin&~np.isnan(atr))[0]
        for g in GRID:
            tp,sl,T=g;busy=-1
            for i in idx:
                if i<=busy or i+1+T>=n: continue
                e=o[i+1];A=atr[i];stop=e-sl*A;tgt=e+tp*A;out=None
                for j in range(i+1,i+1+T):
                    if lo[j]<=stop: out=stop;break
                    if hi[j]>=tgt: out=tgt;break
                if out is None: out=c[i+T];j=i+T
                R=(out-e)/(sl*A)-0.002*e/(sl*A)
                res[(s,g)].append(R);busy=j
days=(pd.Timestamp(end)-pd.Timestamp(start)).days
print(pf,start,end)
for (s,g),v in res.items():
    v=np.array(v)
    if len(v): print(f"{s:13s} tp={g[0]} sl={g[1]} T={g[2]} n={len(v):6d} /day={len(v)/days:5.2f} avgR={v.mean():+.3f} win={np.mean(v>0)*100:.0f}%")
