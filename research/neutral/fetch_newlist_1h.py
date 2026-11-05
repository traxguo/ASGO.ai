# 1h klines (open/high/close) for the first ~75 days of every USDT perp listed after 2020-02-01 (delisted
# included), from data.binance.vision. Used for intraday stops of the new-listing short. Not committed.
# Output: user_data/data/newlist_1h.feather (symbol, date, open, high, close).
import io, sys, time, zipfile, urllib.request
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

FILE = "https://data.binance.vision/data/futures/um/monthly/klines/{s}/1h/{s}-1h-{m}.zip"
D = pd.read_feather("user_data/data/xsec_all_1d.feather")
first = D.groupby("symbol").date.min()
first = first[first > pd.Timestamp("2020-02-01", tz="UTC")]
jobs = []
for s, f in first.items():
    for m in pd.period_range(f.tz_localize(None).to_period("M"), (f + pd.Timedelta(days=75)).tz_localize(None).to_period("M"), freq="M"):
        if str(m) <= "2026-03":
            jobs.append((s, str(m)))
print(len(jobs), "files", flush=True)


def get(url):
    for i in range(4):
        try:
            return urllib.request.urlopen(url, timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1 + 2 * i)
        except Exception:
            time.sleep(1 + 2 * i)
    return None


def one(sm):
    s, m = sm
    raw = get(FILE.format(s=s, m=m))
    if raw is None:
        return None
    z = zipfile.ZipFile(io.BytesIO(raw))
    df = pd.read_csv(z.open(z.namelist()[0]), header=None)
    if not str(df.iloc[0, 0]).isdigit():
        df = df.iloc[1:]
    df = df.iloc[:, [0, 1, 2, 4]].astype(float)
    df.columns = ["ts", "open", "high", "close"]
    df["symbol"] = s
    return df


with ThreadPoolExecutor(16) as ex:
    parts = [p for p in ex.map(one, jobs) if p is not None]
H = pd.concat(parts)
H["date"] = pd.to_datetime(H.ts.astype("int64"), unit="ms", utc=True)
H = H.drop(columns="ts").drop_duplicates(["symbol", "date"]).reset_index(drop=True)
H.to_feather("user_data/data/newlist_1h.feather")
print(H.symbol.nunique(), "symbols,", len(H), "rows")
