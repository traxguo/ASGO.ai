#!/usr/bin/env python3
"""
First-stage analysis for momentum_5m (cards/momentum_5m.md).

The strategy does not use the shared trade-management module, so its trades
carry no "stop=" tag and scripts/make_report.py cannot compute R for them.
Here 1R is the fixed 1.5% stop: R = profit_abs / (stake_amount * 0.015),
costs and funding included (profit_abs is net). Leverage is 1x.

Prints markdown tables (per run: overall and long/short, trades per day, win
rate, avg R, PF, max DD, net, yearly, coins positive, exit reasons, funding)
plus buy-and-hold of the same coins, and saves equity charts.

Usage:
  python research/reports/momentum_5m_analysis.py --out results/<folder> \
      --run normal=<backtest dir or zip> --run fee_x2=<...> ...
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from freqtrade.data.btanalysis import load_backtest_stats

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("make_report", REPO / "scripts" / "make_report.py")
mr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mr)

STOP_PCT = 0.015
START_BALANCE = 10000.0
YEARS = [2022, 2023, 2024]


def trades_frame(trades: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(trades)
    df["open_date"] = pd.to_datetime(df["open_date"], utc=True)
    df["close_date"] = pd.to_datetime(df["close_date"], utc=True)
    df["r"] = df["profit_abs"] / (df["stake_amount"] * STOP_PCT)
    df["side"] = np.where(df["is_short"], "short", "long")
    df["funding"] = df.get("funding_fees", 0.0)
    return df.sort_values("close_date").reset_index(drop=True)


def metrics(df: pd.DataFrame, days: float) -> dict:
    if df.empty:
        return {"n": 0}
    gains = df.loc[df.profit_abs > 0, "profit_abs"].sum()
    losses = -df.loc[df.profit_abs < 0, "profit_abs"].sum()
    equity = pd.concat([pd.Series([START_BALANCE]), START_BALANCE + df["profit_abs"].cumsum()])
    return {
        "n": len(df),
        "per_day": len(df) / days,
        "winrate": float((df.profit_abs > 0).mean()),
        "avg_r": float(df.r.mean()),
        "total_r": float(df.r.sum()),
        "pf": float(gains / losses) if losses > 0 else float("inf"),
        "max_dd": mr.max_drawdown(equity.reset_index(drop=True)),
        "max_dd_r": float((df.r.cumsum().cummax().clip(lower=0) - df.r.cumsum()).max()),
        "net_pct": float(df.profit_abs.sum() / START_BALANCE),
        "funding": float(df.funding.sum()),
        "avg_minutes": float(df.trade_duration.mean()),
    }


def f(x, d=2):
    return mr.fmt(x, d)


def p(x):
    return mr.fmt_pct(x)


def analyse(name: str, strat: str, st: dict, out: Path, pairs: list[str]) -> tuple[str, dict]:
    df = trades_frame(st["trades"])
    start = pd.Timestamp(st["backtest_start"], tz="UTC") if not isinstance(st["backtest_start"], pd.Timestamp) else st["backtest_start"]
    end = pd.Timestamp(st["backtest_end"], tz="UTC") if not isinstance(st["backtest_end"], pd.Timestamp) else st["backtest_end"]
    days = (end - start).total_seconds() / 86400
    res = {"all": metrics(df, days), "long": metrics(df[df.side == "long"], days),
           "short": metrics(df[df.side == "short"], days),
           "ft_max_dd_account": st.get("max_drawdown_account"), "days": days}
    lines = [f"### {name} — `{strat}`", ""]
    lines += ["| Taraf | İşlem | Günde | Kazanan | Ort. R | Toplam R | PF | Max DD (kasa) | Max DD (R) | Net | Funding (USDT) | Ort. süre (dk) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for side in ("all", "long", "short"):
        m = res[side]
        if m["n"] == 0:
            lines.append(f"| {side} | 0 | | | | | | | | | | |")
            continue
        label = {"all": "toplam", "long": "long", "short": "short"}[side]
        lines.append(f"| {label} | {m['n']} | {f(m['per_day'])} | {p(m['winrate'])} | {f(m['avg_r'], 3)} | "
                     f"{f(m['total_r'], 1)} | {f(m['pf'])} | {p(m['max_dd']) if side == 'all' else '—'} | "
                     f"{f(m['max_dd_r'], 1)} | {p(m['net_pct'])} | "
                     f"{f(m['funding'], 0)} | {f(m['avg_minutes'], 0)} |")
    lines.append("")
    lines.append(f"(Freqtrade'in kendi hesapladığı hesap düşüşü: {p(st.get('max_drawdown_account'))}. "
                 "Kasa DD'si long ve short birlikte işlediği için sadece toplamda verilir; "
                 "taraf bazında düşüş, kümülatif R eğrisinin zirveden en büyük düşüşü (R) olarak verilir. "
                 "Net %, işlemlerin USDT kâr/zararının başlangıç kasasına (10000) oranıdır.)")
    lines.append("")

    # yearly (by close date)
    df["year"] = df.close_date.dt.year
    lines += ["| Yıl | Taraf | İşlem | Ort. R | PF | Net (USDT) |", "|---|---|---|---|---|---|"]
    yearly = {}
    for y in YEARS:
        for side in ("all", "long", "short"):
            d = df[(df.year == y) & ((df.side == side) | (side == "all"))]
            m = metrics(d, 365)
            yearly[f"{y}_{side}"] = {"n": m["n"], "avg_r": m.get("avg_r"), "net": float(d.profit_abs.sum())}
            if m["n"]:
                lines.append(f"| {y} | {side if side != 'all' else 'toplam'} | {m['n']} | {f(m['avg_r'], 3)} | "
                             f"{f(m['pf'])} | {f(float(d.profit_abs.sum()), 0)} |")
    res["yearly"] = yearly
    res["years_positive"] = sum(1 for y in YEARS if yearly[f"{y}_all"]["net"] > 0)
    lines.append("")

    # per coin
    g = df.groupby("pair").agg(n=("r", "size"), avg_r=("r", "mean"), total_r=("r", "sum"),
                               net=("profit_abs", "sum"))
    gl = df[df.side == "long"].groupby("pair")["r"].mean()
    gs = df[df.side == "short"].groupby("pair")["r"].mean()
    res["coins_positive"] = int((g.net > 0).sum())
    res["coins_total"] = len(pairs)
    lines += ["| Coin | İşlem | Ort. R | Long ort. R | Short ort. R | Toplam R | Net (USDT) |",
              "|---|---|---|---|---|---|---|"]
    for pair in pairs:
        if pair not in g.index:
            lines.append(f"| {pair} | 0 | | | | | |")
            continue
        r = g.loc[pair]
        lines.append(f"| {pair.split('/')[0]} | {int(r.n)} | {f(r.avg_r, 3)} | {f(gl.get(pair, np.nan), 3)} | "
                     f"{f(gs.get(pair, np.nan), 3)} | {f(r.total_r, 1)} | {f(r.net, 0)} |")
    lines.append("")
    lines.append(f"Artıda biten coin: **{res['coins_positive']}/{len(pairs)}**.")
    lines.append("")

    # exit reasons
    er = df.groupby(["side", "exit_reason"]).size().unstack(fill_value=0)
    lines += ["| Taraf | " + " | ".join(er.columns) + " |", "|---|" + "---|" * len(er.columns)]
    for side, row in er.iterrows():
        tot = row.sum()
        lines.append(f"| {side} | " + " | ".join(f"{int(v)} ({v / tot * 100:.0f}%)" for v in row) + " |")
    lines.append("")
    res["exit_reasons"] = {f"{s}_{k}": int(v) for (s, k), v in er.stack().items()}

    charts = mr.make_charts(f"{strat}_{name}", df[["close_date", "profit_abs", "r"]].copy(), START_BALANCE, out)
    for c in charts:
        lines.append(f"![{c}]({c})")
    lines.append("")
    return "\n".join(lines), res


def buy_hold(pairs, start, end) -> tuple[str, dict]:
    datadir = REPO / "user_data" / "data" / "binance"
    bh = mr.buy_and_hold(pairs, datadir, "5m", start, end)
    yearly = {}
    for y in YEARS:
        yb = mr.buy_and_hold(pairs, datadir, "1h", pd.Timestamp(f"{y}-01-01", tz="UTC"),
                             pd.Timestamp(f"{y}-12-31 23:59", tz="UTC"))
        yearly[y] = float(yb["return"].mean())
    lines = ["| Coin | Al-tut getirisi | Al-tut max DD |", "|---|---|---|"]
    for _, r in bh.iterrows():
        lines.append(f"| {r.pair.split('/')[0]} | {p(r['return'])} | {p(r.max_dd)} |")
    lines.append(f"| **Eşit ağırlık ortalama** | **{p(bh['return'].mean())}** | {p(bh.max_dd.mean())} (ortalama) |")
    lines.append("")
    lines.append("Yıllara göre eşit ağırlıklı al-tut: " + ", ".join(f"{y}: {p(v)}" for y, v in yearly.items()))
    return "\n".join(lines), {"mean_return": float(bh["return"].mean()), "mean_dd": float(bh.max_dd.mean()),
                              "positive": int((bh["return"] > 0).sum()), "yearly": yearly}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--run", action="append", required=True, help="name=path (backtest dir or zip)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pairs = json.loads((REPO / "config" / "pairs_wide16.json").read_text())["exchange"]["pair_whitelist"]
    md, summary = [], {}
    start = end = None
    for spec in a.run:
        name, path = spec.split("=", 1)
        stats = load_backtest_stats(Path(path))
        for strat, st in stats["strategy"].items():
            text, res = analyse(name, strat, st, out, pairs)
            md.append(text)
            summary[f"{name}/{strat}"] = res
            start, end = pd.Timestamp(st["backtest_start"]), pd.Timestamp(st["backtest_end"])
    start = start.tz_localize("UTC") if start.tzinfo is None else start
    end = end.tz_localize("UTC") if end.tzinfo is None else end
    text, bh = buy_hold(pairs, start, end)
    md.append("### Al-tut (aynı dönem, aynı coinler)\n\n" + text)
    summary["buy_and_hold"] = bh
    (out / "analiz_tablolari.md").write_text("\n\n".join(md) + "\n")
    (out / "ozet.json").write_text(json.dumps(summary, indent=1, default=float))
    print("\n\n".join(md))


if __name__ == "__main__":
    main()
