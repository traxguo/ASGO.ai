# OI / long-short / taker-ratio features vs forward 4h return.
# 2026-10-11: the first version shifted the hourly metrics one hour too early, so each
# feature saw ~55 minutes of the future (lookahead). Fixed below; with the fix the edge is gone. Dev 2022-2024, val 2025-01..2026-03.
import glob,zipfile,io,numpy as np,pandas as pd
coins="BTC ETH SOL XRP BNB DOGE ADA LINK AVAX LTC DOT TRX".split()
out=[]
for c in coins:
    parts=[]
    for z in sorted(glob.glob(f"/tmp/claude-0/metrics/{c}USDT-metrics-*.zip")):
        try:
            with zipfile.ZipFile(z) as f: parts.append(pd.read_csv(f.open(f.namelist()[0])))
        except Exception: pass
    m=pd.concat(parts); m["t"]=pd.to_datetime(m.create_time,utc=True); m=m.set_index("t").sort_index()
    m=m[~m.index.duplicated()]
    for k in ["sum_open_interest","sum_toptrader_long_short_ratio","count_long_short_ratio","sum_taker_long_short_vol_ratio"]:
        m[k]=pd.to_numeric(m[k],errors="coerce")
    h=m.resample("1h").last()  # value known at end of hour
    taker=m.sum_taker_long_short_vol_ratio.resample("1h").mean()
    px=pd.read_feather(f"user_data/data/binance/futures/{c}_USDT_USDT-1h-futures.feather").set_index("date")
    # features use info up to hour close; label h stamps hour start -> shift so feature at index t is known at close of candle t
    pass  # FIXED: resample label H already holds values known by the close of candle H
    df=pd.DataFrame(index=px.index)
    oi=h.sum_open_interest.reindex(df.index)
    df["oi4"]=oi.pct_change(4); df["oi24"]=oi.pct_change(24)
    for k,n in (("sum_toptrader_long_short_ratio","top"),("count_long_short_ratio","glob")):
        s=h[k].reindex(df.index); df[n+"_z"]=(s-s.rolling(24*30).mean())/s.rolling(24*30).std()
    df["taker"]=taker.reindex(df.index).rolling(4).mean()
    df["r4"]=px.close.pct_change(4)
    df["f4"]=px.close.shift(-4)/px.open.shift(-1)-1
    df["c"]=c
    out.append(df.dropna())
D=pd.concat(out)
dev=D[(D.index>="2022-01-01")&(D.index<"2025-01-01")]; val=D[(D.index>="2025-01-01")&(D.index<"2026-04-01")]
for feat in ["oi4","oi24","top_z","glob_z","taker"]:
    q=dev[feat].quantile([.05,.95]).values
    res=[]
    for name,S in (("dev",dev),("val",val)):
        lo=S[S[feat]<=q[0]].f4.mean()*100; hi=S[S[feat]>=q[1]].f4.mean()*100; al=S.f4.mean()*100
        res.append(f"{name}: low5% {lo:+.3f} high5% {hi:+.3f} all {al:+.3f}")
    print(f"{feat:7s}", " | ".join(res))
# combos: price drop + OI drop (long liquidation flush) / price up + OI up
for name,S in (("dev",dev),("val",val)):
    qr=dev.r4.quantile([.05,.95]).values; qo=dev.oi4.quantile([.1,.9]).values
    a=S[(S.r4<=qr[0])&(S.oi4<=qo[0])].f4; b=S[(S.r4>=qr[1])&(S.oi4>=qo[1])].f4; e=S[(S.r4<=qr[0])&(S.oi4>=qo[1])].f4
    print(name,f"flush(drop+OI down) n={len(a)} f4={a.mean()*100:+.3f} | pump+OI up n={len(b)} f4={b.mean()*100:+.3f} | drop+OI up n={len(e)} f4={e.mean()*100:+.3f}")
print("--- combos (thresholds from dev)")
qg=dev.glob_z.quantile([.2,.8]).values; qt=dev.taker.quantile([.1,.9]).values
qr=dev.r4.quantile([.05,.95]).values; qo=dev.oi4.quantile([.1,.9]).values
for name,S in (("dev",dev),("val",val)):
    days=(S.index.max()-S.index.min()).days
    L=S[(S.r4>=qr[1])&(S.oi4>=qo[1])&(S.glob_z<=qg[1])].f4
    Sh=S[(S.taker<=qt[0])&(S.glob_z>=qg[1])].f4
    L2=S[(S.taker>=qt[1])&(S.glob_z<=qg[0])].f4
    print(name,f"LONG pump+OIup+not-crowded n={len(L)} /day={len(L)/days:.2f} f4={L.mean()*100:+.3f} win={(L>0).mean():.2f}",
          f"| SHORT sellers+crowded-long n={len(Sh)} /day={len(Sh)/days:.2f} f4={-Sh.mean()*100:+.3f} win={(Sh<0).mean():.2f}",
          f"| LONG buyers+crowded-short n={len(L2)} f4={L2.mean()*100:+.3f}")
print("--- trade sim: next open entry, stop 1.5 ATR, exit after 4h, one trade per coin")
import sys
TH=dict(qg=qg[1],qt=qt[0],qr=qr[1],qo=qo[1]); print({k:round(float(v),5) for k,v in TH.items()})
def sim(S,cost):
    res=[]
    for c,g in S.groupby("c"):
        px=pd.read_feather(f"user_data/data/binance/futures/{c}_USDT_USDT-1h-futures.feather").set_index("date").reindex(g.index)
        tr=pd.concat([px.high-px.low,(px.high-px.close.shift()).abs(),(px.low-px.close.shift()).abs()],axis=1).max(axis=1)
        atr=tr.rolling(14).mean().values; o,h,l,cl=px.open.values,px.high.values,px.low.values,px.close.values
        sh=((g.taker<=TH["qt"])&(g.glob_z>=TH["qg"])).values
        lg=((g.r4>=TH["qr"])&(g.oi4>=TH["qo"])&(g.glob_z<=TH["qg"])).values
        i=20;n=len(g)
        while i<n-6:
            side=-1 if sh[i] else (1 if lg[i] else 0)
            if side==0 or not atr[i]>0: i+=1; continue
            e=o[i+1]; risk=1.5*atr[i]; stop=e-side*risk; r=None
            for j in range(i+1,i+5):
                if (side==1 and l[j]<=stop) or (side==-1 and h[j]>=stop): r=-1.0; break
            if r is None: j=i+4; r=side*(cl[j]-e)/risk
            res.append((g.index[i],side,r-2*cost*e/risk))
            i=j+1
    R=pd.DataFrame(res,columns=["t","side","r"]); days=(S.index.max()-S.index.min()).days
    return R,days
for name,S in (("dev",dev),("val",val)):
    for cost in (0.001,0.0005):
        R,days=sim(S,cost)
        print(name,f"cost {cost}: n={len(R)} /day={len(R)/days:.2f} avgR={R.r.mean():+.3f} long={R[R.side==1].r.mean():+.3f}({(R.side==1).sum()}) short={R[R.side==-1].r.mean():+.3f}({(R.side==-1).sum()})")
print("--- HOLDOUT 2026-04..2026-09 (rules frozen above)")
ho=D[(D.index>="2026-04-01")&(D.index<"2026-10-01")]
for cost in (0.001,0.0005):
    R,days=sim(ho,cost)
    print(f"holdout cost {cost}: n={len(R)} /day={len(R)/days:.2f} avgR={R.r.mean():+.3f} long={R[R.side==1].r.mean():+.3f}({(R.side==1).sum()}) short={R[R.side==-1].r.mean():+.3f}({(R.side==-1).sum()}) win={(R.r>0).mean():.2f}")
    if cost==0.001:
        R["m"]=pd.to_datetime(R.t).dt.to_period("M"); print(R.groupby("m").r.agg(["count","mean"]).round(3).to_string())
