#!/usr/bin/env python3
"""
First-stage analysis for vwap_reversion (cards/vwap_reversion.md).

R per trade comes from the planned stop in the enter_tag (same formula as
scripts/make_report.py): R = profit_abs / (entry amount * |entry price - stop|),
costs and funding included (profit_abs is net).

Prints markdown tables per run (overall and long/short, trades per day, win
rate, avg R, PF, max DD, net, yearly, per coin, outcome, pattern, cost in R,
leverage need, 3-loss pauses), a signal-level count (how many signals the
0.3R rule and the TP1 >= 1R rule remove), buy-and-hold of the same coins, and
saves equity charts.

Usage:
  python research/reports/vwap_reversion_analysis.py --out results/<folder> \
      --run normal=<backtest dir or zip> --run fee_x2=<...> ...
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from freqtrade.data.btanalysis import load_backtest_stats

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
_spec = importlib.util.spec_from_file_location("make_report", REPO / "scripts" / "make_report.py")
mr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mr)

from strategies.candidates import vwap_reversion as vr  # noqa: E402

START_BALANCE = 10000.0
YEARS = [2022, 2023, 2024]
DATADIR = REPO / "user_data" / "data" / "binance"


def trades_frame(trades: list[dict]) -> pd.DataFrame:
    rows = []
    for t in trades:
        info = mr.trade_r(t)
        stop = float(mr.STOP_RE.search(t["enter_tag"]).group(1))
        rows.append({**info, "pair": t["pair"], "profit_abs": t["profit_abs"],
                     "funding": t.get("funding_fees") or 0.0, "open_date": t["open_date"],
                     "close_date": t["close_date"], "open_rate": t["open_rate"], "stop": stop,
                     "leverage": t["leverage"], "pattern": t["enter_tag"].split()[1],
                     "minutes": t["trade_duration"], "fee": t.get("fee_open") or 0.0})
    df = pd.DataFrame(rows)
    df["open_date"] = pd.to_datetime(df["open_date"], utc=True)
    df["close_date"] = pd.to_datetime(df["close_date"], utc=True)
    df["stop_pct"] = (df.open_rate - df.stop).abs() / df.open_rate
    return df.sort_values("close_date").reset_index(drop=True)


def metrics(df: pd.DataFrame, days: float, start_balance: float = START_BALANCE) -> dict:
    if df.empty:
        return {"n": 0}
    gains = df.loc[df.profit_abs > 0, "profit_abs"].sum()
    losses = -df.loc[df.profit_abs < 0, "profit_abs"].sum()
    equity = pd.concat([pd.Series([start_balance]), start_balance + df["profit_abs"].cumsum()])
    return {
        "n": len(df),
        "per_day": len(df) / days,
        "winrate": float((df.profit_abs > 0).mean()),
        "avg_r": float(df.r.mean()),
        "total_r": float(df.r.sum()),
        "pf": float(gains / losses) if losses > 0 else float("inf"),
        "max_dd": mr.max_drawdown(equity.reset_index(drop=True)),
        "max_dd_r": float((df.r.cumsum().cummax().clip(lower=0) - df.r.cumsum()).max()),
        "net_pct": float(df.profit_abs.sum() / start_balance),
        "funding": float(df.funding.sum()),
        "avg_minutes": float(df.minutes.mean()),
    }


def f(x, d=2):
    return mr.fmt(x, d)


def p(x):
    return mr.fmt_pct(x)


def pause_check(df: pd.DataFrame) -> tuple[int, int]:
    """Number of 3-loss pauses and number of trades opened inside a pause (must be 0)."""
    streak, pauses, violations = 0, [], 0
    for _, t in df.sort_values("close_date").iterrows():
        if t.profit_abs < 0:
            streak += 1
            if streak >= vr.LOSS_STREAK:
                pauses.append((t.close_date, t.close_date + timedelta(hours=vr.HALT_HOURS)))
                streak = 0
        else:
            streak = 0
    for a, b in pauses:
        # entry order is placed at open_date; a trade opened strictly inside a pause is a violation
        violations += int(((df.open_date > a) & (df.open_date < b)).sum())
    return len(pauses), violations


def analyse(name: str, strat: str, st: dict, out: Path) -> tuple[str, dict]:
    df = trades_frame(st["trades"])
    pairs = st.get("pairlist") or sorted(df.pair.unique())
    start = pd.Timestamp(st["backtest_start"])
    end = pd.Timestamp(st["backtest_end"])
    days = (end - start).total_seconds() / 86400
    sb = float(st.get("starting_balance") or START_BALANCE)
    res = {"all": metrics(df, days, sb), "long": metrics(df[df.side == "long"], days, sb),
           "short": metrics(df[df.side == "short"], days, sb), "starting_balance": sb,
           "ft_max_dd_account": st.get("max_drawdown_account"), "days": days, "pairs": pairs}
    lines = [f"### {name} — `{strat}` ({len(pairs)} coin, en fazla {st.get('max_open_trades')} açık işlem)", ""]
    lines += ["| Taraf | İşlem | Günde | Kazanan | Ort. R | Toplam R | PF | Max DD (kasa) | Max DD (R) | Net | Funding (USDT) | Ort. süre (dk) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for side in ("all", "long", "short"):
        m = res[side]
        label = {"all": "toplam", "long": "long", "short": "short"}[side]
        if m["n"] == 0:
            lines.append(f"| {label} | 0 | | | | | | | | | | |")
            continue
        lines.append(f"| {label} | {m['n']} | {f(m['per_day'])} | {p(m['winrate'])} | {f(m['avg_r'], 3)} | "
                     f"{f(m['total_r'], 1)} | {f(m['pf'])} | {p(m['max_dd']) if side == 'all' else '—'} | "
                     f"{f(m['max_dd_r'], 1)} | {p(m['net_pct'])} | {f(m['funding'], 0)} | {f(m['avg_minutes'], 0)} |")
    lines.append("")
    if sb > START_BALANCE:
        lines.append("(Sabit risk koşusu: her işlemin riski 10000 USDT'nin %1'i = 100 USDT, bileşik değil; kasa "
                     "dev tutulduğu için hiç bitmez. Bu koşuda Max DD (kasa) ve Net % anlamsızdır, R sütunlarına bakın.)")
    lines.append(f"(Freqtrade'in hesap düşüşü: {p(st.get('max_drawdown_account'))}. Net %, işlemlerin USDT "
                 f"kâr/zararının başlangıç kasasına ({sb:,.0f}) oranıdır; risk her işlemde güncel kasanın %1'i olduğu için bileşiktir.)")
    lines.append("")

    df["year"] = df.close_date.dt.year
    lines += ["| Yıl | Taraf | İşlem | Ort. R | PF | Net (USDT) |", "|---|---|---|---|---|---|"]
    yearly = {}
    for y in YEARS:
        for side in ("all", "long", "short"):
            d = df[(df.year == y) & ((df.side == side) | (side == "all"))]
            m = metrics(d, 365)
            yearly[f"{y}_{side}"] = {"n": m["n"], "avg_r": m.get("avg_r"), "pf": m.get("pf"),
                                     "net": float(d.profit_abs.sum()), "total_r": float(d.r.sum())}
            if m["n"]:
                lines.append(f"| {y} | {side if side != 'all' else 'toplam'} | {m['n']} | {f(m['avg_r'], 3)} | "
                             f"{f(m['pf'])} | {f(float(d.profit_abs.sum()), 0)} |")
    res["yearly"] = yearly
    res["years_positive"] = sum(1 for y in YEARS if yearly[f"{y}_all"]["total_r"] > 0)
    lines.append("")

    g = df.groupby("pair").agg(n=("r", "size"), avg_r=("r", "mean"), total_r=("r", "sum"),
                               net=("profit_abs", "sum"))
    gl = df[df.side == "long"].groupby("pair")["r"].mean()
    gs = df[df.side == "short"].groupby("pair")["r"].mean()
    res["coins_positive"] = int((g.total_r > 0).sum())
    res["coins_total"] = len(pairs)
    res["per_coin"] = {k: {"n": int(r.n), "avg_r": float(r.avg_r)} for k, r in g.iterrows()}
    lines += ["| Coin | İşlem | Ort. R | Long ort. R | Short ort. R | Toplam R | Net (USDT) |",
              "|---|---|---|---|---|---|---|"]
    for pair in pairs:
        if pair not in g.index:
            lines.append(f"| {pair.split('/')[0]} | 0 | | | | | |")
            continue
        r = g.loc[pair]
        lines.append(f"| {pair.split('/')[0]} | {int(r.n)} | {f(r.avg_r, 3)} | {f(gl.get(pair, np.nan), 3)} | "
                     f"{f(gs.get(pair, np.nan), 3)} | {f(r.total_r, 1)} | {f(r.net, 0)} |")
    lines.append("")
    lines.append(f"Artıda biten coin (toplam R > 0): **{res['coins_positive']}/{len(pairs)}**.")
    lines.append("")

    # outcomes and patterns
    oc = df.groupby(["side", "outcome"]).r.agg(["size", "mean"]).reset_index()
    lines += ["| Taraf | Sonuç | İşlem | Ort. R |", "|---|---|---|---|"]
    for _, r in oc.iterrows():
        lines.append(f"| {r.side} | {r.outcome} | {int(r['size'])} | {f(r['mean'], 3)} |")
    lines.append("")
    pt = df.groupby("pattern").r.agg(["size", "mean"])
    lines += ["| Dönüş mumu | İşlem | Ort. R |", "|---|---|---|"]
    for k, r in pt.iterrows():
        lines.append(f"| {k} | {int(r['size'])} | {f(r['mean'], 3)} |")
    lines.append("")
    res["outcomes"] = {f"{r.side}_{r.outcome}": int(r["size"]) for _, r in oc.iterrows()}
    res["patterns"] = {k: {"n": int(r["size"]), "avg_r": float(r["mean"])} for k, r in pt.iterrows()}

    # costs, leverage need, pauses
    fee = float(df.fee.median())
    cost_r = 2 * fee / df.stop_pct
    need_lev = vr.MGMT.risk_per_trade / df.stop_pct
    n_pauses, violations = pause_check(df)
    res.update({"median_stop_pct": float(df.stop_pct.median()), "median_cost_r": float(cost_r.median()),
                "share_need_lev_gt3": float((need_lev > 3).mean()), "pauses": n_pauses,
                "pause_violations": violations, "fee": fee})
    lines.append(f"- Stop mesafesi (medyan): {p(df.stop_pct.median())}; giriş+çıkış masrafı medyan "
                 f"**{f(cost_r.median())}R** (masraf %{fee * 100:.2f}/emir; kısmi çıkış ayrıca masraf öder).")
    lines.append(f"- 1R risk için 3x'ten fazla kaldıraç gereken işlem: {p((need_lev > 3).mean())} "
                 f"(proje kuralı en fazla 3x; GUO kuralı 10x'e kadar).")
    lines.append(f"- 3 kayıp → 24 saat duraklama: {n_pauses} kez devreye girdi; duraklama içinde açılan işlem: {violations}.")
    lines.append("")

    charts = mr.make_charts(f"{strat}_{name}", df[["close_date", "profit_abs", "r"]].copy(), sb, out)
    for c in charts:
        lines.append(f"![{c}]({c})")
    lines.append("")
    return "\n".join(lines), res


def signal_counts(pairs: list[str]) -> tuple[str, dict]:
    """Signal-level counts on development data (before the 1-position limit and pauses)."""
    rows, tot = [], {}
    for pair in pairs:
        fn = DATADIR / "futures" / f"{pair.split(':')[0].replace('/', '_')}_USDT-5m-futures.feather"
        df = pd.read_feather(fn)
        df = df[(df.date >= "2021-12-25") & (df.date < "2025-01-01")].reset_index(drop=True)
        df = vr.plan_columns(vr.vwap_indicators(df))
        conds = vr.signal_conditions(df)
        dev = df.date >= "2022-01-01"
        for side in ("long", "short"):
            c = list(conds[side].values())
            raw = c[0] & c[1] & dev
            ok = raw & df[f"{side}_plan_ok"]
            ok1r = ok & (df[f"{side}_tp1_r"] >= 1.0)
            stop_pct = (df.close - df[f"{side}_stop"]).abs() / df.close
            r = {"pair": pair, "side": side, "raw": int(raw.sum()), "ok": int(ok.sum()), "ok_1r": int(ok1r.sum()),
                 "tp1_vwap": int((ok & df[f"{side}_tp1_is_vwap"]).sum()),
                 "stop_lt_0101": int((ok & (stop_pct < 0.00101)).sum())}
            rows.append(r)
    t = pd.DataFrame(rows)
    s = t[["raw", "ok", "ok_1r", "tp1_vwap", "stop_lt_0101"]].sum()
    tot = {k: int(v) for k, v in s.items()}
    lines = ["| Coin | Taraf | Ham sinyal (uzama + dönüş mumu) | Hedefler ≥ 0.3R (ana sürüm) | TP1 ≥ 1R (varyant) | TP1 = VWAP (sıra değişti) | Stop < %0.101 (10x'e sığmaz) |",
             "|---|---|---|---|---|---|---|"]
    for _, r in t.iterrows():
        lines.append(f"| {r.pair.split('/')[0]} | {r.side} | {r.raw} | {r.ok} | {r.ok_1r} | {r.tp1_vwap} | {r.stop_lt_0101} |")
    lines.append(f"| **Toplam** | | **{tot['raw']}** | **{tot['ok']}** | **{tot['ok_1r']}** | {tot['tp1_vwap']} | {tot['stop_lt_0101']} |")
    lines.append("")
    lines.append(f"TP1 ≥ 1R kuralı, ana sürümün geçerli sinyallerinin **{p(1 - tot['ok_1r'] / tot['ok'])}**'ini "
                 f"({tot['ok'] - tot['ok_1r']} sinyal) eler. (Sinyal sayıları 1 açık işlem sınırı ve duraklamalardan önce.)")
    return "\n".join(lines), tot


def buy_hold(pairs, start, end) -> tuple[str, dict]:
    bh = mr.buy_and_hold(pairs, DATADIR, "5m", start, end)
    yearly = {}
    for y in YEARS:
        yb = mr.buy_and_hold(pairs, DATADIR, "1h", pd.Timestamp(f"{y}-01-01", tz="UTC"),
                             pd.Timestamp(f"{y}-12-31 23:59", tz="UTC"))
        yearly[y] = float(yb["return"].mean())
    lines = ["| Coin | Al-tut getirisi | Al-tut max DD |", "|---|---|---|"]
    for _, r in bh.iterrows():
        lines.append(f"| {r.pair.split('/')[0]} | {p(r['return'])} | {p(r.max_dd)} |")
    lines.append(f"| **Eşit ağırlık ortalama** | **{p(bh['return'].mean())}** | {p(bh.max_dd.mean())} (ortalama) |")
    lines.append("")
    lines.append("Yıllara göre eşit ağırlıklı al-tut: " + ", ".join(f"{y}: {p(v)}" for y, v in yearly.items()))
    return "\n".join(lines), {"mean_return": float(bh["return"].mean()), "yearly": yearly}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--run", action="append", required=True, help="name=path (backtest dir or zip)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    main_pairs = ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT"]
    md, summary = [], {}
    start = end = None
    for spec in a.run:
        name, path = spec.split("=", 1)
        stats = load_backtest_stats(Path(path))
        for strat, st in stats["strategy"].items():
            text, res = analyse(name, strat, st, out)
            md.append(text)
            summary[f"{name}/{strat}"] = res
            start, end = pd.Timestamp(st["backtest_start"]), pd.Timestamp(st["backtest_end"])
    start = start.tz_localize("UTC") if start.tzinfo is None else start
    end = end.tz_localize("UTC") if end.tzinfo is None else end
    text, sig = signal_counts(main_pairs)
    md.append("### Sinyal sayıları (BTC/ETH/SOL, 2022-2024)\n\n" + text)
    summary["signals"] = sig
    text, bh = buy_hold(main_pairs, start, end)
    md.append("### Al-tut (aynı dönem, BTC/ETH/SOL)\n\n" + text)
    summary["buy_and_hold_3"] = bh
    wide = json.loads((REPO / "config" / "pairs_wide16.json").read_text())["exchange"]["pair_whitelist"]
    text, bh16 = buy_hold(wide, start, end)
    md.append("### Al-tut (aynı dönem, 16 coin)\n\n" + text)
    summary["buy_and_hold_16"] = bh16
    (out / "analiz_tablolari.md").write_text("\n\n".join(md) + "\n")
    (out / "ozet.json").write_text(json.dumps(summary, indent=1, default=float))
    print("\n\n".join(md))


if __name__ == "__main__":
    main()
