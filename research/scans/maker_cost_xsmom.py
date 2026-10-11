# Cross-sectional short-horizon momentum/reversal with maker (limit) entries, 1h data.
# Question (2026-10-11): did near-miss short-horizon ideas fail only because of taker costs?
# Every R hours: rank coins by past L-hour return; long top K / short bottom K, hold H hours.
# Entry = limit at signal-bar close, filled only if the next bar trades THROUGH it (no touch fills).
# Exit = market at close of hour H after signal. Costs per round trip: taker 0.20%, maker-in/taker-out 0.10%, maker both 0.04%.
import sys,glob,numpy as np,pandas as pd
pairs_file=sys.argv[1] if len(sys.argv)>1 else "config/pairs_all36.json"
start,end=(sys.argv[2],sys.argv[3]) if len(sys.argv)>3 else ("2020-01-01","2025-01-01")
import json
pl=[p.split("/")[0] for p in json.load(open(pairs_file))["exchange"]["pair_whitelist"]]
C,Hh,Ll={},{},{}
for p in pl:
    f=f"user_data/data/binance/futures/{p}_USDT_USDT-1h-futures.feather"
    try: h=pd.read_feather(f).set_index("date")
    except FileNotFoundError: continue
    h=h[(h.index>=start)&(h.index<end)]
    C[p],Hh[p],Ll[p]=h.close,h.high,h.low
C,Hh,Ll=pd.DataFrame(C),pd.DataFrame(Hh),pd.DataFrame(Ll)
days=(pd.Timestamp(end)-pd.Timestamp(start)).days
print(f"{pairs_file} {start}..{end} coins={C.shape[1]}")
def run(L,H,K,mode):
    past=C/C.shift(L)-1
    sig_idx=C.index[::H]  # non-overlapping rebalances
    fwd=C.shift(-H)/C-1
    nlow=Ll.shift(-1); nhigh=Hh.shift(-1)
    rets=[]
    for t in sig_idx:
        r=past.loc[t].dropna()
        if len(r)<2*K+4: continue
        top,bot=r.nlargest(K).index,r.nsmallest(K).index
        longs,shorts=(top,bot) if mode=="mom" else (bot,top)
        for p in longs:
            if nlow.at[t,p]<C.at[t,p] and pd.notna(fwd.at[t,p]): rets.append(fwd.at[t,p])
        for p in shorts:
            if nhigh.at[t,p]>C.at[t,p] and pd.notna(fwd.at[t,p]): rets.append(-fwd.at[t,p])
    a=np.array(rets)*100
    return len(a),a.mean(),a.std()
for mode in ("mom","rev"):
    for L in (4,8,24):
        for H in (4,8):
            n,m,sd=run(L,H,3,mode)
            print(f"{mode} L={L:2d} H={H} K=3 n={n:6d} /day={n/days:5.1f} gross={m:+.3f}% net0.20={m-0.2:+.3f}% net0.10={m-0.1:+.3f}% net0.04={m-0.04:+.3f}% sd={sd:.2f}")
