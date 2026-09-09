from __future__ import annotations

from dataclasses import dataclass

from .agent_context import InvestmentContext
from .expert_committee import ExpertInvestmentCommittee,ExpertCommitteeResult
from .models import Mandate,TradePlan
from .risk import RiskGovernor


@dataclass
class InvestmentDecision:
    action:str
    committee:ExpertCommitteeResult
    trade_plan:TradePlan|None
    blockers:list[str]


class AutonomousInvestmentEngine:
    """
    Decision engine for research -> specialist committee -> risk governor -> trade plan.

    It may recommend and paper-plan. It cannot transmit live broker orders.
    """
    def __init__(self,mandate:Mandate|None=None)->None:
        self.mandate=mandate or Mandate()
        self.committee=ExpertInvestmentCommittee()
        self.risk=RiskGovernor(self.mandate)

    async def decide(self,ctx:InvestmentContext)->InvestmentDecision:
        committee=await self.committee.evaluate(ctx)
        blockers=self.risk.validate(ctx.market,ctx.portfolio)

        if committee.decision!="BUY":
            return InvestmentDecision(
                action="NO_TRADE",
                committee=committee,
                trade_plan=None,
                blockers=blockers+committee.reasons,
            )

        if blockers:
            return InvestmentDecision(
                action="NO_TRADE",
                committee=committee,
                trade_plan=None,
                blockers=blockers,
            )

        plan=self.risk.size(ctx.market,ctx.portfolio,committee.confidence)
        plan.rationale=[
            *committee.reasons,
            f"Expert committee score: {committee.score:.1f}/100.",
            f"Positive specialist votes: {committee.buy_votes}.",
            f"Data consensus confidence: {ctx.market.consensus_confidence:.1f}/100.",
        ]
        return InvestmentDecision("BUY",committee,plan,[])
