import pytest
from app.agent_context import InvestmentContext
from app.investment_engine import AutonomousInvestmentEngine
from app.models import AssetClass,MarketState,Region


def strong_market():
    return MarketState(
        instrument_id="X",symbol="X",name="X",region=Region.US,
        asset_class=AssetClass.EQUITY,currency="USD",price=100,
        day_change_pct=2,volume_score=95,liquidity_score=95,
        volatility_pct=8,expected_return_pct=6,consensus_confidence=95,
    )


@pytest.mark.asyncio
async def test_engine_never_bypasses_risk_governor():
    ctx=InvestmentContext(
        market=strong_market(),
        fundamentals={"roe_pct":25,"net_margin_pct":20,"net_debt_to_ebitda":.2,"fcf_margin_pct":15},
        valuation={"forward_pe":12,"ev_ebitda":8,"fcf_yield_pct":9,"discount_to_peer_pct":15},
        earnings={"eps_revision_30d_pct":4,"last_eps_surprise_pct":10,"forward_eps_growth_pct":20},
        execution={"spread_bps":5,"depth_score":95,"adv_usd":10_000_000,"expected_slippage_bps":2,"fees_bps":1},
        accounting={"accruals_ratio_pct":1,"cfo_to_net_income":1.3,"restatement_count":0,"related_party_risk_score":2},
        regulatory={"material_flags":0,"uncertainty_score":0,"pending_approvals":0},
        currency={"carry_score":60,"trend_score":60,"devaluation_risk_score":20},
        cross_asset={"rates_support_score":65,"commodity_support_score":60,"credit_conditions_score":70,"usd_support_score":55},
        metadata={"portfolio_correlation":.1,"sector_exposure_after_pct":15,"country_exposure_after_pct":25},
    )
    result=await AutonomousInvestmentEngine().decide(ctx)
    if result.trade_plan:
        assert result.trade_plan.risk_pct_equity==.5
        assert result.trade_plan.max_loss_usd<=.75
