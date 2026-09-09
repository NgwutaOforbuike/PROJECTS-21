# Global Wealth & Trading OS

Personal multi-asset trading operating system.

## Stage 1 scope

This branch implements the safety-critical core before any live brokerage credentials are connected:

- normalized global asset model
- portfolio/account state
- rule-based signal engine
- portfolio-aware risk engine
- paper broker and order ledger
- decision journal with reasons for every proposed action
- hard kill switch
- approval gate for live execution
- provider adapter interfaces for IBKR, Alpaca, Binance/Bybit and FX/CFD venues
- API endpoints for scanning, proposing, approving and paper-executing trades

## Execution policy

The system may autonomously analyse and paper-trade. Live execution is deliberately disabled until a provider adapter is connected and the owner explicitly approves an order.

This is intentional: strategy logic can be wrong, market data can be stale, APIs can fail and leveraged assets can cause losses larger than the initial position.

## Global coverage architecture

- **IBKR**: primary global securities/futures/FX/bonds/funds execution layer.
- **Alpaca**: US equities/options/crypto and paper trading.
- **Crypto exchanges**: exchange-specific spot/derivatives adapters.
- **FX/CFD adapter**: optional regional venue integration.
- **Market data adapters**: can be independent from the execution broker.

No single provider is assumed to cover every asset and jurisdiction.
