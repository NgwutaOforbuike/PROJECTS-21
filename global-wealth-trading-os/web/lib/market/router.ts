import type {InstrumentRequest,NormalizedQuote,ProviderStatus} from "./types";
import {AlpacaProvider} from "./providers/alpaca";
import {BinanceProvider} from "./providers/binance";
import {FredProvider} from "./providers/fred";
import {IbkrProvider} from "./providers/ibkr";
import {TwelveDataProvider} from "./providers/twelveData";
import {unavailable} from "./utils";

const providers=[
  new IbkrProvider(),
  new AlpacaProvider(),
  new BinanceProvider(),
  new TwelveDataProvider(),
  new FredProvider(),
];

export function providerStatuses():ProviderStatus[]{ return providers.map(p=>p.status()); }

function rank(req:InstrumentRequest){
  const preferred:string[]=[];
  if(req.providerHint) preferred.push(req.providerHint);
  if(req.assetClass==="CRYPTO") preferred.push("binance","alpaca","twelve-data","ibkr");
  else if(["EQUITY","ETF","OPTION"].includes(req.assetClass) && req.region==="US") preferred.push("alpaca","ibkr","twelve-data");
  else if(req.assetClass==="BOND") preferred.push("ibkr","fred");
  else if(["FUTURE"].includes(req.assetClass)) preferred.push("ibkr");
  else preferred.push("ibkr","twelve-data");
  return [...new Set(preferred)];
}

export async function getQuote(req:InstrumentRequest):Promise<NormalizedQuote>{
  const ordered=rank(req)
    .map(id=>providers.find(p=>p.id===id))
    .filter(Boolean) as typeof providers;
  const errors:string[]=[];
  for(const p of ordered){
    if(!p.supports(req)) continue;
    const status=p.status();
    if(!status.configured && p.id!=="binance") continue;
    const q=await p.quote(req);
    if(q.available) return q;
    if(q.error) errors.push(`${p.id}: ${q.error}`);
  }
  return unavailable(req.symbol,req.assetClass,req.region,"router",errors.join(" | ")||"No configured provider supports this instrument");
}

export async function getQuotes(requests:InstrumentRequest[]){
  return Promise.all(requests.map(getQuote));
}
