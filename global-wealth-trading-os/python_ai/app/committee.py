from __future__ import annotations

import asyncio
from statistics import mean
from .agents import DEFAULT_AGENTS, InvestmentAgent
from .models import AgentOpinion, Mandate, MarketState, PortfolioState, TradePlan
from .risk import RiskGovernor


class InvestmentCommittee:
    def __init__(self, mandate: Mandate, agents: list[InvestmentAgent] | None = None) -> None:
        self.mandate = mandate
        self.agents = agents or DEFAULT_AGENTS
        self.risk = RiskGovernor(mandate)

    async def assess(self, state: MarketState, portfolio: PortfolioState) -> tuple[list[AgentOpinion], TradePlan]:
        opinions = await asyncio.gather(*(a.evaluate(state) for a in self.agents))
        blockers = self.risk.validate(state, portfolio)

        weighted_score = mean(o.score for o in opinions)
        buy_votes = sum(o.action in {"BUY", "STRONG_BUY"} for o in opinions)
        committee_conf = mean(o.confidence for o in opinions)

        if blockers or buy_votes < 3 or weighted_score < 65:
            plan = TradePlan(
                instrument_id=state.instrument_id,
                symbol=state.symbol,
                region=state.region,
                action="NO_TRADE",
                max_loss_usd=round(portfolio.equity_usd * self.mandate.max_risk_per_trade_pct / 100, 4),
                risk_pct_equity=self.mandate.max_risk_per_trade_pct,
                confidence=committee_conf,
                rationale=blockers or [
                    f"Committee did not clear threshold: {buy_votes}/5 buy votes, score {weighted_score:.1f}."
                ],
                exit_rules=[],
            )
            return opinions, plan

        plan = self.risk.size(state, portfolio, committee_conf)
        plan.rationale = [
            f"Committee: {buy_votes}/5 buy votes.",
            f"Mean committee score: {weighted_score:.1f}/100.",
            f"Market-data consensus confidence: {state.consensus_confidence:.1f}/100.",
            f"Modelled return hurdle cleared at {state.expected_return_pct:.2f}%."
        ]
        return opinions, plan
