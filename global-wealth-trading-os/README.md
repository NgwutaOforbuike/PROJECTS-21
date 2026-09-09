# Global Wealth & Trading OS

Personal multi-asset trading operating system.

## Current scope

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
- private owner sign-in with a signed, HTTP-only session cookie
- research, model, data-source and integration status screens
- protected market, portfolio, risk, mandate and decision APIs

## Run locally

The repository contains the TypeScript trading core at the root and the Vite/Vercel application in `web/`.

1. Copy `.env.example` to `.env.local` and keep that file private.
2. Generate the owner password hash with `node scripts/hash-password.mjs`.
3. Set `OWNER_EMAIL`, `OWNER_PASSWORD_HASH`, and a long random `AUTH_SECRET` in `web/.env.local` or the Vercel project environment.
4. Install and validate the core with `npm install`, `npm test`, and `npm run build`.
5. Install and validate the web app with `cd web`, `npm install`, `npm run build`, and `npm run typecheck:api`.

For Vercel, set the project Root Directory to `web`. Keep Deployment Protection enabled until owner authentication is configured. The Vercel Hobby plan can host this stage without enabling Google Cloud billing, subject to Vercel's current usage limits.

## Optional integrations

The app reports each integration truthfully as configured, missing, or deferred. API keys remain server-side environment variables and must never be committed.

- Binance public market data works without a key.
- FRED and Twelve Data can be added for macro and multi-asset data.
- Alpaca can be connected for paper brokerage; live execution remains disabled.
- Google Drive is an optional research archive.
- Google Cloud is deferred until long-running model jobs genuinely require it.
- The Python intelligence service is separate from the Vercel frontend and is not presented as deployed until `PYTHON_AI_URL` points to a working service.

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


## Institutional feature benchmark

The product roadmap now includes:
- real-time market depth, spreads and liquidity monitoring
- advanced conditional/bracket/algo-order adapters
- factor, sector, geography and currency exposure analytics
- VaR/CVaR, stress testing and what-if portfolios
- intraday P&L and performance attribution
- catalyst and macro event calendars
- research/thesis notebook and post-trade review
- execution quality, slippage and fill analytics
- mandate/compliance monitoring, audit journal and exception escalation

These modules are inspired by recurring capabilities in institutional portfolio/risk and execution platforms. They do not imply equivalence to any specific commercial platform.
