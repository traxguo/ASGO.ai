"""
Collect the trade lists of the five strategies into one standard table for the portfolio backtest.
Rules are NOT changed here: every list comes from the strategy's own frozen research code.

    python research/portfolio/build_trades.py fitil   <wick_catcher_pit TRADES csv> <out>   # Fitil (PIT, no stop)
    python research/portfolio/build_trades.py derin   <wick_catcher_pit TRADES csv> <out>   # Derin Fitil 4% stop + 24h
    python research/portfolio/build_trades.py ft      <freqtrade result zip> <name> <out>   # DalgaPIT / PusulaV2
    python research/portfolio/build_trades.py aslan   <aslan_nas_trades.py csv> <out>       # Aslan NAS100 v2 1h bias

Output columns: strategy, market, pair, side, t_in, t_out, entry, ret, cost, stop_pct
  ret      = net result as a fraction of the position size (fees, slippage, funding included)
  cost     = the round-trip cost already inside ret (used for the 2x cost run: ret - cost)
  stop_pct = distance to the stop as a fraction of entry = what one R is. Fitil has no stop: it gets the
             4% of Derin Fitil as a nominal risk unit (position = risk / 4%), stated in the report.
"""
import json
import re
import sys
import zipfile

import pandas as pd

WICK_COST = 0.0020      # wick_catcher_pit.py COST=0.20 (maker in + taker out + slippage)
FT_COST = 0.0020        # Freqtrade fee 0.1% per order (0.05 fee + 0.05 slippage), two orders
NAS_COST = 0.00010      # research/aslan_nasdaq/sim.py COST["NAS100"]
FITIL_NOMINAL_STOP = 0.04
DERIN_STOP = 0.04
COLS = ["strategy", "market", "pair", "side", "t_in", "t_out", "entry", "ret", "cost", "stop_pct"]


def wick(path, name, stop):
    d = pd.read_csv(path, parse_dates=["t", "t_out"])
    return pd.DataFrame({"strategy": name, "market": "crypto", "pair": d.c, "side": "long", "t_in": d.t,
                         "t_out": d.t_out, "entry": float("nan"), "ret": d.ret, "cost": WICK_COST, "stop_pct": stop})


def ft(path, name):
    z = zipfile.ZipFile(path)
    main = [n for n in z.namelist() if n.endswith(".json") and not n.endswith("_config.json")][0]
    strat = json.load(z.open(main))["strategy"]
    trades = next(iter(strat.values()))["trades"]
    rows = []
    for t in trades:
        stop = float(re.search(r"stop=([0-9.eE+-]+)", t["enter_tag"]).group(1))
        entry = next(o for o in t["orders"] if o["ft_is_entry"])
        px, amt = entry["safe_price"], entry["amount"]
        rows.append((name, "crypto", t["pair"].split("/")[0], "short" if t["is_short"] else "long",
                     pd.Timestamp(t["open_date"]), pd.Timestamp(t["close_date"]), px,
                     t["profit_abs"] / (amt * px), FT_COST, abs(px - stop) / px))
    return pd.DataFrame(rows, columns=COLS)


def aslan(path):
    d = pd.read_csv(path, parse_dates=["t_in", "t_out"])
    return pd.DataFrame({"strategy": "Aslan NAS", "market": "nasdaq", "pair": "NAS100", "side": d.side,
                         "t_in": d.t_in, "t_out": d.t_out, "entry": d.entry,
                         "ret": d.gross_r * d.stop_pct - NAS_COST, "cost": NAS_COST, "stop_pct": d.stop_pct})


if __name__ == "__main__":
    kind = sys.argv[1]
    if kind == "fitil":
        df, out = wick(sys.argv[2], "Fitil", FITIL_NOMINAL_STOP), sys.argv[3]
    elif kind == "derin":
        df, out = wick(sys.argv[2], "Derin Fitil", DERIN_STOP), sys.argv[3]
    elif kind == "ft":
        df, out = ft(sys.argv[2], sys.argv[3]), sys.argv[4]
    elif kind == "aslan":
        df, out = aslan(sys.argv[2]), sys.argv[3]
    else:
        raise SystemExit(__doc__)
    for c in ("t_in", "t_out"):
        df[c] = pd.to_datetime(df[c], utc=True)
    df[COLS].sort_values("t_in").to_csv(out, index=False)
    print(out, len(df), "trades", df.t_in.min(), "->", df.t_in.max())
