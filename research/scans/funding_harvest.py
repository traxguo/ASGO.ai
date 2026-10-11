# Funding-settlement harvest: around each funding settlement S, take the side that RECEIVES funding
# when the previous settlement's rate was extreme (known in advance). Enter close of hour S-1h... i.e. at S-ENTRY_H,
# exit at S+EXIT_H. PnL% = side * price move + |realized rate at S| - 0.2% cost.
import sys,glob,json,numpy as np,pandas as pd
pf,start,end=sys.argv[1],sys.argv[2],sys.argv[3]
pl=[p.split("/")[0] for p in json.load(open(pf))["exchange"]["pair_whitelist"]]
rows=[]
for p in pl:
    try:
        h=pd.read_feather(f"user_data/data/binance/futures/{p}_USDT_USDT-1h-futures.feather").set_index("date").open
        fr=pd.read_feather(f"user_data/data/binance/futures/{p}_USDT_USDT-1h-funding_rate.feather").set_index("date").funding_rate
    except FileNotFoundError: continue
    fr=fr[(fr.index>=start)&(fr.index<end)]
    prev=fr.shift(1)
    for S,r in fr.items():
        pr=prev.get(S)
        if pr!=pr: continue
        for eh,xh in ((1,1),(1,2),(2,2)):
            a,b=S-pd.Timedelta(hours=eh),S+pd.Timedelta(hours=xh)
            if a in h.index and b in h.index:
                rows.append((p,S,eh,xh,pr,r,(h[b]/h[a]-1)))
D=pd.DataFrame(rows,columns=["p","S","eh","xh","prev","rate","move"])
days=(pd.Timestamp(end)-pd.Timestamp(start)).days
for thr in (0.0005,0.001,0.002):
    for side_name,m,side in (("short(rate>+thr)",D.prev>=thr,-1),("long(rate<-thr)",D.prev<=-thr,1)):
        for (eh,xh),g in D[m].groupby(["eh","xh"]):
            pnl=(side*g.move - side*g.rate)*100-0.2   # short receives +rate; long receives -rate
            print(f"thr={thr:.4f} {side_name:17s} in-{eh}h out+{xh}h n={len(g):5d} /day={len(g)/days:4.2f} net={pnl.mean():+.3f}% move={side*g.move.mean()*100:+.3f}% fund={(-side*g.rate).mean()*100:+.3f}%")
