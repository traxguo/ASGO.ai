"""
Charts of four tested trades of the band-breakout rule (research/aslan_5dk/bant.py) for Aslan to check.
Draws the band (resistance / support) the rule saw, the MSP = the broken band edge, entry, stop, target and exit.
Times are Turkey time (UTC+3).

    python research/aslan_5dk/plots_bant.py [--data DIR] [--out DIR]
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
import bant  # noqa: E402
import run  # noqa: E402

TR = pd.Timedelta(hours=3)
OUT = bant.OUT
# two wins and two losses from the last validation week (entry close, Turkey time)
PICKS = [("2026-03-25 10:50", "1"), ("2026-03-27 09:50", "2"), ("2026-03-26 10:00", "3"), ("2026-03-31 11:15", "4")]


def band_at(x, B: int):
    """Same band search as bant.triggers (main setup) for breakout bar B: (N, top, bot)."""
    h, lo, c = x.h, x.lo, x.c
    _, min_n, wmin, wmax, *_ = bant.SETUPS["main"]
    for N in range(48, min_n - 1, -1):
        top, bot = h[B - N:B].max(), lo[B - N:B].min()
        w, p = top - bot, c[B - 1]
        if not (wmin * p <= w <= wmax * p):
            continue
        if not (c[B] > top or c[B] < bot):
            continue
        seg = slice(B - N, B)
        ti = np.flatnonzero(h[seg] >= top - bant.TOUCH * w)
        bi = np.flatnonzero(lo[seg] <= bot + bant.TOUCH * w)
        if len(ti) < 2 or len(bi) < 2 or ti[-1] - ti[0] < 3 or bi[-1] - bi[0] < 3:
            continue
        return N, top, bot
    return None


def chart(x, tr: pd.Series, label: str, out: Path) -> None:
    end = x.start + 5 * run.MIN
    k = int(np.searchsorted(end, (pd.Timestamp(tr.t_in) - TR).tz_localize("UTC").value))
    j = int(np.searchsorted(end, (pd.Timestamp(tr.t_out) - TR).tz_localize("UTC").value))
    band = band_at(x, k)
    N = band[0] if band else 24
    a, b = max(k - N - 12, 0), min(j + 12, len(x.c) - 1)
    o, h, lo, c = (v[a:b + 1] for v in (x.o, x.h, x.lo, x.c))
    side = int(tr.side)
    fig, ax = plt.subplots(figsize=(13, 6.5), dpi=110)
    for q in range(len(c)):
        col = "#26a69a" if c[q] >= o[q] else "#ef5350"
        ax.vlines(q, lo[q], h[q], color=col, lw=1)
        ax.add_patch(plt.Rectangle((q - 0.35, min(o[q], c[q])), 0.7, max(abs(c[q] - o[q]), 1e-6), color=col))
    if band:
        _, top, bot = band
        x0, x1 = k - N - a, k - a
        ax.hlines(top, x0, x1, color="#1e40ff", lw=3 if side > 0 else 1.5)
        ax.hlines(bot, x0, x1, color="#d00000", lw=3 if side < 0 else 1.5)
        ax.text(x0, top, " DİRENÇ" + (" = MSP" if side > 0 else ""), va="bottom", color="#1e40ff", fontsize=10,
                weight="bold")
        ax.text(x0, bot, " DESTEK" + (" = MSP" if side < 0 else ""), va="top", color="#d00000", fontsize=10,
                weight="bold")
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
    ax.set_title(f"Bant işlem {label}: {pd.Timestamp(tr.t_in):%d.%m.%Y} TR {pd.Timestamp(tr.t_in):%H:%M} "
                 f"{'short' if side < 0 else 'long'} | giriş {tr.entry:.0f}, stop {tr.stop:.0f}, hedef {tr.tp:.0f} | "
                 f"{sonuc} {tr.r1:+.2f}R", fontsize=11)
    ax.text(0.01, 0.01, "Nasdaq 5 dk (HistData NAS100, alış fiyatı). Kalın çizgi: kırılan bant ucu (MSP). "
            "Mavi: giriş, kırmızı kesik: stop, yeşil kesik: hedef, siyah nokta: çıkış.", transform=ax.transAxes,
            fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out / f"bant_islem_{label}.png")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=run.efb.DATA)
    ap.add_argument("--out", type=Path, default=OUT / "ornek")
    ap.add_argument("--trades", type=Path, default=OUT / "trades_main.csv")
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
