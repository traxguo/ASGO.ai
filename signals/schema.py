"""
Signal data structure (PROJECT_BRIEF section 7.7).

Every signal is written into this structure and saved under signals/log/
BEFORE any message or image is produced. Messages and images only read from it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

Status = Literal["pending", "open", "tp1_hit", "breakeven", "closed", "cancelled"]
STATUSES: tuple[str, ...] = ("pending", "open", "tp1_hit", "breakeven", "closed", "cancelled")

LOG_DIR = Path(__file__).resolve().parent / "log"


@dataclass
class EntryZone:
    high: float
    low: float


@dataclass
class Target:
    level: str  # "TP1" / "TP2"
    price: float
    R: float
    close_pct: float


@dataclass
class Management:
    model: str  # "A" / "B"
    breakeven_trigger: str  # "TP1" / "2R"
    valid_for_candles: int


@dataclass
class TriggeredCondition:
    id: str  # must match a condition id in the strategy card
    value: str  # the real values, e.g. "close 3418 > EMA200 3210"


@dataclass
class Signal:
    signal_id: str
    timestamp: str
    pair: str
    timeframe: str
    strategy: str
    side: Literal["long", "short"]
    entry_zone: EntryZone
    stop: float
    risk_R: float
    targets: list[Target]
    management: Management
    leverage: float
    liquidation_price_est: float
    funding_rate_at_signal: float | None
    triggered_conditions: list[TriggeredCondition] = field(default_factory=list)
    stop_reason: str = ""
    status: Status = "pending"

    def validate(self) -> None:
        """Hard rules from the brief. Raises ValueError when a rule is broken."""
        if self.side not in ("long", "short"):
            raise ValueError(f"invalid side {self.side}")
        if self.status not in STATUSES:
            raise ValueError(f"invalid status {self.status}")
        if self.entry_zone.low > self.entry_zone.high:
            raise ValueError("entry_zone.low must be <= entry_zone.high")
        mid = (self.entry_zone.low + self.entry_zone.high) / 2
        if abs(abs(mid - self.stop) - self.risk_R) > 1e-6 * max(1.0, mid):
            raise ValueError("risk_R must equal |entry zone middle - stop|")
        s = 1 if self.side == "long" else -1
        if s * (mid - self.stop) <= 0:
            raise ValueError("stop is on the wrong side of the entry")
        if len(self.targets) != 2:
            raise ValueError("exactly 2 targets (TP1, TP2) are required")
        tp1 = self.targets[0]
        if tp1.R < 1.0:
            raise ValueError("TP1 can never be smaller than 1R")
        for t in self.targets:
            expected = mid + s * t.R * self.risk_R
            if abs(t.price - expected) > 1e-6 * max(1.0, mid):
                raise ValueError(f"{t.level} price does not match its R multiple")
        # liquidation must be at least 2x the stop distance away (7.6)
        if abs(mid - self.liquidation_price_est) < 2 * self.risk_R:
            raise ValueError("liquidation price is too close to the stop")
        if not self.triggered_conditions:
            raise ValueError("a signal needs at least one triggered condition")

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "Signal":
        d = dict(d)
        d["entry_zone"] = EntryZone(**d["entry_zone"])
        d["targets"] = [Target(**t) for t in d["targets"]]
        d["management"] = Management(**d["management"])
        d["triggered_conditions"] = [TriggeredCondition(**c) for c in d.get("triggered_conditions", [])]
        return cls(**d)

    def save(self, log_dir: Path = LOG_DIR) -> Path:
        """Validate and write to the log. Called before any message is sent."""
        self.validate()
        log_dir.mkdir(parents=True, exist_ok=True)
        safe_id = self.signal_id.replace(":", "").replace("/", "")
        path = log_dir / f"{safe_id}.json"
        path.write_text(self.to_json(), encoding="utf-8")
        return path


def make_signal_id(ts: datetime, pair: str, strategy: str) -> str:
    """e.g. 2026-10-02T14:00Z_ETHUSDT_trend_ma_v2"""
    ts = ts.astimezone(timezone.utc)
    symbol = pair.split(":")[0].replace("/", "")
    return f"{ts.strftime('%Y-%m-%dT%H:%MZ')}_{symbol}_{strategy}"


def signal_from_plan(plan, *, ts: datetime, pair: str, timeframe: str, strategy: str,
                     conditions: list[TriggeredCondition], funding_rate: float | None) -> Signal:
    """Builds a Signal from a strategies.common.trade_management.TradePlan."""
    m = plan.model
    return Signal(
        signal_id=make_signal_id(ts, pair, strategy),
        timestamp=ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        pair=pair,
        timeframe=timeframe,
        strategy=strategy,
        side=plan.side,
        entry_zone=EntryZone(high=plan.zone_high, low=plan.zone_low),
        stop=plan.stop,
        risk_R=plan.risk_r,
        targets=[
            Target("TP1", plan.tp1, m.tp1_r, m.tp1_close_pct),
            Target("TP2", plan.tp2, m.tp2_r, 100 - m.tp1_close_pct),
        ],
        management=Management(m.name, m.breakeven_trigger, plan.valid_for_candles),
        leverage=plan.leverage,
        liquidation_price_est=plan.liquidation_price_est,
        funding_rate_at_signal=funding_rate,
        triggered_conditions=conditions,
        stop_reason=plan.stop_reason,
        status="pending",
    )
