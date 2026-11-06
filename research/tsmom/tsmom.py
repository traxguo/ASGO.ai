"""Time-series momentum with volatility targeting on BTCUSDT + ETHUSDT perps (daily).

Pre-registered in results/2026-11-06_btc_eth_trend/README.md.
Holdout (>= 2026-04-01) is cut at load time and never used.
"""
from __future__ import annotations

import glob
import io
import itertools
import os
import zipfile

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "results", "2026-11-06_btc_eth_trend")
HOLDOUT_START = pd.Timestamp("2026-04-01", tz="UTC")
DEV = (pd.Timestamp("2020-05-01", tz="UTC"), pd.Timestamp("2024-12-31", tz="UTC"))
VAL = (pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2026-03-31", tz="UTC"))
ASSETS = ["BTC", "ETH"]
COST = 0.001
VOL_WIN = 30
LEV_CAP = 3.0
ANN = 365.0
GRID = list(itertools.product([20, 60, 120], ["ret", "sma"], [0.20, 0.40]))
N_SHUFFLE = 200
BLOCK = 20


def load_prices() -> pd.DataFrame:
    closes = {}
    for a in ASSETS:
        f = os.path.join(ROOT, "user_data/data/binance/futures", f"{a}_USDT_USDT-1d-futures.feather")
        d = pd.read_feather(f)
        d = d[d["date"] < HOLDOUT_START]
        closes[a] = d.set_index("date")["close"]
    px = pd.DataFrame(closes).sort_index()
    assert px.index.max() < HOLDOUT_START
    full = pd.date_range(px.index.min(), px.index.max(), freq="D", tz="UTC")
    missing = full.difference(px.index)
    if len(missing):
        print("WARNING missing days:", len(missing))
    return px.reindex(full).ffill()


def load_funding(index: pd.DatetimeIndex) -> pd.DataFrame:
    """Daily funding sum attributed to the position held over day t (events in (t 00:00, t+1 00:00])."""
    out = {}
    for a in ASSETS:
        rows = []
        for z in sorted(glob.glob(os.path.join(ROOT, f"user_data/data/binance_vision_raw/fundingRate/{a}USDT/*.zip"))):
            ym = z.rsplit("-fundingRate-", 1)[1][:7]
            if pd.Timestamp(ym + "-01", tz="UTC") >= HOLDOUT_START:
                continue
            with zipfile.ZipFile(z) as zf:
                d = pd.read_csv(io.BytesIO(zf.read(zf.namelist()[0])))
            rows.append(d)
        f = pd.concat(rows)
        ts = pd.to_datetime(f["calc_time"], unit="ms", utc=True).dt.round("h")
        f = pd.Series(f["last_funding_rate"].values, index=ts)
        f = f[~f.index.duplicated()].sort_index()
        f = f[f.index <= HOLDOUT_START]  # the 2026-04-01 00:00 event belongs to the 2026-03-31 holding
        day = (f.index - pd.Timedelta(seconds=1)).floor("D")  # 00:00 event -> previous day
        out[a] = f.groupby(day).sum()
    fd = pd.DataFrame(out).reindex(index).fillna(0.0)
    return fd


def signals(px: pd.DataFrame, n: int, kind: str) -> pd.DataFrame:
    if kind == "ret":
        s = np.sign(px / px.shift(n) - 1.0)
    else:
        s = np.sign(px - px.rolling(n).mean())
    return s


def run(px: pd.DataFrame, fund: pd.DataFrame, n: int, kind: str, vt: float, cost: float = COST) -> dict:
    """Return daily series. Weight for day t uses info up to close t-1."""
    r = px.pct_change()
    lr = np.log(px).diff()
    vol = lr.rolling(VOL_WIN).std() * np.sqrt(ANN)
    lev = (vt / vol).clip(upper=LEV_CAP)
    sig = signals(px, n, kind)
    w_target = (0.5 * lev * sig).shift(1)  # decided at close t-1, held over day t
    w = w_target.fillna(0.0)
    # drift(t): weight at close t of the position w(t) held over day t.
    # At close t-1 the book is rebalanced from drift(t-1) to w(t); that turnover is booked on day t.
    rr = r.fillna(0.0)
    port_gross = (w * rr).sum(axis=1)
    drift = (w * (1 + rr)).div(1 + port_gross, axis=0)
    trade = (w - drift.shift(1).fillna(0.0)).abs()
    pnl_px = w * r.fillna(0.0)
    pnl_f = -w * fund
    pnl_c = -cost * trade
    contrib = pnl_px + pnl_f + pnl_c  # per-asset daily contribution
    port = contrib.sum(axis=1)
    return {"w": w, "contrib": contrib, "port": port, "pnl_f": pnl_f, "pnl_c": pnl_c, "valid": w_target.notna().all(axis=1)}


def stats(res: dict, start, end) -> dict:
    m = (res["port"].index >= start) & (res["port"].index <= end)
    p = res["port"][m]
    w = res["w"][m]
    c = res["contrib"][m]
    eq = (1 + p).cumprod()
    yrs = len(p) / ANN
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    dd = (eq / eq.cummax() - 1).min()
    sh = p.mean() / p.std() * np.sqrt(ANN) if p.std() > 0 else 0.0
    side = np.sign(w)
    # trades = direction changes per asset (incl. entering from flat), entry into window counted once
    full_side = np.sign(res["w"])
    chg = (full_side != full_side.shift(1)) & (full_side != 0)
    trades = chg[m].sum().sum()
    long_pnl = c.where(side > 0, 0.0).sum().sum()
    short_pnl = c.where(side < 0, 0.0).sum().sum()
    return {
        "cagr": cagr, "max_dd": dd, "sharpe": sh, "trades_per_year": trades / yrs,
        "long_pnl": long_pnl, "short_pnl": short_pnl, "total_ret": eq.iloc[-1] - 1,
        "funding": res["pnl_f"][m].sum().sum(), "costs": res["pnl_c"][m].sum().sum(),
        "avg_gross_lev": w.abs().sum(axis=1).mean(), "days_short_frac": (side < 0).values.mean(),
    }


def buy_hold(px, fund, start, end):
    r = px.pct_change().fillna(0.0)
    out = {}
    for name, w in [("BTC", {"BTC": 1.0, "ETH": 0.0}), ("ETH", {"BTC": 0.0, "ETH": 1.0}), ("50/50", {"BTC": 0.5, "ETH": 0.5})]:
        W = pd.DataFrame({a: w[a] for a in ASSETS}, index=px.index)
        p = (W * r - W * fund).sum(axis=1)
        m = (p.index >= start) & (p.index <= end)
        p = p[m]
        eq = (1 + p).cumprod()
        yrs = len(p) / ANN
        out[name] = {"cagr": eq.iloc[-1] ** (1 / yrs) - 1, "max_dd": (eq / eq.cummax() - 1).min(),
                     "sharpe": p.mean() / p.std() * np.sqrt(ANN), "total_ret": eq.iloc[-1] - 1}
    return out


def shuffle_dev(px, fund, rng):
    """Block-shuffle daily returns + funding inside 2020-01-01..2024-12-31 (same permutation for both assets)."""
    m = px.index <= DEV[1]
    p = px[m]
    r = p.pct_change().iloc[1:]
    f = fund[m].iloc[1:]
    nb = int(np.ceil(len(r) / BLOCK))
    order = rng.permutation(nb)
    idx = np.concatenate([np.arange(b * BLOCK, min((b + 1) * BLOCK, len(r))) for b in order])
    rs = r.iloc[idx].values
    fs = f.iloc[idx].values
    newpx = pd.DataFrame(p.iloc[0].values * np.cumprod(1 + rs, axis=0), index=r.index, columns=ASSETS)
    newpx = pd.concat([p.iloc[:1], newpx])
    newf = pd.concat([fund[m].iloc[:1], pd.DataFrame(fs, index=r.index, columns=ASSETS)])
    return newpx, newf


def main():
    px = load_prices()
    fund = load_funding(px.index)
    print("data", px.index.min().date(), px.index.max().date(), len(px))
    rows = []
    curves = {}
    for n, kind, vt in GRID:
        cfg = f"N{n}_{kind}_vt{int(vt*100)}"
        res = run(px, fund, n, kind, vt)
        assert res["valid"][res["port"].index >= DEV[0]].all()
        res2 = run(px, fund, n, kind, vt, cost=2 * COST)
        curves[cfg] = res["port"]
        for per, (s, e) in [("dev", DEV), ("val", VAL)]:
            st = stats(res, s, e)
            st2 = stats(res2, s, e)
            rows.append({"config": cfg, "lookback": n, "signal": kind, "vol_target": vt, "period": per, **st,
                         "sharpe_2x_cost": st2["sharpe"], "cagr_2x_cost": st2["cagr"]})
    df = pd.DataFrame(rows)

    # shuffled control (dev)
    rng = np.random.default_rng(20261106)
    sh_rows = []
    for i in range(N_SHUFFLE):
        spx, sf = shuffle_dev(px, fund, rng)
        for n, kind, vt in GRID:
            cfg = f"N{n}_{kind}_vt{int(vt*100)}"
            res = run(spx, sf, n, kind, vt)
            sh_rows.append({"run": i, "config": cfg, "sharpe": stats(res, *DEV)["sharpe"]})
    sh = pd.DataFrame(sh_rows)
    sh.to_csv(os.path.join(OUT, "shuffle_control_dev.csv"), index=False)
    dev = df[df.period == "dev"].set_index("config")
    pct = {c: (sh[sh.config == c].sharpe < dev.loc[c, "sharpe"]).mean() * 100 for c in dev.index}
    p90 = {c: sh[sh.config == c].sharpe.quantile(0.9) for c in dev.index}
    df["shuffle_pctile_dev"] = df.config.map(pct)
    df["shuffle_p90_sharpe_dev"] = df.config.map(p90)
    df.to_csv(os.path.join(OUT, "configs_dev_val.csv"), index=False)

    # pass/fail
    piv = df.pivot(index="config", columns="period")
    verdict = []
    for c in dev.index:
        g = lambda col, per: piv.loc[c, (col, per)]
        c1 = g("sharpe", "dev") > 0 and g("sharpe", "val") > 0
        c2 = g("short_pnl", "dev") > 0 and g("short_pnl", "val") > 0
        c3 = g("shuffle_pctile_dev", "dev") > 90
        c4 = g("sharpe_2x_cost", "dev") > 0 and g("sharpe_2x_cost", "val") > 0
        verdict.append({"config": c, "sharpe_pos_dev_val": c1, "short_pnl_pos_dev_val": c2,
                        "above_shuffle_p90_dev": c3, "sharpe_pos_2x_cost": c4, "PASS": c1 and c2 and c3 and c4})
    v = pd.DataFrame(verdict)
    v.to_csv(os.path.join(OUT, "pass_fail.csv"), index=False)

    bh = []
    for per, (s, e) in [("dev", DEV), ("val", VAL)]:
        for k, st in buy_hold(px, fund, s, e).items():
            bh.append({"asset": k, "period": per, **st})
    bh = pd.DataFrame(bh)
    bh.to_csv(os.path.join(OUT, "buy_hold.csv"), index=False)
    pd.DataFrame(curves).to_csv(os.path.join(OUT, "daily_returns_all_configs.csv"))

    pd.set_option("display.width", 250)
    cols = ["config", "period", "cagr", "max_dd", "sharpe", "trades_per_year", "long_pnl", "short_pnl",
            "funding", "costs", "sharpe_2x_cost", "shuffle_pctile_dev"]
    print(df[cols].round(3).to_string())
    print(v.to_string())
    print(bh.round(3).to_string())


if __name__ == "__main__":
    main()
