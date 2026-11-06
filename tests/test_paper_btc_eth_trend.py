import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import paper_btc_eth_trend as pt  # noqa: E402

T = pt.T


def fake(days=400, seed=7):
    idx = pd.date_range("2025-01-01", periods=days, freq="D", tz="UTC")
    rng = np.random.default_rng(seed)
    px = pd.DataFrame({"BTC": 60000 * np.exp(np.cumsum(rng.normal(0.001, 0.03, days))),
                       "ETH": 3000 * np.exp(np.cumsum(rng.normal(-0.001, 0.04, days)))}, index=idx)
    fund = pd.DataFrame({"BTC": rng.normal(1e-4, 1e-4, days), "ETH": rng.normal(1e-4, 1e-4, days)}, index=idx)
    return px, fund


def at_close(px):
    """`now` = 20 minutes after the last candle in px closed."""
    return (px.index[-1] + timedelta(days=1, minutes=20)).to_pydatetime()


def test_target_is_the_frozen_rule_from_closes_only():
    px, fund = fake()
    _, target = pt.evaluate(px, fund)
    c = px.iloc[-1]
    sma = px.rolling(120).mean().iloc[-1]
    vol = np.log(px).diff().rolling(30).std().iloc[-1] * np.sqrt(365)
    expect = 0.5 * np.minimum(0.20 / vol, 3.0) * np.sign(c - sma)
    assert np.allclose(target.values, expect.values)


def test_no_lookahead_target_ignores_future_days():
    px, fund = fake()
    cut = px.index[300]
    _, t_short = pt.evaluate(px.loc[:cut], fund.loc[:cut])
    # change everything after the cut: the target decided at the cut must not move
    px2 = px.copy()
    px2.loc[px2.index > cut] *= 3.0
    res, _ = pt.evaluate(px2, fund)
    assert np.allclose(res["w"].loc[cut + pd.Timedelta(days=1)].values, t_short.values)
    # and the weight held over day t equals the target computed with closes up to t-1
    res_full, _ = pt.evaluate(px, fund)
    assert np.allclose(res_full["w"].loc[cut + pd.Timedelta(days=1)].values, t_short.values)


def test_closed_days_drop_the_running_candle_and_fill_gaps():
    px, _ = fake(10)
    gap = px.drop(px.index[4])
    out = pt.closed_days(gap, (px.index[-1] + timedelta(hours=5)).to_pydatetime())
    assert out.index[-1] == px.index[-2] and len(out) == 9
    assert out.iloc[4].equals(px.iloc[3])


def test_funding_events_go_to_the_held_day():
    idx = pd.date_range("2026-01-01", periods=3, freq="D", tz="UTC")
    ev = pd.Series([0.1, 0.2, 0.3, 0.4], index=pd.to_datetime(
        ["2026-01-02 00:00:00.004", "2026-01-02 08:00:00", "2026-01-02 16:00:00", "2026-01-03 00:00:00"], utc=True, format="mixed"))
    f = pt.daily_funding({"BTC": ev}, idx)
    assert f["BTC"].tolist() == pytest.approx([0.1, 0.9, 0.0])


def test_equity_update_matches_the_research_returns():
    px, fund = fake()
    start = 299
    state: dict = {}
    msgs, rows = pt.run_once(px.iloc[: start + 1], fund.iloc[: start + 1], "test", state, at_close(px.iloc[: start + 1]))
    assert rows == [] and state["equity"] == 10_000 and msgs[0].startswith("Takip başladı")
    first_target = dict(state["target"])
    all_rows = []
    for end in [*range(start + 3, len(px), 3), len(px) - 1]:  # every 3 days: missed days are booked once each
        _, r = pt.run_once(px.iloc[: end + 1], fund.iloc[: end + 1], "test", state, at_close(px.iloc[: end + 1]))
        all_rows += r
    days = px.index[start + 1:]
    assert [r["date"] for r in all_rows] == [d.date().isoformat() for d in days]
    # held weights on the first day are the target set at the start
    assert all_rows[0]["w_BTC"] == pytest.approx(first_target["BTC"], abs=1e-4)
    # daily P&L equals the research `run` output, except the first day pays the full entry cost from flat
    res = T.run(px, fund, 120, "sma", 0.20)
    port = res["port"].loc[days].copy()
    w0 = res["w"].loc[days[0]]
    port.iloc[0] += -res["pnl_c"].loc[days[0]].sum() - T.COST * w0.abs().sum()
    got = np.array([r["pnl_pct"] for r in all_rows]) / 100
    assert np.allclose(got, port.values, atol=1e-6)
    assert state["equity"] == pytest.approx(10_000 * (1 + port).prod(), rel=1e-6)
    # P&L parts add up
    for r in all_rows:
        assert r["pnl_pct"] == pytest.approx(r["price_pct"] + r["funding_pct"] + r["cost_pct"], abs=2e-4)
    # running again on the same data books nothing twice
    _, again = pt.run_once(px, fund, "test", state, at_close(px))
    assert again == []


def test_telegram_only_on_direction_change_or_monday():
    px, fund = fake()
    state: dict = {}
    end = 300
    pt.run_once(px.iloc[:end], fund.iloc[:end], "test", state, at_close(px.iloc[:end]))
    sent = []
    for e in range(end + 1, len(px)):
        now = at_close(px.iloc[:e])
        before = dict(state["target"])
        msgs, _ = pt.run_once(px.iloc[:e], fund.iloc[:e], "test", state, now)
        flip = any(np.sign(before[a]) != np.sign(state["target"][a]) for a in pt.ASSETS)
        assert bool(msgs) == (flip or now.weekday() == 0)
        if flip:
            assert msgs[0].startswith("YÖN DEĞİŞTİ")
        sent.append(bool(msgs))
    # a second run on the same Monday sends nothing new
    mon = next(e for e in range(end + 1, len(px)) if at_close(px.iloc[:e]).weekday() == 0)
    st: dict = {}
    pt.run_once(px.iloc[: mon - 1], fund.iloc[: mon - 1], "test", st, at_close(px.iloc[: mon - 1]))
    m1, _ = pt.run_once(px.iloc[:mon], fund.iloc[:mon], "test", st, at_close(px.iloc[:mon]))
    m2, _ = pt.run_once(px.iloc[:mon], fund.iloc[:mon], "test", st, at_close(px.iloc[:mon]))
    assert m1 and not m2


def test_save_appends_daily_rows(tmp_path):
    px, fund = fake()
    state: dict = {}
    pt.run_once(px.iloc[:300], fund.iloc[:300], "test", state, at_close(px.iloc[:300]))
    pt.save(state, [], tmp_path)
    _, rows = pt.run_once(px.iloc[:305], fund.iloc[:305], "test", state, at_close(px.iloc[:305]))
    pt.save(state, rows, tmp_path)
    d = pd.read_csv(tmp_path / "daily.csv")
    assert len(d) == 5 and list(d.columns) == pt.FIELDS
    assert d["equity"].iloc[-1] == pytest.approx(state["equity"])
