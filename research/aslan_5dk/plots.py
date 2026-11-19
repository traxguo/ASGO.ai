"""
Charts of a few tested trades so Aslan can check that the rule was understood (entry order, stop, target).
Rule and code: research/aslan_5dk/run.py. Times on the charts are Turkey time (UTC+3).

    python research/aslan_5dk/plots.py [--data DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run  # noqa: E402

TR = pd.Timedelta(hours=3)
# (entry close time in Turkey time, label) - two wins and two losses from the last validation week
PICKS = [("2026-03-25 09:55", "1"), ("2026-03-27 09:05", "2"), ("2026-03-26 14:10", "3"), ("2026-03-31 18:45", "4")]


def swings(h, lo, k):
    """Confirmed 2/2 swing highs and lows up to bar k (index lists)."""
    H, L = [], []
    for i in range(2, k - 1):
        if i + 2 > k:
            break
        if h[i] > max(h[i - 2], h[i - 1], h[i + 1], h[i + 2]):
            H.append(i)
        if lo[i] < min(lo[i - 2], lo[i - 1], lo[i + 1], lo[i + 2]):
            L.append(i)
    return H, L


def chart(x, tr: pd.Series, label: str, out: Path) -> None:
    end = x.start + 5 * run.MIN
    t_in = pd.Timestamp(tr.t_in) - TR
    k = int(np.searchsorted(end, pd.Timestamp(t_in, tz="UTC").value))
    j = int(np.searchsorted(end, (pd.Timestamp(tr.t_out) - TR).tz_localize("UTC").value))
    a, b = max(k - 60, 0), min(j + 12, len(x.c) - 1)
    o, h, lo, c = (v[a:b + 1] for v in (x.o, x.h, x.lo, x.c))
    H, L = swings(x.h, x.lo, k)
    H, L = [i for i in H if i >= a], [i for i in L if i >= a]
    side = int(tr.side)
    fig, ax = plt.subplots(figsize=(13, 6.5), dpi=110)
    for q in range(len(c)):
        col = "#26a69a" if c[q] >= o[q] else "#ef5350"
        ax.vlines(q, lo[q], h[q], color=col, lw=1)
        ax.add_patch(plt.Rectangle((q - 0.35, min(o[q], c[q])), 0.7, max(abs(c[q] - o[q]), 1e-6), color=col))
    for i in H[-2:]:
        ax.annotate("T", (i - a, x.h[i]), xytext=(0, 6), textcoords="offset points", ha="center", color="black", fontsize=9)
    for i in L[-2:]:
        ax.annotate("D", (i - a, x.lo[i]), xytext=(0, -14), textcoords="offset points", ha="center", color="black", fontsize=9)
    msp = x.lo[L[-1]] if side < 0 else x.h[H[-1]]
    msp_i = L[-1] if side < 0 else H[-1]
    ax.hlines(msp, msp_i - a, k - a, color="#555", lw=1.5)
    ax.text(msp_i - a, msp, " MSP", va="bottom", fontsize=9)
    xe = k - a
    ax.hlines(tr.entry, xe, j - a, color="#1565c0", lw=1.5)
    ax.hlines(tr.stop, xe, j - a, color="#c62828", lw=1.5, ls="--")
    ax.hlines(tr.tp, xe, j - a, color="#2e7d32", lw=1.5, ls="--")
    ax.annotate("SHORT" if side < 0 else "LONG", (xe, tr.entry), xytext=(-40, 18 if side > 0 else -22),
                textcoords="offset points", arrowprops=dict(arrowstyle="->"), fontsize=10, weight="bold")
    ax.plot(j - a, tr.exit, "ko", ms=6)
    ts = pd.DatetimeIndex(x.start[a:b + 1]).tz_localize("UTC") + TR + pd.Timedelta(minutes=5)
    ticks = list(range(0, len(c), 12))
    ax.set_xticks(ticks, [ts[t].strftime("%H:%M") for t in ticks])
    sonuc = "KAZANÇ" if tr.r1 > 0 else "KAYIP"
    ax.set_title(f"İşlem {label}: {pd.Timestamp(tr.t_in):%d.%m.%Y} TR {pd.Timestamp(tr.t_in):%H:%M} "
                 f"{'short' if side < 0 else 'long'} | giriş {tr.entry:.0f}, stop {tr.stop:.0f}, hedef {tr.tp:.0f} | "
                 f"{sonuc} {tr.r1:+.2f}R", fontsize=11)
    ax.text(0.01, 0.01, "Nasdaq 5 dk (HistData NAS100, alış fiyatı). T/D: botun gördüğü son tepe/dipler. "
            "Mavi: giriş, kırmızı: stop, yeşil: hedef, siyah nokta: çıkış.", transform=ax.transAxes, fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out / f"islem_{label}.png")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=run.efb.DATA)
    ap.add_argument("--out", type=Path, default=run.OUT / "ornek")
    ap.add_argument("--trades", type=Path, default=run.OUT / "trades_main.csv")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    x = run.efb.load("NAS100", a.data)
    t = pd.read_csv(a.trades)
    for when, label in PICKS:
        row = t[t.t_in == when]
        if row.empty:
            print(f"no trade at {when}")
            continue
        chart(x, row.iloc[0], label, a.out)
        print(f"chart {label}: {when}")


if __name__ == "__main__":
    main()
