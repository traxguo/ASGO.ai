# Kivilcim confirmation variant: after the 1h RSI<35 pullback in a +3 daily trend, wait up to K candles
# for a reversal candle (close above the previous candle's high), then enter at the next open.
# Exits: stop = signal-swing low - 0.1 ATR ("swing") or entry - SL*ATR ("atr"); target TP x risk; time stop T hours.
# Same conventions as kivilcim_lab.py: SL first on ties, cost 0.2% round trip, ATR >= MIN_ATR% filter.
import sys,json,numpy as np,pandas as pd
pf,start,end=sys.argv[1],sys.argv[2],sys.argv[3]
K,TP,T,MODE=int(sys.argv[4]),float(sys.argv[5]),int(sys.argv[6]),sys.argv[7]
MIN_ATR=1.5;SL=1.5
pl=[p.split("/")[0] for p in json.load(open(pf))["exchange"]["pair_whitelist"]]
B="user_data/data/binance/futures/"
rows=[]
for p in pl:
    try:
        h=pd.read_feather(B+f"{p}_USDT_USDT-1h-futures.feather").set_index("date")
        d=pd.read_feather(B+f"{p}_USDT_USDT-1d-futures.feather").set_index("date").close
    except FileNotFoundError: continue
    e20,e50=d.ewm(span=20,adjust=False).mean(),d.ewm(span=50,adjust=False).mean()
    sc=(np.sign(d-e50)+np.sign(e20-e50)+np.sign(d/d.shift(90)-1)).shift(1)
    score=sc.reindex(h.index.floor("D")).values
    o,hi,lo,c=(h[k].values for k in ("open","high","low","close"))
    pc=np.r_[np.nan,c[:-1]]
    tr=np.maximum(hi-lo,np.maximum(abs(hi-pc),abs(lo-pc)))
    atr=pd.Series(tr).rolling(14).mean().values
    dl=np.diff(c,prepend=np.nan);up=pd.Series(np.where(dl>0,dl,0)).ewm(alpha=1/14).mean();dn=pd.Series(np.where(dl<0,-dl,0)).ewm(alpha=1/14).mean()
    rsi=(100-100/(1+up/dn)).values
    win=(h.index>=start)&(h.index<end)
    sig=(score==3)&(rsi<35)&win&(atr/c*100>=MIN_ATR)
    n=len(c);busy=-1
    for i in np.where(sig)[0]:
        if i<=busy: continue
        k=next((j for j in range(i+1,min(i+1+K,n-1)) if c[j]>hi[j-1]),None) if K>0 else i
        if k is None or k+1+T>=n: continue
        e=o[k+1];A=atr[k]
        stop=(lo[i:k+1].min()-0.1*A) if MODE=="swing" else e-SL*A
        risk=e-stop
        if risk<=0.003*e: continue  # stop too close: costs would dominate
        tgt=e+TP*risk;x=None;why="time"
        for j in range(k+1,k+1+T):
            if lo[j]<=stop: x=stop;why="sl";break
            if hi[j]>=tgt: x=tgt;why="tp";break
        if x is None: x=c[k+T];j=k+T
        rows.append(dict(p=p,t=h.index[i],gross=(x-e)/risk,cost=0.002*e/risk,why=why))
        busy=j
D=pd.DataFrame(rows);D["net"]=D.gross-D.cost
days=(pd.Timestamp(end)-pd.Timestamp(start)).days
print(f"K{K} TP{TP} T{T} {MODE}: {len(D)} tr, {len(D)/days:.1f}/day, win {(D.net>0).mean()*100:.0f}%, gross {D.gross.mean():+.3f} cost {D.cost.mean():.3f} net {D.net.mean():+.3f}")
