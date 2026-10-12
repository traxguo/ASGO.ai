# MAKER variant of kinetic_pullback.py: limit entry at the signal close (+OFF fraction, the favourable side),
# valid W candles, filled only if price trades THROUGH the limit by 0.02% (queue-safe). Optional fixed take-profit
# as a resting limit (maker). Fees: maker 0.02%, taker 0.06% + 0.03% slippage on market exits (Bitget base tier).
# Args: pairs start end out|- TP_ATR(0=original trailing exits) OFF W
# "Kinetik Geri Cekilme" (owner-supplied spec, 2026-10-12): 1h trend filter + 15m pullback / StochRSI turn.
# Event simulation on 15m candles, long and short reported separately. Cost 0.2% round trip.
# 1h values come from the last CLOSED 1h candle at the 15m candle's close (no lookahead).
# Entry: next 15m open. Stop: entry -/+ 2.5 ATR15 (capped at 5%). Trailing: after +1.5% best price, trail 0.5%.
# Custom exits at 15m close: dead trade (>=16 candles, 0 <= pnl < 0.5%), momentum loss (pnl >= 1.5%, RSI was >70 now <60),
# panic (close beyond EMA50 with volume > SMA20 while pnl >= -1%). Hard cap 7 days.
import sys,json,numpy as np,pandas as pd
pf,start,end=sys.argv[1],sys.argv[2],sys.argv[3]
out=sys.argv[4] if len(sys.argv)>4 and sys.argv[4]!="-" else None
TPA=float(sys.argv[5]);OFF=float(sys.argv[6]);W=int(sys.argv[7]);PANIC=False
MAKER,TAKER=0.0002,0.0009
B="user_data/data/binance/futures/"
pl=[p.split("/")[0] for p in json.load(open(pf))["exchange"]["pair_whitelist"]]
def rsi(c,n=14):
    d=c.diff();u=d.clip(lower=0).ewm(alpha=1/n,adjust=False).mean();v=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean()
    return 100-100/(1+u/v)
def atr(h,n=14):
    pc=h.close.shift();tr=pd.concat([h.high-h.low,(h.high-pc).abs(),(h.low-pc).abs()],axis=1).max(axis=1)
    return tr.ewm(alpha=1/n,adjust=False).mean(),tr
def adx(h,n=14):
    up=h.high.diff();dn=-h.low.diff()
    pdm=np.where((up>dn)&(up>0),up,0.0);mdm=np.where((dn>up)&(dn>0),dn,0.0)
    a,_=atr(h,n)
    pdi=100*pd.Series(pdm,index=h.index).ewm(alpha=1/n,adjust=False).mean()/a
    mdi=100*pd.Series(mdm,index=h.index).ewm(alpha=1/n,adjust=False).mean()/a
    dx=100*(pdi-mdi).abs()/(pdi+mdi)
    return dx.ewm(alpha=1/n,adjust=False).mean()
rows=[]
for p in pl:
    try:
        m=pd.read_feather(B+f"{p}_USDT_USDT-15m-futures.feather").set_index("date")
        H=pd.read_feather(B+f"{p}_USDT_USDT-1h-futures.feather").set_index("date")
    except FileNotFoundError: continue
    H["e50"]=H.close.ewm(span=50,adjust=False).mean();H["e200"]=H.close.ewm(span=200,adjust=False).mean();H["adx"]=adx(H)
    H["up"]=(H.close>H.e50)&(H.e50>H.e200)&(H.adx>25);H["dn"]=(H.close<H.e50)&(H.e50<H.e200)&(H.adx>25)
    key=(m.index+pd.Timedelta(minutes=15)).floor("h")-pd.Timedelta(hours=1)  # last closed 1h candle
    up=H.up.reindex(key).fillna(False).to_numpy();dn=H.dn.reindex(key).fillna(False).to_numpy()
    c=m.close;e50=c.ewm(span=50,adjust=False).mean();r=rsi(c);a,_=atr(m)
    st=(r-r.rolling(14).min())/(r.rolling(14).max()-r.rolling(14).min())*100
    K=st.rolling(3).mean();D=K.rolling(3).mean();vs=m.volume.rolling(20).mean()
    red=(m.close<m.open);grn=~red
    prev_red_vol=m.volume.where(red).shift().ffill();prev_grn_vol=m.volume.where(grn).shift().ffill()
    volok_l=(m.volume>prev_red_vol)|(m.volume>vs);volok_s=(m.volume>prev_grn_vol)|(m.volume>vs)
    near_l=(m.low.rolling(5).min()<=e50*1.002);near_s=(m.high.rolling(5).max()>=e50*0.998)
    kx_up=(K>D)&(K.shift()<=D.shift())&(K.rolling(3).min()<20)
    kx_dn=(K<D)&(K.shift()>=D.shift())&(K.rolling(3).max()>80)
    L=up&near_l.to_numpy()&kx_up.to_numpy()&r.between(40,55).to_numpy()&volok_l.to_numpy()
    S=dn&near_s.to_numpy()&kx_dn.to_numpy()&r.between(45,60).to_numpy()&volok_s.to_numpy()
    win=(m.index>=start)&(m.index<end)
    o,hi,lo,cl,vv=(m[k].to_numpy() for k in ("open","high","low","close","volume"))
    E,RR,A,VS=e50.to_numpy(),r.to_numpy(),a.to_numpy(),vs.to_numpy();n=len(cl);busy=-1
    for i in np.where((L|S)&win)[0]:
        if i<=busy or i+W+2>=n: continue
        sd=1 if L[i] else -1;lim=cl[i]*(1-sd*OFF)
        k=next((j for j in range(i+1,i+1+W) if (sd==1 and lo[j]<lim*(1-0.0002)) or (sd==-1 and hi[j]>lim*(1+0.0002))),None)
        if k is None: busy=i+W;continue
        e=lim;Ak=A[i]
        stop=e-sd*min(2.5*Ak,0.05*e);risk=abs(e-stop);best=e;was70=False;x=None;why="cap";fee_out=TAKER
        tgt=e+sd*TPA*Ak if TPA>0 else None
        for j in range(k,min(k+672,n)):
            if j>k or True:
                trail=best*(1-sd*0.005) if (tgt is None and sd*(best/e-1)>=0.015) else None
                lvl=stop if trail is None else (max(stop,trail) if sd==1 else min(stop,trail))
                if j>k and ((sd==1 and lo[j]<=lvl) or (sd==-1 and hi[j]>=lvl)):
                    x=min(lvl,o[j]) if sd==1 else max(lvl,o[j]);why="trail" if trail is not None and lvl==trail else "sl";break
                if j==k and ((sd==1 and cl[j]<=stop) or (sd==-1 and cl[j]>=stop)):
                    x=cl[j];why="sl";break  # fill candle: only its close is known to be after the fill
                if tgt is not None and j>k and ((sd==1 and hi[j]>tgt*(1+0.0002)) or (sd==-1 and lo[j]<tgt*(1-0.0002))):
                    x=tgt;why="tp";fee_out=MAKER;break
            best=max(best,hi[j]) if sd==1 else min(best,lo[j])
            pnl=sd*(cl[j]/e-1)
            if sd*(RR[j]-50)>20: was70=True
            held=j-k+1
            if held>=16 and 0<=pnl<0.005: x=cl[j];why="dead";break
            if tgt is None and pnl>=0.015 and was70 and sd*(RR[j]-50)<10: x=cl[j];why="momentum";break
        if x is None: x=cl[j]
        c_pct=MAKER+fee_out
        rows.append(dict(p=p,t=m.index[i],side="long" if sd==1 else "short",gross=sd*(x-e)/risk,cost=c_pct*e/risk,
                         pct=(sd*(x/e-1)-c_pct)*100,hours=(j-k+1)/4,why=why))
        busy=j
Dd=pd.DataFrame(rows);Dd["net"]=Dd.gross-Dd.cost
days=(pd.Timestamp(end)-pd.Timestamp(start)).days
for s,g in Dd.groupby("side"):
    print(f"{start}..{end} {s}: {len(g)} tr ({len(g)/days:.1f}/day), win {(g.net>0).mean()*100:.0f}%, net {g.net.mean():+.3f}R "
          f"(gross {g.gross.mean():+.3f}, cost {g.cost.mean():.3f}), avg {g.pct.mean():+.3f}%/tr, hold {g.hours.median():.1f}h, "
          f"exits {g.why.value_counts(normalize=True).round(2).to_dict()}")
if out: Dd.to_feather(out)
