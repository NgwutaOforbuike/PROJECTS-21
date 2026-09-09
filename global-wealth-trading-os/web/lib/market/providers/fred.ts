import type {InstrumentRequest,MarketProvider,NormalizedQuote,ProviderStatus} from "../types";
import {n,nowIso,unavailable} from "../utils";

const KEY=()=>process.env.FRED_API_KEY||"";

export class FredProvider implements MarketProvider{
  id="fred";
  status():ProviderStatus{
    return {
      id:this.id,name:"FRED",configured:Boolean(KEY()),assetClasses:["BOND"],
      regions:["US","GLOBAL"],realtime:false,
      notes:"Official rates/yield reference data. Not an executable security quote."
    };
  }
  supports(req:InstrumentRequest){ return req.assetClass==="BOND"; }
  async quote(req:InstrumentRequest):Promise<NormalizedQuote>{
    if(!KEY()) return unavailable(req.symbol,req.assetClass,req.region,"FRED","FRED_API_KEY not configured");
    const series=req.providerSymbol||req.symbol;
    try{
      const u=new URL("https://api.stlouisfed.org/fred/series/observations");
      u.searchParams.set("series_id",series); u.searchParams.set("api_key",KEY());
      u.searchParams.set("file_type","json"); u.searchParams.set("sort_order","desc"); u.searchParams.set("limit","1");
      const r=await fetch(u,{cache:"no-store"}); if(!r.ok) throw new Error(String(r.status));
      const d=await r.json(); const row=d.observations?.[0]; const price=n(row?.value);
      return {
        symbol:req.symbol,assetClass:req.assetClass,region:req.region,price,bid:null,ask:null,
        previousClose:null,change:null,changePct:null,volume:null,currency:"PERCENT",
        marketState:"REFERENCE",observedAt:row?.date?new Date(row.date+"T00:00:00Z").toISOString():null,
        receivedAt:nowIso(),source:"FRED",sourceTier:1,delayed:true,stale:false,
        confidence:95,available:price!=null
      };
    }catch(e:any){ return unavailable(req.symbol,req.assetClass,req.region,"FRED",e?.message||String(e)); }
  }
}
