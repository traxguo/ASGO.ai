"""
Akis paper test (cards/akis.md; RETIRED 2026-10-11, kept for the record): the frozen rules on NEW days only, from Binance's
public archive (data.binance.vision publishes each day a day later, so this runs
once a day and judges the day before yesterday). No orders, no keys.

For each coin it loads the last 40 days of 5-minute metrics and 1h candles, finds
the signals of the target day with the frozen thresholds, simulates each trade
(next open entry, 1.5 ATR stop, exit after 4 hours, one trade per coin) and
appends them to forward/akis_paper/trades.csv. Cost: 0.1% per order (R_net) and
the low-fee case 0.05% (R_low).

Usage: python research/forward/akis_paper.py [--day YYYY-MM-DD]
"""

import argparse
import csv
import io
import urllib.request
import zipfile
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "forward" / "akis_paper" / "trades.csv"
COINS = "BTC ETH SOL XRP BNB DOGE ADA LINK AVAX LTC DOT TRX".split()
ARCHIVE = "https://data.binance.vision/data/futures/um/daily"
# frozen 2026-10-11 from 2022-2024 quantiles (research/scans/oi_flow_scan.py)
CROWD_Z, TAKER_MAX, SURGE, OI_UP = 1.15239, 0.97527, 0.02302, 0.01901
STOP_ATR, HOLD = 1.5, 4
FIELDS = ["coin", "signal_hour", "side", "entry", "stop", "exit", "exit_reason", "r_gross", "r_net", "r_low"]


def fetch_zip_csv(url: str) -> pd.DataFrame | None:
    try:
        with urllib.request.urlopen(url, timeout=30) as r, zipfile.ZipFile(io.BytesIO(r.read())) as z:
            return pd.read_csv(z.open(z.namelist()[0]))
    except Exception:
        return None


def load(coin: str, day: date) -> pd.DataFrame:
    m_parts, k_parts = [], []
    for i in range(40, -2, -1):  # 40 days back to the day after the target (for the 4h exits)
        d = day - timedelta(days=i)
        m = fetch_zip_csv(f"{ARCHIVE}/metrics/{coin}USDT/{coin}USDT-metrics-{d}.zip")
        k = fetch_zip_csv(f"{ARCHIVE}/klines/{coin}USDT/1h/{coin}USDT-1h-{d}.zip")
        if m is not None:
            m_parts.append(m)
        if k is not None:
            k_parts.append(k)
    m = pd.concat(m_parts)
    m["t"] = pd.to_datetime(m["create_time"], utc=True)
    m = m.set_index("t").sort_index()
    m = m[~m.index.duplicated()]
    for c in ("sum_open_interest", "count_long_short_ratio", "sum_taker_long_short_vol_ratio"):
        m[c] = pd.to_numeric(m[c], errors="coerce")
    k = pd.concat(k_parts)
    k = k[pd.to_numeric(k["open_time"], errors="coerce").notna()]  # files may carry a header row
    k.index = pd.to_datetime(pd.to_numeric(k["open_time"]), unit="ms", utc=True)
    px = k[["open", "high", "low", "close"]].astype(float).sort_index()
    px = px[~px.index.duplicated()]
    h = m.resample("1h").last()
    taker = m["sum_taker_long_short_vol_ratio"].resample("1h").mean()
    # resample label H already holds values known by the close of candle H (no shift)
    df = px.copy()
    oi = h["sum_open_interest"].reindex(df.index)
    ls = h["count_long_short_ratio"].reindex(df.index)
    df["oi4"] = oi.pct_change(4)
    df["ls_z"] = (ls - ls.rolling(24 * 30).mean()) / ls.rolling(24 * 30).std()
    df["taker"] = taker.reindex(df.index).rolling(4).mean()
    df["r4"] = df["close"].pct_change(4)
    tr = pd.concat([df.high - df.low, (df.high - df.close.shift()).abs(), (df.low - df.close.shift()).abs()], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()
    return df


def trades_for_day(coin: str, df: pd.DataFrame, day: date) -> list[dict]:
    out = []
    idx = df.index
    i = int(np.searchsorted(idx, pd.Timestamp(day, tz="UTC")))
    end = int(np.searchsorted(idx, pd.Timestamp(day + timedelta(days=1), tz="UTC")))
    while i < end and i + HOLD < len(df):
        row = df.iloc[i]
        short = row.taker <= TAKER_MAX and row.ls_z >= CROWD_Z
        long_ = row.r4 >= SURGE and row.oi4 >= OI_UP and row.ls_z < CROWD_Z
        if not (short or long_) or not row.atr > 0:
            i += 1
            continue
        side = -1 if short else 1
        e = df.open.iloc[i + 1]
        risk = STOP_ATR * row.atr
        stop = e - side * risk
        reason, j = "time", i + HOLD
        r = side * (df.close.iloc[j] - e) / risk
        for j2 in range(i + 1, i + HOLD + 1):
            if (side == 1 and df.low.iloc[j2] <= stop) or (side == -1 and df.high.iloc[j2] >= stop):
                r, reason, j = -1.0, "stop", j2
                break
        exit_px = stop if reason == "stop" else df.close.iloc[j]
        out.append({"coin": coin, "signal_hour": idx[i].isoformat(), "side": "long" if side == 1 else "short",
                    "entry": e, "stop": stop, "exit": exit_px, "exit_reason": reason, "r_gross": round(r, 4),
                    "r_net": round(r - 2 * 0.001 * e / risk, 4), "r_low": round(r - 2 * 0.0005 * e / risk, 4)})
        i = j + 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", help="target day (default: the day before yesterday, UTC)")
    a = ap.parse_args()
    day = date.fromisoformat(a.day) if a.day else date.today() - timedelta(days=2)
    done = set()
    if OUT.is_file():
        with OUT.open(encoding="utf-8") as f:
            done = {r["signal_hour"][:10] for r in csv.DictReader(f)}
    if day.isoformat() in done:
        print(f"{day}: already recorded")
        return
    rows = []
    for coin in COINS:
        try:
            rows += trades_for_day(coin, load(coin, day), day)
        except Exception as e:  # a missing coin must not stop the others
            print(f"{coin}: skipped ({e})")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    new = not OUT.is_file()
    with OUT.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
    r = pd.DataFrame(rows)
    print(f"{day}: {len(rows)} trades" + (f", avg R net {r.r_net.mean():+.3f}, low-fee {r.r_low.mean():+.3f}" if rows else ""))


if __name__ == "__main__":
    main()
