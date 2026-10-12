# Hour-of-day seasonality scan: mean forward H-hour return after each UTC hour, per side,
# pooled over coins, dev vs validation. Cost 0.2% round trip. Is there an hour where a 1-3h hold beats costs?
import sys,json,numpy as np,pandas as pd
pf=sys.argv[1];H=int(sys.argv[2])
pl=[p.split("/")[0] for p in json.load(open(pf))["exchange"]["pair_whitelist"]]
B="user_data/data/binance/futures/";rows=[]
for p in pl:
    try: h=pd.read_feather(B+f"{p}_USDT_USDT-1h-futures.feather").set_index("date")
    except FileNotFoundError: continue
    fwd=h.close.shift(-H)/h.open-1  # buy at open of hour, exit at close of hour+H-1
    rows.append(pd.DataFrame({"r":fwd,"hr":h.index.hour,"per":np.where(h.index<"2025-01-01","dev",np.where(h.index<"2026-04-01","val","x"))}))
D=pd.concat(rows);D=D[D.per!="x"].dropna()
t=D.groupby(["hr","per"]).r.mean().unstack()*100
t["dev_net_long"]=t.dev-0.2;t["val_net_long"]=t.val-0.2;t["dev_net_short"]=-t.dev-0.2;t["val_net_short"]=-t.val-0.2
print(f"H={H}h, % per trade (cost 0.2%)");print(t.round(3).to_string())
