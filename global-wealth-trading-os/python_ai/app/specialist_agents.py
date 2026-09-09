from __future__ import annotations

from abc import ABC, abstractmethod
from statistics import mean

from .agent_context import InvestmentContext, num
from .models import AgentOpinion


def clip(x:float)->float:
    return max(0.0,min(100.0,float(x)))


def action(score:float)->str:
    if score>=82:return "STRONG_BUY"
    if score>=67:return "BUY"
    if score>=50:return "WATCH"
    if score>=32:return "AVOID"
    return "EXIT"


def missing(name:str)->AgentOpinion:
    return AgentOpinion(
        agent=name,action="WATCH",score=50,confidence=20,
        thesis="Insufficient verified data for a high-confidence specialist conclusion.",
        risks=["Required specialist inputs are missing or incomplete."]
    )


class SpecialistAgent(ABC):
    name:str
    @abstractmethod
    async def evaluate(self,ctx:InvestmentContext)->AgentOpinion:...


class FundamentalQualityAgent(SpecialistAgent):
    name="fundamental_quality"
    async def evaluate(self,ctx):
        roe=num(ctx.fundamentals,"roe_pct")
        margin=num(ctx.fundamentals,"net_margin_pct")
        debt=num(ctx.fundamentals,"net_debt_to_ebitda")
        fcf=num(ctx.fundamentals,"fcf_margin_pct")
        if all(v is None for v in [roe,margin,debt,fcf]): return missing(self.name)
        score=50
        if roe is not None: score+=max(-18,min(18,(roe-12)*.8))
        if margin is not None: score+=max(-12,min(12,(margin-8)*.6))
        if debt is not None: score+=max(-15,min(12,(2.5-debt)*5))
        if fcf is not None: score+=max(-10,min(12,(fcf-5)*.5))
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=75,
            thesis="Profitability, free-cash-flow conversion and balance-sheet quality composite.",
            risks=["Accounting quality and sector-specific capital structures can distort headline ratios."])


class ValuationAgent(SpecialistAgent):
    name="valuation"
    async def evaluate(self,ctx):
        pe=num(ctx.valuation,"forward_pe")
        ev=num(ctx.valuation,"ev_ebitda")
        fcfy=num(ctx.valuation,"fcf_yield_pct")
        rel=num(ctx.valuation,"discount_to_peer_pct")
        if all(v is None for v in [pe,ev,fcfy,rel]): return missing(self.name)
        score=50
        if pe is not None: score+=max(-14,min(14,(22-pe)*.8))
        if ev is not None: score+=max(-12,min(12,(14-ev)*.8))
        if fcfy is not None: score+=max(-10,min(14,(fcfy-4)*2))
        if rel is not None: score+=max(-10,min(14,rel*.5))
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=70,
            thesis="Absolute and relative valuation with cash-flow yield preference.",
            risks=["Cheap securities may be value traps; valuation is not a timing signal."])


class EarningsRevisionAgent(SpecialistAgent):
    name="earnings_revisions"
    async def evaluate(self,ctx):
        rev=num(ctx.earnings,"eps_revision_30d_pct")
        surprise=num(ctx.earnings,"last_eps_surprise_pct")
        growth=num(ctx.earnings,"forward_eps_growth_pct")
        if all(v is None for v in [rev,surprise,growth]): return missing(self.name)
        score=50
        if rev is not None: score+=max(-22,min(22,rev*3))
        if surprise is not None: score+=max(-14,min(14,surprise*.8))
        if growth is not None: score+=max(-12,min(12,(growth-5)*.4))
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=78,
            thesis="Earnings surprise, revision breadth and forward growth momentum.",
            risks=["Consensus estimates may lag new information or be sparse in smaller markets."])


class LiquidityMicrostructureAgent(SpecialistAgent):
    name="liquidity_microstructure"
    async def evaluate(self,ctx):
        spread=num(ctx.execution,"spread_bps")
        depth=num(ctx.execution,"depth_score")
        adv=num(ctx.execution,"adv_usd")
        m=ctx.market
        if spread is None and depth is None and adv is None:
            score=m.liquidity_score
        else:
            score=50
            if spread is not None: score+=max(-25,min(20,(25-spread)*.8))
            if depth is not None: score+=(depth-50)*.35
            if adv is not None: score+=max(-10,min(15,(adv/100000)-1))
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=85,
            thesis="Spread, depth, participation and executable-liquidity assessment.",
            risks=["Displayed depth can disappear during volatility; small-account fees can dominate edge."])


class VolatilityAgent(SpecialistAgent):
    name="volatility"
    async def evaluate(self,ctx):
        vol=ctx.market.volatility_pct
        atr=num(ctx.execution,"atr_pct")
        gap=num(ctx.execution,"gap_risk_pct")
        score=70-min(45,vol*.9)
        if atr is not None: score-=min(15,atr*2)
        if gap is not None: score-=min(20,gap*2)
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=82,
            thesis="Volatility, ATR and discontinuous gap-risk control.",
            risks=["High-volatility assets can breach stops before execution."])


class CatalystAgent(SpecialistAgent):
    name="catalyst"
    async def evaluate(self,ctx):
        if not ctx.events:return missing(self.name)
        scores=[]
        for e in ctx.events:
            impact=float(e.get("impact_score",0))
            direction=float(e.get("direction",0))
            confidence=float(e.get("confidence",50))/100
            scores.append(direction*impact*confidence)
        raw=mean(scores) if scores else 0
        score=clip(50+raw)
        return AgentOpinion(agent=self.name,action=action(score),score=score,confidence=70,
            thesis="Upcoming corporate, macro and regulatory catalyst impact assessment.",
            risks=["Event outcomes and market reactions are inherently uncertain."])


class NewsCredibilityAgent(SpecialistAgent):
    name="news_credibility"
    async def evaluate(self,ctx):
        if not ctx.news:return missing(self.name)
        weighted=[]
        reliabilities=[]
        for n in ctx.news:
            rel=float(n.get("reliability",.5))
            sent=float(n.get("sentiment",0))
            freshness=float(n.get("freshness",1))
            weighted.append(sent*rel*freshness)
            reliabilities.append(rel)
        score=clip(50+mean(weighted)*35)
        return AgentOpinion(agent=self.name,action=action(score),score=score,
            confidence=clip(mean(reliabilities)*100),
            thesis="Source-weighted, freshness-adjusted news evidence rather than raw headline sentiment.",
            risks=["Narrative crowding and duplicated news can amplify false consensus."])


class RegulatoryAgent(SpecialistAgent):
    name="regulatory"
    async def evaluate(self,ctx):
        flags=int(num(ctx.regulatory,"material_flags",0) or 0)
        uncertainty=num(ctx.regulatory,"uncertainty_score",0) or 0
        approvals=num(ctx.regulatory,"pending_approvals",0) or 0
        score=clip(75-flags*18-uncertainty*.4-approvals*5)
        return AgentOpinion(agent=self.name,action=action(score),score=score,confidence=75,
            thesis="Licensing, enforcement, disclosure and pending-approval risk assessment.",
            risks=["Regulatory events can be binary and jurisdiction-specific."])


class AccountingForensicsAgent(SpecialistAgent):
    name="accounting_forensics"
    async def evaluate(self,ctx):
        if not ctx.accounting:return missing(self.name)
        accrual=num(ctx.accounting,"accruals_ratio_pct",0) or 0
        cfo_ni=num(ctx.accounting,"cfo_to_net_income",1) or 1
        restatements=num(ctx.accounting,"restatement_count",0) or 0
        related=num(ctx.accounting,"related_party_risk_score",0) or 0
        score=75-min(25,abs(accrual)*1.5)-max(0,(1-cfo_ni)*25)-restatements*12-related*.25
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=78,
            thesis="Cash conversion, accrual intensity, restatements and related-party forensic screen.",
            risks=["Accounting classifications differ across sectors and jurisdictions."])


class OwnershipAgent(SpecialistAgent):
    name="ownership"
    async def evaluate(self,ctx):
        insider=num(ctx.ownership,"insider_buying_score")
        inst=num(ctx.ownership,"institutional_flow_score")
        concentration=num(ctx.ownership,"holder_concentration_pct")
        if all(v is None for v in [insider,inst,concentration]):return missing(self.name)
        score=50
        if insider is not None:score+=(insider-50)*.3
        if inst is not None:score+=(inst-50)*.3
        if concentration is not None and concentration>70:score-=min(15,(concentration-70)*.5)
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=60,
            thesis="Insider activity, institutional flows and ownership concentration assessment.",
            risks=["Ownership data can be delayed and incomplete."])


class DerivativesAgent(SpecialistAgent):
    name="derivatives"
    async def evaluate(self,ctx):
        if not ctx.derivatives:return missing(self.name)
        skew=num(ctx.derivatives,"put_call_skew_score",50) or 50
        iv=num(ctx.derivatives,"iv_percentile",50) or 50
        flow=num(ctx.derivatives,"bullish_flow_score",50) or 50
        score=50+(flow-50)*.35+(skew-50)*.15-(iv-50)*.15
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=60,
            thesis="Options-implied volatility, skew and directional-flow overlay.",
            risks=["Options markets can reflect hedging rather than directional conviction."])


class CurrencyAgent(SpecialistAgent):
    name="currency"
    async def evaluate(self,ctx):
        if not ctx.currency:return missing(self.name)
        carry=num(ctx.currency,"carry_score",50) or 50
        trend=num(ctx.currency,"trend_score",50) or 50
        deval=num(ctx.currency,"devaluation_risk_score",50) or 50
        score=50+(carry-50)*.2+(trend-50)*.25-(deval-50)*.35
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=72,
            thesis="Currency trend, carry and devaluation-risk overlay on investor returns.",
            risks=["FX can dominate local-asset returns for cross-border investors."])


class CrossAssetAgent(SpecialistAgent):
    name="cross_asset"
    async def evaluate(self,ctx):
        if not ctx.cross_asset:return missing(self.name)
        rates=num(ctx.cross_asset,"rates_support_score",50) or 50
        commodities=num(ctx.cross_asset,"commodity_support_score",50) or 50
        credit=num(ctx.cross_asset,"credit_conditions_score",50) or 50
        dollar=num(ctx.cross_asset,"usd_support_score",50) or 50
        score=mean([rates,commodities,credit,dollar])
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=68,
            thesis="Rates, credit, commodity and dollar regime cross-check.",
            risks=["Cross-asset relationships can break during regime transitions."])


class PortfolioFitAgent(SpecialistAgent):
    name="portfolio_fit"
    async def evaluate(self,ctx):
        corr=num(ctx.metadata,"portfolio_correlation",0) or 0
        sector=num(ctx.metadata,"sector_exposure_after_pct",0) or 0
        country=num(ctx.metadata,"country_exposure_after_pct",0) or 0
        score=80-abs(corr)*25-max(0,sector-35)*.7-max(0,country-60)*.5
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=80,
            thesis="Incremental diversification, concentration and portfolio-risk contribution.",
            risks=["Correlations rise during stress and historical estimates are unstable."])


class ExecutionAgent(SpecialistAgent):
    name="execution"
    async def evaluate(self,ctx):
        spread=num(ctx.execution,"spread_bps",50) or 50
        slip=num(ctx.execution,"expected_slippage_bps",20) or 20
        fees=num(ctx.execution,"fees_bps",10) or 10
        total=spread/2+slip+fees
        score=clip(90-total*.9)
        return AgentOpinion(agent=self.name,action=action(score),score=score,confidence=85,
            thesis="Expected spread, slippage and fee burden relative to the opportunity.",
            risks=["Execution costs can expand sharply around news and market opens/closes."])


class AlternativeDataAgent(SpecialistAgent):
    name="alternative_data"
    async def evaluate(self,ctx):
        if not ctx.alternative:return missing(self.name)
        signal=num(ctx.alternative,"signal_score",50) or 50
        quality=num(ctx.alternative,"quality_score",50) or 50
        freshness=num(ctx.alternative,"freshness_score",50) or 50
        score=signal*.5+quality*.3+freshness*.2
        return AgentOpinion(agent=self.name,action=action(score),score=clip(score),confidence=clip(quality),
            thesis="Lawfully sourced alternative-data signal with quality and freshness weighting.",
            risks=["Alternative data can be noisy, biased, expensive or legally restricted."])


SPECIALIST_AGENTS=[
    FundamentalQualityAgent(),ValuationAgent(),EarningsRevisionAgent(),
    LiquidityMicrostructureAgent(),VolatilityAgent(),CatalystAgent(),
    NewsCredibilityAgent(),RegulatoryAgent(),AccountingForensicsAgent(),
    OwnershipAgent(),DerivativesAgent(),CurrencyAgent(),CrossAssetAgent(),
    PortfolioFitAgent(),ExecutionAgent(),AlternativeDataAgent()
]
