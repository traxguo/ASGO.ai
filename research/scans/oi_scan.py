# Open-interest / positioning scan (Binance 5m "metrics", 2022-01..2026-03) for short holds.
# At each 15m close t we use metrics stamped <= t-5min (one snapshot of safety margin) and the 15m candles.
# Candidate events (both sides), forward return from the next 15m open, held H hours, cost 0.2% round trip:
#   flush   : OI falls >= X% in 1h while price falls >= 1.5% (long liquidation)  -> long (bounce)
#   squeeze : OI falls >= X% in 1h while price rises >= 1.5% (short covering)    -> short (fade)
#   crowd_l : OI rises >= X% in 1h while price rises >= 1.5% (new longs pile in) -> long (follow) / short (fade)
#   crowd_s : OI rises >= X% in 1h while price falls >= 1.5% (new shorts)        -> short (follow) / long (fade)
#   taker   : 1h taker buy/sell ratio z-score (vs 7 days) >= 2.5 -> follow
# Prints mean net % per trade for dev (2022-2024) and validation (2025-01..2026-03), non-overlapping per coin.
import sys,numpy as np,pandas as pd
coins=sys.argv[1:]
B="user_data/data/binance/futures/";Mt="user_data/data/metrics/"
res=[]
for c in coins:
    k=pd.read_feather(B+f"{c}_USDT_USDT-15m-futures.feather").set_index("date")
    m=pd.read_feather(Mt+f"{c}-5m.feather").set_index("date").sort_index()
    t_close=k.index+pd.Timedelta(minutes=15)-pd.Timedelta(minutes=5)
    mm=m.reindex(t_close,method="ffill");mm.index=k.index
    oi=mm.sum_open_interest;tk=mm.sum_taker_long_short_vol_ratio
    oi1=oi/oi.shift(4)-1;r1=k.close/k.close.shift(4)-1
    tk1=np.log(tk).rolling(12).mean();z=(tk1-tk1.rolling(672).mean())/tk1.rolling(672).std()
    o=k.open.to_numpy();cl=k.close.to_numpy();n=len(cl)
    per=np.where(k.index<"2022-01-02","x",np.where(k.index<"2025-01-01","dev",np.where(k.index<"2026-04-01","val","x")))
    for X in (0.02,0.04):
        ev={"flush>long":((oi1<=-X)&(r1<=-0.015),1),"squeeze>short":((oi1<=-X)&(r1>=0.015),-1),
            "crowdL>long":((oi1>=X)&(r1>=0.015),1),"crowdL>short":((oi1>=X)&(r1>=0.015),-1),
            "crowdS>short":((oi1>=X)&(r1<=-0.015),-1),"crowdS>long":((oi1>=X)&(r1<=-0.015),1)}
        if X==0.02: ev.update({"taker+>long":((z>=2.5),1),"taker->short":((z<=-2.5),-1),"taker+>short":((z>=2.5),-1),"taker->long":((z<=-2.5),1)})
        for name,(sig,sd) in ev.items():
            idx=np.where(sig.fillna(False).to_numpy())[0]
            for H in (1,2,3):
                busy=-1;h=H*4
                for i in idx:
                    if i<=busy or i+1+h>=n or per[i]=="x": continue
                    res.append((name,X,H,per[i],(sd*(cl[i+h]/o[i+1]-1)-0.002)*100));busy=i+h
R=pd.DataFrame(res,columns=["ev","X","H","per","net"])
T=R.groupby(["ev","X","H","per"]).net.agg(["mean","count"]).unstack("per")
T.columns=[f"{a}_{b}" for a,b in T.columns];print(T.round(3).to_string())
