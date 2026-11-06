"""
"ASGO Portfoy" paper tracker: the live forward logs of the portfolio strategies added up on ONE shared
10,000 USDT equity, with the risk per trade chosen in results/2026-11-06_portfoy_sistem (0.25%).

It only reads trades the other trackers already logged and adds them up. It never places, changes or
closes an order and needs no keys. A logged trade is never changed here.

Sources (all in forward/, written by their own bots):
  Fitil + Derin Fitil  forward/paper_fitil/state.json        real Bitget prices, paper; result in % of position
  Dalga                forward/bitget_demo_dalga/state.json  Bitget demo bot; result in R
  PusulaV2             forward/pusula_kagit.json             Pusula paper (research/forward/pusula_paper.py); R
  Aslan NAS            forward/paper_aslan_nas/state.json    frozen line only (not the loosened variants); R

Sizing, same as the portfolio backtest (research/portfolio/portfolio.py):
  R trades     P&L = equity at entry x RISK x R
  Fitil/Derin  no stop; position = equity at entry x RISK / 4% (the 4% stop of Derin Fitil as risk unit),
               P&L = position x net %.
"Equity at entry" is the realized equity when the trade opened (trades that closed before it). Open trades
are listed, not marked to market. Each bot keeps its own slot limits, so none are re-applied here.

    python scripts/paper_portfoy.py            # write forward/paper_portfoy/
    python scripts/paper_portfoy.py --check    # print the result, write nothing
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "forward" / "paper_portfoy"
BASE = 10_000.0
RISK = 0.0025          # results/2026-11-06_portfoy_sistem: val max drawdown 12.0% at 0.25%
FITIL_UNIT = 0.04      # nominal stop of Fitil (research/portfolio/build_trades.py FITIL_NOMINAL_STOP)
START = "2026-10-01T00:00:00+00:00"
SOURCES = {
    "fitil": REPO / "forward" / "paper_fitil" / "state.json",
    "dalga": REPO / "forward" / "bitget_demo_dalga" / "state.json",
    "pusula": REPO / "forward" / "pusula_kagit.json",
    "aslan": REPO / "forward" / "paper_aslan_nas" / "state.json",
}
NAMES = {"Fitil": "Fitil Avcısı (kâğıt)", "Derin Fitil": "Derin Fitil (kâğıt)", "Dalga": "Dalga (demo)",
         "PusulaV2": "Pusula v2 (kâğıt)", "Aslan NAS": "Aslan Nasdaq (kâğıt, donuk)"}
FIELDS = ["strategy", "source", "symbol", "side", "entry_time", "exit_time", "result", "unit",
          "weight", "equity_at_entry", "pnl_usdt", "equity_after"]


def _iso(s) -> str | None:
    """Any timestamp text -> ISO UTC string (None stays None)."""
    if s in (None, "", "None"):
        return None
    s = str(s).replace(" ", "T", 1) if "T" not in str(s) else str(s)
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).isoformat()


def _num(v) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) or math.isinf(f) else f


def _read_json(path: Path):
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    return json.loads(text.replace("NaN", "null").replace("-Infinity", "null").replace("Infinity", "null"))


# ------------------------------------------------------------------ readers (one per log format)

def fitil_trades(state) -> list[dict]:
    out = []
    for t in (state or {}).get("trades", []):
        name = "Derin Fitil" if t.get("mode") == "derin" else "Fitil"
        closed = bool(t.get("exit_time")) and _num(t.get("ret_pct")) is not None
        out.append({"strategy": name, "source": "paper_fitil", "symbol": str(t["pair"]).split("/")[0], "side": "long",
                    "entry_time": _iso(t.get("fill_time")), "exit_time": _iso(t["exit_time"]) if closed else None,
                    "result": _num(t.get("ret_pct")) if closed else None, "unit": "%"})
    return out


def dalga_trades(state) -> list[dict]:
    out = []
    for t in ((state or {}).get("trades") or {}).values():
        if t.get("status") not in ("open", "closed") or not t.get("fill_time"):
            continue  # pending entry orders are not trades yet
        closed = t["status"] == "closed" and _num(t.get("r")) is not None
        out.append({"strategy": "Dalga", "source": "bitget_demo_dalga", "symbol": str(t["pair"]).split("/")[0],
                    "side": t.get("side") or "long", "entry_time": _iso(t["fill_time"]),
                    "exit_time": _iso(t.get("exit_time")) if closed else None,
                    "result": _num(t.get("r")) if closed else None, "unit": "R"})
    return out


def pusula_trades(data) -> list[dict]:
    out = []
    for t in ((data or {}).get("strategies") or {}).get("PusulaV2", []):
        closed = not t.get("open") and _num(t.get("r")) is not None
        out.append({"strategy": "PusulaV2", "source": "pusula_kagit", "symbol": t["coin"], "side": "long",
                    "entry_time": _iso(t["entry_time"]), "exit_time": _iso(t.get("exit_time")) if closed else None,
                    "result": _num(t.get("r")) if closed else None, "unit": "R"})
    return out


def aslan_trades(state) -> list[dict]:
    out = []
    for t in (state or {}).get("trades", []):
        r = _num(t.get("net_r"))
        out.append({"strategy": "Aslan NAS", "source": "paper_aslan_nas", "symbol": "NASDAQ", "side": t.get("side"),
                    "entry_time": _iso(t.get("t_in") or t.get("sig_t")), "exit_time": _iso(t.get("t_out")) if r is not None else None,
                    "result": r, "unit": "R"})
    o = (state or {}).get("open")
    if o and o.get("status") == "pozisyon":
        out.append({"strategy": "Aslan NAS", "source": "paper_aslan_nas", "symbol": "NASDAQ", "side": o.get("side"),
                    "entry_time": _iso(o.get("t_in") or o.get("sig_t")), "exit_time": None, "result": None, "unit": "R"})
    return out


def collect(sources: dict[str, Path] = SOURCES) -> list[dict]:
    trades = (fitil_trades(_read_json(sources["fitil"])) + dalga_trades(_read_json(sources["dalga"]))
              + pusula_trades(_read_json(sources["pusula"])) + aslan_trades(_read_json(sources["aslan"])))
    return [t for t in trades if t["entry_time"] and t["entry_time"] >= START]


# ------------------------------------------------------------------ the shared equity

def weight(t: dict, risk: float = RISK) -> float:
    """Share of equity at entry that one unit of the result moves: P&L = equity x weight x result."""
    return risk / FITIL_UNIT / 100 if t["unit"] == "%" else risk


def combine(trades: list[dict], risk: float = RISK, base: float = BASE) -> dict:
    """Event loop: at the same time exits are booked before entries. Returns closed trades with P&L,
    the realized equity curve and the open trades."""
    events = []
    for i, t in enumerate(trades):
        events.append((t["entry_time"], 1, i))
        if t["exit_time"]:
            events.append((t["exit_time"], 0, i))
    events.sort()
    eq, peak, max_dd = base, base, 0.0
    eq_in: dict[int, float] = {}
    curve = [{"t": START, "eq": base}]
    closed = []
    for ts, kind, i in events:
        t = trades[i]
        if kind == 1:
            eq_in[i] = eq
            continue
        w = weight(t, risk)
        eq_in.setdefault(i, eq)  # entry and exit at the same time
        pnl = eq_in[i] * w * t["result"]
        eq += pnl
        peak = max(peak, eq)
        max_dd = max(max_dd, (peak - eq) / peak)
        closed.append({**t, "weight": w, "equity_at_entry": round(eq_in[i], 2), "pnl_usdt": round(pnl, 2),
                       "equity_after": round(eq, 2)})
        curve.append({"t": ts, "eq": round(eq, 2)})
    open_ = [{**t, "equity_at_entry": round(eq_in[i], 2)} for i, t in enumerate(trades) if not t["exit_time"]]
    by = {}
    for name in NAMES:
        mine = [c for c in closed if c["strategy"] == name]
        by[name] = {"closed": len(mine), "open": sum(1 for o in open_ if o["strategy"] == name),
                    "wins": sum(1 for c in mine if c["result"] > 0),
                    "pnl_usdt": round(sum(c["pnl_usdt"] for c in mine), 2)}
    return {"equity": round(eq, 2), "return_pct": round((eq / base - 1) * 100, 3), "max_dd_pct": round(max_dd * 100, 3),
            "closed": closed, "open": open_, "curve": curve, "by_strategy": by}


def build_state(res: dict, risk: float = RISK) -> dict:
    last = max([c["exit_time"] for c in res["closed"]] + [o["entry_time"] for o in res["open"]] + [START])
    return {
        "name": "ASGO Portföy", "start": START, "base_usdt": BASE, "risk_per_trade": risk,
        "fitil_risk_unit": FITIL_UNIT, "last_event": last,
        "equity": res["equity"], "return_pct": res["return_pct"], "max_dd_pct": res["max_dd_pct"],
        "trades_closed": len(res["closed"]), "trades_open": len(res["open"]),
        "wins": sum(1 for c in res["closed"] if c["result"] > 0),
        "by_strategy": res["by_strategy"], "curve": res["curve"],
        "open": [{k: o[k] for k in ("strategy", "symbol", "side", "entry_time", "unit", "equity_at_entry")} for o in res["open"]],
        "note": "Sadece kayıtlı işlemler toplanır; emir yok. Açık işlemler kasaya kapanınca yazılır.",
    }


def summary_md(state: dict) -> str:
    s = state
    lines = [
        "# ASGO Portföy — kâğıt takip (emir yok)", "",
        f"Tek kasa {s['base_usdt']:,.0f} USDT, işlem başı risk %{s['risk_per_trade'] * 100:.2f}, başlangıç {s['start'][:10]}. "
        f"Son olay: {s['last_event'][:16].replace('T', ' ')} UTC.", "",
        f"- **Kasa:** {s['equity']:,.2f} USDT ({s['return_pct']:+.2f}%)",
        f"- **En büyük düşüş (kapanan işlemlerle):** %{s['max_dd_pct']:.2f}",
        f"- **İşlem:** {s['trades_closed']} kapandı ({s['wins']} kazanan), {s['trades_open']} açık", "",
        "| Strateji | Kapanan | Kazanan | Açık | Katkı (USDT) |", "|---|---|---|---|---|",
    ]
    for k, v in s["by_strategy"].items():
        lines.append(f"| {NAMES[k]} | {v['closed']} | {v['wins']} | {v['open']} | {v['pnl_usdt']:+.2f} |")
    lines += ["", "Kaynaklar: forward/paper_fitil, forward/bitget_demo_dalga, forward/pusula_kagit.json, "
              "forward/paper_aslan_nas (sadece donuk hat). R işlemleri: kâr = kasa × %0.25 × R. "
              "Fitil/Derin (stopsuz): pozisyon = kasa × %0.25 / %4. Kural ve risk seçimi: results/2026-11-06_portfoy_sistem.", ""]
    return "\n".join(lines)


def trades_csv(closed: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for c in closed:
        w.writerow(c)
    return buf.getvalue()


def write(state: dict, closed: list[dict], out: Path = OUT_DIR) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "state.json").write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "trades.csv").write_text(trades_csv(closed), encoding="utf-8")
    (out / "ozet.md").write_text(summary_md(state), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="print, write nothing")
    a = ap.parse_args()
    res = combine(collect())
    state = build_state(res)
    print(summary_md(state))
    if not a.check:
        write(state, res["closed"])


if __name__ == "__main__":
    main()
