import type {InstrumentRequest,MarketProvider,NormalizedQuote,ProviderStatus} from "../types";
import {n,nowIso,pctChange,unavailable,withFreshness} from "../utils";

const KEY=()=>process.env.TWELVE_DATA_API_KEY||"";

export class TwelveDataProvider implements MarketProvider{
  id="twelve-data";
  status():ProviderStatus{
    return {
      id:this.id,name:"Twelve Data",configured:Boolean(KEY()),
      assetClasses:["EQUITY","ETF","FX","CRYPTO","FUND","COMMODITY"],
      regions:["US","UK","NG","GLOBAL"],realtime:true,
      notes:"Broad normalized quote fallback/enrichment; actual exchange coverage depends on subscription."
    };
  }
  supports(req:InstrumentRequest){
    return ["EQUITY","ETF","FX","CRYPTO","FUND","COMMODITY"].includes(req.assetClass);
  }
  async quote(req:InstrumentRequest):Promise<NormalizedQuote>{
    if(!KEY()) return unavailable(req.symbol,req.assetClass,req.region,"Twelve Data","TWELVE_DATA_API_KEY not configured");
    const symbol=req.providerSymbol||req.symbol;
    try{
      const url=new URL("https://api.twelvedata.com/quote");
      url.searchParams.set("symbol",symbol);
      url.searchParams.set("apikey",KEY());
      const r=await fetch(url,{cache:"no-store"});
      if(!r.ok) throw new Error(`${r.status}`);
      const d=await r.json();
      if(d.status==="error") throw new Error(d.message||"provider error");
      const price=n(d.close)||n(d.price), previous=n(d.previous_close);
      const observed=d.timestamp?new Date(Number(d.timestamp)*1000).toISOString():nowIso();
      return withFreshness({
        symbol:req.symbol,assetClass:req.assetClass,region:req.region,price,
        bid:n(d.bid),ask:n(d.ask),previousClose:previous,
        change:n(d.change) ?? (price!=null&&previous!=null?price-previous:null),
        changePct:n(d.percent_change) ?? pctChange(price,previous),
        volume:n(d.volume),currency:d.currency||null,marketState:d.is_market_open===true?"OPEN":d.is_market_open===false?"CLOSED":null,
        observedAt:observed,receivedAt:nowIso(),source:"Twelve Data",sourceTier:3,
        delayed:false,stale:false,confidence:75,available:price!=null
      },120_000);
    }catch(e:any){
      return unavailable(req.symbol,req.assetClass,req.region,"Twelve Data",e?.message||String(e));
    }
  }
}
