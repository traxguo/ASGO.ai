"""
Rejection funnel of the frozen Nasdaq rule (AslanLiq2_1h, daily bias filter), dev + val only
(2020-01 .. 2026-03; the holdout is not loaded). Aslan (via GUO, 2026-11-06): "about 10 trades a month
means the rules are too strict ... it refuses to enter too often". This shows where candidate setups die,
without changing any rule, and draws random rejected setups for Aslan to mark "would take / would not".

Stages (in the order the code applies them):
  1. liquidity sweep: a 1d / 4h swing or previous-day level is taken -> a setup opens (12 1h candles)
  2. MSS or iFVG confirmation inside those 12 candles          (else: "no confirmation")
  3. stop on the right side of the signal close                  (else: "stop invalid")
  4. stop distance <= 8%                                         (else: "stop too wide")
  5. daily bias in the trade direction                           (else: "bias neutral" / "bias opposite")
  6. no FOMC / CPI / NFP within 1 hour                           (else: "news")
  7. not a long and a short signal on the same candle            (else: "long+short same candle")
  8. stop not too small for the 1% risk at 20x                   (else: "stop too small")
  9. no trade or order already open on NAS100                    (else: "already in a trade")
 10. the limit order at the signal close fills within 2 candles  (else: "not filled" / "stop before fill")
The rule has no session filter (Aslan: "can enter any time"); a "max open" limit exists only as 9.

The instrumented loop below repeats strategies/candidates/aslan_liquidity.find_signals step by step and
the script asserts that it gives exactly the same signals, and that the instrumented order replay gives
exactly the same trades as sim.replay.

    python research/aslan_nasdaq/funnel.py --out funnel_out
"""

from __future__ import annotations

import argparse
import heapq
import sys
from bisect import bisect_left
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim  # noqa: E402
from sim import news_calendar, v1  # noqa: E402

END = pd.Timestamp("2026-04-01", tz="UTC")  # dev + val only
CLS = v1.AslanLiq2_1h
NY = "America/New_York"

KILL_TR = {
    "no confirmation": "12 saat içinde MSS / iFVG teyidi gelmedi",
    "stop invalid": "stop, sinyal kapanışının yanlış tarafında",
    "stop too wide": "stop %8'den uzak",
    "bias neutral": "günlük yön nötr (ne yukarı ne aşağı)",
    "bias opposite": "günlük yön ters",
    "news": "1 saat içinde önemli ABD haberi",
    "long+short same candle": "aynı mumda hem long hem short sinyali",
    "stop too small": "stop çok dar (%0.05 altı)",
    "already in a trade": "zaten açık işlem / bekleyen emir var",
    "not filled": "limit emir 2 mumda dolmadı",
    "stop before fill": "emir dolmadan önce stop'a değdi",
    "trade": "işleme girildi",
}


def labelled_levels(d1: pd.DataFrame, h4: pd.DataFrame) -> pd.DataFrame:
    """Same levels as AslanLiqBase.populate_indicators, with where each one comes from."""
    def swings(df, mins, name):
        x = v1.htf_levels(df, mins)
        x["src"] = np.where(x["side"] == "high", f"{name} tepe", f"{name} dip")
        return x
    prev = v1.htf_levels(d1, 1440, prev_day=True)
    sw = v1.htf_levels(d1, 1440)
    key = set(zip(sw["avail"], sw["price"], sw["side"]))
    prev = prev[[k not in key for k in zip(prev["avail"], prev["price"], prev["side"])]].copy()
    prev["src"] = np.where(prev["side"] == "high", "önceki gün tepesi", "önceki gün dibi")
    out = pd.concat([swings(d1, 1440, "günlük"), prev, swings(h4, 240, "4 saatlik")], ignore_index=True)
    return out.sort_values("avail", kind="stable").reset_index(drop=True)


def _rank(src: str) -> int:
    return 0 if src.startswith("günlük") else 1 if src.startswith("önceki") else 2


def setups(df: pd.DataFrame, levels: pd.DataFrame, setup_window: int, wick_cap: float) -> list[dict]:
    """find_signals with a log: one record per setup (sweep that opened it, how it ended)."""
    o, h, lo, c = (df[x].to_numpy(float) for x in ("open", "high", "low", "close"))
    t_open = pd.to_datetime(df["date"], utc=True).to_numpy(dtype="datetime64[ns]")
    n = len(df)
    ph, pl = v1.pivots(h, lo)
    lv_time = pd.to_datetime(levels["avail"], utc=True).dt.tz_localize(None).to_numpy(dtype="datetime64[ns]")
    lv_price, lv_side, lv_src = levels["price"].to_numpy(float), levels["side"].to_numpy(), levels["src"].to_numpy()
    lows_heap, highs_heap, ph_idx, pl_idx = [], [], [], []
    li = 0
    setup = {"long": None, "short": None}
    log = []
    for k in range(n):
        while li < len(lv_time) and lv_time[li] <= t_open[k]:
            if lv_side[li] == "low":
                heapq.heappush(lows_heap, (-lv_price[li], lv_src[li]))
            else:
                heapq.heappush(highs_heap, (lv_price[li], lv_src[li]))
            li += 1
        j = k - v1.PIVOT_N
        if j >= 0 and ph[j]:
            ph_idx.append(j)
        if j >= 0 and pl[j]:
            pl_idx.append(j)
        swept_low = []
        while lows_heap and -lows_heap[0][0] > lo[k]:
            p, s = heapq.heappop(lows_heap)
            swept_low.append((-p, s))
        swept_high = []
        while highs_heap and highs_heap[0][0] < h[k]:
            p, s = heapq.heappop(highs_heap)
            swept_high.append((p, s))
        # for the label only: the most important level taken on this candle (daily > previous day > 4h)
        swept_low = min(swept_low, key=lambda x: _rank(x[1])) if swept_low else None
        swept_high = min(swept_high, key=lambda x: _rank(x[1])) if swept_high else None
        for side, swept in (("long", swept_low), ("short", swept_high)):
            st = setup[side]
            if st is not None and k - st["start"] > setup_window:
                st["end"], st["kill"] = k - 1, "no confirmation"
                setup[side] = st = None
            if swept:
                if st is None:
                    st = setup[side] = {"side": side, "first": k, "start": k, "ext": k, "level": swept[0],
                                        "src": swept[1], "resweeps": 0}
                    log.append(st)
                else:
                    st["start"] = k
                    st["resweeps"] += 1
            if st is None:
                continue
            e = st["ext"]
            if (side == "long" and lo[k] < lo[e]) or (side == "short" and h[k] > h[e]):
                st["ext"] = e = k
            trig = ""
            if side == "long":
                pos = bisect_left(ph_idx, e) - 1
                if pos >= 0 and c[k] > h[ph_idx[pos]]:
                    trig, st["ref"] = "mss", ("price", ph_idx[pos], h[ph_idx[pos]])
                else:
                    for f in range(max(2, st["start"] - 10), k):
                        top = lo[f - 2]
                        if h[f] < top and c[k] > top and c[f + 1:k].max(initial=-np.inf) <= top:
                            trig, st["ref"] = "ifvg", ("gap", f, h[f], top)
                            break
            else:
                pos = bisect_left(pl_idx, e) - 1
                if pos >= 0 and c[k] < lo[pl_idx[pos]]:
                    trig, st["ref"] = "mss", ("price", pl_idx[pos], lo[pl_idx[pos]])
                else:
                    for f in range(max(2, st["start"] - 10), k):
                        bottom = h[f - 2]
                        if lo[f] > bottom and c[k] < bottom and c[f + 1:k].min(initial=np.inf) >= bottom:
                            trig, st["ref"] = "ifvg", ("gap", f, bottom, lo[f])
                            break
            if trig:
                st.update(end=k, trig=trig, sig_k=k,
                          stop=v1.stop_from_candle(side, o[e], h[e], lo[e], c[e], wick_cap))
                setup[side] = None
    for side in ("long", "short"):
        if setup[side] is not None:
            setup[side].update(end=n - 1, kill="no confirmation (data end)")
    return log


def replay_log(p: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """sim.replay with the fate of every signal candle: {k: fate}."""
    t = pd.to_datetime(p["date"], utc=True).to_numpy(dtype="datetime64[ns]").astype("int64") // 60_000_000_000
    o, h, lo = (p[c].to_numpy(float) for c in ("open", "high", "low"))
    sig = {s: p[f"{s}_sig"].to_numpy() for s in ("long", "short")}
    ent = {s: p[f"{s}_entry"].to_numpy(float) for s in ("long", "short")}
    stp = {s: p[f"{s}_stop"].to_numpy(float) for s in ("long", "short")}
    tgt = {s: p[f"{s}_tp"].to_numpy(float) for s in ("long", "short")}
    valid = p.attrs["valid_min"]
    fate, rows = {}, []
    order = pos = None
    for j in range(1, len(p)):
        if order is not None:
            if t[j] >= order["t0"] + valid or order["stop_seen"]:
                fate[order["k"]] = "stop before fill" if order["stop_seen"] else "not filled"
                order = None
        k = j - 1
        for side in ("long", "short"):
            if not sig[side][k]:
                continue
            if order is not None or pos is not None:
                fate[k] = "already in a trade"
                continue
            if abs(ent[side][k] - stp[side][k]) / ent[side][k] < sim.MIN_STOP_PCT:
                fate[k] = "stop too small"
                continue
            price = min(ent[side][k], h[j]) if side == "long" else max(ent[side][k], lo[j])
            order = {"side": side, "t0": t[j], "price": price, "stop": stp[side][k], "tp": tgt[side][k],
                     "stop_seen": False, "k": k}
            break
        filled_now = False
        if order is not None:
            if lo[j] <= order["price"] <= h[j]:
                pos = {**order, "entry": order["price"], "t_in": t[j]}
                fate[order["k"]] = "trade"
                order, filled_now = None, True
            else:
                s = order["side"]
                order["stop_seen"] = lo[j] <= order["stop"] if s == "long" else h[j] >= order["stop"]
        if pos is not None:
            s, stop, tp = pos["side"], pos["stop"], pos["tp"]
            px = None
            if s == "long":
                if lo[j] <= stop:
                    px = stop if (o[j] > stop or filled_now) else o[j]
                elif h[j] >= tp:
                    px = tp
            else:
                if h[j] >= stop:
                    px = stop if (o[j] < stop or filled_now) else o[j]
                elif lo[j] <= tp:
                    px = tp
            if px is not None:
                sign = 1 if s == "long" else -1
                rows.append((pd.Timestamp(pos["t_in"] * 60_000_000_000, tz="UTC"), s,
                             sign * (px - pos["entry"]) / abs(pos["entry"] - stop)))
                pos = None
    return fate, pd.DataFrame(rows, columns=["t_in", "side", "gross_r"])


def funnel(f: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df, d1, h4 = f["1h"], f["1d"], f["4h"]
    lv = labelled_levels(d1, h4)
    log = setups(df, lv, CLS.setup_window, CLS.wick_cap)

    # check: identical signals to the strategy code
    ref = v1.find_signals(df, pd.concat([v1.htf_levels(d1, 1440, prev_day=True), v1.htf_levels(h4, 240)],
                                        ignore_index=True).sort_values("avail", kind="stable"),
                          CLS.setup_window, wick_cap=CLS.wick_cap)
    mine = {(s["side"], s["sig_k"]) for s in log if "sig_k" in s}
    theirs = {(side, k) for side in ("long", "short") for k in np.flatnonzero(ref[f"{side}_trigger"].to_numpy() != "")}
    assert mine == theirs, f"instrumented signals differ: {len(mine ^ theirs)}"

    p = sim.signals_v2(f, "1h", True)
    fate, trades = replay_log(p)
    r = sim.replay(p)
    assert len(r) == len(trades) and np.allclose(r["gross_r"].to_numpy(), trades["gross_r"].to_numpy()), \
        "instrumented replay differs from sim.replay"

    c = df["close"].to_numpy(float)
    mins = 60
    bias = sim.asof(df, mins, v1.daily_bias(d1), "bias")
    news = news_calendar.blocked(sim.close_time(df, mins), CLS.news_before, CLS.news_after).to_numpy()
    both = (p["long_sig"] | p["short_sig"]).to_numpy()  # after the same-candle cancel
    raw_both = np.zeros(len(df), bool)
    for s in log:
        s["date"] = pd.Timestamp(df["date"].iloc[s["first"]])
        if "sig_k" not in s:
            s["kill"] = s.get("kill", "no confirmation")
            s["bias"] = int(bias[s["end"]])  # shown on the chart only
            continue
        k, side, stop = s["sig_k"], s["side"], s["stop"]
        sign = 1 if side == "long" else -1
        stop_pct = abs(c[k] - stop) / c[k]
        if not (stop < c[k] if side == "long" else stop > c[k]):
            s["kill"] = "stop invalid"
        elif not (0 < stop_pct <= sim.MAX_STOP_PCT):
            s["kill"] = "stop too wide"
        elif bias[k] != sign:
            s["kill"] = "bias neutral" if bias[k] == 0 else "bias opposite"
        elif news[k]:
            s["kill"] = "news"
        elif not both[k]:
            s["kill"] = "long+short same candle"
        else:
            s["kill"] = fate.get(k, "not filled (data end)")
        s["bias"] = int(bias[k])
        raw_both[k] = True
    tab = pd.DataFrame([{k: s.get(k) for k in ("date", "side", "first", "end", "sig_k", "trig", "level", "src",
                                               "stop", "resweeps", "kill", "bias", "ext", "ref")} for s in log])
    tab = tab[tab["date"] < END].reset_index(drop=True)
    return tab, p, {"trades": len(r[r["t_in"] < END])}


ORDER = ["no confirmation", "stop invalid", "stop too wide", "bias neutral", "bias opposite", "news",
         "long+short same candle", "stop too small", "already in a trade", "stop before fill", "not filled", "trade"]


def report(tab: pd.DataFrame) -> str:
    tab = tab.copy()
    tab["kill"] = tab["kill"].str.replace(r" \(data end\)", "", regex=True)
    months = tab["date"].dt.tz_convert(None).dt.to_period("M").nunique()
    lines = [f"Setups (liquidity sweeps that opened a setup): {len(tab)} in {months} months "
             f"({len(tab) / months:.1f}/month); re-sweeps inside an open setup are not counted again.", "",
             "| Stage killed at | Setups | Share | Per month | Left after this stage | Long / short |",
             "|---|---|---|---|---|---|"]
    left = len(tab)
    for k in ORDER:
        x = tab[tab["kill"] == k]
        if k != "trade":
            left -= len(x)
        lines.append(f"| {k} ({KILL_TR[k]}) | {len(x)} | {len(x) / len(tab):.1%} | {len(x) / months:.1f} | "
                     f"{left if k != 'trade' else len(x)} | {(x['side'] == 'long').sum()} / {(x['side'] == 'short').sum()} |")
    lines += ["", "By year (setups / trades / main killers):", ""]
    tab["year"] = tab["date"].dt.year
    for y, g in tab.groupby("year"):
        top = g["kill"].value_counts().head(3)
        lines.append(f"- {y}: {len(g)} setups, {int((g['kill'] == 'trade').sum())} trades; "
                     + ", ".join(f"{k} {v}" for k, v in top.items()))
    lines += ["", "Confirmed setups by daily bias (before the bias filter):", ""]
    conf = tab[tab["sig_k"].notna() & (tab["kill"] != "no confirmation")]
    for side in ("long", "short"):
        g = conf[conf["side"] == side]
        lines.append(f"- {side}: {len(g)} confirmed; bias up {int((g['bias'] == 1).sum())}, "
                     f"neutral {int((g['bias'] == 0).sum())}, down {int((g['bias'] == -1).sum())}")
    lines += ["", "Sweeps by level type:", ""]
    for src, g in tab.groupby("src"):
        lines.append(f"- {src}: {len(g)} setups, {int((g['kill'] == 'trade').sum())} trades")
    return "\n".join(lines)


# ---------------------------------------------------------------- charts

SURF, T1, T2, GRID = "#1a1a19", "#ffffff", "#c3c2b7", "#33332f"
BLUE, ORANGE, GREEN, RED, PURPLE = "#3987e5", "#d95926", "#199e70", "#d03b3b", "#9a6bd8"


def fmt(v: float) -> str:
    return f"{v:,.0f}".replace(",", ".") if v >= 1000 else f"{v:.2f}"


def draw(no: int, s: pd.Series, df: pd.DataFrame, out: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    lbl = dict(boxstyle="round,pad=0.2", fc=SURF, ec="none", alpha=0.85)
    o, h, lo, c = (df[x].to_numpy(float) for x in ("open", "high", "low", "close"))
    dates = pd.to_datetime(df["date"], utc=True).dt.tz_convert(NY).dt.tz_localize(None)
    side, first, end = s["side"], int(s["first"]), int(s["end"])
    a, b = max(0, first - 36), min(len(df), end + 24)
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=110)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    w = pd.Timedelta(minutes=60) * 0.6
    span = h[a:b].max() - lo[a:b].min()
    for i in range(a, b):
        col = "#e8e6df" if c[i] >= o[i] else "#7d7b73"
        ax.vlines(dates[i], lo[i], h[i], color=col, lw=0.9, zorder=3)
        ax.bar(dates[i], max(abs(c[i] - o[i]), span * 0.002), bottom=min(o[i], c[i]), width=w, color=col, zorder=3)
    x0, x1 = dates[a], dates[b - 1]
    level = float(s["level"])
    ax.hlines(level, x0, dates[first], color=BLUE, lw=2, ls="--", zorder=2)
    ax.text(x0, level, f" Likidite {fmt(level)} ({s['src']})", color=BLUE, bbox=lbl, zorder=8, fontsize=9,
            va="bottom" if side == "short" else "top")
    ax.axvspan(dates[first], dates[min(first + CLS.setup_window, len(df) - 1)], color=BLUE, alpha=0.08, zorder=0)
    ax.annotate("1) Likidite alındı", (dates[first], lo[first] if side == "long" else h[first]),
                xytext=(-80, -35 if side == "long" else 35), textcoords="offset points", color=T1, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=T2))
    if pd.notna(s["sig_k"]):
        k = int(s["sig_k"])
        ref = s["ref"]
        if ref[0] == "price":
            ax.hlines(ref[2], dates[ref[1]], dates[k], color=ORANGE, lw=1.5, zorder=2)
            ax.text(dates[ref[1]], ref[2], " kırılan küçük tepe/dip", color=ORANGE, bbox=lbl, zorder=8, fontsize=8)
        else:
            ax.add_patch(plt.Rectangle((mdates.date2num(dates[ref[1]]), ref[2]),
                                       mdates.date2num(dates[k]) - mdates.date2num(dates[ref[1]]), ref[3] - ref[2],
                                       color=ORANGE, alpha=0.3, zorder=1))
        trig = "MSS (son küçük tepe/dip kırıldı)" if s["trig"] == "mss" else "iFVG (boşluk ters kırıldı)"
        ax.annotate(f"2) Teyit: {trig}", (dates[k], c[k]), xytext=(-220, 70 if side == "long" else -70),
                    textcoords="offset points", color=T1, bbox=lbl, zorder=8, fontsize=9,
                    arrowprops=dict(arrowstyle="->", color=ORANGE))
        entry, stop = c[k], float(s["stop"])
        tp = entry + (2 if side == "long" else -2) * abs(entry - stop)
        ax.hlines(entry, dates[k], x1, color=GREEN, lw=1.2, zorder=2)
        ax.text(x1, entry, f"giriş olurdu {fmt(entry)} ", color=GREEN, bbox=lbl, zorder=8, fontsize=9, ha="right")
        ax.hlines(stop, dates[k], x1, color=RED, lw=1.2, zorder=2)
        ax.text(x1, stop, f"stop {fmt(stop)} ", color=RED, bbox=lbl, zorder=8, fontsize=9, ha="right")
        ax.hlines(tp, dates[k], x1, color=GREEN, lw=1.2, ls=":", zorder=2)
        ax.text(x1, tp, f"hedef 2R {fmt(tp)} ", color=GREEN, bbox=lbl, zorder=8, fontsize=9, ha="right")
    kill = s["kill"].replace(" (data end)", "")
    ax.text(0.01, 0.02, f"ELENDİ: {KILL_TR[kill]}", transform=ax.transAxes, color=RED, fontsize=12,
            fontweight="bold", bbox=lbl)
    ax.yaxis.tick_right()
    ax.tick_params(colors=T2, labelsize=8)
    ax.grid(color=GRID, lw=0.5)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m %H:%M"))
    bias = {1: "yukarı", -1: "aşağı", 0: "nötr"}.get(s["bias"], "—") if pd.notna(s["bias"]) else "—"
    ax.set_title(f"#{no}  NASDAQ 1 saat  {dates[first]:%d.%m.%Y} (saat New York)  "
                 f"{'LONG (dip alındı)' if side == 'long' else 'SHORT (tepe alındı)'}   günlük yön: {bias}",
                 color=T1, fontsize=12, loc="left")
    plt.tight_layout()
    path = out / f"red_{no:02d}.png"
    plt.savefig(path, facecolor=SURF)
    plt.close(fig)
    return path


def sample(tab: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    """Random rejected setups, every killing rule with >= 2 cases gets at least 2, rest proportional."""
    rej = tab[~tab["kill"].isin(["trade"]) & ~tab["kill"].str.contains("data end")]
    rng = np.random.default_rng(seed)
    counts = rej["kill"].value_counts()
    alloc = {k: min(2, v) for k, v in counts.items()}
    rest = n - sum(alloc.values())
    if rest > 0:
        share = (counts - pd.Series(alloc)).clip(lower=0)
        extra = np.floor(share / share.sum() * rest).astype(int)
        while extra.sum() < rest:
            extra[(share / share.sum() * rest - extra).idxmax()] += 1
        for k, v in extra.items():
            alloc[k] += int(v)
    picks = []
    for k, m in alloc.items():
        idx = rej.index[rej["kill"] == k].to_numpy()
        picks += list(rng.choice(idx, size=min(m, len(idx)), replace=False))
    return tab.loc[sorted(picks)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--data", type=Path, default=sim.DATA / "NAS100_1m.feather")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    m1 = sim.load_1m(a.data)
    m1 = m1[m1.index < END]
    f = sim.frames(m1, session=True)
    tab, p, info = funnel(f)
    rep = report(tab)
    print(rep)
    print(f"\ntrades from sim.replay (dev+val): {info['trades']}")
    (a.out / "funnel.md").write_text(rep + "\n", encoding="utf-8")
    monthly = tab.assign(month=tab["date"].dt.tz_convert(None).dt.to_period("M").astype(str),
                         kill=tab["kill"].str.replace(r" \(data end\)", "", regex=True))
    monthly.pivot_table(index="month", columns="kill", values="side", aggfunc="count", fill_value=0) \
        .reindex(columns=[k for k in ORDER if k in set(monthly["kill"])]).to_csv(a.out / "monthly.csv")
    pick = sample(tab, a.n, a.seed)
    rows = []
    for no, (_, s) in enumerate(pick.iterrows(), 1):
        draw(no, s, f["1h"], a.out)
        rows.append({"no": no, "date_ny": pd.Timestamp(s["date"]).tz_convert(NY).strftime("%d.%m.%Y %H:%M"),
                     "side": s["side"], "level": round(float(s["level"]), 2), "level_src": s["src"],
                     "killed_by": s["kill"], "killed_by_tr": KILL_TR[s["kill"]], "trigger": s["trig"] or ""})
    pd.DataFrame(rows).to_csv(a.out / "rejected.csv", index=False)
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt

    with PdfPages(a.out / "aslan_nas_reddedilen_20.pdf") as pdf:
        for no in range(1, len(rows) + 1):
            img = mpimg.imread(a.out / f"red_{no:02d}.png")
            fig = plt.figure(figsize=(12, 7.5))
            plt.imshow(img)
            plt.axis("off")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
