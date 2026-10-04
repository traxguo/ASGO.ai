import pytest

from strategies.common import trade_management as tm


def plan(side="long", model=tm.MODEL_B):
    p, reason = tm.build_plan(side, close=100.0, atr=2.0, swing_level=None, model=model)
    assert reason == "ok"
    return p


def test_tp1_never_below_1r():
    with pytest.raises(ValueError):
        tm.TPModel("bad", 0.9, 4.0, 50, "TP1")


def test_long_levels_are_consistent():
    p = plan("long")
    assert p.zone_low == pytest.approx(99.5)  # close - 0.25 ATR
    assert p.zone_high == pytest.approx(100.0)
    assert p.entry == pytest.approx(99.75)
    assert p.stop == pytest.approx(99.75 - 3.0)  # 1.5 ATR
    assert p.risk_r == pytest.approx(3.0)
    assert p.tp1 == pytest.approx(99.75 + 6.0)
    assert p.tp2 == pytest.approx(99.75 + 12.0)


def test_short_is_mirror_of_long():
    p = plan("short")
    assert p.zone_low == pytest.approx(100.0)
    assert p.zone_high == pytest.approx(100.5)
    assert p.stop > p.entry > p.tp1 > p.tp2


def test_wider_stop_uses_swing_when_further():
    p, _ = tm.build_plan("long", 100.0, 2.0, swing_level=95.0, model=tm.MODEL_B)
    assert p.stop == pytest.approx(95.0 - 0.2)
    assert p.stop_reason == "below_swing_low"


def test_stop_too_far_gives_no_signal():
    p, reason = tm.build_plan("long", 100.0, 10.0, swing_level=None, model=tm.MODEL_B)
    assert p is None and reason == "stop_too_far"


def test_liquidation_at_least_twice_stop_distance():
    p = plan("long")
    assert abs(p.entry - p.liquidation_price_est) >= 2 * p.risk_r
    assert p.leverage <= 3


def test_leverage_reduced_for_wide_stop():
    # 3x liquidation is ~32.8% away: fine for a 7% stop, too close for a 20% stop
    assert tm.safe_leverage("long", 100, 93, tm.DEFAULT_PARAMS) == 3.0
    params = tm.ManagementParams(max_stop_pct=0.5)
    assert tm.safe_leverage("long", 100, 80, params) == 2.0
    assert tm.safe_leverage("long", 100, 50, params) is None


def test_position_size_risks_one_percent():
    notional = tm.position_notional(10_000, 100, 97)
    assert notional * 0.03 == pytest.approx(100)  # 1% of 10k


# --- outcomes match the brief's table (before costs) -----------------------

def test_model_b_outcomes():
    p = plan("long", tm.MODEL_B)
    e, r = p.entry, p.risk_r
    fill = (e + 0.1, e - 0.1)
    # stop -> -1R
    assert tm.simulate_plan(p, [fill[0], e], [fill[1], e - 1.1 * r])["r"] == pytest.approx(-1)
    # TP1 then break even -> +1R
    out = tm.simulate_plan(p, [fill[0], e + 2.1 * r, e], [fill[1], e + 0.1, e - 0.5 * r])
    assert out == {"status": "breakeven", "r": pytest.approx(1.0)}
    # TP2 -> +3R
    out = tm.simulate_plan(p, [fill[0], e + 2.1 * r, e + 4.1 * r], [fill[1], e + 0.1, e + 3 * r])
    assert out == {"status": "tp2", "r": pytest.approx(3.0)}


def test_model_a_outcomes():
    p = plan("long", tm.MODEL_A)
    e, r = p.entry, p.risk_r
    fill = (e + 0.1, e - 0.1)
    assert tm.simulate_plan(p, [fill[0], e], [fill[1], e - 1.1 * r])["r"] == pytest.approx(-1)
    out = tm.simulate_plan(p, [fill[0], e + 2.1 * r, e], [fill[1], e + 0.1, e - 0.5 * r])
    assert out == {"status": "breakeven", "r": pytest.approx(0.0)}
    out = tm.simulate_plan(p, [fill[0], e + 2.1 * r, e + 4.1 * r], [fill[1], e + 0.1, e + 3 * r])
    assert out == {"status": "tp2", "r": pytest.approx(4.0)}


def test_short_model_b_tp2():
    p = plan("short", tm.MODEL_B)
    e, r = p.entry, p.risk_r
    out = tm.simulate_plan(p, [e + 0.1, e - 0.1, e - 3 * r], [e - 0.1, e - 2.1 * r, e - 4.1 * r])
    assert out == {"status": "tp2", "r": pytest.approx(3.0)}


def test_signal_cancelled_when_zone_not_reached():
    p = plan("long")
    above = p.entry + 1
    out = tm.simulate_plan(p, [above + 1] * 5, [above] * 5)
    assert out["status"] == "cancelled"


def test_signal_cancelled_when_stop_hit_before_entry():
    p = plan("long")
    # gap straight below the stop without trading at the entry price
    out = tm.simulate_plan(p, [p.stop - 0.5], [p.stop - 2])
    assert out["status"] == "cancelled"


def test_variant_grid_is_fixed_size():
    assert len(tm.tp_variant_grid()) == 16
