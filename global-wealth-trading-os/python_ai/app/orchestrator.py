from __future__ import annotations

from dataclasses import dataclass
from .committee import InvestmentCommittee
from .models import Mandate, MarketState, PortfolioState, TradePlan, AgentOpinion


@dataclass
class AssessedCandidate:
    state: MarketState
    opinions: list[AgentOpinion]
    plan: TradePlan


class AutonomousInvestmentOrchestrator:
    """
    Autonomous research/decision orchestration.

    It may independently rank and paper-plan investments. Live order execution
    is intentionally outside this class and remains separately permissioned.
    """

    def __init__(self, mandate: Mandate | None = None) -> None:
        self.mandate = mandate or Mandate()
        self.committee = InvestmentCommittee(self.mandate)

    async def daily_best(
        self,
        universe: list[MarketState],
        portfolio: PortfolioState,
    ) -> AssessedCandidate | None:
        assessed: list[AssessedCandidate] = []
        for state in universe:
            opinions, plan = await self.committee.assess(state, portfolio)
            assessed.append(AssessedCandidate(state, opinions, plan))

        qualified = [x for x in assessed if x.plan.action == "BUY"]
        if not qualified:
            return None

        def rank(x: AssessedCandidate) -> float:
            er = x.plan.expected_return_pct or 0
            data = x.state.consensus_confidence
            liquidity = x.state.liquidity_score
            confidence = x.plan.confidence
            volatility_penalty = min(30, x.state.volatility_pct)
            return er * 3.2 + data * 0.22 + liquidity * 0.18 + confidence * 0.20 - volatility_penalty * 0.25

        return max(qualified, key=rank)
