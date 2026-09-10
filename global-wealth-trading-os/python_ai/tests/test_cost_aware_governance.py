from __future__ import annotations

import pytest

from app.backtest import evaluate_returns
from app.calibration import ForecastRecord, assess
from app.models import AssetClass, Mandate, MarketState, PortfolioState, Region
from app.risk import RiskGovernor, conservative_net_return_pct


def _state(expected_return_pct: float = 6.0, price: float = 100.0) -> MarketState:
    return MarketState(
        instrument_id="US:TEST",
        symbol="TEST",
        name="Test Asset",
        region=Region.US,
        asset_class=AssetClass.EQUITY,
        currency="USD",
        price=price,
        day_change_pct=0.0,
        volume_score=80.0,
        liquidity_score=80.0,
        volatility_pct=1.0,
        expected_return_pct=expected_return_pct,
        consensus_confidence=85.0,
    )


def test_conservative_net_hurdle_deducts_error_and_costs() -> None:
    governor = RiskGovernor(Mandate())
    portfolio = PortfolioState()

    reasons = governor.validate(
        _state(6.0),
        portfolio,
        calibration_error_pct=0.8,
        estimated_roundtrip_cost_pct=0.4,
    )

    assert any("Conservative net modelled return 4.80%" in reason for reason in reasons)
    assert conservative_net_return_pct(
        6.5,
        calibration_error_pct=0.8,
        estimated_roundtrip_cost_pct=0.4,
    ) == pytest.approx(5.3)


def test_position_size_includes_costs_in_half_percent_loss_budget() -> None:
    governor = RiskGovernor(Mandate(max_risk_per_trade_pct=0.5))
    portfolio = PortfolioState(equity_usd=150.0, cash_usd=150.0)

    plan = governor.size(
        _state(price=100.0),
        portfolio,
        confidence=85.0,
        estimated_roundtrip_cost_pct=1.0,
    )

    assert plan.quantity == pytest.approx(0.375)
    assert plan.max_loss_usd <= 0.75
    assert plan.risk_pct_equity <= 0.5


def test_position_size_never_uses_leverage() -> None:
    governor = RiskGovernor(Mandate())
    portfolio = PortfolioState(equity_usd=150.0, cash_usd=10.0)

    plan = governor.size(_state(price=100.0), portfolio, confidence=90.0)

    assert plan.quantity == pytest.approx(0.1)
    assert plan.quantity * 100.0 <= portfolio.cash_usd


def test_backtest_metrics_are_net_of_transaction_costs() -> None:
    gross = evaluate_returns([0.01, 0.01])
    net = evaluate_returns([0.01, 0.01], transaction_costs_pct=[0.2, 0.2])

    assert net.total_return_pct < gross.total_return_pct
    assert net.total_cost_pct == pytest.approx(0.4)
    assert net.trades == 2


def test_backtest_rejects_invalid_cost_series() -> None:
    with pytest.raises(ValueError):
        evaluate_returns([0.01], transaction_costs_pct=[0.1, 0.2])
    with pytest.raises(ValueError):
        evaluate_returns([0.01], transaction_costs_pct=[-0.1])


def test_calibration_reports_probability_quality() -> None:
    well_calibrated = assess(
        [
            ForecastRecord(5.0, 3.0, 90.0),
            ForecastRecord(-4.0, -2.0, 90.0),
        ]
    )
    badly_wrong = assess(
        [
            ForecastRecord(5.0, -3.0, 90.0),
            ForecastRecord(-4.0, 2.0, 90.0),
        ]
    )

    assert well_calibrated.brier_score == pytest.approx(0.01)
    assert badly_wrong.brier_score == pytest.approx(0.81)
    assert well_calibrated.expected_calibration_error_pct == pytest.approx(10.0)
