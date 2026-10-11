from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade")

from strategies.candidates import fvg_ob as f  # noqa: E402

# 15m candles (open, close, high, low); 3m candles are a straight path open -> close.
CANDLES_15M = [
    (99, 100, 100.5, 98.5),
    (100, 104, 104.5, 99.5),
    (104, 109, 110.0, 103.5),   # 2: swing high 110 (later the untaken target)
    (109, 104, 109.2, 103.5),
    (104, 100, 104.2, 99.5),
    (100, 103, 103.3, 99.8),
    (103, 104, 105.0, 102.5),   # 6: swing high 105 (broken by the MSS)
    (104, 101, 104.2, 100.8),
    (101, 98, 101.0, 97.0),     # 8: red candle at the low = order block 97..101
    (98, 104, 104.1, 97.9),     # 9: expansion (3m FVGs inside the OB zone)
    (104, 107, 107.1, 103.9),   # 10: closes above 105 = MSS
    (107, 107.5, 107.8, 106.8),
]


def _frame(candles=CANDLES_15M):
    rows = []
    t0 = pd.Timestamp("2023-01-02 00:00", tz="UTC")
    for k, (o, c, hi, lo) in enumerate(candles):
        path = np.linspace(o, c, 6)
        for j in range(5):
            a, b = path[j], path[j + 1]
            rows.append({
                "date": t0 + pd.Timedelta(minutes=15 * k + 3 * j),
                "open": a, "close": b,
                "high": max(a, b) + 0.05, "low": min(a, b) - 0.05, "volume": 10.0,
            })
    df = pd.DataFrame(rows)
    # make the 15m extremes exactly the listed ones
    for k, (o, c, hi, lo) in enumerate(candles):
        g = df.index[5 * k:5 * k + 5]
        df.loc[g[int(np.argmax(df.loc[g, "high"]))], "high"] = hi
        df.loc[g[int(np.argmin(df.loc[g, "low"]))], "low"] = lo
    return df


def _mirror(df):
    m = df.copy()
    m["open"], m["close"] = 200 - df["open"], 200 - df["close"]
    m["high"], m["low"] = 200 - df["low"], 200 - df["high"]
    return m


def test_condition_ids_match_the_card():
    card = (Path(__file__).resolve().parents[1] / "cards" / "fvg_ob.md").read_text()
    s = f.FvgOb({})
    df = f.find_setups(_frame())
    for side, conds in s.signal_conditions(df).items():
        for cid in conds:
            assert f"[{cid}]" in card or (side == "short" and cid == "mss_down_15m"), cid


def test_long_setup_levels():
    df = _frame()
    r = f.find_setups(df)
    sig = np.flatnonzero(r["long_rr_ok"].to_numpy())
    mss_row = 10 * 5 + 4  # last 3m candle of 15m candle 10
    assert list(sig) == [mss_row]
    row = r.iloc[mss_row]
    assert row["long_swing"] == pytest.approx(105.0)
    assert (row["long_ob_low"], row["long_ob_high"]) == (pytest.approx(97.0), pytest.approx(101.0))
    assert row["long_stop"] == pytest.approx(97.0 * (1 - f.STOP_BUFFER))
    assert row["long_tp"] == pytest.approx(110.0)
    assert row["long_entry"] == pytest.approx((row["long_fvg_low"] + row["long_fvg_high"]) / 2)
    assert row["long_fvg_low"] <= 101.0 and row["long_fvg_high"] >= 97.0  # overlaps the OB
    assert row["long_rr"] >= 2
    # expansion = 3m candles after the OB up to the MSS close
    assert row["long_leg_start"] == df["date"].iloc[9 * 5].timestamp()
    assert not r["short_rr_ok"].any()


def test_edge_variant_uses_near_edge():
    candles = list(CANDLES_15M)
    candles[2] = (104, 109, 112.0, 103.5)  # farther target so the edge entry keeps R/R >= 2
    r = f.find_setups(_frame(candles), entry_mode="edge")
    row = r.iloc[54]
    assert row["long_rr_ok"]
    assert row["long_entry"] == pytest.approx(row["long_fvg_high"])


def test_short_is_the_mirror():
    df = _mirror(_frame())
    r = f.find_setups(df)
    assert list(np.flatnonzero(r["short_rr_ok"].to_numpy())) == [54]
    row = r.iloc[54]
    assert row["short_stop"] == pytest.approx((200 - 97.0) * (1 + f.STOP_BUFFER))
    assert row["short_tp"] == pytest.approx(200 - 110.0)
    assert not r["long_rr_ok"].any()


def test_no_lookahead_truncated_data_gives_same_signals():
    df = _frame()
    full = f.find_setups(df)
    for cut in range(20, len(df) + 1):
        part = f.find_setups(df.iloc[:cut].reset_index(drop=True))
        pd.testing.assert_frame_equal(part, full.iloc[:cut].reset_index(drop=True), check_dtype=False)


def test_rr_below_two_blocks_the_signal():
    candles = list(CANDLES_15M)
    candles[2] = (104, 106, 106.2, 103.5)  # target only 106.2 -> R/R < 2
    candles[3] = (106, 104, 106.0, 103.5)
    r = f.find_setups(_frame(candles))
    assert r["long_fvg"].iloc[54] and not r["long_rr_ok"].any()


def test_pullback_volume_rule():
    high = np.array([1, 2, 3, 4, 3.5, 3.2, 3.0], dtype=float)
    low = high - 0.5
    vol = np.array([10, 10, 10, 10, 4, 4, 4], dtype=float)
    cum = np.r_[0.0, np.cumsum(vol)]
    # fill on candle 6: pullback = candles 4, 5 (after the top at 3) -> 4 < 9
    assert f.pullback_volume_ok("long", 6, 0, high, low, cum, 9.0)
    assert not f.pullback_volume_ok("long", 6, 0, high, low, cum, 3.0)
    # fill on candle 4: the top is candle 3, no closed pullback candle yet -> no fill
    assert not f.pullback_volume_ok("long", 4, 0, high, low, cum, 9.0)
    # short: extreme = lowest low
    assert f.pullback_volume_ok("short", 6, 0, -high + 10, -high + 9.5, cum, 9.0)


def test_limit_fill_needs_trade_through():
    buf = f.trade_through_buffer(100.0, 0.01, f.FILL_THROUGH_PCT)
    assert buf == pytest.approx(0.02)
    assert not f.limit_filled("buy", 100.0, 99.99, 101, buf)
    assert f.limit_filled("buy", 100.0, 99.98, 101, buf)
    assert not f.limit_filled("sell", 100.0, 99, 100.01, buf)
    assert f.limit_filled("sell", 100.0, 99, 100.02, buf)


def test_three_losses_halt_24h_then_reset():
    t = datetime(2023, 1, 1, tzinfo=timezone.utc)
    h = timedelta(hours=1)
    assert f.loss_streak_halt_until([(t, -1), (t + h, -1)]) is None
    assert f.loss_streak_halt_until([(t, -1), (t + h, 5), (t + 2 * h, -1), (t + 3 * h, -1)]) is None
    trades = [(t, -1), (t + h, -1), (t + 2 * h, -1)]
    assert f.loss_streak_halt_until(trades) == t + 2 * h + timedelta(hours=24)
    # after the halt the streak starts again: two more losses do not extend it
    later = trades + [(t + 30 * h, -1), (t + 31 * h, -1)]
    assert f.loss_streak_halt_until(later) == t + 2 * h + timedelta(hours=24)
    assert f.loss_streak_halt_until(later + [(t + 32 * h, -1)]) == t + 32 * h + timedelta(hours=24)
