# Global Wealth AI — Python Intelligence Layer

This is the autonomous research and decision layer behind Global Wealth & Trading OS.

It is separate from the React dashboard and the TypeScript market/execution service.

## What it already does

- Maintains an append-only source-backed knowledge memory.
- Represents market observations with provenance and evidence.
- Runs independent Macro, Fundamental, Technical, Sentiment and Quant agents.
- Aggregates them through an Investment Committee.
- Enforces the owner's mandate:
  - starting equity: USD 150
  - Nigeria, USA and UK only
  - maximum planned loss per trade: 0.5% of equity
  - minimum modelled daily return hurdle: 5%
- Generates an entry zone, stop, target, quantity and exit rules.
- Returns NO_TRADE when nothing clears the mandate.
- Exposes a FastAPI service for knowledge ingestion and daily-best decisions.
- Never gives an AI agent permission to bypass the risk governor.

## Knowledge-building design

The system is designed to become more useful over time by storing:

1. Primary-source market and macro observations.
2. Corporate filings and corporate actions.
3. Research evidence and news with provenance.
4. Agent opinions and the evidence used.
5. Trade plans and actual paper/live outcomes.
6. Post-trade reviews explaining what worked and what failed.

The current portable store is JSONL. Production will move to PostgreSQL + pgvector/object storage so evidence can be retrieved semantically and audited by source/version.

## Planned intelligence services

- real market-data connectors and streaming feature pipeline
- filings/fundamentals parser
- macro regime classifier
- event/catalyst engine
- news/sentiment classifier
- feature store
- vector knowledge retrieval
- walk-forward backtester
- portfolio optimiser
- calibration engine comparing predicted vs realised returns
- strategy registry with versioned promotion/retirement
- paper execution simulator
- broker execution adapters behind an owner/risk permission boundary

## Critical design principle

The system may learn from outcomes and autonomously improve rankings, but it must not silently rewrite its own risk limits or deploy a new live strategy without validation and a promotion gate.
