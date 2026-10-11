#!/usr/bin/env python3
"""
First-stage analysis for sfp_sweep (cards/sfp_sweep.md).

R per trade comes from scripts/make_report.trade_r: 1R = entry amount x |fill price -
planned stop| (stop from the "stop=" enter tag), result = net profit incl. fees,
funding and the partial exit. The tag also carries "tp1r=" (TP1 distance in R at the
signal close) so trades with TP1 < 1R (project rule TP1 >= 1R) can be counted.

Prints markdown tables per run (overall and long/short, trades per day, win rate,
avg R, PF, max DD, net, yearly, per coin, outcomes, TP1 < 1R, loss-streak pauses)
plus buy-and-hold of the same coins, and saves equity charts.

Usage:
  python research/reports/sfp_sweep_analysis.py --out results/<folder> \
      --pairs config/pairs_btc_eth_sol.json --run normal=<backtest zip> --run ...
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

START_BALANCE = 10000.0
YEARS = [2022, 2023, 2024]
OUTCOMES = ["Stop", "BE", "TP1 sonrası BE", "TP2"]


def trades_frame(trades: list[dict]) -> pd.DataFrame:
    rows = []
    for t in trades:
        tr = mr.trade_r(t)
        tag = t.get("enter_tag") or ""
        tp1r = float(tag.split("tp1r=")[1].split()[0]) if "tp1r=" in tag else np.nan
        rows.append({**tr, "pair": t["pair"], "profit_abs": t["profit_abs"],
                     "funding": t.get("funding_fees") or 0.0, "open_date": t["open_date"],
                     "close_date": t["close_date"], "minutes": t["trade_duration"], "tp1r": tp1r,
                     "leverage": t["leverage"],
                     "stop_pct": abs(t["open_rate"] - float(mr.STOP_RE.search(tag).group(1))) / t["open_rate"]})
    df = pd.DataFrame(rows)
    df["open_date"] = pd.to_datetime(df["open_date"], utc=True)
    df["close_date"] = pd.to_datetime(df["close_date"], utc=True)
    return df.sort_values("close_date").reset_index(drop=True)


def metrics(df: pd.DataFrame, days: float) -> dict:
    if df.empty:
        return {"n": 0}
    gains = df.loc[df.profit_abs > 0, "profit_abs"].sum()
    losses = -df.loc[df.profit_abs < 0, "profit_abs"].sum()
    equity = pd.concat([pd.Series([START_BALANCE]), START_BALANCE + df["profit_abs"].cumsum()])
    rgain = df.loc[df.r > 0, "r"].sum()
    rloss = -df.loc[df.r < 0, "r"].sum()
    return {
        "n": len(df),
        "per_day": len(df) / days,
        "winrate": float((df.profit_abs > 0).mean()),
        "avg_r": float(df.r.mean()),
        "total_r": float(df.r.sum()),
        "pf": float(gains / losses) if losses > 0 else float("inf"),
        "pf_r": float(rgain / rloss) if rloss > 0 else float("inf"),
        "max_dd": mr.max_drawdown(equity.reset_index(drop=True)),
        "max_dd_r": float((df.r.cumsum().cummax().clip(lower=0) - df.r.cumsum()).max()),
        "net_pct": float(df.profit_abs.sum() / START_BALANCE),
        "funding": float(df.funding.sum()),
        "avg_minutes": float(df.minutes.mean()),
    }


def pauses(df: pd.DataFrame) -> int:
    """Number of 3-loss pauses the account went through (same rule as the strategy)."""
    n = streak = 0
    for p in df.sort_values("close_date").profit_abs:
        if p < 0:
            streak += 1
            if streak >= 3:
                n += 1
                streak = 0
        else:
            streak = 0
    return n


def f(x, d=2):
    return mr.fmt(x, d)


def p(x):
    return mr.fmt_pct(x)


def analyse(name: str, strat: str, st: dict, out: Path, pairs: list[str]) -> tuple[str, dict]:
    df = trades_frame(st["trades"])
    start = pd.Timestamp(st["backtest_start"])
    end = pd.Timestamp(st["backtest_end"])
    start = start.tz_localize("UTC") if start.tzinfo is None else start
    end = end.tz_localize("UTC") if end.tzinfo is None else end
    days = (end - start).total_seconds() / 86400
    res = {"all": metrics(df, days), "long": metrics(df[df.side == "long"], days),
           "short": metrics(df[df.side == "short"], days),
           "ft_max_dd_account": st.get("max_drawdown_account"), "days": days, "pauses": pauses(df)}
    lines = [f"### {name} — `{strat}`", ""]
    lines += ["| Taraf | İşlem | Günde | Kazanan | Ort. R | Toplam R | PF (USDT) | PF (R) | Max DD (kasa) | Max DD (R) | Net | Funding (USDT) | Ort. süre (dk) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for side in ("all", "long", "short"):
        m = res[side]
        label = {"all": "toplam", "long": "long", "short": "short"}[side]
        if m["n"] == 0:
            lines.append(f"| {label} | 0 | | | | | | | | | | | |")
            continue
        lines.append(f"| {label} | {m['n']} | {f(m['per_day'])} | {p(m['winrate'])} | {f(m['avg_r'], 3)} | "
                     f"{f(m['total_r'], 1)} | {f(m['pf'])} | {f(m['pf_r'])} | {p(m['max_dd']) if side == 'all' else '—'} | "
                     f"{f(m['max_dd_r'], 1)} | {p(m['net_pct'])} | {f(m['funding'], 0)} | {f(m['avg_minutes'], 0)} |")
    lines.append("")
    lines.append(f"Freqtrade'in hesap düşüşü: {p(st.get('max_drawdown_account'))}. "
                 f"3 kayıp → 24 saat duraklaması: **{res['pauses']}** kez. "
                 f"Ortalama kaldıraç: {f(df.leverage.mean(), 1)}x.")
    lines.append("")
    fx = df.outcome == "force_exit"
    res["force_exit"] = int(fx.sum())
    res["avg_r_ex_force_exit"] = float(df.loc[~fx, "r"].mean())
    for side in ("long", "short"):
        res[f"avg_r_ex_force_exit_{side}"] = float(df.loc[~fx & (df.side == side), "r"].mean())
    if fx.any():
        lines.append(f"Veri sonunda zorla kapatılan işlem: {int(fx.sum())} (ortalama {f(df.loc[fx, 'r'].mean(), 1)}R). "
                     f"Bunlar hariç ortalama: toplam **{f(res['avg_r_ex_force_exit'], 3)}R**, long "
                     f"{f(res['avg_r_ex_force_exit_long'], 3)}R, short {f(res['avg_r_ex_force_exit_short'], 3)}R.")
        lines.append("")

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

    g = df.groupby("pair").agg(n=("r", "size"), avg_r=("r", "mean"), total_r=("r", "sum"), net=("profit_abs", "sum"))
    gl = df[df.side == "long"].groupby("pair")["r"].mean()
    gs = df[df.side == "short"].groupby("pair")["r"].mean()
    res["coins_positive"] = int((g.net > 0).sum())
    res["coins_total"] = len(pairs)
    lines += ["| Coin | İşlem | Ort. R | Long ort. R | Short ort. R | Toplam R | Net (USDT) |", "|---|---|---|---|---|---|---|"]
    for pair in pairs:
        if pair not in g.index:
            lines.append(f"| {pair.split('/')[0]} | 0 | | | | | |")
            continue
        r = g.loc[pair]
        lines.append(f"| {pair.split('/')[0]} | {int(r.n)} | {f(r.avg_r, 3)} | {f(gl.get(pair, np.nan), 3)} | "
                     f"{f(gs.get(pair, np.nan), 3)} | {f(r.total_r, 1)} | {f(r.net, 0)} |")
    lines.append("")
    lines.append(f"Artıda biten coin: **{res['coins_positive']}/{len(pairs)}**.")
    lines.append("")

    # outcomes
    oc = df.groupby(["side", "outcome"]).r.agg(["size", "mean"])
    lines += ["| Taraf | Sonuç | İşlem | Pay | Ort. R |", "|---|---|---|---|---|"]
    for (side, outcome), row in oc.iterrows():
        tot = (df.side == side).sum()
        lines.append(f"| {side} | {outcome} | {int(row['size'])} | {row['size'] / tot * 100:.0f}% | {f(row['mean'], 3)} |")
    lines.append("")
    res["outcomes"] = {f"{s}_{o}": int(v) for (s, o), v in oc["size"].items()}

    # TP1 < 1R (project rule TP1 >= 1R; not filtered, counted)
    real = df[df.outcome != "force_exit"]  # end-of-data exits are not rule outcomes
    small = real[real.tp1r < 1.0]
    big = real[real.tp1r >= 1.0]
    res["tp1_below_1r"] = {"n": len(small), "share": len(small) / len(real), "avg_r": float(small.r.mean()) if len(small) else None,
                           "avg_r_rest": float(big.r.mean()) if len(big) else None, "median_tp1r": float(df.tp1r.median())}
    lines.append(f"TP1 < 1R olan işlem (veri sonunda zorla kapatılanlar hariç): **{len(small)}/{len(real)}** "
                 f"({len(small) / len(real) * 100:.0f}%), ortalama "
                 f"{f(small.r.mean(), 3)}R; TP1 ≥ 1R olanlar {f(big.r.mean(), 3)}R. TP1 mesafesi ortancası "
                 f"{f(df.tp1r.median())}R (sinyal kapanışına göre).")
    lines.append("")
    res["stop_pct_median"] = float(df.stop_pct.median())
    cost_r = 2 * 0.001 / df.stop_pct  # entry + exit at the main 0.1%/order cost, in R
    lines.append(f"Stop mesafesi ortancası: **%{df.stop_pct.median() * 100:.2f}** (çeyrekler %{df.stop_pct.quantile(.25) * 100:.2f} – "
                 f"%{df.stop_pct.quantile(.75) * 100:.2f}). Normal masrafta (%0.1/emir) giriş+çıkış masrafı ortanca "
                 f"**{cost_r.median():.2f}R**.")
    lines.append("")

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
                              "yearly": yearly}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pairs", default="config/pairs_btc_eth_sol.json")
    ap.add_argument("--run", action="append", required=True, help="name=path (backtest zip)")
    ap.add_argument("--tables", default="analiz_tablolari.md")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pairs = json.loads((REPO / a.pairs).read_text())["exchange"]["pair_whitelist"]
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
    (out / a.tables).write_text("\n\n".join(md) + "\n")
    (out / a.tables.replace(".md", ".json")).write_text(json.dumps(summary, indent=1, default=float))
    print("\n\n".join(md))


if __name__ == "__main__":
    main()
