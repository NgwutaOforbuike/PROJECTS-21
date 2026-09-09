# Global Wealth & Trading OS — Engineering Architecture

## Core principle
This is a multi-language investment intelligence system, not a dashboard.

## Runtime layers
1. React/TypeScript command centre.
2. Fastify/TypeScript market-data and execution API.
3. Python AI/research/quant layer.
4. Market-data fabric with source hierarchy and consensus.
5. Knowledge and feature stores.
6. Backtesting, calibration, portfolio optimisation and strategy registry.
7. Paper execution simulator.
8. Broker adapters behind explicit risk/owner permissions.

## Python AI modules
- knowledge.py — evidence memory.
- agents.py — independent investment agents.
- committee.py — committee aggregation.
- orchestrator.py — daily-best ranking.
- risk.py — immutable mandate enforcement.
- feature_store.py — versioned model features.
- regime.py — market-regime classification.
- backtest.py — strategy metrics.
- calibration.py — predicted-vs-realised learning.
- portfolio.py — portfolio optimisation and risk contribution.
- strategy_registry.py — versioned strategy promotion lifecycle.
- paper_execution.py — slippage-aware paper fills.
- event_engine.py — event/catalyst risk.

## Strategy lifecycle
DRAFT -> BACKTESTED -> PAPER -> APPROVED -> RETIRED

No strategy may jump directly from code to live trading.

## Learning loop
evidence -> features -> agent opinions -> committee -> plan -> paper outcome -> realised result -> calibration -> strategy weighting/version review.

## Non-negotiable permissions
The learning system may change rankings and model weights only after validation.
It may not increase risk limits or activate live execution by itself.


## Expanded autonomous intelligence stack

- technical_features.py — momentum, volatility, RSI, MACD, ATR, range and volume features.
- forecasting.py — conservative multi-model return ensemble.
- walk_forward.py — expanding-window out-of-sample validation.
- data_quality.py — missing/stale/duplicate/impossible-price and extreme-move gates.
- monte_carlo.py — bootstrap portfolio path simulation.
- correlation.py — concentration/correlation alerts.
- outcomes.py — prediction-versus-realised outcome memory.
- promotion.py — quantitative promotion gates; live promotion is always denied without owner approval.
- daily_cycle.py — end-to-end daily recommendation cycle.
- research_score.py — primary/fresh/independent evidence scoring.
- audit.py — hash-chained audit events.
- connectors/fred.py — FRED macro observations.
- connectors/bea.py — BEA economic data queries.
- connectors/official_web.py — allowlisted snapshots from official Nigeria/UK authority websites.

## Decision safety gates

A recommendation is not considered decision-ready merely because an AI model likes it. The pipeline is designed to require:
1. acceptable source/data quality;
2. allowed geography;
3. liquidity threshold;
4. modelled return hurdle;
5. committee support;
6. 0.5% maximum planned equity risk;
7. auditability and reproducibility.

Backtest and paper results may change model weighting or strategy status after validation, but may not loosen the owner's mandate.
