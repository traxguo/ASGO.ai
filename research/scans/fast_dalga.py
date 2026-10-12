# "Hizli Dalga": Dalga's idea on 15m. Long when a coin in a daily uptrend (score >= SCORE, daily close > EMA20)
# breaks its last N-candle high (first breakout), entry next 15m open. Exit: stop K*ATR(15m) under entry
# (0 = none, SL checked on lows, filled at stop or gap open), else close after H hours. Cost 0.2% round trip.
# One trade per coin at a time. Prints per-trade mean/median/win, trades/day and per-year means. Dev only by default.
# Usage: python research/scans/fast_dalga.py N H K SCORE [start end]
import sys,json,numpy as np,pandas as pd
N,H,K,SC=int(sys.argv[1]),int(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4])
a,b=(sys.argv[5],sys.argv[6]) if len(sys.argv)>6 else ("2020-03-01","2025-01-01")
pl=[p.split("/")[0] for p in json.load(open("config/pairs_all36.json"))["exchange"]["pair_whitelist"]]
B="user_data/data/binance/futures/";R=[]
for c in pl:
    try:
        k=pd.read_feather(B+f"{c}_USDT_USDT-15m-futures.feather").set_index("date")
        d=pd.read_feather(B+f"{c}_USDT_USDT-1d-futures.feather").set_index("date").close
    except FileNotFoundError: continue
    e20,e50=d.ewm(span=20,adjust=False).mean(),d.ewm(span=50,adjust=False).mean()
    sc=(np.sign(d-e50)+np.sign(e20-e50)+np.sign(d/d.shift(90)-1)).shift(1)  # last closed day only
    above=(d>e20).shift(1)
    day=k.index.floor("D");score=sc.reindex(day).to_numpy();ab=above.reindex(day).to_numpy()
    o,hi,lo,cl=(k[x].to_numpy() for x in ("open","high","low","close"))
    pc=np.r_[np.nan,cl[:-1]];tr=np.maximum(hi-lo,np.maximum(abs(hi-pc),abs(lo-pc)));atr=pd.Series(tr).rolling(14).mean().to_numpy()
    up=pd.Series(hi).rolling(N).max().shift(1).to_numpy();brk=cl>up;first=brk&~np.r_[False,brk[:-1]]
    win=(k.index>=a)&(k.index<b)
    sig=first&(score>=SC)&(ab==True)&win&~np.isnan(atr)
    n=len(cl);h=H*4;busy=-1
    for i in np.where(sig)[0]:
        if i<=busy or i+1+h>=n: continue
        e=o[i+1];st=e-K*atr[i] if K>0 else -1;x=None
        for j in range(i+1,i+1+h):
            if lo[j]<=st: x=min(st,o[j]);break
        if x is None: x=cl[i+h];j=i+h
        R.append((k.index[i+1],c,x/e-1-0.002,(e-st)/e if K>0 else np.nan));busy=j
D=pd.DataFrame(R,columns=["t","c","ret","risk"]);days=(pd.Timestamp(b)-pd.Timestamp(a)).days
yr=D.groupby(D.t.dt.year).ret.mean().mul(100).round(3).to_dict()
print(f"N{N} H{H} K{K} S{SC}: {len(D)} tr ({len(D)/days:.1f}/day), mean {D.ret.mean()*100:+.3f}%, median {D.ret.median()*100:+.3f}%, "
      f"win {(D.ret>0).mean()*100:.0f}%, stop dist {D.risk.median()*100:.2f}%, years {yr}")
