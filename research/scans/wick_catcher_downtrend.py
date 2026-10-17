# Downtrend variant of the wick catcher: same code, but only coins in a daily DOWNtrend (score <= -SCORE and
# close below EMA20). Tested with deep limits (6-10% under the hour open) = capitulation-wick buyer ("Derin Fitil").
# "Fitil avcisi" (wick catcher): built against every failure seen so far.
# - costs ate short holds -> enter with a resting LIMIT (maker) far below price, so one fill = a large discount
# - limit fills were adversely selected near price -> only deep levels (X% under), only in daily uptrends,
#   where panic wicks tend to snap back (the Tasfiye effect, without needing OI data)
# - fixed tight stops cut trades in noise -> no stop inside the hold, time exit after H hours (or TP limit +Y%)
# Each hour, for coins with daily score >= SCORE and daily close > EMA20 (last closed day), a buy limit sits at
# hour-open*(1-X). Fill only if the 15m low trades at least FILLPAD below it (conservative). Exit: TP limit at
# entry*(1+Y) (maker) checked on 15m highs, else market close after H hours. One trade per coin at a time.
# Costs: maker 0.02% in, TP exit maker 0.02% or time exit taker 0.06% + 0.05% slippage.
# Usage: python research/scans/wick_catcher.py X Y H SCORE [start end]
import sys,json,numpy as np,pandas as pd
X,Y,H,SC=float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]);FILLPAD=0.001
a,b=(sys.argv[5],sys.argv[6]) if len(sys.argv)>6 else ("2020-03-01","2025-01-01")
PF=__import__("os").environ.get("PAIRS","config/pairs_all36.json")
pl=[p.split("/")[0] for p in json.load(open(PF))["exchange"]["pair_whitelist"]]
B="user_data/data/binance/futures/";R=[]
import os
SL=float(os.environ.get("SL","0"))  # catastrophe stop under entry (0 = none), taker exit
GUARD=float(os.environ.get("GUARD","0"))  # skip if BTC fell more than GUARD in the hour so far (market cascade)
MAXNEW=int(os.environ.get("MAXNEW","99"))  # at most this many new fills per hour across coins
bk=pd.read_feather(B+"BTC_USDT_USDT-15m-futures.feather").set_index("date")
for c in pl:
    try:
        k=pd.read_feather(B+f"{c}_USDT_USDT-15m-futures.feather").set_index("date")
        d=pd.read_feather(B+f"{c}_USDT_USDT-1d-futures.feather").set_index("date").close
    except FileNotFoundError: continue
    e20,e50=d.ewm(span=20,adjust=False).mean(),d.ewm(span=50,adjust=False).mean()
    sc=(np.sign(d-e50)+np.sign(e20-e50)+np.sign(d/d.shift(90)-1)).shift(1);ab=(d>e20).shift(1)
    day=k.index.floor("D");score=sc.reindex(day).to_numpy();abv=ab.reindex(day).to_numpy()
    o,hi,lo,cl=(k[x].to_numpy() for x in ("open","high","low","close"));idx=k.index;n=len(cl)
    ok=(score<=-SC)&(abv==False)&(idx>=a)&(idx<b)&(idx.minute==0);busy=-1;h=H*4
    for i in np.where(ok)[0]:
        if i<=busy or i+4+h>=n: continue
        lim=o[i]*(1-X);f=None
        for j in range(i,i+4):  # the order rests for one hour
            if lo[j]<=lim*(1-FILLPAD): f=j;break
        if f is None: continue
        if GUARD>0:
            t0=idx[i];bo=bk.open.get(t0);bl=bk.low.loc[t0:idx[f]].min() if bo is not None else None
            if bo is not None and bl<=bo*(1-GUARD): continue
        e=min(lim,o[f]);tp=e*(1+Y) if Y>0 else np.inf;st=e*(1-SL) if SL>0 else -1;x=None
        if SL>0 and cl[f]<=st: x=cl[f];j=f;cost=0.0002+0.0011  # fell through the stop inside the fill candle
        for j in ([] if x is not None else range(f+1,f+1+h)):
            if lo[j]<=st: x=min(st,o[j]);cost=0.0002+0.0011;break
            if hi[j]>=tp: x=tp;cost=0.0004;break
        if x is None: x=cl[f+h];j=f+h;cost=0.0002+0.0011
        R.append((idx[f],c,x/e-1-cost,idx[j]+pd.Timedelta(minutes=15)));busy=j
D=pd.DataFrame(R,columns=["t","c","ret","t_out"]).sort_values("t").reset_index(drop=True)
D=D[D.groupby(D.t.dt.floor("h")).cumcount()<MAXNEW].reset_index(drop=True);days=(pd.Timestamp(b)-pd.Timestamp(a)).days
yr=D.groupby(D.t.dt.year).ret.mean().mul(100).round(3).to_dict()
top=D.groupby(D.t.dt.floor("D")).ret.sum().nlargest(5).index;Rx=D[~D.t.dt.floor("D").isin(top)]
print(f"X{X} Y{Y} H{H} S{SC}: {len(D)} tr ({len(D)/days:.2f}/day), mean {D.ret.mean()*100:+.3f}%, median {D.ret.median()*100:+.3f}%, "
      f"win {(D.ret>0).mean()*100:.0f}%, w/o top5 days {Rx.ret.mean()*100:+.3f}%, years {yr}")
# Portfolio: at most MAXO open trades, each gets equity/MAXO (1x in total), fills taken in time order.
import os
MAXO=int(os.environ.get("MAXO","5"));open_=[];T=[]
for r in D.itertuples():
    open_=[t for t in open_ if t>r.t]
    if len(open_)<MAXO: open_.append(r.t_out);T.append(r)
T=pd.DataFrame(T);daily=T.groupby(T.t_out.dt.floor("D")).ret.sum()/MAXO;e=(1+daily).cumprod()
print(f"  portfolio max {MAXO}: {len(T)} tr ({len(T)/days:.2f}/day), mean {T.ret.mean()*100:+.3f}%, equity {(e.iloc[-1]-1)*100:+.1f}%, "
      f"maxDD {((e/e.cummax())-1).min()*100:.1f}%, worst day {daily.min()*100:.1f}%, by year {(daily.groupby(daily.index.year).sum()*100).round(1).to_dict()}")
