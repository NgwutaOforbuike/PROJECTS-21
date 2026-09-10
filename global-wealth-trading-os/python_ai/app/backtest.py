from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


@dataclass
class BacktestMetrics:
    total_return_pct: float
    annualized_return_pct: float
    annualized_volatility_pct: float
    sharpe: float
    sortino: float
    max_drawdown_pct: float
    hit_rate_pct: float
    profit_factor: float
    trades: int
    total_cost_pct: float = 0.0


def _max_drawdown(equity: np.ndarray) -> float:
    peaks = np.maximum.accumulate(equity)
    dd = (equity - peaks) / np.where(peaks == 0, 1, peaks)
    return float(dd.min() * 100)


def evaluate_returns(
    returns: list[float],
    periods_per_year: int = 252,
    *,
    transaction_costs_pct: list[float] | None = None,
) -> BacktestMetrics:
    """Evaluate net trade returns, optionally deducting per-trade all-in costs.

    ``returns`` are decimal returns (0.01 == 1%). ``transaction_costs_pct`` are
    percentage-point costs (0.20 == 0.20%) to make broker/FX estimates readable.
    """
    if not returns:
        return BacktestMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    r = np.asarray(returns, dtype=float)
    total_cost_pct = 0.0
    if transaction_costs_pct is not None:
        if len(transaction_costs_pct) != len(returns):
            raise ValueError("transaction_costs_pct must match returns length")
        costs = np.asarray(transaction_costs_pct, dtype=float)
        if np.any(costs < 0):
            raise ValueError("transaction costs cannot be negative")
        total_cost_pct = float(costs.sum())
        r = r - costs / 100.0

    equity = np.cumprod(1 + r)
    total = (equity[-1] - 1) * 100
    years = max(len(r) / periods_per_year, 1 / periods_per_year)
    ann = ((equity[-1]) ** (1 / years) - 1) * 100 if equity[-1] > 0 else -100
    vol = float(r.std(ddof=1) * math.sqrt(periods_per_year) * 100) if len(r) > 1 else 0
    mean = float(r.mean() * periods_per_year)
    std = float(r.std(ddof=1) * math.sqrt(periods_per_year)) if len(r) > 1 else 0
    sharpe = mean / std if std else 0
    downside = r[r < 0]
    dstd = float(downside.std(ddof=1) * math.sqrt(periods_per_year)) if len(downside) > 1 else 0
    sortino = mean / dstd if dstd else 0
    wins = r[r > 0]
    losses = r[r < 0]
    hit = float((r > 0).mean() * 100)
    pf = float(wins.sum() / abs(losses.sum())) if len(losses) and losses.sum() != 0 else float("inf")
    return BacktestMetrics(
        total_return_pct=float(total),
        annualized_return_pct=float(ann),
        annualized_volatility_pct=vol,
        sharpe=float(sharpe),
        sortino=float(sortino),
        max_drawdown_pct=_max_drawdown(equity),
        hit_rate_pct=hit,
        profit_factor=pf,
        trades=len(r),
        total_cost_pct=total_cost_pct,
    )
