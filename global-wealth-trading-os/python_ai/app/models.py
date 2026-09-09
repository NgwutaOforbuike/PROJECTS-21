from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class Region(str, Enum):
    NG = "NG"
    US = "US"
    UK = "UK"


class AssetClass(str, Enum):
    EQUITY = "EQUITY"
    ETF = "ETF"
    BOND = "BOND"
    FX = "FX"
    COMMODITY = "COMMODITY"
    OPTION = "OPTION"
    FUTURE = "FUTURE"
    CASH = "CASH"


class Evidence(BaseModel):
    source_id: str
    source_name: str
    source_tier: int = Field(ge=1, le=4)
    url: str | None = None
    published_at: datetime | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    text: str
    reliability: float = Field(ge=0, le=1)
    stale: bool = False


class MarketState(BaseModel):
    instrument_id: str
    symbol: str
    name: str
    region: Region
    asset_class: AssetClass
    currency: str
    price: float = Field(gt=0)
    day_change_pct: float
    volume_score: float = Field(ge=0, le=100)
    liquidity_score: float = Field(ge=0, le=100)
    volatility_pct: float = Field(ge=0)
    expected_return_pct: float | None = None
    consensus_confidence: float = Field(ge=0, le=100)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: list[Evidence] = []


class AgentOpinion(BaseModel):
    agent: str
    action: Literal["STRONG_BUY", "BUY", "WATCH", "AVOID", "EXIT"]
    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    thesis: str
    risks: list[str] = []
    evidence_ids: list[str] = []


class TradePlan(BaseModel):
    instrument_id: str
    symbol: str
    region: Region
    action: Literal["BUY", "NO_TRADE"]
    entry_low: float | None = None
    entry_high: float | None = None
    stop_loss: float | None = None
    target_price: float | None = None
    expected_return_pct: float | None = None
    quantity: float | None = None
    max_loss_usd: float
    risk_pct_equity: float
    confidence: float = Field(ge=0, le=100)
    rationale: list[str]
    exit_rules: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioState(BaseModel):
    equity_usd: float = 150.0
    cash_usd: float = 150.0
    gross_exposure_pct: float = 0.0
    drawdown_pct: float = 0.0


class Mandate(BaseModel):
    allowed_regions: set[Region] = {Region.NG, Region.US, Region.UK}
    max_risk_per_trade_pct: float = 0.5
    min_modelled_return_pct: float = 5.0
    max_drawdown_pct: float = 12.0
    min_consensus_confidence: float = 70.0
    min_liquidity_score: float = 55.0
    live_execution_enabled: bool = False
