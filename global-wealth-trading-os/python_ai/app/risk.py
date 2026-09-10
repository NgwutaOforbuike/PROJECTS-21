from __future__ import annotations

from .models import Mandate, MarketState, PortfolioState, TradePlan


def conservative_net_return_pct(
    expected_return_pct: float | None,
    *,
    calibration_error_pct: float = 0.0,
    estimated_roundtrip_cost_pct: float = 0.0,
) -> float | None:
    """Return a conservative net forecast after model error and trading costs."""
    if expected_return_pct is None:
        return None
    if calibration_error_pct < 0:
        raise ValueError("calibration_error_pct cannot be negative")
    if estimated_roundtrip_cost_pct < 0:
        raise ValueError("estimated_roundtrip_cost_pct cannot be negative")
    return expected_return_pct - calibration_error_pct - estimated_roundtrip_cost_pct


class RiskGovernor:
    def __init__(self, mandate: Mandate) -> None:
        self.mandate = mandate

    def validate(
        self,
        state: MarketState,
        portfolio: PortfolioState,
        *,
        calibration_error_pct: float = 0.0,
        estimated_roundtrip_cost_pct: float = 0.0,
    ) -> list[str]:
        reasons: list[str] = []
        if state.region not in self.mandate.allowed_regions:
            reasons.append("Region is outside the Nigeria/USA/UK mandate.")
        if state.consensus_confidence < self.mandate.min_consensus_confidence:
            reasons.append("Market-data consensus confidence is below threshold.")
        if state.liquidity_score < self.mandate.min_liquidity_score:
            reasons.append("Liquidity score is below threshold.")
        if portfolio.drawdown_pct >= self.mandate.max_drawdown_pct:
            reasons.append("Portfolio drawdown limit has been reached.")

        conservative_return = conservative_net_return_pct(
            state.expected_return_pct,
            calibration_error_pct=calibration_error_pct,
            estimated_roundtrip_cost_pct=estimated_roundtrip_cost_pct,
        )
        if conservative_return is None:
            reasons.append("No modelled return estimate is available.")
        elif conservative_return < self.mandate.min_modelled_return_pct:
            reasons.append(
                f"Conservative net modelled return {conservative_return:.2f}% is below "
                f"{self.mandate.min_modelled_return_pct:.2f}% hurdle after "
                "calibration error and estimated round-trip costs."
            )
        return reasons

    def size(
        self,
        state: MarketState,
        portfolio: PortfolioState,
        confidence: float,
        *,
        estimated_roundtrip_cost_pct: float = 0.0,
    ) -> TradePlan:
        if estimated_roundtrip_cost_pct < 0:
            raise ValueError("estimated_roundtrip_cost_pct cannot be negative")

        max_loss = portfolio.equity_usd * self.mandate.max_risk_per_trade_pct / 100
        stop_pct = max(1.0, min(5.0, state.volatility_pct * 0.55))
        stop_distance = state.price * stop_pct / 100
        entry_low = state.price * 0.9975
        entry_high = state.price * 1.0025

        cost_per_unit = state.price * estimated_roundtrip_cost_pct / 100
        loss_per_unit = stop_distance + cost_per_unit
        risk_quantity = max_loss / loss_per_unit if loss_per_unit else 0.0

        # Leverage is off: use the top of the permitted entry band so even an
        # adverse planned entry cannot push BUY notional above available cash.
        cash_quantity = portfolio.cash_usd / entry_high if entry_high else 0.0
        quantity = min(risk_quantity, cash_quantity)

        target_return = max(self.mandate.min_modelled_return_pct, state.expected_return_pct or 0)
        target = state.price * (1 + target_return / 100)
        planned_loss = quantity * loss_per_unit

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
            max_loss_usd=round(planned_loss, 4),
            risk_pct_equity=round((planned_loss / portfolio.equity_usd * 100), 6)
            if portfolio.equity_usd
            else 0.0,
            confidence=confidence,
            rationale=[
                "Position size includes estimated round-trip trading costs in the loss budget.",
                "BUY notional is capped at the top of the entry band by cash available; leverage remains disabled.",
            ],
            exit_rules=[
                "Exit immediately if stop-loss/invalidation is reached.",
                "Exit early if committee consensus falls below BUY.",
                "Reassess before the relevant market closes if target and stop are not reached.",
                "Never widen the stop merely to keep a losing position alive.",
            ],
        )
