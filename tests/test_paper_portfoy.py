import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import paper_portfoy as pp  # noqa: E402


def _write(tmp: Path, fitil=None, dalga=None, pusula=None, aslan=None) -> dict:
    files = {"fitil": fitil, "dalga": dalga, "pusula": pusula, "aslan": aslan}
    out = {}
    for k, v in files.items():
        p = tmp / f"{k}.json"
        if v is not None:
            p.write_text(json.dumps(v))
        out[k] = p
    return out


FITIL = {"trades": [
    {"pair": "FIL/USDT:USDT", "mode": "fitil", "fill_time": "2026-10-17T21:30:00+00:00",
     "exit_time": "2026-10-18T00:45:00+00:00", "ret_pct": 2.0},
    {"pair": "ONE/USDT:USDT", "mode": "derin", "fill_time": "2026-11-06T13:45:00+00:00",
     "exit_time": None, "ret_pct": None},
]}
DALGA = {"equity_peak": 1, "trades": {
    "a": {"pair": "SOL/USDT:USDT", "status": "closed", "fill_time": "2026-10-20T01:00:00+00:00",
          "exit_time": "2026-10-25T01:00:00+00:00", "r": 2.0},
    "b": {"pair": "ETH/USDT:USDT", "status": "pending", "signal_time": "2026-10-21T00:00:00+00:00"},
}}
PUSULA = {"strategies": {
    "PusulaTrendLong": [{"coin": "BTC", "entry_time": "2026-10-02 08:00:00+00:00", "exit_time": "2026-10-07 13:00:00+00:00",
                         "r": -5.0, "open": False}],
    "PusulaV2": [{"coin": "BTC", "entry_time": "2026-10-02 08:00:00+00:00", "exit_time": "2026-10-07 13:00:00+00:00",
                  "r": -1.0, "open": False}],
}}
ASLAN = {"trades": [{"side": "short", "t_in": "2026-11-05T15:00:00+00:00", "t_out": "2026-11-05T18:00:00+00:00",
                     "net_r": 1.5}], "open": {"status": "emir", "side": "long", "sig_t": "2026-11-06T10:00:00+00:00"}}


def test_collect_reads_every_source_and_skips_pending(tmp_path):
    t = pp.collect(_write(tmp_path, FITIL, DALGA, PUSULA, ASLAN))
    names = sorted(x["strategy"] for x in t)
    # frozen Pusula is not in the portfolio, a pending Dalga order and an Aslan limit order are not trades
    assert names == ["Aslan NAS", "Dalga", "Derin Fitil", "Fitil", "PusulaV2"]
    assert next(x for x in t if x["strategy"] == "PusulaV2")["entry_time"] == "2026-10-02T08:00:00+00:00"


def test_missing_files_give_an_empty_flat_portfolio(tmp_path):
    res = pp.combine(pp.collect(_write(tmp_path)))
    assert res["equity"] == pp.BASE and res["closed"] == [] and res["max_dd_pct"] == 0


def test_shared_equity_sizing_and_compounding(tmp_path):
    res = pp.combine(pp.collect(_write(tmp_path, FITIL, DALGA, PUSULA, ASLAN)), risk=0.0025)
    c = {x["strategy"]: x for x in res["closed"]}
    # Pusula first: -1R on 10,000 at 0.25% = -25
    assert c["PusulaV2"]["pnl_usdt"] == pytest.approx(-25.0)
    # Fitil: position = 9,975 x 0.25% / 4% = 623.4; +2% = +12.47
    assert c["Fitil"]["pnl_usdt"] == pytest.approx(9975 * 0.0025 / 0.04 * 0.02, abs=0.01)
    # Dalga entered after the Fitil exit, so on the compounded equity
    assert c["Dalga"]["equity_at_entry"] == pytest.approx(9975 + 12.47, abs=0.01)
    assert c["Dalga"]["pnl_usdt"] == pytest.approx(c["Dalga"]["equity_at_entry"] * 0.0025 * 2, abs=0.01)
    assert res["max_dd_pct"] == pytest.approx(0.25, abs=1e-6)
    assert [o["strategy"] for o in res["open"]] == ["Derin Fitil"]
    assert res["curve"][0] == {"t": pp.START, "eq": pp.BASE} and res["curve"][-1]["eq"] == res["equity"]


def test_write_is_stable_without_new_trades(tmp_path):
    src = _write(tmp_path, FITIL, DALGA, PUSULA, ASLAN)
    out = tmp_path / "out"
    for _ in range(2):
        res = pp.combine(pp.collect(src))
        pp.write(pp.build_state(res), res["closed"], out)
        first = (out / "state.json").read_text()
    res = pp.combine(pp.collect(src))
    pp.write(pp.build_state(res), res["closed"], out)
    assert (out / "state.json").read_text() == first  # no run timestamp, so no hourly empty commits
    state = json.loads(first)
    assert state["risk_per_trade"] == 0.0025 and state["trades_closed"] == 4
    assert (out / "trades.csv").read_text().splitlines()[0].startswith("strategy,source,symbol")


def test_coin_age_rule_and_risk_choice():
    pd = pytest.importorskip("pandas")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "portfolio"))
    import system  # noqa: E402

    listed = pd.Series(pd.to_datetime(["2020-01-01", "2026-01-01"], utc=True), index=["BTC", "NEW"])
    t = pd.DataFrame({"market": ["crypto", "crypto", "crypto", "nasdaq"], "pair": ["BTC", "NEW", "GONE", "NAS100"],
                      "t_in": pd.to_datetime(["2020-03-01", "2026-03-01", "2026-03-01", "2026-03-01"], utc=True)})
    assert system.coin_age_mask(t, listed).tolist() == [False, False, False, True]
    t.loc[0, "t_in"] = pd.Timestamp("2020-07-01", tz="UTC")
    assert system.coin_age_mask(t, listed).tolist()[0]
    rr = {"0.25": {"stats": {"val": {"maxdd_pct": -12.0}}}, "0.50": {"stats": {"val": {"maxdd_pct": -21.5}}}}
    assert system.choose_risk(rr) == 0.0025
