# Trade list of the new-listing short, card rule N7 M30 stop 30% (2026-11-04).
# Per trade: short return of the coin vs the same-days BTC return (hedge), funding and 0.20% x2 legs cost included.
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "research/neutral")
from common import load, simple_ret, PERIODS  # noqa: E402

N, M, S = (int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (7, 30, 0.3)
C, R, U, F = load()
D = pd.read_feather("user_data/data/xsec_all_1d.feather")
Vv = D.pivot(index="date", columns="symbol", values="quote_volume").reindex(C.index)
vr = Vv.rolling(30, min_periods=5).mean().rank(axis=1, ascending=False)
first = C.apply(lambda s: s.first_valid_index())
first = first[(first > pd.Timestamp("2020-02-01", tz="UTC")) & (first.index != "BTCUSDT")]
rows = []
for sym, f in first.items():
    i0 = C.index.get_loc(f) + N
    if i0 >= len(C.index) or not (vr[sym].iat[i0] <= 100):
        continue
    px = C[sym].values
    ent, j, why = px[i0], i0, "time"
    for j in range(i0 + 1, min(i0 + M, len(C.index) - 1) + 1):
        if np.isnan(px[j]):
            j -= 1; why = "delist"; break
        if px[j] >= ent * (1 + S):
            why = "stop"; break
    if np.isnan(ent) or j <= i0:
        continue
    coin = -(px[j] / ent - 1)
    b = C["BTCUSDT"].values
    hedge = b[j] / b[i0] - 1
    fund = F[sym].iloc[i0 + 1:j + 1].sum() - F["BTCUSDT"].iloc[i0 + 1:j + 1].sum()
    rows.append({"sym": sym, "entry": C.index[i0], "days": j - i0, "short": coin, "btc": hedge,
                 "pair": (coin + hedge) / 2 + fund / 2 - 0.002, "why": why})
T = pd.DataFrame(rows)
for per, (s, e) in PERIODS.items():
    t = T[(T.entry >= s) & (T.entry < e)]
    print(f"{per}: {len(t)} trades ({len(t) / ((pd.Timestamp(e) - pd.Timestamp(s)).days / 30.4):.1f}/month), "
          f"pair avg {t.pair.mean()*100:+.2f}% median {t.pair.median()*100:+.2f}%, win {(t.pair > 0).mean()*100:.0f}%, "
          f"short leg avg {t.short.mean()*100:+.1f}%, stops {(t.why == 'stop').mean()*100:.0f}%, delisted {(t.why == 'delist').mean()*100:.0f}%, "
          f"worst {t.pair.min()*100:+.0f}% ({t.loc[t.pair.idxmin(), 'sym']}), best {t.pair.max()*100:+.0f}% ({t.loc[t.pair.idxmax(), 'sym']})")
    print(f"     without best 5 trades avg {t.pair.drop(t.pair.nlargest(5).index).mean()*100:+.2f}%")
T.to_csv(f"research/neutral/newlist_trades_N{N}_M{M}_S{int(S*100)}.csv", index=False)
