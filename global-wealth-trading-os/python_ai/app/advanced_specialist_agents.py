from __future__ import annotations

from statistics import mean
from .agent_context import InvestmentContext,num
from .models import AgentOpinion
from .specialist_agents import SpecialistAgent,action,clip,missing


class FactorExposureAgent(SpecialistAgent):
    name="factor_exposure"
    async def evaluate(self,ctx):
        if not ctx.factors:return missing(self.name)
        momentum=num(ctx.factors,"momentum_score",50) or 50
        quality=num(ctx.factors,"quality_score",50) or 50
        value=num(ctx.factors,"value_score",50) or 50
        size=num(ctx.factors,"size_score",50) or 50
        lowvol=num(ctx.factors,"low_vol_score",50) or 50
        score=momentum*.28+quality*.28+value*.20+lowvol*.16+size*.08
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=72,
            thesis="Multi-factor exposure across momentum, quality, value, size and low-volatility characteristics.",
            risks=["Factor leadership rotates and can reverse abruptly."])


class CorporateActionsAgent(SpecialistAgent):
    name="corporate_actions"
    async def evaluate(self,ctx):
        if not ctx.corporate_actions:return missing(self.name)
        accretive=num(ctx.corporate_actions,"accretive_score",50) or 50
        dilution=num(ctx.corporate_actions,"dilution_risk_score",50) or 50
        certainty=num(ctx.corporate_actions,"completion_certainty_score",50) or 50
        score=accretive*.45+certainty*.30+(100-dilution)*.25
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=70,
            thesis="Rights issues, buybacks, M&A, placements, splits and other capital-event impact assessment.",
            risks=["Corporate actions can create dilution, execution risk and binary repricing."])


class DividendAgent(SpecialistAgent):
    name="dividend"
    async def evaluate(self,ctx):
        if not ctx.dividends:return missing(self.name)
        yield_=num(ctx.dividends,"yield_pct",0) or 0
        cover=num(ctx.dividends,"coverage_score",50) or 50
        growth=num(ctx.dividends,"growth_score",50) or 50
        cut=num(ctx.dividends,"cut_risk_score",50) or 50
        score=45+min(15,yield_*2)+cover*.15+growth*.12-cut*.20
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=65,
            thesis="Dividend yield, sustainability, growth and cut-risk assessment.",
            risks=["Dividend yield can be elevated because the market expects a cut."])


class CrowdingShortInterestAgent(SpecialistAgent):
    name="crowding_short_interest"
    async def evaluate(self,ctx):
        if not ctx.crowding:return missing(self.name)
        short=num(ctx.crowding,"short_interest_pct",0) or 0
        days=num(ctx.crowding,"days_to_cover",0) or 0
        crowded_long=num(ctx.crowding,"crowded_long_score",50) or 50
        squeeze=num(ctx.crowding,"squeeze_score",50) or 50
        score=50+(squeeze-50)*.18-(crowded_long-50)*.22+min(10,short*.4)+min(8,days)
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=58,
            thesis="Crowded positioning, short interest, days-to-cover and squeeze-risk overlay.",
            risks=["Crowding data can be delayed and squeezes are highly path-dependent."])


class TaxFrictionAgent(SpecialistAgent):
    name="tax_friction"
    async def evaluate(self,ctx):
        if not ctx.tax:return missing(self.name)
        effective=num(ctx.tax,"effective_transaction_tax_pct",0) or 0
        withholding=num(ctx.tax,"withholding_pct",0) or 0
        stamp=num(ctx.tax,"stamp_duty_pct",0) or 0
        reclaim=num(ctx.tax,"reclaim_efficiency_score",50) or 50
        total=effective+withholding+stamp
        score=clip(90-total*8+(reclaim-50)*.12)
        return AgentOpinion(agent=self.name,action=action(score),score=score,confidence=65,
            thesis="Tax, withholding, stamp-duty and recovery friction relative to expected return.",
            risks=["Tax treatment depends on investor status, instrument and jurisdiction."])


class ManagementQualityAgent(SpecialistAgent):
    name="management_quality"
    async def evaluate(self,ctx):
        if not ctx.management:return missing(self.name)
        allocation=num(ctx.management,"capital_allocation_score",50) or 50
        governance=num(ctx.management,"governance_score",50) or 50
        guidance=num(ctx.management,"guidance_accuracy_score",50) or 50
        turnover=num(ctx.management,"leadership_stability_score",50) or 50
        score=allocation*.32+governance*.30+guidance*.23+turnover*.15
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=62,
            thesis="Capital allocation, governance, guidance credibility and leadership stability assessment.",
            risks=["Management-quality scoring contains qualitative judgement and must remain evidence-backed."])


class SupplyChainAgent(SpecialistAgent):
    name="supply_chain"
    async def evaluate(self,ctx):
        if not ctx.supply_chain:return missing(self.name)
        resilience=num(ctx.supply_chain,"resilience_score",50) or 50
        concentration=num(ctx.supply_chain,"supplier_concentration_risk_score",50) or 50
        logistics=num(ctx.supply_chain,"logistics_score",50) or 50
        inventory=num(ctx.supply_chain,"inventory_health_score",50) or 50
        score=resilience*.35+(100-concentration)*.25+logistics*.20+inventory*.20
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=55,
            thesis="Supplier concentration, logistics resilience and inventory-health operating-risk overlay.",
            risks=["Supply-chain data is often sparse or lagged."])


class GeopoliticalAgent(SpecialistAgent):
    name="geopolitical"
    async def evaluate(self,ctx):
        if not ctx.geopolitical:return missing(self.name)
        country=num(ctx.geopolitical,"country_risk_score",50) or 50
        sanctions=num(ctx.geopolitical,"sanctions_risk_score",0) or 0
        conflict=num(ctx.geopolitical,"conflict_risk_score",0) or 0
        policy=num(ctx.geopolitical,"policy_stability_score",50) or 50
        score=(100-country)*.30+(100-sanctions)*.25+(100-conflict)*.25+policy*.20
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=62,
            thesis="Country, sanctions, conflict and policy-stability risk overlay.",
            risks=["Geopolitical risk is discontinuous and difficult to model."])


class CapitalStructureAgent(SpecialistAgent):
    name="capital_structure"
    async def evaluate(self,ctx):
        if not ctx.capital_structure:return missing(self.name)
        debt=num(ctx.capital_structure,"debt_service_score",50) or 50
        maturity=num(ctx.capital_structure,"maturity_profile_score",50) or 50
        convert=num(ctx.capital_structure,"dilution_risk_score",50) or 50
        covenant=num(ctx.capital_structure,"covenant_headroom_score",50) or 50
        score=debt*.30+maturity*.25+(100-convert)*.20+covenant*.25
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=72,
            thesis="Debt service, maturity wall, dilution and covenant-headroom assessment.",
            risks=["Refinancing conditions can deteriorate quickly when rates or credit spreads move."])


class TrendPersistenceAgent(SpecialistAgent):
    name="trend_persistence"
    async def evaluate(self,ctx):
        m=ctx.market
        strength=num(ctx.factors,"trend_strength_score")
        breadth=num(ctx.factors,"breadth_score")
        base=50+m.day_change_pct*4
        if strength is not None:base+=(strength-50)*.35
        if breadth is not None:base+=(breadth-50)*.20
        return AgentOpinion(agent=self.name,action=action(base),score=clip(base),confidence=65,
            thesis="Trend strength, breadth and short-horizon continuation assessment.",
            risks=["Strong trends can reverse sharply after crowded moves."])


class MeanReversionAgent(SpecialistAgent):
    name="mean_reversion"
    async def evaluate(self,ctx):
        distance=num(ctx.factors,"distance_from_mean_z")
        oversold=num(ctx.factors,"oversold_score")
        if distance is None and oversold is None:return missing(self.name)
        score=50
        if distance is not None:score+=max(-20,min(20,-distance*8))
        if oversold is not None:score+=(oversold-50)*.25
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=58,
            thesis="Statistical distance-from-mean and oversold/overbought reversion assessment.",
            risks=["Mean reversion fails when the underlying regime has structurally changed."])


class TailRiskAgent(SpecialistAgent):
    name="tail_risk"
    async def evaluate(self,ctx):
        gap=num(ctx.execution,"gap_risk_pct",0) or 0
        event=num(ctx.metadata,"binary_event_risk_score",0) or 0
        liquidity=ctx.market.liquidity_score
        volatility=ctx.market.volatility_pct
        score=85-min(25,gap*3)-min(25,event*.3)-min(20,volatility*.6)-max(0,(70-liquidity)*.4)
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=78,
            thesis="Gap, binary-event, volatility and liquidity tail-loss assessment.",
            risks=["Tail events are by definition poorly represented by ordinary historical samples."])


ADVANCED_AGENTS=[
    FactorExposureAgent(),CorporateActionsAgent(),DividendAgent(),
    CrowdingShortInterestAgent(),TaxFrictionAgent(),ManagementQualityAgent(),
    SupplyChainAgent(),GeopoliticalAgent(),CapitalStructureAgent(),
    TrendPersistenceAgent(),MeanReversionAgent(),TailRiskAgent()
]
