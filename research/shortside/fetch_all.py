# Daily OHLCV + funding for EVERY Binance USDⓈ-M USDT perpetual ever listed (delisted included), from data.binance.vision.
# Survivorship-free universe for the short-side research (cards/yeni_coin_short.md etc.).
# Output (not committed): user_data/data/allc_1d.feather, user_data/data/allc_funding.feather
import io, os, re, time, zipfile, urllib.request
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix={p}&delimiter=/&marker={m}"
KL = "data/futures/um/monthly/klines/{s}/1d/"
FR = "data/futures/um/monthly/fundingRate/{s}/"
BASE = "https://data.binance.vision/"
LAST = os.environ.get("LAST", "2026-03")  # holdout months only with LAST=2026-10 and SUFFIX=_full (approved one-off run)
SUF = os.environ.get("SUFFIX", "")


def get(url):
    for i in range(5):
        try:
            return urllib.request.urlopen(url, timeout=40).read()
        except Exception:
            time.sleep(1 + 2 * i)
    return None


def listing(prefix):
    out, marker = [], ""
    while True:
        x = (get(S3.format(p=prefix, m=marker)) or b"").decode()
        out += re.findall(r"<Prefix>([^<]+)</Prefix>", x)[1:] + re.findall(r"<Key>([^<]+)</Key>", x)
        nm = re.search(r"<NextMarker>([^<]+)</NextMarker>", x)
        if "<IsTruncated>true" not in x or not nm:
            return out
        marker = nm.group(1)


def symbols():
    ps = listing("data/futures/um/monthly/klines/")
    s = [p.rstrip("/").split("/")[-1] for p in ps]
    return sorted(x for x in s if x.endswith("USDT") and "_" not in x)


def read_zip(raw):
    z = zipfile.ZipFile(io.BytesIO(raw))
    df = pd.read_csv(z.open(z.namelist()[0]), header=None)
    if not str(df.iloc[0, 0]).replace(".", "").isdigit():
        df = df.iloc[1:]
    return df


def kl(s):
    keys = [k for k in listing(KL.format(s=s)) if k.endswith(".zip") and k[-11:-4] <= LAST]
    parts = []
    for k in keys:
        raw = get(BASE + k)
        if raw is None:
            print("missing", k, flush=True)
            continue
        df = read_zip(raw).iloc[:, [0, 1, 2, 3, 4, 7]].astype(float)
        df.columns = ["ts", "open", "high", "low", "close", "qv"]
        parts.append(df)
    if not parts:
        return None
    d = pd.concat(parts)
    d["symbol"] = s
    return d


def fr(s):
    keys = [k for k in listing(FR.format(s=s)) if k.endswith(".zip") and k[-11:-4] <= LAST]
    parts = []
    for k in keys:
        raw = get(BASE + k)
        if raw is None:
            continue
        df = read_zip(raw).iloc[:, [0, 2]].astype(float)
        df.columns = ["ts", "rate"]
        parts.append(df)
    if not parts:
        return None
    d = pd.concat(parts)
    d["symbol"] = s
    return d


if __name__ == "__main__":
    syms = symbols()
    print(len(syms), "symbols", flush=True)
    with ThreadPoolExecutor(24) as ex:
        K = [p for p in ex.map(kl, syms) if p is not None]
    D = pd.concat(K)
    D["date"] = pd.to_datetime(D.ts.astype("int64"), unit="ms", utc=True).dt.normalize()
    D = D.drop(columns="ts").drop_duplicates(["symbol", "date"]).sort_values(["symbol", "date"]).reset_index(drop=True)
    D.to_feather(f"user_data/data/allc_1d{SUF}.feather")
    print(D.symbol.nunique(), "kline symbols", len(D), "rows", flush=True)
    with ThreadPoolExecutor(24) as ex:
        F = [p for p in ex.map(fr, syms) if p is not None]
    F = pd.concat(F)
    F["time"] = pd.to_datetime(F.ts.astype("int64"), unit="ms", utc=True)
    F = F.drop(columns="ts").drop_duplicates(["symbol", "time"]).reset_index(drop=True)
    F.to_feather(f"user_data/data/allc_funding{SUF}.feather")
    print(F.symbol.nunique(), "funding symbols", len(F), "rows")
