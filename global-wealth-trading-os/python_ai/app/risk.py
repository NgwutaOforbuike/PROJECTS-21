from __future__ import annotations

from .models import Mandate, MarketState, PortfolioState, TradePlan


class RiskGovernor:
    def __init__(self, mandate: Mandate) -> None:
        self.mandate = mandate

    def validate(self, state: MarketState, portfolio: PortfolioState) -> list[str]:
        reasons: list[str] = []
        if state.region not in self.mandate.allowed_regions:
            reasons.append("Region is outside the Nigeria/USA/UK mandate.")
        if state.consensus_confidence < self.mandate.min_consensus_confidence:
            reasons.append("Market-data consensus confidence is below threshold.")
        if state.liquidity_score < self.mandate.min_liquidity_score:
            reasons.append("Liquidity score is below threshold.")
        if portfolio.drawdown_pct >= self.mandate.max_drawdown_pct:
            reasons.append("Portfolio drawdown limit has been reached.")
        if state.expected_return_pct is None:
            reasons.append("No modelled return estimate is available.")
        elif state.expected_return_pct < self.mandate.min_modelled_return_pct:
            reasons.append(
                f"Modelled return {state.expected_return_pct:.2f}% is below "
                f"{self.mandate.min_modelled_return_pct:.2f}% hurdle."
            )
        return reasons

    def size(self, state: MarketState, portfolio: PortfolioState, confidence: float) -> TradePlan:
        max_loss = portfolio.equity_usd * self.mandate.max_risk_per_trade_pct / 100
        stop_pct = max(1.0, min(5.0, state.volatility_pct * 0.55))
        stop_distance = state.price * stop_pct / 100
        quantity = max_loss / stop_distance if stop_distance else 0
        entry_low = state.price * 0.9975
        entry_high = state.price * 1.0025
        target_return = max(self.mandate.min_modelled_return_pct, state.expected_return_pct or 0)
        target = state.price * (1 + target_return / 100)
        return TradePlan(
            instrument_id=state.instrument_id,
            symbol=state.symbol,
            region=state.region,
            action="BUY",
            entry_low=round(entry_low, 6),
            entry_high=round(entry_high, 6),
            stop_loss=round(state.price - stop_distance, 6),
            target_price=round(target, 6),
            expected_return_pct=target_return,
            quantity=round(quantity, 6),
            max_loss_usd=round(max_loss, 4),
            risk_pct_equity=self.mandate.max_risk_per_trade_pct,
            confidence=confidence,
            rationale=[],
            exit_rules=[
                "Exit immediately if stop-loss/invalidation is reached.",
                "Exit early if committee consensus falls below BUY.",
                "Reassess before the relevant market closes if target and stop are not reached.",
                "Never widen the stop merely to keep a losing position alive.",
            ],
        )
