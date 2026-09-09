import type {InstrumentRequest,MarketProvider,NormalizedQuote,ProviderStatus} from "../types";
import {n,nowIso,pctChange,unavailable,withFreshness} from "../utils";

export class BinanceProvider implements MarketProvider{
  id="binance";
  status():ProviderStatus{
    return {
      id:this.id,name:"Binance Public Market Data",configured:true,
      assetClasses:["CRYPTO"],regions:["GLOBAL"],realtime:true,
      notes:"Public exchange-native crypto quotes. Execution remains disabled."
    };
  }
  supports(req:InstrumentRequest){ return req.assetClass==="CRYPTO"; }

  async quote(req:InstrumentRequest):Promise<NormalizedQuote>{
    const symbol=(req.providerSymbol||req.symbol).replace(/[-/]/g,"").toUpperCase();
    try{
      const [ticker,book]=await Promise.all([
        fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${encodeURIComponent(symbol)}`,{cache:"no-store"}),
        fetch(`https://api.binance.com/api/v3/ticker/bookTicker?symbol=${encodeURIComponent(symbol)}`,{cache:"no-store"})
      ]);
      if(!ticker.ok) throw new Error(`ticker ${ticker.status}`);
      const t=await ticker.json();
      const b=book.ok?await book.json():{};
      const price=n(t.lastPrice), prev=n(t.prevClosePrice);
      return withFreshness({
        symbol:req.symbol,assetClass:req.assetClass,region:req.region,
        price,bid:n(b.bidPrice),ask:n(b.askPrice),previousClose:prev,
        change:n(t.priceChange),changePct:n(t.priceChangePercent),volume:n(t.volume),
        currency:symbol.endsWith("USDT")?"USDT":null,marketState:"OPEN_24_7",
        observedAt:nowIso(),receivedAt:nowIso(),source:"Binance",sourceTier:2,
        delayed:false,stale:false,confidence:90,available:price!=null
      },30_000);
    }catch(e:any){
      return unavailable(req.symbol,req.assetClass,req.region,"Binance",e?.message||String(e));
    }
  }
}
