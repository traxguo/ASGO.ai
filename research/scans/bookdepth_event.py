# Event sim: "bid wall surge" long. Signal when dimb5 (imb5 minus its 1-day mean) exceeds its
# rolling 30-day 99th percentile (threshold uses past data only). Enter at close of signal bar,
# exit after H hours at close. One trade per coin at a time. Cost 0.2% round trip.
import sys,numpy as np,pandas as pd
start,end=sys.argv[1],sys.argv[2]; Q=float(sys.argv[3]) if len(sys.argv)>3 else 0.99
B="user_data/data/bookdepth/"; out=[]
for c in ("BTC","ETH","SOL"):
    k=pd.read_feather(B+f"{c}-5m-klines.feather").set_index("date")
    d=pd.read_feather(B+f"{c}-5m.feather").set_index("date")
    df=k.join(d,how="left")
    x=df.imb5-df.imb5.rolling(288,min_periods=200).mean()
    thr=x.rolling(288*30,min_periods=288*10).quantile(Q).shift(1)
    sig=(x>thr)
    m=(df.index>=start)&(df.index<end)
    cl=df.close.values;idx=np.where(sig.values&m)[0]
    busy=-1
    for i in idx:
        if i<=busy: continue
        for H in (48,):
            if i+H<len(cl): out.append((c,df.index[i],(cl[i+H]/cl[i]-1)*100,(df.close.iloc[i+12]/cl[i]-1)*100,(df.close.iloc[i+24]/cl[i]-1)*100))
        busy=i+48
T=pd.DataFrame(out,columns=["c","t","f4h","f1h","f2h"])
days=(pd.Timestamp(end)-pd.Timestamp(start)).days
print(f"{start}..{end} Q={Q} trades={len(T)} /day={len(T)/days:.2f}  net(4h)={T.f4h.mean()-0.2:+.3f}%  net(2h)={T.f2h.mean()-0.2:+.3f}% net(1h)={T.f1h.mean()-0.2:+.3f}% win4h={(T.f4h>0.2).mean()*100:.0f}%")
for c,g in T.groupby("c"): print(" ",c,len(g),f"net4h={g.f4h.mean()-0.2:+.3f}%")
for y,g in T.groupby(T.t.dt.to_period("Q")): print(" ",y,len(g),f"net4h={g.f4h.mean()-0.2:+.3f}%")
