import type {NormalizedQuote} from "./types";

export const nowIso=()=>new Date().toISOString();

export function n(value:any):number|null{
  if(value===null||value===undefined||value==="") return null;
  const x=Number(String(value).replace(/[,%$£₦]/g,""));
  return Number.isFinite(x)?x:null;
}

export function pctChange(price:number|null,previous:number|null):number|null{
  if(price==null||previous==null||previous===0) return null;
  return (price/previous-1)*100;
}

export function withFreshness(q:NormalizedQuote,maxAgeMs=60_000):NormalizedQuote{
  const ts=q.observedAt?new Date(q.observedAt).getTime():NaN;
  const stale=!Number.isFinite(ts)||Date.now()-ts>maxAgeMs;
  return {...q,stale,confidence:Math.max(0,q.confidence-(stale?30:0))};
}

export function unavailable(
  symbol:string,assetClass:any,region:any,source:string,error:string
):NormalizedQuote{
  return {
    symbol,assetClass,region,price:null,bid:null,ask:null,previousClose:null,
    change:null,changePct:null,volume:null,currency:null,marketState:null,
    observedAt:null,receivedAt:nowIso(),source,sourceTier:3,delayed:false,
    stale:true,confidence:0,available:false,error
  };
}
