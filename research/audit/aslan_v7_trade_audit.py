"""
Trade audit charts for aslan_liquidity v7 (sweep -> 5m MSS -> 1m FVG/iFVG, or the
retest variant). Top panel: 5m chart with the liquidity level, the sweep, the
broken swing (MSS), entry, stop, 1R target and exit. Bottom panel: 1m zoom from
the MSS to the entry with the gap that triggered it.

Usage:
  python research/audit/aslan_v7_trade_audit.py --trades results/2026-10-09_aslan_liquidity_v7/AslanLiq7_1m_trades.csv \
      --zips '/tmp/claude-0/bt7/AslanLiq7_1m_[A-Z][A-Z][A-Z]-*.zip' --strategy AslanLiq7_1m --n 10 --out DIR
Dev period trades only.
"""

import argparse
import glob
import sys
from bisect import bisect_left
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from freqtrade.data.btanalysis import load_backtest_stats  # noqa: E402

import make_report as mr  # noqa: E402
from aslan_trade_audit import (  # noqa: E402
    BLUE, DEV_END, GREEN, GRID, LBL, ORANGE, PURPLE, RED, SURF, T1, T2, fmt, labelled_levels, level_source, load,
)
from strategies.candidates import aslan_liquidity_v3 as v3  # noqa: E402
from strategies.candidates.aslan_liquidity import PIVOT_N, pivots  # noqa: E402


def candles(ax, d, a, b, minutes):
    o, h, lo, c = (d[x].to_numpy(float) for x in ("open", "high", "low", "close"))
    w = pd.Timedelta(minutes=minutes) * 0.6
    span = h[a:b].max() - lo[a:b].min()
    for i in range(a, b):
        col = "#e8e6df" if c[i] >= o[i] else "#7d7b73"
        ax.vlines(d["date"].iloc[i], lo[i], h[i], color=col, lw=0.8, zorder=3)
        ax.bar(d["date"].iloc[i], max(abs(c[i] - o[i]), span * 0.002), bottom=min(o[i], c[i]), width=w, color=col, zorder=3)


def style(ax, fmt_x):
    ax.set_facecolor(SURF)
    ax.yaxis.tick_right()
    ax.tick_params(colors=T2, labelsize=8)
    ax.grid(color=GRID, lw=0.5)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt_x))


def gap_1m(m1, k, s0, side):
    """Recreate the 1m trigger gap of aslan_liquidity_v7.find_entries_1m: (kind, x_index, bottom, top)."""
    h = m1["high"].to_numpy(float)
    lo = m1["low"].to_numpy(float)
    c = m1["close"].to_numpy(float)
    if side == "long":
        if k - 2 >= s0 and lo[k] > h[k - 2]:
            return "fvg", k - 2, h[k - 2], lo[k]
        for f in range(s0 + 2, k):
            top = lo[f - 2]
            if h[f] < top and c[k] > top and c[f + 1:k].max(initial=-np.inf) <= top:
                return "ifvg", f - 2, h[f], top
    else:
        if k - 2 >= s0 and h[k] < lo[k - 2]:
            return "fvg", k - 2, h[k], lo[k - 2]
        for f in range(s0 + 2, k):
            bottom = h[f - 2]
            if lo[f] > bottom and c[k] < bottom and c[f + 1:k].min(initial=np.inf) >= bottom:
                return "ifvg", f - 2, bottom, lo[f]
    return None


def draw(no, t, ctx, out_dir, retest):
    m5, sig5, lv, m1 = ctx
    side = "short" if t["is_short"] else "long"
    open_t = pd.Timestamp(t["open_date"])
    close_t = pd.Timestamp(t["close_date"])
    entry = float(t["open_rate"])
    stop = float(t["enter_tag"].split("stop=")[1].split()[0])
    r = mr.trade_r(t)["r"]
    tp = entry + abs(entry - stop) * (1 if side == "long" else -1)

    # the 5m MSS behind this trade: latest one known before the order, same stop
    t5 = m5["date"]
    known = (t5 + pd.Timedelta(minutes=5)) <= open_t
    cand = np.flatnonzero(((sig5[f"{side}_trigger"] == "mss") & known & np.isclose(sig5[f"{side}_struct_stop"], stop)).to_numpy())
    k5 = int(cand[-1])
    start = int(sig5[f"{side}_setup_at"].iloc[k5])
    e = int(sig5[f"{side}_ext_at"].iloc[k5])
    level = float(sig5[f"{side}_level"].iloc[k5])
    src, _ = level_source(lv, level, "low" if side == "long" else "high", t5.iloc[start])
    h5 = m5["high"].to_numpy(float)
    l5 = m5["low"].to_numpy(float)
    ph, pl = pivots(h5, l5)
    idx = [i for i in np.flatnonzero(ph if side == "long" else pl) if i + PIVOT_N <= k5]
    j = idx[bisect_left(idx, e) - 1]
    mss_px = h5[j] if side == "long" else l5[j]

    k_in5 = int(np.searchsorted(t5, open_t, side="right")) - 1
    k_out5 = int(np.searchsorted(t5, close_t, side="right")) - 1
    a = max(0, min(start, j) - 15)
    cut = k_out5 - k_in5 > 100
    b = min(len(m5), (k_in5 + 100 if cut else k_out5) + 6)

    fig, (ax, bx) = plt.subplots(2, 1, figsize=(12, 10), dpi=110, gridspec_kw={"height_ratios": [3, 2]})
    fig.patch.set_facecolor(SURF)
    candles(ax, m5, a, b, 5)
    x0, x1 = t5.iloc[a], t5.iloc[b - 1]
    ax.hlines(level, x0, t5.iloc[start], color=BLUE, lw=2, ls="--", zorder=2)
    ax.text(x0, level, f" Likidite {fmt(level)} ({src})", color=BLUE, bbox=LBL, zorder=8, fontsize=9,
            va="top" if side == "long" else "bottom")
    ax.annotate("1) Likidite alındı", (t5.iloc[start], l5[start] if side == "long" else h5[start]),
                xytext=(-70, -35 if side == "long" else 35), textcoords="offset points", color=T1, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=T2))
    ax.hlines(mss_px, t5.iloc[j], t5.iloc[k5], color=ORANGE, lw=1.5, zorder=2)
    ax.annotate("2) 5 dk MSS: bu seviyenin ötesinde kapanış", (t5.iloc[k5], mss_px),
                xytext=(-230, 50 if side == "long" else -50), textcoords="offset points", color=T1, fontsize=9,
                bbox=LBL, zorder=8, arrowprops=dict(arrowstyle="->", color=ORANGE))
    mk = "^" if side == "long" else "v"
    ax.plot(open_t, entry, mk, color=GREEN, ms=12, mec=SURF, mew=2, zorder=6)
    ax.text(open_t, entry, f"  3) {side.upper()} giriş {fmt(entry)}", color=GREEN, bbox=LBL, zorder=8, fontsize=9,
            fontweight="bold", va="center")
    ax.hlines(stop, t5.iloc[e], x1, color=RED, lw=1.4, zorder=2)
    ax.text(x1, stop, f"Stop {fmt(stop)} ", color=RED, bbox=LBL, zorder=8, fontsize=9, ha="right",
            va="top" if side == "long" else "bottom")
    ax.hlines(tp, open_t, x1, color=GREEN, lw=1.4, ls=":", zorder=2)
    ax.text(x1, tp, f"Hedef 1R {fmt(tp)} ", color=GREEN, bbox=LBL, zorder=8, fontsize=9, ha="right",
            va="bottom" if side == "long" else "top")
    if not cut:
        ax.plot(close_t, float(t["close_rate"]), "o", color=PURPLE, ms=9, zorder=6)
    res = "KAZANÇ" if r > 0 else "KAYIP"
    exit_tr = {"tp2": "hedef", "stoploss": "stop", "stop_loss": "stop"}.get(t["exit_reason"], t["exit_reason"])
    ax.text(0.01, 0.02, f"Sonuç: {res} {r:+.2f}R (masraflar dahil), çıkış: {exit_tr}, {close_t:%d.%m.%Y %H:%M}"
            + ("  [grafik kısaltıldı]" if cut else ""), transform=ax.transAxes, color=PURPLE, fontsize=10,
            fontweight="bold")
    style(ax, "%d.%m %H:%M")
    pair = t["pair"].split("/")[0]
    kind = "MSS boşluğuna geri dönüşte limit giriş" if retest else "1 dk FVG/iFVG ile giriş"
    ax.set_title(f"#{no}  {pair}  {open_t:%d.%m.%Y} (saat UTC)  {side.upper()}  - üst: 5 dk, alt: 1 dk  ({kind})",
                 color=T1, fontsize=12, loc="left")

    # 1m zoom: from the MSS candle to a little after the entry
    t1 = m1["date"]
    s0 = int(np.searchsorted(t1, t5.iloc[k5] + pd.Timedelta(minutes=5)))
    k1 = int(np.searchsorted(t1, open_t)) - (0 if retest else 1)
    za, zb = max(0, s0 - 15), min(len(m1), max(k1, s0) + 25)
    candles(bx, m1, za, zb, 1)
    bx.axvline(t1.iloc[s0], color=ORANGE, lw=1, ls="--")
    bx.text(t1.iloc[s0], bx.get_ylim()[1], " MSS burada belli oldu", color=ORANGE, fontsize=8, va="top")
    if retest:
        bx.hlines(entry, t1.iloc[s0], t1.iloc[zb - 1], color=GREEN, lw=1.2, ls="--")
        bx.text(t1.iloc[za], entry, " MSS mumunun bıraktığı boşluğun kenarı (limit emir)", color=GREEN, bbox=LBL,
                zorder=8, fontsize=8, va="bottom")
    else:
        g = gap_1m(m1, k1, s0, side)
        if g:
            kind1, gx, g0, g1 = g
            bx.add_patch(plt.Rectangle((mdates.date2num(t1.iloc[gx]), g0),
                                       mdates.date2num(t1.iloc[k1]) - mdates.date2num(t1.iloc[gx]), g1 - g0,
                                       color=ORANGE, alpha=0.35, zorder=1))
            bx.text(t1.iloc[gx], g1, f" 1 dk {'FVG' if kind1 == 'fvg' else 'iFVG'}", color=ORANGE, bbox=LBL,
                    zorder=8, fontsize=8, va="bottom")
    bx.plot(open_t, entry, mk, color=GREEN, ms=11, mec=SURF, mew=2, zorder=6)
    bx.hlines(stop, t1.iloc[za], t1.iloc[zb - 1], color=RED, lw=1, zorder=2) if (
        m1["low"].iloc[za:zb].min() <= stop <= m1["high"].iloc[za:zb].max()) else None
    style(bx, "%H:%M")
    plt.tight_layout()
    f = out_dir / f"islem_{no:02d}.png"
    plt.savefig(f, facecolor=SURF)
    plt.close(fig)
    return dict(no=no, pair=pair, date=f"{open_t:%d.%m.%Y %H:%M}", side=side, src=src, r=round(r, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zips", required=True, help="glob of per-pair backtest zips")
    ap.add_argument("--strategy", default="AslanLiq7_1m")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    trades = []
    for f in sorted(glob.glob(args.zips)):
        trades += load_backtest_stats(Path(f))["strategy"][args.strategy]["trades"]
    trades = sorted((t for t in trades if pd.Timestamp(t["open_date"]) < DEV_END), key=lambda t: t["open_date"])
    rng = np.random.default_rng(args.seed)
    sample = [trades[i] for i in sorted(rng.choice(len(trades), size=args.n, replace=False))]
    retest = args.strategy.endswith("Retest")
    cache, rows = {}, []
    for no, t in enumerate(sample, 1):
        pair = t["pair"]
        if pair not in cache:
            m5, h1, h4, d1 = (load(pair, x) for x in ("5m", "1h", "4h", "1d"))
            sig5 = v3.find_signals_v3(m5, v3.all_levels(h1, h4, d1), 144, allow_break=False, stop_buffer_pct=0.001,
                                      mss_only=True)
            cache[pair] = (m5, sig5, labelled_levels(h1, h4, d1), load(pair, "1m"))
        rows.append(draw(no, t, cache[pair], out_dir, retest))
    table = pd.DataFrame(rows)
    print(table.to_string(index=False))
    table.to_csv(out_dir / "islemler.csv", index=False)


if __name__ == "__main__":
    main()
