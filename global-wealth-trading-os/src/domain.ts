export type AssetClass =
  | "EQUITY" | "ETF" | "OPTION" | "FUTURE" | "FX"
  | "CRYPTO" | "BOND" | "FUND" | "COMMODITY" | "CASH";

export type Side = "BUY" | "SELL";
export type OrderType = "MARKET" | "LIMIT" | "STOP" | "STOP_LIMIT";
export type Decision = "STRONG_BUY" | "BUY" | "WATCH" | "AVOID" | "EXIT";

export interface Asset {
  id: string;
  symbol: string;
  name: string;
  assetClass: AssetClass;
  venue: string;
  currency: string;
  country?: string;
}

export interface MarketSnapshot {
  asset: Asset;
  price: number;
  change1dPct: number;
  change20dPct: number;
  volatility20dPct: number;
  volumeScore: number;
  timestamp: string;
}

export interface Position {
  assetId: string;
  symbol: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  currency: string;
}

export interface Portfolio {
  baseCurrency: string;
  cash: number;
  equity: number;
  peakEquity: number;
  positions: Position[];
}

export interface Signal {
  assetId: string;
  score: number;
  decision: Decision;
  reasons: string[];
  confidence: number;
}

export interface RiskLimits {
  maxPositionPct: number;
  maxGrossExposurePct: number;
  maxSingleTradeRiskPct: number;
  maxPortfolioDrawdownPct: number;
  maxVolatilityPct: number;
  allowLeverage: boolean;
  killSwitch: boolean;
}

export interface TradeProposal {
  id: string;
  asset: Asset;
  side: Side;
  orderType: OrderType;
  quantity: number;
  referencePrice: number;
  limitPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
  riskAmount: number;
  signal: Signal;
  status: "PROPOSED" | "APPROVED" | "REJECTED" | "PAPER_FILLED" | "LIVE_SENT";
  createdAt: string;
}

export interface DecisionJournalEntry {
  id: string;
  assetId: string;
  proposalId?: string;
  decision: Decision;
  reasons: string[];
  confidence: number;
  createdAt: string;
}
