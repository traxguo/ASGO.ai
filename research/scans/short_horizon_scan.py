# Short-horizon edge scan, dev 2020-2024, 36 coins, 1h. Mean forward return (%) net of 0.2% round trip.
import glob,numpy as np,pandas as pd
fs=sorted(glob.glob("user_data/data/binance/futures/*-1h-futures.feather"))
btc=pd.read_feather("user_data/data/binance/futures/BTC_USDT_USDT-1h-futures.feather").set_index("date")
bret=btc.close.pct_change()
rows=[]
for f in fs:
    p=f.split("/")[-1].split("_")[0]
    h=pd.read_feather(f).set_index("date"); h=h[(h.index>="2020-01-01")&(h.index<"2025-01-01")]
    if len(h)<2000: continue
    d=pd.read_feather(f.replace("-1h-","-1d-")).set_index("date").close
    e20,e50=d.ewm(span=20,adjust=False).mean(),d.ewm(span=50,adjust=False).mean()
    sc=(np.sign(d-e50)+np.sign(e20-e50)+np.sign(d/d.shift(90)-1)).shift(1)  # last closed day
    h["score"]=sc.reindex(h.index.floor("D")).values
    tr=pd.concat([h.high-h.low,(h.high-h.close.shift()).abs(),(h.low-h.close.shift()).abs()],axis=1).max(axis=1)
    atrp=(tr.rolling(14).mean()/h.close).shift(1)
    r1=h.close.pct_change(); r3=h.close.pct_change(3)
    z3=r3/atrp
    o=h.open.shift(-1)  # enter next open
    fw={H:(h.close.shift(-H)/o-1) for H in (2,4,8)}
    df=pd.DataFrame({"p":p,"hour":h.index.hour,"score":h.score,"z3":z3,"r1":r1,"b1":bret.reindex(h.index).values,**{f"f{H}":fw[H] for H in fw}})
    rows.append(df)
D=pd.concat(rows).dropna()
days=(pd.Timestamp("2025-01-01")-pd.Timestamp("2020-01-01")).days
def rep(name,m,side=1):
    s=D[m]
    print(f"{name:38s} n={len(s):6d} /day={len(s)/days:5.2f} "+" ".join(f"f{H}={side*s[f'f{H}'].mean()*100-0.2:+.3f}%" for H in (2,4,8)))
rep("all long (baseline)",D.z3.notna())
rep("A capitulation z3<=-3, uptrend",(D.z3<=-3)&(D.score>=1))
rep("A2 capitulation z3<=-4, any",(D.z3<=-4))
rep("A3 capitulation z3<=-3, downtrend",(D.z3<=-3)&(D.score<=-1))
rep("E pump z3>=3 uptrend long",(D.z3>=3)&(D.score>=1))
rep("E2 pump z3>=4 short any",(D.z3>=4),-1)
rep("E3 pump z3>=3 downtrend short",(D.z3>=3)&(D.score<=-1),-1)
rep("C BTC +1.5% laggard long",(D.b1>0.015)&(D.r1<0.5*D.b1)&(D.p!="BTC"))
rep("C2 BTC -1.5% laggard short",(D.b1<-0.015)&(D.r1>0.5*D.b1)&(D.p!="BTC"),-1)
g=D.groupby("hour").f2.mean()*100
print("best hours f2 gross %:",g.sort_values().tail(4).round(3).to_dict(),"worst:",g.sort_values().head(3).round(3).to_dict())
print("--- A by year / clustering")
D["t"]=D.index
m=(D.z3<=-3)&(D.score>=1)
s=D[m]
for y,g in s.groupby(s.t.dt.year): print(y,len(g),f"f4={g.f4.mean()*100-0.2:+.3f}%","win%",round((g.f4>0.002).mean()*100))
k=s.groupby("t").f4.mean()
print("distinct hours",len(k),"avg per hour-cluster f4 net",round(k.mean()*100-0.2,3),"median trade f4",round(s.f4.median()*100-0.2,3))
print("worst 1% f4",round(s.f4.quantile(.01)*100,2),"best 1%",round(s.f4.quantile(.99)*100,2))
