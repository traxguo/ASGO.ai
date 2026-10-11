# "Firsat" rule sim, 1h, 36 coins: uptrend (score>=1) + 3h drop <= -3 ATR -> long next open,
# stop entry-2ATR, target entry+K*ATR, time exit after H candles. Cost c per side. One trade per coin at a time.
import glob,sys,numpy as np,pandas as pd
start,end=sys.argv[1],sys.argv[2]
res=[]
for f in sorted(glob.glob("user_data/data/binance/futures/*-1h-futures.feather")):
    h=pd.read_feather(f).set_index("date"); h=h[(h.index>=start)&(h.index<end)]
    if len(h)<500: continue
    d=pd.read_feather(f.replace("-1h-","-1d-")).set_index("date").close
    e20,e50=d.ewm(span=20,adjust=False).mean(),d.ewm(span=50,adjust=False).mean()
    sc=(np.sign(d-e50)+np.sign(e20-e50)+np.sign(d/d.shift(90)-1)).shift(1)
    score=sc.reindex(h.index.floor("D")).values
    tr=pd.concat([h.high-h.low,(h.high-h.close.shift()).abs(),(h.low-h.close.shift()).abs()],axis=1).max(axis=1)
    atr=tr.rolling(14).mean().shift(1).values
    c=h.close.values; o=h.open.values; hi=h.high.values; lo=h.low.values; t=h.index
    z3=(c/np.roll(c,3)-1)/(atr/c)
    i=20; n=len(h)
    while i<n-10:
        if score[i]>=1 and z3[i]<=-3 and atr[i]>0:
            e=o[i+1]; a=atr[i]; stop=e-2*a
            for K,H in ((2,4),):
                tgt=e+K*a; r=None
                for j in range(i+1,min(i+1+H,n)):
                    if lo[j]<=stop: r=-1.0; break
                    if hi[j]>=tgt: r=K/2; break
                if r is None: r=(c[min(i+H,n-1)]-e)/(2*a); j=min(i+H,n-1)
                res.append((t[i],r,2*a/e))
            i=j+1
        else: i+=1
R=pd.DataFrame(res,columns=["t","r","stop"]).set_index("t")
days=(pd.Timestamp(end)-pd.Timestamp(start)).days
for cost in (0.001,0.0003):
    net=R.r-2*cost/R.stop
    print(f"cost/side {cost}: n={len(R)} /day={len(R)/days:.2f} gross={R.r.mean():+.3f}R net={net.mean():+.3f}R win%={(net>0).mean()*100:.0f} median stop {R.stop.median()*100:.2f}%")
    print("  by year:",{y:round(g.mean(),3) for y,g in net.groupby(net.index.year)})
