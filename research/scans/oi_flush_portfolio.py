# Tasfiye portfolio test: OI flush long on many coins with a stop, a cap on open trades and an equity curve.
# Signal as oi_flush.py. Entry next 15m open. Exit: stop (fixed % under entry, 0 = none; checked on 15m lows,
# fill at the stop or the open if it gapped), else close after H hours. Cost 0.2% round trip.
# Each trade gets equity/MAXO notional (no leverage beyond 1x in total). Reports per period: trades, mean %,
# win, equity return, max drawdown, worst day, share of days with >=1 trade.
import sys,numpy as np,pandas as pd
X,P,H,STOP,MAXO=float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4]),int(sys.argv[5]);coins=sys.argv[6:]
B="user_data/data/binance/futures/";Mt="user_data/data/metrics/";cand=[]
for c in coins:
    try:
        k=pd.read_feather(B+f"{c}_USDT_USDT-15m-futures.feather").set_index("date")
        m=pd.read_feather(Mt+f"{c}-5m.feather").set_index("date").sort_index()
    except FileNotFoundError: continue
    mm=m.reindex(k.index+pd.Timedelta(minutes=10),method="ffill");mm.index=k.index
    oi1=mm.sum_open_interest/mm.sum_open_interest.shift(4)-1;r1=k.close/k.close.shift(4)-1
    sig=((oi1<=-X)&(r1<=-P)).fillna(False).to_numpy()
    o,lo,cl=k.open.to_numpy(),k.low.to_numpy(),k.close.to_numpy();n=len(cl);h=H*4;busy=-1
    for i in np.where(sig)[0]:
        if i<=busy or i+1+h>=n: continue
        e=o[i+1];x=None;st=e*(1-STOP) if STOP>0 else -1
        for j in range(i+1,i+1+h):
            if lo[j]<=st: x=min(st,o[j]);why="sl";break
        if x is None: x=cl[i+h];j=i+h;why="time"
        cand.append(dict(c=c,t_in=k.index[i+1],t_out=k.index[j]+pd.Timedelta(minutes=15),ret=x/e-1-0.002,why=why));busy=j
C=pd.DataFrame(cand).sort_values("t_in").reset_index(drop=True)
C=C[(C.t_in>="2022-01-02")&(C.t_in<"2026-04-01")]
for per,(a,b) in {"dev":("2022-01-02","2025-01-01"),"val":("2025-01-01","2026-04-01")}.items():
    g=C[(C.t_in>=a)&(C.t_in<b)];eq=1.0;open_=[];taken=[];curve=[]
    for r in g.itertuples():
        open_=[t for t in open_ if t>r.t_in]
        if len(open_)>=MAXO: continue
        open_.append(r.t_out);taken.append(r)
    T=pd.DataFrame(taken);T["pnl"]=T.ret/MAXO
    daily=T.groupby(T.t_out.dt.floor("D")).pnl.sum()
    e=(1+daily).cumprod();dd=(e/e.cummax()-1).min()
    days=(pd.Timestamp(b)-pd.Timestamp(a)).days
    print(f"{per} stop {STOP:.0%} maxopen {MAXO}: {len(T)} tr ({len(T)/days:.2f}/day), mean {T.ret.mean()*100:+.3f}%, "
          f"win {(T.ret>0).mean()*100:.0f}%, stops {(T.why=='sl').mean()*100:.0f}%, equity {(e.iloc[-1]-1)*100:+.1f}%, "
          f"maxDD {dd*100:.1f}%, worst day {daily.min()*100:.1f}%, trade days {T.t_in.dt.date.nunique()/days*100:.0f}%")
