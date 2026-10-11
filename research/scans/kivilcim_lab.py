# Kivilcim lab: trade-level anatomy of the 1h pullback rule, to find what separates winners.
# Same engine as short_trade_grid.py (entry next open, SL/TP in ATR, time stop, SL first on ties).
# Writes one row per trade with features known at signal time.
import sys,json,numpy as np,pandas as pd
pf,start,end,out=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
TP,SL,T=(float(x) for x in (sys.argv[5:8] if len(sys.argv)>7 else (1.5,1.5,3))); T=int(T)
pl=[p.split("/")[0] for p in json.load(open(pf))["exchange"]["pair_whitelist"]]
B="user_data/data/binance/futures/"
btc=pd.read_feather(B+"BTC_USDT_USDT-1h-futures.feather").set_index("date").close
btc_r24=(btc/btc.shift(24)-1); btc_r3=(btc/btc.shift(3)-1)
rows=[]
for p in pl:
    try:
        h=pd.read_feather(B+f"{p}_USDT_USDT-1h-futures.feather").set_index("date")
        d=pd.read_feather(B+f"{p}_USDT_USDT-1d-futures.feather").set_index("date").close
    except FileNotFoundError: continue
    e20,e50=d.ewm(span=20,adjust=False).mean(),d.ewm(span=50,adjust=False).mean()
    sc=(np.sign(d-e50)+np.sign(e20-e50)+np.sign(d/d.shift(90)-1)).shift(1)
    score=sc.reindex(h.index.floor("D")).values
    o,hi,lo,c,v=(h[k].values for k in ("open","high","low","close","volume"))
    pc=np.r_[np.nan,c[:-1]]
    tr=np.maximum(hi-lo,np.maximum(abs(hi-pc),abs(lo-pc)))
    atr=pd.Series(tr).rolling(14).mean().values
    dl=np.diff(c,prepend=np.nan);up=pd.Series(np.where(dl>0,dl,0)).ewm(alpha=1/14).mean();dn=pd.Series(np.where(dl<0,-dl,0)).ewm(alpha=1/14).mean()
    rsi=(100-100/(1+up/dn)).values
    ema50h=pd.Series(c).ewm(span=50,adjust=False).mean().values
    ema200h=pd.Series(c).ewm(span=200,adjust=False).mean().values
    vrel=v/pd.Series(v).rolling(48).mean().values
    r24=c/np.r_[[np.nan]*24,c[:-24]]-1
    lowpos=(c-lo)/np.where(hi-lo>0,hi-lo,np.nan)
    br24=btc_r24.reindex(h.index).values; br3=btc_r3.reindex(h.index).values
    win=(h.index>=start)&(h.index<end)
    sig=(score==3)&(rsi<35)&win&~np.isnan(atr)
    n=len(c);busy=-1
    for i in np.where(sig)[0]:
        if i<=busy or i+1+T>=n: continue
        e=o[i+1];A=atr[i];stop=e-SL*A;tgt=e+TP*A;x=None;why="time"
        for j in range(i+1,i+1+T):
            if lo[j]<=stop: x=stop;why="sl";break
            if hi[j]>=tgt: x=tgt;why="tp";break
        if x is None: x=c[i+T];j=i+T
        risk=SL*A
        rows.append(dict(p=p,t=h.index[i],gross=(x-e)/risk,cost=0.002*e/risk,why=why,
            atrp=A/c[i]*100,rsi=rsi[i],d50=c[i]/ema50h[i]-1,d200=c[i]/ema200h[i]-1,vrel=vrel[i],
            r24=r24[i],lowpos=lowpos[i],btc24=br24[i],btc3=br3[i],hour=h.index[i].hour,dow=h.index[i].dayofweek))
        busy=j
D=pd.DataFrame(rows);D["net"]=D.gross-D.cost
D.to_feather(out);print(len(D),"trades; mean gross",round(D.gross.mean(),3),"cost",round(D.cost.mean(),3),"net",round(D.net.mean(),3))
