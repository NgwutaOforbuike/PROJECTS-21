export type SourceTier = 1 | 2 | 3 | 4;
export type AccessMode = "PUBLIC" | "API_KEY" | "BROKER_ACCOUNT" | "LICENSED" | "WEB_EXPORT" | "PARTNER";
export type DataDomain =
  | "REALTIME_QUOTES" | "HISTORICAL_BARS" | "DEPTH" | "TRADES" | "CORPORATE_ACTIONS"
  | "FUNDAMENTALS" | "FILINGS" | "NEWS" | "MACRO" | "FX" | "RATES"
  | "BONDS" | "OPTIONS" | "FUTURES" | "CRYPTO" | "REFERENCE";

export interface MarketDataSourceSpec {
  id: string;
  name: string;
  tier: SourceTier;
  regions: Array<"NG"|"US"|"UK"|"GLOBAL">;
  domains: DataDomain[];
  access: AccessMode;
  authoritativeFor?: string[];
  docsUrl?: string;
  notes: string;
}

export const marketDataSources: MarketDataSourceSpec[] = [
  {id:"ngx",name:"Nigerian Exchange (NGX)",tier:1,regions:["NG"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","TRADES","CORPORATE_ACTIONS","REFERENCE"],access:"LICENSED",authoritativeFor:["NGX listed securities","official exchange prices"],notes:"Primary exchange source; production real-time use may require market-data licensing or an authorised redistributor."},
  {id:"fmdq",name:"FMDQ Exchange / FMDQ Markets",tier:1,regions:["NG"],domains:["BONDS","RATES","FX","REFERENCE","HISTORICAL_BARS"],access:"LICENSED",authoritativeFor:["Nigerian fixed income and money-market reference data"],notes:"Primary Nigerian fixed-income/OTC market source; use official/licensed channels where required."},
  {id:"cbn",name:"Central Bank of Nigeria",tier:1,regions:["NG"],domains:["FX","RATES","MACRO"],access:"PUBLIC",authoritativeFor:["NFEM official exchange rate","CBN policy and monetary statistics"],docsUrl:"https://www.cbn.gov.ng/rates/ExchRateByCurrency.html",notes:"Use for official FX and monetary-policy data, not executable equity prices."},
  {id:"nbs-ng",name:"National Bureau of Statistics Nigeria",tier:1,regions:["NG"],domains:["MACRO"],access:"PUBLIC",authoritativeFor:["Nigeria CPI","GDP","labour and official statistics"],docsUrl:"https://www.nigerianstat.gov.ng/",notes:"Primary macro source for Nigeria."},
  {id:"dmo-ng",name:"Debt Management Office Nigeria",tier:1,regions:["NG"],domains:["BONDS","RATES","REFERENCE"],access:"PUBLIC",authoritativeFor:["FGN bond issuance","auction results","debt statistics"],docsUrl:"https://www.dmo.gov.ng/fgn-bonds",notes:"Primary sovereign-debt source."},
  {id:"sec-ng",name:"Securities and Exchange Commission Nigeria",tier:1,regions:["NG"],domains:["FILINGS","REFERENCE","CORPORATE_ACTIONS"],access:"PUBLIC",notes:"Regulatory notices, rules, issuer/public-market information where published."},

  {id:"nyse",name:"New York Stock Exchange",tier:1,regions:["US"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","DEPTH","TRADES","CORPORATE_ACTIONS","REFERENCE"],access:"LICENSED",authoritativeFor:["NYSE venue data"],docsUrl:"https://www.nyse.com/market-data",notes:"Direct exchange feeds include top/depth/trades/auction imbalance; licensed use."},
  {id:"nasdaq",name:"Nasdaq Market Data",tier:1,regions:["US"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","DEPTH","TRADES","CORPORATE_ACTIONS","REFERENCE"],access:"LICENSED",authoritativeFor:["Nasdaq venue data"],notes:"Direct exchange and consolidated-feed products; licensing applies."},
  {id:"sec-edgar",name:"SEC EDGAR / data.sec.gov",tier:1,regions:["US"],domains:["FILINGS","FUNDAMENTALS","REFERENCE"],access:"PUBLIC",authoritativeFor:["SEC filings","XBRL company facts"],docsUrl:"https://www.sec.gov/search-filings/edgar-application-programming-interfaces",notes:"No API key required for public EDGAR data APIs; respect SEC fair-access rules."},
  {id:"finra",name:"FINRA",tier:1,regions:["US"],domains:["BONDS","TRADES","REFERENCE"],access:"PUBLIC",authoritativeFor:["TRACE fixed-income transparency"],docsUrl:"https://www.finra.org/finra-data/fixed-income",notes:"Use for US corporate-bond/TRACE transparency and regulatory market data."},
  {id:"fred",name:"Federal Reserve Bank of St. Louis FRED/ALFRED",tier:1,regions:["US","GLOBAL"],domains:["MACRO","RATES"],access:"API_KEY",authoritativeFor:["curated US/global macro series and vintages"],docsUrl:"https://fred.stlouisfed.org/docs/api/fred/",notes:"Excellent macro aggregation; retain original source metadata for each series."},
  {id:"bls",name:"U.S. Bureau of Labor Statistics",tier:1,regions:["US"],domains:["MACRO"],access:"PUBLIC",authoritativeFor:["US CPI","employment","wages","productivity"],docsUrl:"https://www.bls.gov/developers/",notes:"Official labour/inflation data; v1 public, v2 registered."},
  {id:"bea",name:"U.S. Bureau of Economic Analysis",tier:1,regions:["US"],domains:["MACRO","FUNDAMENTALS"],access:"API_KEY",authoritativeFor:["US GDP","national accounts","international transactions"],docsUrl:"https://apps.bea.gov/api/signup/",notes:"Official economic statistics API."},
  {id:"ust",name:"U.S. Treasury",tier:1,regions:["US"],domains:["RATES","BONDS","MACRO"],access:"PUBLIC",authoritativeFor:["Treasury yield curve","Treasury fiscal/market reference data"],notes:"Use official Treasury datasets/feeds where available."},
  {id:"fed",name:"Federal Reserve Board",tier:1,regions:["US"],domains:["RATES","MACRO"],access:"PUBLIC",authoritativeFor:["policy rates","monetary and financial statistics"],notes:"Primary policy and central-bank source."},

  {id:"lse",name:"London Stock Exchange",tier:1,regions:["UK"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","DEPTH","TRADES","CORPORATE_ACTIONS","REFERENCE"],access:"LICENSED",authoritativeFor:["LSE venue data"],docsUrl:"https://www.londonstockexchange.com/market-data",notes:"Primary UK exchange source; direct real-time redistribution generally requires licensing."},
  {id:"boe",name:"Bank of England",tier:1,regions:["UK"],domains:["FX","RATES","MACRO"],access:"PUBLIC",authoritativeFor:["UK Bank Rate","official BoE yield curves","UK monetary statistics"],docsUrl:"https://www.bankofengland.co.uk/boeapps/database/",notes:"Primary UK central-bank database."},
  {id:"ons",name:"Office for National Statistics",tier:1,regions:["UK"],domains:["MACRO"],access:"PUBLIC",authoritativeFor:["UK CPI","GDP","labour and official statistics"],notes:"Primary UK macro source."},
  {id:"companies-house",name:"Companies House",tier:1,regions:["UK"],domains:["FILINGS","REFERENCE"],access:"API_KEY",authoritativeFor:["UK company registry data"],docsUrl:"https://developer.company-information.service.gov.uk/",notes:"Live real-time company information via official API."},
  {id:"fca",name:"Financial Conduct Authority / NSM",tier:1,regions:["UK"],domains:["FILINGS","REFERENCE","CORPORATE_ACTIONS"],access:"PUBLIC",notes:"Regulatory disclosures, prospectuses and National Storage Mechanism documents."},

  {id:"ibkr",name:"Interactive Brokers Market Data",tier:2,regions:["US","UK","GLOBAL"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","DEPTH","TRADES","OPTIONS","FUTURES","BONDS","FX","NEWS","REFERENCE"],access:"BROKER_ACCOUNT",docsUrl:"https://www.interactivebrokers.com/docs/tws-api/doc/introduction",notes:"Broad multi-asset broker feed with L1/L2, tick, historical, scanner and news capabilities subject to subscriptions and account permissions."},
  {id:"alpaca",name:"Alpaca Market Data",tier:2,regions:["US"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","TRADES","OPTIONS","CRYPTO"],access:"API_KEY",docsUrl:"https://docs.alpaca.markets/us/docs/about-market-data-api",notes:"HTTP/WebSocket market data; free tier is limited, paid plans expand US market coverage."},
  {id:"binance",name:"Binance Public Market Data",tier:2,regions:["GLOBAL"],domains:["CRYPTO","REALTIME_QUOTES","HISTORICAL_BARS","DEPTH","TRADES"],access:"PUBLIC",notes:"Use only where the instrument and user's jurisdictional constraints permit; exchange-native crypto market data."},
  {id:"bybit",name:"Bybit Public Market Data",tier:2,regions:["GLOBAL"],domains:["CRYPTO","REALTIME_QUOTES","HISTORICAL_BARS","DEPTH","TRADES"],access:"PUBLIC",notes:"Exchange-native crypto data; jurisdictional availability must be checked before execution."},

  {id:"databento",name:"Databento",tier:3,regions:["US","GLOBAL"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","DEPTH","TRADES","OPTIONS","FUTURES","REFERENCE"],access:"API_KEY",docsUrl:"https://databento.com/docs",notes:"Institutional-style normalized live/historical direct-feed data across multiple venues and asset classes."},
  {id:"massive",name:"Massive (formerly Polygon.io)",tier:3,regions:["US","GLOBAL"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","TRADES","OPTIONS","FUTURES","FX","CRYPTO","MACRO"],access:"API_KEY",docsUrl:"https://massive.com/docs",notes:"REST, WebSocket and bulk historical coverage across multiple asset classes."},
  {id:"twelve-data",name:"Twelve Data",tier:3,regions:["US","UK","GLOBAL"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","FX","CRYPTO","REFERENCE"],access:"API_KEY",notes:"Broad multi-market API; use as secondary/fallback unless venue entitlement is confirmed."},
  {id:"tiingo",name:"Tiingo",tier:3,regions:["US","GLOBAL"],domains:["HISTORICAL_BARS","REALTIME_QUOTES","NEWS","CRYPTO","FUNDAMENTALS"],access:"API_KEY",notes:"Useful for historical data/news and redundancy."},
  {id:"finnhub",name:"Finnhub",tier:3,regions:["US","UK","GLOBAL"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","FUNDAMENTALS","NEWS","MACRO","FX","CRYPTO"],access:"API_KEY",notes:"Multi-domain aggregator suitable for cross-checking and enrichment."},
  {id:"alpha-vantage",name:"Alpha Vantage",tier:3,regions:["US","UK","GLOBAL"],domains:["HISTORICAL_BARS","REALTIME_QUOTES","FUNDAMENTALS","NEWS","FX","CRYPTO","MACRO"],access:"API_KEY",docsUrl:"https://www.alphavantage.co/documentation/",notes:"Useful backup/enrichment source; real-time intraday access is plan/licensing dependent."},
  {id:"nasdaq-data-link",name:"Nasdaq Data Link",tier:3,regions:["US","GLOBAL"],domains:["HISTORICAL_BARS","MACRO","FUNDAMENTALS","REFERENCE"],access:"API_KEY",notes:"Dataset marketplace/aggregator; provenance varies by dataset."},

  {id:"stooq",name:"Stooq",tier:4,regions:["US","UK","GLOBAL"],domains:["HISTORICAL_BARS"],access:"PUBLIC",notes:"Fallback historical/discovery source only; never authoritative for live execution."},
  {id:"yahoo-fallback",name:"Yahoo Finance web data",tier:4,regions:["US","UK","GLOBAL"],domains:["REALTIME_QUOTES","HISTORICAL_BARS","NEWS"],access:"WEB_EXPORT",notes:"Discovery/fallback only because it is not the authoritative venue feed and unofficial programmatic use can be fragile."}
];

export const sourcesByTier = (tier:SourceTier) => marketDataSources.filter(s=>s.tier===tier);
export const sourcesForRegion = (region:"NG"|"US"|"UK") =>
  marketDataSources.filter(s=>s.regions.includes(region) || s.regions.includes("GLOBAL"));
