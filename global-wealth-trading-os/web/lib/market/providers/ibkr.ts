import type {InstrumentRequest,MarketProvider,NormalizedQuote,ProviderStatus} from "../types";
import {n,nowIso,unavailable} from "../utils";

const BASE=()=>process.env.IBKR_WEB_API_URL||"";
const TOKEN=()=>process.env.IBKR_TOKEN||"";

export class IbkrProvider implements MarketProvider{
  id="ibkr";
  status():ProviderStatus{
    return {
      id:this.id,name:"Interactive Brokers Web API",configured:Boolean(BASE()),
      assetClasses:["EQUITY","ETF","OPTION","FUTURE","FX","CRYPTO","BOND","FUND","COMMODITY"],
      regions:["US","UK","NG","GLOBAL"],realtime:true,
      notes:"Broad multi-asset market data. Requires authenticated IBKR session and market-data entitlements."
    };
  }
  supports(req:InstrumentRequest){ return Boolean(req.metadata?.conid); }
  async quote(req:InstrumentRequest):Promise<NormalizedQuote>{
    if(!BASE()) return unavailable(req.symbol,req.assetClass,req.region,"IBKR","IBKR_WEB_API_URL not configured");
    const conid=String(req.metadata?.conid||"");
    if(!conid) return unavailable(req.symbol,req.assetClass,req.region,"IBKR","Instrument requires IBKR conid metadata");
    try{
      const u=new URL("/v1/api/iserver/marketdata/snapshot",BASE());
      u.searchParams.set("conids",conid);
      u.searchParams.set("fields","31,84,86,87,82,83,70,71");
      const headers:TwelveDataHeader={};
      if(TOKEN()) headers.Authorization=`Bearer ${TOKEN()}`;
      // IBKR snapshot endpoint may require an initial warm-up request before values appear.
      await fetch(u,{headers,cache:"no-store"});
      const r=await fetch(u,{headers,cache:"no-store"});
      if(!r.ok) throw new Error(`${r.status}`);
      const d=await r.json(); const row=Array.isArray(d)?d[0]:d;
      const price=n(row?.["31"]),bid=n(row?.["84"]),ask=n(row?.["86"]);
      return {
        symbol:req.symbol,assetClass:req.assetClass,region:req.region,price,bid,ask,
        previousClose:null,change:n(row?.["82"]),changePct:n(row?.["83"]),volume:n(row?.["87"]),
        currency:null,marketState:null,observedAt:nowIso(),receivedAt:nowIso(),
        source:"Interactive Brokers",sourceTier:2,delayed:false,stale:false,
        confidence:90,available:price!=null
      };
    }catch(e:any){ return unavailable(req.symbol,req.assetClass,req.region,"IBKR",e?.message||String(e)); }
  }
}

type TwelveDataHeader=Record<string,string>;
