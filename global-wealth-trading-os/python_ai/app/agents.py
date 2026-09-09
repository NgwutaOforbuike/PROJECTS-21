from __future__ import annotations

from abc import ABC, abstractmethod
from statistics import mean
from .models import AgentOpinion, MarketState


def _clip(x: float) -> float:
    return max(0.0, min(100.0, x))


def _action(score: float) -> str:
    if score >= 82:
        return "STRONG_BUY"
    if score >= 68:
        return "BUY"
    if score >= 52:
        return "WATCH"
    if score >= 35:
        return "AVOID"
    return "EXIT"


class InvestmentAgent(ABC):
    name: str

    @abstractmethod
    async def evaluate(self, state: MarketState) -> AgentOpinion:
        raise NotImplementedError


class TechnicalAgent(InvestmentAgent):
    name = "technical"

    async def evaluate(self, state: MarketState) -> AgentOpinion:
        trend = _clip(50 + state.day_change_pct * 7)
        liquidity = state.liquidity_score
        volatility_penalty = _clip(state.volatility_pct * 2)
        score = trend * 0.5 + liquidity * 0.3 + (100 - volatility_penalty) * 0.2
        return AgentOpinion(
            agent=self.name,
            action=_action(score),
            score=score,
            confidence=min(95, 55 + abs(score - 50)),
            thesis="Momentum, liquidity and volatility composite.",
            risks=["Short-term momentum can reverse rapidly."],
        )


class FundamentalAgent(InvestmentAgent):
    name = "fundamental"

    async def evaluate(self, state: MarketState) -> AgentOpinion:
        evidence_quality = mean([e.reliability for e in state.evidence]) * 100 if state.evidence else 40
        score = _clip(45 + 0.35 * evidence_quality + 0.15 * state.volume_score)
        return AgentOpinion(
            agent=self.name,
            action=_action(score),
            score=score,
            confidence=min(90, evidence_quality),
            thesis="Source-backed fundamental evidence quality and market participation composite.",
            risks=["Fundamental model is intentionally conservative until filings/fundamentals adapters are populated."],
        )


class MacroAgent(InvestmentAgent):
    name = "macro"

    async def evaluate(self, state: MarketState) -> AgentOpinion:
        # Placeholder feature model; macro adapters will enrich this with rates,
        # inflation, FX and growth regime inputs.
        score = _clip(55 + (state.consensus_confidence - 70) * 0.25)
        return AgentOpinion(
            agent=self.name,
            action=_action(score),
            score=score,
            confidence=65,
            thesis=f"Macro-regime neutral prior for {state.region.value}; confidence rises with primary-source coverage.",
            risks=["Macro feature set not fully activated yet."],
        )


class SentimentAgent(InvestmentAgent):
    name = "sentiment"

    async def evaluate(self, state: MarketState) -> AgentOpinion:
        news = [e for e in state.evidence if "news" in e.source_name.lower() or "filing" in e.source_name.lower()]
        score = 50 if not news else _clip(50 + 8 * mean([e.reliability for e in news]))
        return AgentOpinion(
            agent=self.name,
            action=_action(score),
            score=score,
            confidence=45 if not news else 70,
            thesis="Evidence-backed news/sentiment prior; avoids inventing sentiment when no source is present.",
            risks=["Sparse evidence lowers confidence."],
        )


class QuantAgent(InvestmentAgent):
    name = "quant"

    async def evaluate(self, state: MarketState) -> AgentOpinion:
        expected = state.expected_return_pct or 0
        score = _clip(45 + expected * 3 + state.volume_score * 0.18 - state.volatility_pct * 0.45)
        return AgentOpinion(
            agent=self.name,
            action=_action(score),
            score=score,
            confidence=min(95, 50 + state.consensus_confidence * 0.4),
            thesis="Expected return, participation and volatility cross-sectional score.",
            risks=["Expected-return estimates are uncertain and must be validated out of sample."],
        )


DEFAULT_AGENTS = [MacroAgent(), FundamentalAgent(), TechnicalAgent(), SentimentAgent(), QuantAgent()]
