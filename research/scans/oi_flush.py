# Focus on the "flush" event from oi_scan.py: OI falls >= X in 1h while price falls >= P in 1h -> long at next 15m open,
# hold H hours. Reports trade list stats per period: mean, median, win rate, mean without the best 5 trades, by year.
import sys,numpy as np,pandas as pd
X,P,H=float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3]);coins=sys.argv[4:]
B="user_data/data/binance/futures/";Mt="user_data/data/metrics/";rows=[]
for c in coins:
    k=pd.read_feather(B+f"{c}_USDT_USDT-15m-futures.feather").set_index("date")
    m=pd.read_feather(Mt+f"{c}-5m.feather").set_index("date").sort_index()
    mm=m.reindex(k.index+pd.Timedelta(minutes=10),method="ffill");mm.index=k.index
    oi1=mm.sum_open_interest/mm.sum_open_interest.shift(4)-1;r1=k.close/k.close.shift(4)-1
    sig=((oi1<=-X)&(r1<=-P)).fillna(False).to_numpy()
    o=k.open.to_numpy();cl=k.close.to_numpy();n=len(cl);busy=-1;h=H*4
    for i in np.where(sig)[0]:
        if i<=busy or i+1+h>=n or k.index[i]<pd.Timestamp("2022-01-02",tz="UTC") or k.index[i]>=pd.Timestamp("2026-04-01",tz="UTC"): continue
        rows.append(dict(c=c,t=k.index[i],net=(cl[i+h]/o[i+1]-1-0.002)*100));busy=i+h
D=pd.DataFrame(rows);D["per"]=np.where(D.t<"2025-01-01","dev","val");D["yr"]=D.t.dt.year
for p,g in D.groupby("per"):
    s=g.net.sort_values()
    print(f"{p}: n {len(g)}, mean {g.net.mean():+.3f}%, median {g.net.median():+.3f}%, win {(g.net>0).mean()*100:.0f}%, mean w/o best5 {s.iloc[:-5].mean():+.3f}%")
print(D.groupby("yr").net.agg(["count","mean","median"]).round(3).to_string())
print("top days:",D.groupby(D.t.dt.date).net.sum().sort_values().tail(5).round(2).to_dict())
