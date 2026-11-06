# For perp-delisting events (E3): was the short entry (announcement + 2h) inside Binance's "no new non-reduce-only
# orders" window? Parses the window start from the announcement body. Uses the base-rule trade files.
import re, pandas as pd

B = pd.read_csv("research/events/binance_announcement_bodies.csv")
A = pd.read_csv("research/events/binance_announcements.csv").drop_duplicates("code")
body = dict(zip(B.code, B.body.fillna("")))
code_of = dict(zip(A.title, A.code))


def ro_start(code):
    b = body.get(code, "")
    m = re.search(r"not (?:be )?allowed to open new non-reduce[- ]only orders[^0-9]{0,80}?(20\d\d-\d\d-\d\d \d\d:\d\d) \(UTC\)", b)
    return pd.Timestamp(m.group(1), tz="UTC") if m else None


rows = []
for f, lab in (("research/events/out_base_trades.csv", None), ("research/events/holdout_out_base_trades.csv", "HOLD")):
    T = pd.read_csv(f, parse_dates=["entry"])
    if lab:
        T = T[T.per == "VAL"].assign(per="HOLD")
    for _, r in T[T.typ == "E3"].iterrows():
        rs = ro_start(code_of.get(r.title))
        rows.append(dict(per=r.per, sym=r.sym, entry=r.entry, ro_start=rs, R=r.R,
                         inside=None if rs is None else r.entry >= rs))
X = pd.DataFrame(rows)
X.to_csv("research/events/out_e3_reduce_only.csv", index=False)
g = X.groupby("per").agg(n=("R", "size"), known=("ro_start", lambda s: s.notna().sum()),
                         inside=("inside", lambda s: int((s == True).sum())), avgR_all=("R", "mean"))
g["avgR_outside_or_unknown"] = X[X.inside != True].groupby("per").R.mean()
print(g.round(3).to_string())
