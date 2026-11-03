# Robustness of the best weekly_xsmom cell (mom L14 S0 R14 K5): start-day offset, neighbours, legs.
import sys
sys.argv = ["x", "config/pairs_wide81.json"]
exec(open("research/xsec/weekly_xsmom.py").read().split("rows = []")[0])
import pandas as pd
dev, val = PERIODS["dev"], PERIODS["val"]
def sh(start, off):
    return str((pd.Timestamp(start) + pd.Timedelta(days=off)).date())
print("offset  dev_avg  val_avg")
for off in range(14):
    d = run(14, 0, 14, 5, "mom", sh(dev[0], off), dev[1]); v = run(14, 0, 14, 5, "mom", sh(val[0], off), val[1])
    print(f"{off:6d} {d[1]:8.2f} {v[1]:8.2f}")
print("neighbours (avg over 7 offsets) L K R -> dev val")
for L in (10, 14, 21):
    for K in (3, 5, 8):
        for R in (10, 14, 21):
            ds = [run(L, 0, R, K, "mom", sh(dev[0], o), dev[1])[1] for o in range(0, R, max(1, R // 7))]
            vs = [run(L, 0, R, K, "mom", sh(val[0], o), val[1])[1] for o in range(0, R, max(1, R // 7))]
            print(f"L{L:2d} K{K} R{R:2d}  dev {np.mean(ds):+.2f}  val {np.mean(vs):+.2f}")
for side in ("long", "short"):
    print(side, run(14, 0, 14, 5, "mom", *dev, side=side), run(14, 0, 14, 5, "mom", *val, side=side))
