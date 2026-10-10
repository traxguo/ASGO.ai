#!/usr/bin/env python3
"""
Forward paper test of the frozen pusula version (no money, no orders).

Runs PusulaTrendLong on the 16-coin list from FORWARD_START up to the newest
candle on disk, with exactly the tested settings, and writes
forward/pusula_kagit.md: a short owner note, every trade (closed and still
open), and the current view of each coin from pusula.commentary().

Data first:  python research/data/fetch_binance_vision.py --pairs ... \
                 --timeframes 1h 4h 1d --start 2020-01 --current-month
Then:        FT_LOCAL=1 FT_OFFLINE=1 python research/forward/pusula_paper.py

The current month has no funding archive yet, so its results are provisional
(funding counted as zero until the month is over).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import talib.abstract as ta

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from strategies.candidates import pusula  # noqa: E402

FORWARD_START = "20261001"  # first day after the holdout period
STRATEGY = "PusulaTrendLong"
PAIRS_FILE = ROOT / "config" / "pairs_wide16.json"
RES_DIR = ROOT / "user_data" / "forward_results"
OUT = ROOT / "forward" / "pusula_kagit.md"
DATA = ROOT / "user_data" / "data" / "binance" / "futures"


def run_backtest() -> Path:
    RES_DIR.mkdir(parents=True, exist_ok=True)
    for old in RES_DIR.glob("*"):
        old.unlink()
    cmd = ["./scripts/ft.sh", "backtesting", "-c", str(PAIRS_FILE.relative_to(ROOT)), "--strategy", STRATEGY,
           "--max-open-trades", "3", "--timeframe", "4h", "--timeframe-detail", "1h",
           "--timerange", f"{FORWARD_START}-", "--export", "trades",
           "--backtest-directory", str(RES_DIR), "--cache", "none"]
    log = RES_DIR / "backtest.log"
    with log.open("w") as fh:
        subprocess.run(cmd, cwd=ROOT, env=dict(os.environ), stdout=fh, stderr=subprocess.STDOUT, check=True)
    return next(RES_DIR.glob("*.zip"))


def load(pair: str, tf: str) -> pd.DataFrame:
    return pd.read_feather(DATA / f"{pair.replace('/', '_').replace(':', '_')}-{tf}-futures.feather")


def coin_view(pair: str, btc_daily: pd.DataFrame) -> dict:
    """Same columns the strategy builds, on the last closed 4h candle."""
    df = load(pair, "4h")
    df["atr"] = ta.ATR(df, timeperiod=14)
    df["swing_low"] = df["low"].rolling(10).min()
    df["swing_high"] = df["high"].rolling(10).max()
    df["dc_upper"] = df["high"].rolling(pusula.CHANNEL).max().shift(1)
    df["dc_lower"] = df["low"].rolling(pusula.CHANNEL).min().shift(1)
    reg = pusula.daily_regime_frame(load(pair, "1d"), btc_daily)
    # a daily candle is usable only after it closed: shift by one day like merge_informative_pair
    reg = reg.assign(date=reg["date"] + pd.Timedelta(days=1)).rename(
        columns={c: f"{c}_1d" for c in reg.columns if c != "date"})
    df["date"] = df["date"].astype("datetime64[ns, UTC]")
    reg["date"] = reg["date"].astype("datetime64[ns, UTC]")
    row = pd.merge_asof(df[["date", "close", "atr", "swing_low", "swing_high", "dc_upper", "dc_lower"]],
                        reg, on="date").iloc[-1]
    view = pusula.commentary(row.to_dict(), pair, trend_exit=True, long_only=True)
    view["time"] = row["date"]
    return view


def main() -> None:
    from freqtrade.data.btanalysis import load_backtest_stats
    from make_report import trade_r

    zip_path = run_backtest()
    stats = load_backtest_stats(zip_path)["strategy"][STRATEGY]
    trades = stats["trades"]
    rows = []
    for t in trades:
        r = trade_r(t)["r"]
        is_open = t["exit_reason"] == "force_exit"
        rows.append({"coin": t["pair"].split("/")[0], "giris": t["open_date"][:16], "giris_fiyati": t["open_rate"],
                     "cikis": "açık" if is_open else t["close_date"][:16],
                     "sebep": {"stop_loss": "stop", "trailing_stop_loss": "BE stop", "exit_signal": "trend bozuldu",
                               "force_exit": "hâlâ açık (anlık)"}.get(t["exit_reason"], t["exit_reason"]),
                     "R": r, "acik": is_open})
    df = pd.DataFrame(rows)
    closed = df[~df["acik"]] if not df.empty else df
    open_ = df[df["acik"]] if not df.empty else df
    pairs = json.loads(PAIRS_FILE.read_text())["exchange"]["pair_whitelist"]
    btc_daily = load(pusula.MARKET_PAIR, "1d")
    views = [coin_view(p, btc_daily) for p in pairs]
    last_candle = max(v["time"] for v in views)

    total_r = closed["R"].sum() if len(closed) else 0.0
    lines = [
        "# Pusula kâğıt takibi (para yok, emir yok)",
        "",
        f"Güncelleme: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC. Son veri mumu: {last_candle:%Y-%m-%d %H:%M} UTC.",
        f"Kurallar donduruldu: `{STRATEGY}`, 16 coin, en fazla 3 işlem, başlangıç {FORWARD_START[:4]}-{FORWARD_START[4:6]}-{FORWARD_START[6:]}.",
        "",
        "## GUO'ya not",
        f"- Kâğıt takipte şu ana kadar {len(closed)} işlem kapandı, {len(open_)} işlem açık.",
        f"- Kapanan işlemlerin toplamı: **{total_r:+.2f}R** (1R = kasanın %1'i; yaklaşık %{total_r:+.1f}).",
    ]
    if len(open_):
        lines.append(f"- Açık işlemlerin şu anki durumu: {open_['R'].sum():+.2f}R (henüz kesin değil).")
    lines += ["- Bu strateji ayda 2-3 işlem açar; birkaç haftalık sonuç bir şey söylemez. Anlamlı karar için en az 2-3 ay gerekir.",
              "- İçinde bulunulan ayın funding verisi ay bitince gelir; o yüzden bu ayın rakamları geçicidir.", ""]
    lines += ["## İşlemler", "", "| Coin | Giriş (UTC) | Giriş fiyatı | Çıkış | Sebep | Sonuç (R) |", "|---|---|---|---|---|---|"]
    for _, x in df.iterrows():
        lines.append(f"| {x.coin} | {x.giris} | {x.giris_fiyati:.6g} | {x.cikis} | {x.sebep} | {x.R:+.2f} |")
    if df.empty:
        lines.append("| — | henüz işlem yok | | | | |")
    lines += ["", "## Coinlerin şu anki durumu (son kapanmış 4 saatlik mum)", ""]
    for v in views:
        lines += [v["text"].replace("\n", "  \n"), ""]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(OUT)


if __name__ == "__main__":
    main()
