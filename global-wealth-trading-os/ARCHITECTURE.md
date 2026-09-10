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


## Operational resilience
- drift.py — detects material return/distribution regime drift.
- transaction_costs.py — spread, market impact, commission and FX cost estimation.
- reconciliation.py — expected-versus-actual position reconciliation.
- alerts.py — critical/high/medium operational and risk alerts.
- database.py — SQLAlchemy persistence for decisions, evidence and realised outcomes.

These controls sit outside the forecasting models so a model cannot suppress its own risk, data-quality or reconciliation alarms.


## Governed training lifecycle

- dataset_builder.py — constructs labelled supervised datasets from provenance-labelled OHLCV observations.
- leakage.py — blocks temporal leakage, target contamination, duplicate timestamps and invalid split ordering.
- splits.py — strictly chronological train/validation/test partitions.
- trainer.py — fits multiple candidate regressors, selects on validation data and evaluates once on held-out test data.
- model_artifacts.py — persists model binaries with SHA-256 integrity hashes and metadata.
- dataset_registry.py — records dataset lineage, source IDs, timestamps, feature/label versions and dataset hashes.
- model_registry.py — champion/challenger promotion history by strategy.
- champion_challenger.py — prevents automatic replacement unless the challenger clears minimum validation criteria.
- retraining.py — retraining triggers based on model age, new clean observations or drift.
- training_service.py — end-to-end dataset -> train -> artifact -> registry pipeline.
- training_cli.py — reproducible command-line training entry point.

Production models are trained only on time-ordered, provenance-labelled datasets. The system never trains on the held-out test set and never promotes directly to live execution.

## Cost-aware decision and calibration layer — 2026-09-10

The 5% modelled-return hurdle is evaluated conservatively when calibration error and estimated round-trip costs are available:

`conservative net return = point forecast - calibration error buffer - estimated round-trip costs`

A point forecast that clears 5% but falls below 5% after those deductions is a no-trade. This is intentionally asymmetric: missing upside is preferable to weakening the owner's hurdle.

Risk sizing now treats estimated round-trip costs as part of the planned loss budget. Position notional is also capped by cash available, so the sizing layer cannot create leverage. The owner's core mandate remains unchanged: Nigeria/USA/UK only, 0.5% maximum planned risk per trade, minimum 5% modelled-return hurdle, no forced trades, leverage off, and live execution disabled unless separately authorised.

Backtest metrics can accept per-trade transaction-cost estimates and report net performance rather than only gross strategy returns. Calibration diagnostics include Brier score and expected calibration error for directional confidence, making it possible to distinguish a model that is directionally accurate from one whose confidence estimates are trustworthy.

### External operating context checked for this revision

- Nigeria SEC: proposed Digital and Virtual Assets Operations, Custody and Markets rules published 20 August 2026. Digital-asset logic must remain jurisdiction-aware and should not assume rules are static.
- UK HM Treasury: T+1 settlement is planned to become mandatory from 11 October 2027, increasing the importance of execution, cash and settlement-state realism.
- U.S. SEC: the 2023 predictive-data-analytics conflict proposal was formally withdrawn in June 2025. Internal AI governance therefore remains a system control rather than being hard-coded to a withdrawn proposal.

These developments are context for governance and testing; they do not autonomously relax or activate any trading permission.
