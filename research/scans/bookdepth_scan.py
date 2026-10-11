# Order-book (bookDepth) imbalance vs forward returns, dev 2023-01..2024-12, BTC/ETH/SOL, 5m.
# Alignment: bookDepth bucket T and kline T both cover [T, T+5m) -> known at T+5m.
# Entry = close of kline T. Forward return to close of kline T+H. Gross %, cost 0.2% round trip.
import sys,numpy as np,pandas as pd
start,end=(sys.argv[1],sys.argv[2]) if len(sys.argv)>2 else ("2023-01-01","2025-01-01")
B="user_data/data/bookdepth/"
rows=[]
for c in ("BTC","ETH","SOL"):
    k=pd.read_feather(B+f"{c}-5m-klines.feather").set_index("date")
    d=pd.read_feather(B+f"{c}-5m.feather").set_index("date")
    df=k.join(d,how="left");df=df[(df.index>=start)&(df.index<end)]
    f=pd.DataFrame(index=df.index);f["c"]=c
    f["imb1"]=df.imb1;f["imb5"]=df.imb5
    f["imb5_1h"]=df.imb5.rolling(12).mean();f["imb1_1h"]=df.imb1.rolling(12).mean()
    f["dimb5"]=df.imb5-df.imb5.rolling(288).mean()          # vs 1-day mean
    f["taker_1h"]=df.taker_buy.rolling(12).sum()/df.volume.rolling(12).sum()
    f["ret_1h"]=df.close/df.close.shift(12)-1
    for H,n in (("1h",12),("2h",24),("4h",48)): f["f"+H]=(df.close.shift(-n)/df.close-1)*100
    rows.append(f)
D=pd.concat(rows).dropna()
print(start,end,"rows",len(D))
for feat in ("imb1","imb5","imb1_1h","imb5_1h","dimb5","taker_1h","ret_1h"):
    D["q"]=D.groupby("c")[feat].transform(lambda s:pd.qcut(s.rank(method="first"),10,labels=False))
    g=D.groupby("q")[["f1h","f2h","f4h"]].mean()
    top,bot=g.loc[9],g.loc[0]
    ic=D[[feat,"f2h"]].corr(method="spearman").iloc[0,1]
    print(f"{feat:9s} IC(2h)={ic:+.3f}  top-dec "+" ".join(f"{h}={top[h]:+.3f}" for h in g.columns)+"  bot-dec "+" ".join(f"{h}={bot[h]:+.3f}" for h in g.columns))
print("--- tails and combos (mean fwd %, count/day across 3 coins, non-overlap not enforced)")
days=(pd.Timestamp(end)-pd.Timestamp(start)).days
for feat in ("imb5","dimb5","imb5_1h"):
    r=D.groupby("c")[feat].rank(pct=True)
    for lo,hi in ((0.99,1.01),(0.0,0.01)):
        s=D[(r>=lo)&(r<hi)]
        print(f"{feat} pct[{lo},{hi}) n/day={len(s)/days:5.1f} "+" ".join(f"{h}={s[h].mean():+.3f}" for h in ("f1h","f2h","f4h")))
r5=D.groupby("c").imb5.rank(pct=True);rr=D.groupby("c").ret_1h.rank(pct=True)
for nm,m in (("dip+bid wall (ret<10%,imb5>90%)",(rr<.1)&(r5>.9)),("pump+ask wall (ret>90%,imb5<10%)",(rr>.9)&(r5<.1))):
    s=D[m];print(f"{nm} n/day={len(s)/days:5.1f} "+" ".join(f"{h}={s[h].mean():+.3f}" for h in ("f1h","f2h","f4h")))
