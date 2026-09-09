import pytest
from app.agent_context import InvestmentContext
from app.expert_committee import ExpertInvestmentCommittee
from app.models import AssetClass,MarketState,Region


def base_market():
    return MarketState(
        instrument_id="X",symbol="X",name="X",region=Region.US,
        asset_class=AssetClass.EQUITY,currency="USD",price=100,
        day_change_pct=1,volume_score=90,liquidity_score=90,
        volatility_pct=12,expected_return_pct=6,consensus_confidence=95
    )


@pytest.mark.asyncio
async def test_expert_committee_runs_all_specialists():
    ctx=InvestmentContext(
        market=base_market(),
        fundamentals={"roe_pct":22,"net_margin_pct":18,"net_debt_to_ebitda":.5,"fcf_margin_pct":14},
        valuation={"forward_pe":15,"ev_ebitda":10,"fcf_yield_pct":7,"discount_to_peer_pct":10},
        earnings={"eps_revision_30d_pct":3,"last_eps_surprise_pct":8,"forward_eps_growth_pct":18},
        execution={"spread_bps":8,"depth_score":90,"adv_usd":5_000_000,"expected_slippage_bps":3,"fees_bps":2},
        accounting={"accruals_ratio_pct":2,"cfo_to_net_income":1.2,"restatement_count":0,"related_party_risk_score":5},
        regulatory={"material_flags":0,"uncertainty_score":5,"pending_approvals":0},
        currency={"carry_score":55,"trend_score":60,"devaluation_risk_score":25},
        cross_asset={"rates_support_score":65,"commodity_support_score":55,"credit_conditions_score":70,"usd_support_score":60},
        metadata={"portfolio_correlation":.2,"sector_exposure_after_pct":20,"country_exposure_after_pct":30},
    )
    result=await ExpertInvestmentCommittee().evaluate(ctx)
    assert len(result.opinions)>=16
    assert result.decision in {"BUY","WATCH","AVOID"}


@pytest.mark.asyncio
async def test_regulatory_veto_can_block():
    ctx=InvestmentContext(
        market=base_market(),
        regulatory={"material_flags":4,"uncertainty_score":90,"pending_approvals":4},
        execution={"spread_bps":10,"depth_score":90,"adv_usd":5_000_000},
    )
    result=await ExpertInvestmentCommittee().evaluate(ctx)
    assert "regulatory" in result.vetoes
    assert result.decision=="AVOID"
