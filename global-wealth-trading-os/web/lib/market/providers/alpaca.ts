import type {InstrumentRequest,MarketProvider,NormalizedQuote,ProviderStatus} from "../types";
import {n,nowIso,pctChange,unavailable,withFreshness} from "../utils";

const KEY=()=>process.env.ALPACA_API_KEY||process.env.APCA_API_KEY_ID||"";
const SECRET=()=>process.env.ALPACA_SECRET_KEY||process.env.APCA_API_SECRET_KEY||"";
const headers=()=>({"APCA-API-KEY-ID":KEY(),"APCA-API-SECRET-KEY":SECRET()});

export class AlpacaProvider implements MarketProvider{
  id="alpaca";
  status():ProviderStatus{
    return {
      id:this.id,name:"Alpaca Market Data",configured:Boolean(KEY()&&SECRET()),
      assetClasses:["EQUITY","ETF","OPTION","CRYPTO"],regions:["US","GLOBAL"],
      realtime:true,notes:"Stocks/options/crypto. Actual feed depends on Alpaca subscription entitlement."
    };
  }
  supports(req:InstrumentRequest){
    return ["EQUITY","ETF","OPTION","CRYPTO"].includes(req.assetClass) &&
      (req.region==="US"||req.assetClass==="CRYPTO");
  }

  async quote(req:InstrumentRequest):Promise<NormalizedQuote>{
    if(!KEY()||!SECRET()) return unavailable(req.symbol,req.assetClass,req.region,"Alpaca","ALPACA_API_KEY / ALPACA_SECRET_KEY not configured");
    const s=encodeURIComponent(req.providerSymbol||req.symbol);
    try{
      let url="";
      if(req.assetClass==="OPTION"){
        url=`https://data.alpaca.markets/v1beta1/options/snapshots/${s}`;
      }else if(req.assetClass==="CRYPTO"){
        url=`https://data.alpaca.markets/v1beta3/crypto/us/latest/quotes?symbols=${s}`;
      }else{
        url=`https://data.alpaca.markets/v2/stocks/${s}/snapshot`;
      }
      const r=await fetch(url,{headers:headers(),cache:"no-store"});
      if(!r.ok) throw new Error(`${r.status} ${await r.text()}`);
      const d=await r.json();

      if(req.assetClass==="CRYPTO"){
        const q=d.quotes?.[req.providerSymbol||req.symbol]||d.quotes?.[Object.keys(d.quotes||{})[0]]||{};
        const price=q.ap&&q.bp?(n(q.ap)!+n(q.bp)!)/2:n(q.ap)||n(q.bp);
        return withFreshness({
          symbol:req.symbol,assetClass:req.assetClass,region:req.region,price,
          bid:n(q.bp),ask:n(q.ap),previousClose:null,change:null,changePct:null,volume:null,
          currency:"USD",marketState:"OPEN_24_7",observedAt:q.t||nowIso(),receivedAt:nowIso(),
          source:"Alpaca",sourceTier:2,delayed:false,stale:false,confidence:88,available:price!=null
        },30_000);
      }

      const snap=req.assetClass==="OPTION"?(d.snapshot||d):d;
      const trade=snap.latestTrade||snap.latest_trade||{};
      const quote=snap.latestQuote||snap.latest_quote||{};
      const daily=snap.dailyBar||snap.daily_bar||{};
      const prev=snap.prevDailyBar||snap.prev_daily_bar||{};
      const price=n(trade.p)||n(daily.c);
      const previousClose=n(prev.c);
      return withFreshness({
        symbol:req.symbol,assetClass:req.assetClass,region:req.region,price,
        bid:n(quote.bp),ask:n(quote.ap),previousClose,
        change:price!=null&&previousClose!=null?price-previousClose:null,
        changePct:pctChange(price,previousClose),volume:n(daily.v),currency:"USD",
        marketState:null,observedAt:trade.t||quote.t||daily.t||nowIso(),receivedAt:nowIso(),
        source:"Alpaca",sourceTier:2,delayed:false,stale:false,confidence:90,available:price!=null
      },60_000);
    }catch(e:any){
      return unavailable(req.symbol,req.assetClass,req.region,"Alpaca",e?.message||String(e));
    }
  }
}
