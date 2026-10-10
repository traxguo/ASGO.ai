#!/usr/bin/env python3
"""
Data validation (PROJECT_BRIEF section 5).

Checks downloaded futures data and REPORTS problems. It never fixes data silently.
  - first/last candle per pair (futures history can be short for some coins)
  - missing candles, duplicate candles
  - zero-volume candles
  - extreme jumps (|close-to-close| above a threshold)
  - funding rate gaps, mark price coverage

Usage:
  python research/data/validate.py --config config/base.json --config config/pairs_level1.json \
      [--datadir user_data/data/binance] [--timeframes 1h 4h] [--out research/data/validation_report.md]
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd
from freqtrade.data.history import get_datahandler
from freqtrade.enums import CandleType

JUMP_THRESHOLD = {"1h": 0.15, "4h": 0.25, "1d": 0.35}  # flag single-candle moves larger than this
FUNDING_MAX_GAP = pd.Timedelta(hours=8)  # Binance funding is every 8h (some pairs 4h)


def load_pairs(configs: list[str]) -> list[str]:
    pairs: list[str] = []
    for c in configs:
        data = json.loads(Path(c).read_text())
        pairs = data.get("exchange", {}).get("pair_whitelist", pairs) or pairs
    return pairs


def check_ohlcv(df: pd.DataFrame, timeframe: str) -> dict:
    td = pd.Timedelta(timeframe.replace("d", "D"))
    dates = df["date"]
    dup = int(dates.duplicated().sum())
    full = pd.date_range(dates.min(), dates.max(), freq=td)
    missing = full.difference(dates)
    zero_vol = int((df["volume"] <= 0).sum())
    ret = df["close"].pct_change().abs()
    jumps = df.loc[ret > JUMP_THRESHOLD.get(timeframe, 0.2), ["date", "close"]]
    return {
        "start": dates.min(),
        "end": dates.max(),
        "candles": len(df),
        "duplicates": dup,
        "missing": len(missing),
        "missing_examples": [str(x) for x in missing[:3]],
        "zero_volume": zero_vol,
        "jumps": len(jumps),
        "jump_examples": [f"{r.date} ({r.close})" for r in jumps.head(3).itertuples()],
    }


def check_funding(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"rows": 0}
    df = df.sort_values("date")
    # Keep only real funding events (rows where a rate was published).
    col = "funding_rate" if "funding_rate" in df.columns else "open"
    events = df.loc[df[col].notna(), "date"]
    gaps = events.diff().dropna()
    big = gaps[gaps > FUNDING_MAX_GAP]
    return {
        "rows": len(df),
        "start": df["date"].min(),
        "end": df["date"].max(),
        "gaps_over_8h": len(big),
        "largest_gap": str(gaps.max()) if len(gaps) else "-",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", action="append", default=["config/base.json", "config/pairs_level1.json"])
    ap.add_argument("--datadir", default="user_data/data/binance")
    ap.add_argument("--timeframes", nargs="+", default=["1h", "4h", "1d"])
    ap.add_argument("--out", default="research/data/validation_report.md")
    a = ap.parse_args()

    pairs = load_pairs(a.config)
    dh = get_datahandler(Path(a.datadir), "feather")
    lines = [f"# Veri doğrulama raporu — {date.today().isoformat()}", "",
             f"Veri klasörü: `{a.datadir}`", "",
             "Sorunlar sadece raporlanır, veri sessizce düzeltilmez.", ""]
    problems = 0

    lines += ["## Fiyat mumları (futures)", "",
              "| Coin | TF | Başlangıç | Bitiş | Mum | Eksik | Tekrar | Sıfır hacim | Aşırı sıçrama |",
              "|---|---|---|---|---|---|---|---|---|"]
    details: list[str] = []
    for pair in pairs:
        for tf in a.timeframes:
            df = dh.ohlcv_load(pair, tf, candle_type=CandleType.FUTURES, fill_missing=False)
            if df.empty:
                lines.append(f"| {pair} | {tf} | **VERİ YOK** | | | | | | |")
                problems += 1
                continue
            r = check_ohlcv(df, tf)
            lines.append(f"| {pair} | {tf} | {r['start']:%Y-%m-%d} | {r['end']:%Y-%m-%d} | {r['candles']} | "
                         f"{r['missing']} | {r['duplicates']} | {r['zero_volume']} | {r['jumps']} |")
            if r["missing"] or r["duplicates"] or r["zero_volume"] or r["jumps"]:
                problems += 1
                details.append(f"- {pair} {tf}: eksik örnekleri {r['missing_examples']}, sıçrama örnekleri {r['jump_examples']}")

    lines += ["", "## Funding oranı ve mark price", "",
              "| Coin | Funding başlangıç | Funding satır | 8 saatten uzun boşluk | En büyük boşluk | Mark price başlangıç | Mark mum |",
              "|---|---|---|---|---|---|---|"]
    for pair in pairs:
        fr = dh.ohlcv_load(pair, "1h", candle_type=CandleType.FUNDING_RATE, fill_missing=False)
        mk = dh.ohlcv_load(pair, "1h", candle_type=CandleType.MARK, fill_missing=False)
        f = check_funding(fr)
        if f["rows"] == 0 or mk.empty:
            problems += 1
        lines.append(
            f"| {pair} | {f.get('start', '—'):%Y-%m-%d} | {f['rows']} | {f.get('gaps_over_8h', '—')} | {f.get('largest_gap', '—')} | "
            if f["rows"] else f"| {pair} | **VERİ YOK** | 0 | — | — | "
        )
        lines[-1] += (f"{mk['date'].min():%Y-%m-%d} | {len(mk)} |" if not mk.empty else "**VERİ YOK** | 0 |")
        if f.get("gaps_over_8h"):
            problems += 1

    if details:
        lines += ["", "## Ayrıntılar", *details]
    lines += ["", f"**Sonuç:** {'sorun bulunmadı' if problems == 0 else f'{problems} kalemde dikkat edilmesi gereken durum var'}."]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(lines) + "\n")
    print(f"{a.out} yazıldı ({problems} uyarı)")


if __name__ == "__main__":
    main()
