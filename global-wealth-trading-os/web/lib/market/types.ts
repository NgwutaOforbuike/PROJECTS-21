export type AssetClass =
  | "EQUITY" | "ETF" | "OPTION" | "FUTURE" | "FX" | "CRYPTO"
  | "BOND" | "FUND" | "COMMODITY" | "CASH";

export type Region = "NG" | "US" | "UK" | "GLOBAL";

export interface InstrumentRequest {
  symbol:string;
  assetClass:AssetClass;
  region:Region;
  providerHint?:string;
  providerSymbol?:string;
  metadata?:Record<string,string|number|boolean|null>;
}

export interface NormalizedQuote {
  symbol:string;
  assetClass:AssetClass;
  region:Region;
  price:number|null;
  bid:number|null;
  ask:number|null;
  previousClose:number|null;
  change:number|null;
  changePct:number|null;
  volume:number|null;
  currency:string|null;
  marketState:string|null;
  observedAt:string|null;
  receivedAt:string;
  source:string;
  sourceTier:1|2|3|4;
  delayed:boolean;
  stale:boolean;
  confidence:number;
  available:boolean;
  error?:string;
}

export interface ProviderStatus {
  id:string;
  name:string;
  configured:boolean;
  assetClasses:AssetClass[];
  regions:Region[];
  realtime:boolean;
  notes:string;
}

export interface MarketProvider {
  id:string;
  status():ProviderStatus;
  supports(req:InstrumentRequest):boolean;
  quote(req:InstrumentRequest):Promise<NormalizedQuote>;
}
