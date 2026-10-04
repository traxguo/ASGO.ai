#!/usr/bin/env python3
"""
Builds a Turkish report (PROJECT_BRIEF section 11) from a Freqtrade backtest result.

Results are expressed in R (risk units), costs and funding included. Every
report compares the strategy with buy-and-hold of the same coins.

Usage:
  python scripts/make_report.py --results user_data/backtest_results \
      --datadir user_data/data/binance --test ilk_backtest \
      [--out results/2026-10-04_trend_ma_ilk_backtest] [--synthetic]

If the backtest ran several strategies (e.g. TrendMA_A and TrendMA_B),
the report compares them side by side.
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from freqtrade.data.btanalysis import load_backtest_stats
from freqtrade.data.history import load_pair_history
from freqtrade.enums import CandleType

STOP_RE = re.compile(r"stop=([0-9.eE+-]+)")


# ---------------------------------------------------------------- per trade


def trade_r(trade: dict) -> dict:
    """Result of one trade in R, plus how it ended."""
    orders = trade["orders"]
    entry = next(o for o in orders if o["ft_is_entry"])
    m = STOP_RE.search(trade.get("enter_tag") or "")
    if not m:
        raise ValueError(f"trade has no planned stop in enter_tag: {trade.get('enter_tag')}")
    stop = float(m.group(1))
    risk_abs = entry["amount"] * abs(entry["safe_price"] - stop)
    r = trade["profit_abs"] / risk_abs if risk_abs > 0 else np.nan
    exit_tags = [o["ft_order_tag"] for o in orders if not o["ft_is_entry"]]
    if trade["exit_reason"] == "tp2":
        outcome = "TP2"
    elif "tp1" in exit_tags:
        outcome = "TP1 sonrası BE"
    elif trade["exit_reason"] in ("stop_loss", "trailing_stop_loss"):
        long = not trade["is_short"]
        be = trade["stop_loss_abs"] >= trade["open_rate"] if long else trade["stop_loss_abs"] <= trade["open_rate"]
        outcome = "BE" if be else "Stop"
    else:
        outcome = str(trade["exit_reason"])  # e.g. force_exit at end of data
    return {"r": r, "outcome": outcome, "side": "short" if trade["is_short"] else "long"}


def r_table(trades: list[dict]) -> pd.DataFrame:
    rows = []
    for t in trades:
        rows.append({**trade_r(t), "pair": t["pair"], "profit_abs": t["profit_abs"],
                     "funding": t.get("funding_fees") or 0.0, "close_date": t["close_date"]})
    df = pd.DataFrame(rows)
    if not df.empty:
        df["close_date"] = pd.to_datetime(df["close_date"], utc=True)
    return df


# ---------------------------------------------------------------- metrics


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float(((equity - peak) / peak).min() * -1) if len(equity) else 0.0


def side_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"n": 0, "avg_r": np.nan, "pf": np.nan, "winrate": np.nan, "total_r": 0.0}
    gains = df.loc[df["profit_abs"] > 0, "profit_abs"].sum()
    losses = -df.loc[df["profit_abs"] < 0, "profit_abs"].sum()
    return {
        "n": len(df),
        "avg_r": df["r"].mean(),
        "pf": gains / losses if losses > 0 else np.inf,
        "winrate": (df["profit_abs"] > 0).mean(),
        "total_r": df["r"].sum(),
    }


def buy_and_hold(pairs, datadir: Path, timeframe: str, start, end) -> pd.DataFrame:
    rows = []
    for pair in pairs:
        df = load_pair_history(pair, timeframe, datadir, candle_type=CandleType.FUTURES)
        df = df[(df["date"] >= start) & (df["date"] <= end)]
        if df.empty:
            continue
        close = df["close"].reset_index(drop=True)
        rows.append({"pair": pair, "return": close.iloc[-1] / close.iloc[0] - 1, "max_dd": max_drawdown(close)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- charts


def make_charts(name: str, rt: pd.DataFrame, start_balance: float, out: Path) -> list[str]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return []
    files = []
    rt = rt.sort_values("close_date")
    equity = start_balance + rt["profit_abs"].cumsum()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    a1.plot(rt["close_date"], equity, color="#2b6cb0")
    a1.set_title(f"{name}: sermaye eğrisi (USDT)")
    dd = (equity - equity.cummax()) / equity.cummax() * 100
    a2.fill_between(rt["close_date"], dd, 0, color="#c53030", alpha=0.4)
    a2.set_title("Drawdown (%)")
    fig.tight_layout()
    f = out / f"{name}_sermaye.png"
    fig.savefig(f, dpi=110)
    plt.close(fig)
    files.append(f.name)

    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.hist(rt["r"].dropna(), bins=30, color="#2f855a")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_title(f"{name}: işlem başına sonuç (R) dağılımı")
    fig.tight_layout()
    f = out / f"{name}_R_dagilimi.png"
    fig.savefig(f, dpi=110)
    plt.close(fig)
    files.append(f.name)
    return files


# ---------------------------------------------------------------- report


def fmt_pct(x):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x * 100:.1f}%"


def fmt(x, d=2):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    if isinstance(x, float) and np.isinf(x):
        return "∞"
    return f"{x:.{d}f}"


def build_report(stats: dict, datadir: Path, test: str, out: Path, synthetic: bool) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    strategies = stats["strategy"]
    first = next(iter(strategies.values()))
    start = pd.Timestamp(first["backtest_start"], tz="UTC")
    end = pd.Timestamp(first["backtest_end"], tz="UTC")
    pairs = first["pairlist"]
    bh = buy_and_hold(pairs, datadir, first["timeframe"], start, end)
    bh_ret = bh["return"].mean() if not bh.empty else np.nan
    bh_dd = bh["max_dd"].mean() if not bh.empty else np.nan

    names = list(strategies)
    lines: list[str] = []
    title_names = " vs ".join(names)
    lines.append(f"# {title_names} — {test} — {date.today().isoformat()}")
    if synthetic:
        lines.append("")
        lines.append("> ⚠️ **SENTETİK VERİ.** Bu rapor gerçek piyasa verisiyle değil, rastgele üretilmiş "
                     "veriyle yapılmış bir **boru hattı testidir**. Rakamların hiçbir anlamı yoktur; "
                     "sadece sistemin uçtan uca çalıştığını gösterir.")

    per = {}
    for n in names:
        st = strategies[n]
        rt = r_table(st["trades"])
        per[n] = (st, rt)

    # --- summary
    lines += ["", "## Özet"]
    for n, (st, rt) in per.items():
        m = side_metrics(rt)
        lines.append(
            f"- **{n}**: {m['n']} işlem, işlem başına ortalama **{fmt(m['avg_r'])}R** (maliyet ve funding dahil), "
            f"net getiri {fmt_pct(st['profit_total'])}, en büyük düşüş {fmt_pct(st['max_drawdown_account'])}."
        )
    lines.append(f"- Aynı dönemde coinleri al-tut (eşit ağırlık): getiri {fmt_pct(bh_ret)}, ortalama en büyük düşüş {fmt_pct(bh_dd)}.")

    # --- settings
    lines += [
        "",
        "## Ayarlar",
        f"- Dönem: {first['backtest_start']} → {first['backtest_end']}",
        f"- Coinler: {', '.join(pairs)}",
        f"- Zaman dilimi: {first['timeframe']}",
        "- Yön: long + short",
        f"- Mod: {first.get('trading_mode')} / {first.get('margin_mode')}",
        "- Kaldıraç: en fazla 3x, likidasyon stop mesafesinin en az 2 katı uzakta (bölüm 7.6)",
        "- Risk: işlem başına sermayenin %1'i (pozisyon büyüklüğü stop mesafesine göre)",
        "- Maliyet: her emir için %0.05 komisyon + %0.05 kayma (= %0.1), funding geçmiş veriden",
        f"- Başlangıç sermayesi: {first['starting_balance']} {first['stake_currency']}",
    ]

    # --- metrics table
    header = "| Metrik | " + " | ".join(names) + " | Al-tut |"
    sep = "|---|" + "---|" * (len(names) + 1)
    rows = {
        "Net getiri": [fmt_pct(st["profit_total"]) for st, _ in per.values()] + [fmt_pct(bh_ret)],
        "Max drawdown": [fmt_pct(st["max_drawdown_account"]) for st, _ in per.values()] + [fmt_pct(bh_dd)],
        "Profit factor": [fmt(side_metrics(rt)["pf"]) for _, rt in per.values()] + ["—"],
        "Ortalama R": [fmt(side_metrics(rt)["avg_r"]) for _, rt in per.values()] + ["—"],
        "İşlem sayısı": [str(len(rt)) for _, rt in per.values()] + ["—"],
        "Winrate": [fmt_pct(side_metrics(rt)["winrate"]) for _, rt in per.values()] + ["—"],
    }
    lines += ["", "## Metrikler", header, sep]
    for k, v in rows.items():
        lines.append(f"| {k} | " + " | ".join(v) + " |")
    lines.append("")
    lines.append("Winrate tek başına başarı ölçütü değildir; asıl ölçüt ortalama R (expectancy) ve drawdown'dur.")

    # --- long/short
    lines += ["", "## Long / short ayrımı", "| Strateji | Yön | İşlem | Ortalama R | Toplam R | Profit factor |", "|---|---|---|---|---|---|"]
    for n, (_, rt) in per.items():
        for side in ("long", "short"):
            m = side_metrics(rt[rt["side"] == side] if not rt.empty else rt)
            lines.append(f"| {n} | {side} | {m['n']} | {fmt(m['avg_r'])} | {fmt(m['total_r'])} | {fmt(m['pf'])} |")

    # --- signal statistics
    lines += ["", "## Sinyal istatistikleri",
              "| Strateji | Stop | BE | TP1 sonrası BE | TP2 | Diğer | İptal (bölgeye gelmedi / önce stop) | Toplam funding (USDT) |",
              "|---|---|---|---|---|---|---|---|"]
    for n, (st, rt) in per.items():
        total = len(rt)
        cancelled = st.get("timedout_entry_orders", 0) + st.get("canceled_trade_entries", 0)
        signals = total + cancelled
        counts = rt["outcome"].value_counts() if total else pd.Series(dtype=int)

        def pct(k):
            return fmt_pct(counts.get(k, 0) / total) if total else "—"

        other = total - sum(counts.get(k, 0) for k in ("Stop", "BE", "TP1 sonrası BE", "TP2"))
        lines.append(
            f"| {n} | {pct('Stop')} | {pct('BE')} | {pct('TP1 sonrası BE')} | {pct('TP2')} | "
            f"{fmt_pct(other / total) if total else '—'} | "
            f"{fmt_pct(cancelled / signals) if signals else '—'} | {fmt(rt['funding'].sum() if total else 0.0)} |"
        )

    # --- per pair
    lines += ["", "## Coin bazında", "| Strateji | Coin | İşlem | Ortalama R | Toplam R | Al-tut getirisi |", "|---|---|---|---|---|---|"]
    bh_map = dict(zip(bh["pair"], bh["return"])) if not bh.empty else {}
    for n, (_, rt) in per.items():
        for pair in pairs:
            sub = rt[rt["pair"] == pair] if not rt.empty else rt
            m = side_metrics(sub)
            lines.append(f"| {n} | {pair} | {m['n']} | {fmt(m['avg_r'])} | {fmt(m['total_r'])} | {fmt_pct(bh_map.get(pair))} |")

    # --- charts
    lines += ["", "## Grafikler"]
    for n, (st, rt) in per.items():
        if rt.empty:
            continue
        for f in make_charts(n, rt, st["starting_balance"], out):
            lines.append(f"![{f}]({f})")

    # --- placeholders for the human/Claude judgement
    lines += [
        "",
        "## Yorum: güçlü yanlar / şüpheli noktalar",
        "_(Claude tarafından rakamlara bakılarak yazılır.)_",
        "",
        "## Karar: devam / düzelt / emekli",
        "_(Claude tarafından yazılır, gerekçesiyle.)_",
        "",
    ]
    path = out / "rapor.md"
    path.write_text("\n".join(lines))
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="user_data/backtest_results", help="backtest result file or folder (latest is used)")
    ap.add_argument("--datadir", default="user_data/data/binance")
    ap.add_argument("--test", required=True, help="short test name, e.g. ilk_backtest")
    ap.add_argument("--out", help="output folder (default: results/<today>_<strategies>_<test>)")
    ap.add_argument("--synthetic", action="store_true", help="stamp the report as synthetic pipeline test")
    a = ap.parse_args()
    stats = load_backtest_stats(Path(a.results))
    names = "_".join(stats["strategy"].keys())
    out = Path(a.out) if a.out else Path("results") / f"{date.today().isoformat()}_{names}_{a.test}"
    print(build_report(stats, Path(a.datadir), a.test, out, a.synthetic))


if __name__ == "__main__":
    main()
