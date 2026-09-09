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
