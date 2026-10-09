"""
Trade audit for Aslan's strategy (v5: AslanLiq5_15m / AslanLiq5_5m).

Takes a random sample of backtest trades and draws one chart per trade with
every step the code saw: the liquidity level and where it came from, the
candle that took it, the extreme, the confirmation (MSS / iFVG / order block),
entry, stop, target and the result in R. Aslan marks each chart "would take /
would not take, because ...". Charts he rejects point to a rule-translation
(implementation) error; losing charts he accepts point to the strategy itself.

Usage:
  python research/audit/aslan_trade_audit.py BACKTEST.zip --strategy AslanLiq5_15m \
      --n 20 --seed 7 --out /mnt/project-files/raporlar/aslan_denetim
Dev period trades only (the script refuses anything after 2024-12-31).
"""

import argparse
import sys
from bisect import bisect_left
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from freqtrade.data.btanalysis import load_backtest_stats  # noqa: E402

import make_report as mr  # noqa: E402
from strategies.candidates import aslan_liquidity_v3 as v3  # noqa: E402
from strategies.candidates.aslan_liquidity import PIVOT_N, htf_levels, pivots  # noqa: E402

DATA = ROOT / "user_data/data/binance/futures"
DEV_END = pd.Timestamp("2025-01-01", tz="UTC")
TF_MIN = {"15m": 15, "5m": 5}
SETUP = {"15m": 48, "5m": 144}

LBL = dict(boxstyle="round,pad=0.2", fc="#1a1a19", ec="none", alpha=0.85)
SURF, T1, T2, GRID = "#1a1a19", "#ffffff", "#c3c2b7", "#33332f"
BLUE, ORANGE, GREEN, RED, PURPLE = "#3987e5", "#d95926", "#199e70", "#d03b3b", "#9a6bd8"
TRIG_TR = {"mss": "MSS (son tepe/dip kırıldı)", "ifvg": "iFVG (boşluk ters kırıldı)", "ob": "Order block kırıldı"}


def load(pair: str, tf: str) -> pd.DataFrame:
    f = DATA / f"{pair.split('/')[0]}_USDT_USDT-{tf}-futures.feather"
    df = pd.read_feather(f)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df


def labelled_levels(h1, h4, d1) -> pd.DataFrame:
    parts = []
    for src, lv in (
        ("günlük tepe/dip", htf_levels(d1, 1440)),
        ("4 saatlik tepe/dip", htf_levels(h4, 240)),
        ("1 saatlik tepe/dip", htf_levels(h1, 60)),
        ("seans tepe/dip", v3.session_levels(h1)),
    ):
        parts.append(lv.assign(src=src))
    pd_ = htf_levels(d1, 1440, prev_day=True)
    sw = htf_levels(d1, 1440)
    pd_ = pd_.merge(sw, how="left", indicator=True).query("_merge == 'left_only'").drop(columns="_merge")
    parts.append(pd_.assign(src="önceki gün tepe/dip"))
    lv = pd.concat(parts, ignore_index=True)
    lv["avail"] = pd.to_datetime(lv["avail"], utc=True)
    return lv


def level_source(lv, price, side, t) -> tuple[str, pd.Timestamp]:
    m = lv[(np.isclose(lv.price, price)) & (lv.side == side) & (lv.avail <= t)]
    if m.empty:
        return "?", t
    rank = ["günlük tepe/dip", "önceki gün tepe/dip", "4 saatlik tepe/dip", "1 saatlik tepe/dip", "seans tepe/dip"]
    srcs = sorted(set(m.src), key=rank.index)
    return srcs[0] + (f" +{len(srcs) - 1} çakışan" if len(srcs) > 1 else ""), m.avail.max()


def confirm_detail(trig, side, k, e, start, o, h, lo, c, ph_idx, pl_idx, fvg_lookback=10):
    """Which candle / price the confirmation broke (mirrors v3._confirm / _ob_confirm)."""
    if trig == "mss":
        idx = ph_idx if side == "long" else pl_idx
        j = idx[bisect_left(idx, e) - 1]
        return {"ref": j, "price": h[j] if side == "long" else lo[j]}
    if trig == "ifvg":
        for f in range(max(2, start - fvg_lookback), k):
            if side == "long":
                top = lo[f - 2]
                if h[f] < top and c[k] > top and c[f + 1:k].max(initial=-np.inf) <= top:
                    return {"ref": f - 2, "gap": (h[f], top)}
            else:
                bottom = h[f - 2]
                if lo[f] > bottom and c[k] < bottom and c[f + 1:k].min(initial=np.inf) >= bottom:
                    return {"ref": f - 2, "gap": (bottom, lo[f])}
    if trig == "ob":
        for j in range(e, max(-1, e - 20), -1):
            if (side == "long" and c[j] < o[j]) or (side == "short" and c[j] > o[j]):
                return {"ref": j, "price": h[j] if side == "long" else lo[j]}
    return {}


def fmt(v: float) -> str:
    if v >= 1000:
        return f"{v:,.0f}".replace(",", ".")
    if v >= 10:
        return f"{v:.2f}"
    return f"{v:.4f}"


def draw(no, t, sig_k, df, sig, lv, trend4h, out_dir, tf):
    side = "short" if t["is_short"] else "long"
    o, h, lo, c = (df[x].to_numpy(float) for x in ("open", "high", "low", "close"))
    dates = df["date"]
    start = int(sig[f"{side}_setup_at"].iloc[sig_k])
    e = int(sig[f"{side}_ext_at"].iloc[sig_k])
    level = float(sig[f"{side}_level"].iloc[sig_k])
    stop = float(sig[f"{side}_struct_stop"].iloc[sig_k])
    trig = sig[f"{side}_trigger"].iloc[sig_k]
    lv_side = "low" if side == "long" else "high"
    src, lv_t = level_source(lv, level, lv_side, dates[start])
    ph, pl = pivots(h, lo)
    ph_idx = [i for i in np.flatnonzero(ph) if i + PIVOT_N <= sig_k]
    pl_idx = [i for i in np.flatnonzero(pl) if i + PIVOT_N <= sig_k]
    det = confirm_detail(trig, side, sig_k, e, start, o, h, lo, c, ph_idx, pl_idx)

    open_t = pd.Timestamp(t["open_date"])
    close_t = pd.Timestamp(t["close_date"])
    k_in = int(np.searchsorted(dates, open_t))
    k_out = int(np.searchsorted(dates, close_t))
    r = mr.trade_r(t)["r"]
    entry = float(t["open_rate"])
    risk = abs(entry - stop)
    tp = entry + risk if side == "long" else entry - risk
    a = max(0, min(start, det.get("ref", start)) - 30)
    cut = k_out - k_in > 120
    b = min(len(df), (k_in + 120 if cut else k_out) + 10)

    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=110)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    w = pd.Timedelta(minutes=TF_MIN[tf]) * 0.6
    for i in range(a, b):
        col = "#e8e6df" if c[i] >= o[i] else "#7d7b73"
        ax.vlines(dates[i], lo[i], h[i], color=col, lw=0.9, zorder=3)
        ax.bar(dates[i], max(abs(c[i] - o[i]), (h[a:b].max() - lo[a:b].min()) * 0.002),
               bottom=min(o[i], c[i]), width=w, color=col, zorder=3)
    x0, x1 = dates[a], dates[b - 1]
    ax.hlines(level, x0, dates[start], color=BLUE, lw=2, ls="--", zorder=2)
    ax.text(x0, level, f" Likidite {fmt(level)} ({src})", color=BLUE, bbox=LBL, zorder=8, fontsize=9,
            va="bottom" if side == "short" else "top")
    ax.annotate("1) Likidite alındı", (dates[start], lo[start] if side == "long" else h[start]),
                xytext=(-80, -35 if side == "long" else 35), textcoords="offset points", color=T1, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=T2))
    if e != start:
        ax.annotate("en uç nokta", (dates[e], lo[e] if side == "long" else h[e]),
                    xytext=(10, -25 if side == "long" else 25), textcoords="offset points", color=T2, fontsize=8,
                    arrowprops=dict(arrowstyle="->", color=T2))
    if "gap" in det:
        g0, g1 = det["gap"]
        ref = det["ref"]
        ax.add_patch(plt.Rectangle((mdates.date2num(dates[ref]), g0),
                                   mdates.date2num(dates[sig_k]) - mdates.date2num(dates[ref]), g1 - g0,
                                   color=ORANGE, alpha=0.3, zorder=1))
        ax.text(dates[ref], g1 if side == "long" else g0, " boşluk (FVG)", color=ORANGE, bbox=LBL, zorder=8, fontsize=8,
                va="bottom" if side == "long" else "top")
    elif "price" in det:
        ref = det["ref"]
        ax.hlines(det["price"], dates[ref], dates[sig_k], color=ORANGE, lw=1.5, zorder=2)
        ax.text(dates[ref], det["price"], " kırılan seviye", color=ORANGE, bbox=LBL, zorder=8, fontsize=8,
                va="bottom" if side == "long" else "top")
    ax.annotate(f"2) Teyit: {TRIG_TR.get(trig, trig)}", (dates[sig_k], c[sig_k]),
                xytext=(-200, 70 if side == "long" else -70), textcoords="offset points", color=T1, bbox=LBL, zorder=8, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=ORANGE))
    mk = "^" if side == "long" else "v"
    ax.plot(dates[k_in], entry, mk, color=GREEN, ms=12, mec=SURF, mew=2, zorder=6)
    ax.text(dates[k_in], entry, f"  3) {side.upper()} giriş {fmt(entry)}", color=GREEN, bbox=LBL, zorder=8, fontsize=9,
            fontweight="bold", va="center")
    ax.hlines(stop, dates[e], x1, color=RED, lw=1.4, zorder=2)
    ax.text(x1, stop, f"Stop {fmt(stop)} ", color=RED, bbox=LBL, zorder=8, fontsize=9, ha="right",
            va="top" if side == "long" else "bottom")
    ax.hlines(tp, dates[k_in], x1, color=GREEN, lw=1.4, ls=":", zorder=2)
    ax.text(x1, tp, f"Hedef 1R {fmt(tp)} ", color=GREEN, bbox=LBL, zorder=8, fontsize=9, ha="right",
            va="bottom" if side == "long" else "top")
    if not cut:
        ax.plot(dates[min(k_out, len(df) - 1)], float(t["close_rate"]), "o", color=PURPLE, ms=9, zorder=6)
    res = "KAZANÇ" if r > 0 else "KAYIP"
    exit_tr = {"tp2": "hedef", "stoploss": "stop", "stop_loss": "stop"}.get(t["exit_reason"], t["exit_reason"])
    ax.text(0.01, 0.02,
            f"Sonuç: {res} {r:+.2f}R (masraflar dahil), çıkış: {exit_tr}, {close_t:%d.%m.%Y %H:%M}"
            + ("  [grafik kısaltıldı]" if cut else ""),
            transform=ax.transAxes, color=PURPLE, fontsize=10, fontweight="bold")
    ax.yaxis.tick_right()
    ax.tick_params(colors=T2, labelsize=8)
    ax.grid(color=GRID, lw=0.5)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m %H:%M"))
    pair = t["pair"].split("/")[0]
    tr = {1: "yukarı", -1: "aşağı", 0: "yatay"}[trend4h]
    ax.set_title(f"#{no}  {pair} {tf.replace('m', ' dk')}  {open_t:%d.%m.%Y} (saat UTC)  {side.upper()}   "
                 f"4 saatlik trend: {tr}", color=T1, fontsize=12, loc="left")
    plt.tight_layout()
    f = out_dir / f"islem_{no:02d}.png"
    plt.savefig(f, facecolor=SURF)
    plt.close(fig)
    return dict(no=no, pair=pair, date=f"{open_t:%d.%m.%Y %H:%M}", side=side, trig=trig, src=src, r=round(r, 2),
                stop_ok=bool(np.isclose(stop, float(t["enter_tag"].split("stop=")[1].split()[0]), rtol=1e-6)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip")
    ap.add_argument("--strategy", default="AslanLiq5_15m")
    ap.add_argument("--tf", default="15m")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    trades = load_backtest_stats(Path(args.zip))["strategy"][args.strategy]["trades"]
    trades = [t for t in trades if pd.Timestamp(t["open_date"]) < DEV_END]
    rng = np.random.default_rng(args.seed)
    pick = sorted(rng.choice(len(trades), size=min(args.n, len(trades)), replace=False))
    sample = [trades[i] for i in pick]

    cache = {}
    rows = []
    for no, t in enumerate(sample, 1):
        pair = t["pair"]
        if pair not in cache:
            df = load(pair, args.tf)
            h1, h4, d1 = (load(pair, x) for x in ("1h", "4h", "1d"))
            sig = v3.find_signals_v3(df, v3.all_levels(h1, h4, d1), SETUP[args.tf],
                                     allow_break=False, use_ob=True, stop_buffer_pct=0.001)
            ct = (df["date"] + pd.Timedelta(minutes=TF_MIN[args.tf])).astype("datetime64[ns, UTC]")
            tr4 = pd.merge_asof(pd.DataFrame({"avail": ct}), v3.structure_trend(h4, 240), on="avail")
            cache[pair] = (df, sig, labelled_levels(h1, h4, d1), tr4["trend"].fillna(0).astype(int).to_numpy())
        df, sig, lv, tr4 = cache[pair]
        side = "short" if t["is_short"] else "long"
        open_t = pd.Timestamp(t["open_date"])
        cand = np.flatnonzero((sig[f"{side}_trigger"] != "").to_numpy() & (df["date"] < open_t).to_numpy())
        sig_k = int(cand[-1])
        rows.append(draw(no, t, sig_k, df, sig, lv, int(tr4[sig_k]), out_dir, args.tf))
    table = pd.DataFrame(rows)
    print(table.to_string(index=False))
    table.to_csv(out_dir / "islemler.csv", index=False)


if __name__ == "__main__":
    main()
