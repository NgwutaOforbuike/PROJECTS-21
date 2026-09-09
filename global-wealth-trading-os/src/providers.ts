import { Asset, MarketSnapshot, TradeProposal } from "./domain.js";

export interface MarketDataProvider {
  name: string;
  searchAssets(query:string): Promise<Asset[]>;
  getSnapshot(asset:Asset): Promise<MarketSnapshot>;
}

export interface ExecutionProvider {
  name: string;
  mode: "PAPER" | "LIVE";
  submitOrder(proposal:TradeProposal): Promise<{providerOrderId:string; status:string}>;
  cancelOrder(providerOrderId:string): Promise<void>;
}

export const providerRoadmap = {
  primaryGlobal:"IBKR",
  usEquitiesOptionsCrypto:"ALPACA",
  crypto:["BINANCE","BYBIT"],
  fxCfd:["OANDA_OR_REGIONAL_PROVIDER"],
  note:"Execution providers are adapters. Live credentials are never committed to source control."
} as const;
