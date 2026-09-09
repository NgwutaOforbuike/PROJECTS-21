import pytest
from app.committee import InvestmentCommittee
from app.models import AssetClass, Mandate, MarketState, PortfolioState, Region


@pytest.mark.asyncio
async def test_risk_is_capped_at_half_percent():
    state = MarketState(
        instrument_id="TEST",
        symbol="TEST",
        name="Test",
        region=Region.US,
        asset_class=AssetClass.EQUITY,
        currency="USD",
        price=10,
        day_change_pct=4,
        volume_score=95,
        liquidity_score=95,
        volatility_pct=4,
        expected_return_pct=6,
        consensus_confidence=95,
    )
    _, plan = await InvestmentCommittee(Mandate()).assess(state, PortfolioState())
    if plan.action == "BUY":
        assert plan.max_loss_usd <= 0.75
        assert plan.risk_pct_equity == 0.5


@pytest.mark.asyncio
async def test_below_five_percent_is_rejected():
    state = MarketState(
        instrument_id="LOW",
        symbol="LOW",
        name="Low Return",
        region=Region.US,
        asset_class=AssetClass.EQUITY,
        currency="USD",
        price=10,
        day_change_pct=2,
        volume_score=90,
        liquidity_score=90,
        volatility_pct=3,
        expected_return_pct=4.99,
        consensus_confidence=95,
    )
    _, plan = await InvestmentCommittee(Mandate()).assess(state, PortfolioState())
    assert plan.action == "NO_TRADE"
