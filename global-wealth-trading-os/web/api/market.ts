type AssetClass="EQUITY"|"ETF"|"OPTION"|"FUTURE"|"FX"|"CRYPTO"|"BOND"|"FUND"|"COMMODITY"|"CASH";
import {requireOwner} from "../lib/auth";
type Region="NG"|"US"|"UK"|"GLOBAL";
type Req={symbol:string;assetClass:AssetClass;region:Region;providerHint?:string;providerSymbol?:string;metadata?:Record<string,any>};
type Quote={symbol:string;assetClass:AssetClass;region:Region;price:number|null;bid:number|null;ask:number|null;previousClose:number|null;change:number|null;changePct:number|null;volume:number|null;currency:string|null;marketState:string|null;observedAt:string|null;receivedAt:string;source:string;sourceTier:1|2|3|4;delayed:boolean;stale:boolean;confidence:number;available:boolean;error?:string};

const now=()=>new Date().toISOString();
const num=(v:any)=>{if(v===null||v===undefined||v==="")return null;const x=Number(String(v).replace(/[,%$£₦]/g,""));return Number.isFinite(x)?x:null};
const pct=(p:number|null,prev:number|null)=>p==null||prev==null||prev===0?null:(p/prev-1)*100;
const nope=(r:Req,source:string,error:string):Quote=>({symbol:r.symbol,assetClass:r.assetClass,region:r.region,price:null,bid:null,ask:null,previousClose:null,change:null,changePct:null,volume:null,currency:null,marketState:null,observedAt:null,receivedAt:now(),source,sourceTier:3,delayed:false,stale:true,confidence:0,available:false,error});

function freshness(q:Quote,maxAge=60000):Quote{
  const ts=q.observedAt?new Date(q.observedAt).getTime():NaN;
  const stale=!Number.isFinite(ts)||Date.now()-ts>maxAge;
  return {...q,stale,confidence:Math.max(0,q.confidence-(stale?30:0))};
}

async function binance(r:Req):Promise<Quote>{
  const s=(r.providerSymbol||r.symbol).replace(/[-/]/g,"").toUpperCase();
  try{
    const [tr,br]=await Promise.all([
      fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${encodeURIComponent(s)}`,{cache:"no-store"}),
      fetch(`https://api.binance.com/api/v3/ticker/bookTicker?symbol=${encodeURIComponent(s)}`,{cache:"no-store"})
    ]);
    if(!tr.ok)throw new Error(`ticker ${tr.status}`);
    const t=await tr.json(),b=br.ok?await br.json():{};
    const p=num(t.lastPrice),prev=num(t.prevClosePrice);
    return freshness({symbol:r.symbol,assetClass:r.assetClass,region:r.region,price:p,bid:num(b.bidPrice),ask:num(b.askPrice),previousClose:prev,change:num(t.priceChange),changePct:num(t.priceChangePercent),volume:num(t.volume),currency:s.endsWith("USDT")?"USDT":null,marketState:"OPEN_24_7",observedAt:now(),receivedAt:now(),source:"Binance",sourceTier:2,delayed:false,stale:false,confidence:90,available:p!=null},30000);
  }catch(e:any){return nope(r,"Binance",e?.message||String(e))}
}

async function alpaca(r:Req):Promise<Quote>{
  const key=process.env.ALPACA_API_KEY||process.env.APCA_API_KEY_ID||"";
  const secret=process.env.ALPACA_SECRET_KEY||process.env.APCA_API_SECRET_KEY||"";
  if(!key||!secret)return nope(r,"Alpaca","ALPACA_API_KEY / ALPACA_SECRET_KEY not configured");
  const headers={"APCA-API-KEY-ID":key,"APCA-API-SECRET-KEY":secret};
  const sym=encodeURIComponent(r.providerSymbol||r.symbol);
  try{
    if(r.assetClass==="CRYPTO"){
      const x=await fetch(`https://data.alpaca.markets/v1beta3/crypto/us/latest/quotes?symbols=${sym}`,{headers,cache:"no-store"});
      if(!x.ok)throw new Error(String(x.status));const d=await x.json();const q=d.quotes?.[r.providerSymbol||r.symbol]||d.quotes?.[Object.keys(d.quotes||{})[0]]||{};
      const bp=num(q.bp),ap=num(q.ap),p=bp!=null&&ap!=null?(bp+ap)/2:ap??bp;
      return freshness({symbol:r.symbol,assetClass:r.assetClass,region:r.region,price:p,bid:bp,ask:ap,previousClose:null,change:null,changePct:null,volume:null,currency:"USD",marketState:"OPEN_24_7",observedAt:q.t||now(),receivedAt:now(),source:"Alpaca",sourceTier:2,delayed:false,stale:false,confidence:88,available:p!=null},30000);
    }
    const url=r.assetClass==="OPTION"?`https://data.alpaca.markets/v1beta1/options/snapshots/${sym}`:`https://data.alpaca.markets/v2/stocks/${sym}/snapshot`;
    const x=await fetch(url,{headers,cache:"no-store"});if(!x.ok)throw new Error(`${x.status} ${await x.text()}`);
    const d=await x.json(),s=r.assetClass==="OPTION"?(d.snapshot||d):d,trade=s.latestTrade||s.latest_trade||{},quote=s.latestQuote||s.latest_quote||{},daily=s.dailyBar||s.daily_bar||{},prev=s.prevDailyBar||s.prev_daily_bar||{};
    const p=num(trade.p)||num(daily.c),pc=num(prev.c);
    return freshness({symbol:r.symbol,assetClass:r.assetClass,region:r.region,price:p,bid:num(quote.bp),ask:num(quote.ap),previousClose:pc,change:p!=null&&pc!=null?p-pc:null,changePct:pct(p,pc),volume:num(daily.v),currency:"USD",marketState:null,observedAt:trade.t||quote.t||daily.t||now(),receivedAt:now(),source:"Alpaca",sourceTier:2,delayed:false,stale:false,confidence:90,available:p!=null},60000);
  }catch(e:any){return nope(r,"Alpaca",e?.message||String(e))}
}

async function twelve(r:Req):Promise<Quote>{
  const key=process.env.TWELVE_DATA_API_KEY||"";
  if(!key)return nope(r,"Twelve Data","TWELVE_DATA_API_KEY not configured");
  try{
    const u=new URL("https://api.twelvedata.com/quote");u.searchParams.set("symbol",r.providerSymbol||r.symbol);u.searchParams.set("apikey",key);
    const x=await fetch(u,{cache:"no-store"});if(!x.ok)throw new Error(String(x.status));const d=await x.json();if(d.status==="error")throw new Error(d.message||"provider error");
    const p=num(d.close)||num(d.price),pc=num(d.previous_close),obs=d.timestamp?new Date(Number(d.timestamp)*1000).toISOString():now();
    return freshness({symbol:r.symbol,assetClass:r.assetClass,region:r.region,price:p,bid:num(d.bid),ask:num(d.ask),previousClose:pc,change:num(d.change)??(p!=null&&pc!=null?p-pc:null),changePct:num(d.percent_change)??pct(p,pc),volume:num(d.volume),currency:d.currency||null,marketState:d.is_market_open===true?"OPEN":d.is_market_open===false?"CLOSED":null,observedAt:obs,receivedAt:now(),source:"Twelve Data",sourceTier:3,delayed:false,stale:false,confidence:75,available:p!=null},120000);
  }catch(e:any){return nope(r,"Twelve Data",e?.message||String(e))}
}

async function fred(r:Req):Promise<Quote>{
  const key=process.env.FRED_API_KEY||"";if(!key)return nope(r,"FRED","FRED_API_KEY not configured");
  try{
    const u=new URL("https://api.stlouisfed.org/fred/series/observations");u.searchParams.set("series_id",r.providerSymbol||r.symbol);u.searchParams.set("api_key",key);u.searchParams.set("file_type","json");u.searchParams.set("sort_order","desc");u.searchParams.set("limit","1");
    const x=await fetch(u,{cache:"no-store"});if(!x.ok)throw new Error(String(x.status));const d=await x.json(),row=d.observations?.[0],p=num(row?.value);
    return {symbol:r.symbol,assetClass:r.assetClass,region:r.region,price:p,bid:null,ask:null,previousClose:null,change:null,changePct:null,volume:null,currency:"PERCENT",marketState:"REFERENCE",observedAt:row?.date?new Date(row.date+"T00:00:00Z").toISOString():null,receivedAt:now(),source:"FRED",sourceTier:1,delayed:true,stale:false,confidence:95,available:p!=null};
  }catch(e:any){return nope(r,"FRED",e?.message||String(e))}
}

async function ibkr(r:Req):Promise<Quote>{
  const base=process.env.IBKR_WEB_API_URL||"",token=process.env.IBKR_TOKEN||"",conid=String(r.metadata?.conid||"");
  if(!base)return nope(r,"IBKR","IBKR_WEB_API_URL not configured");
  if(!conid)return nope(r,"IBKR","Instrument requires IBKR conid metadata");
  try{
    const u=new URL("/v1/api/iserver/marketdata/snapshot",base);u.searchParams.set("conids",conid);u.searchParams.set("fields","31,84,86,87,82,83,70,71");
    const headers:Record<string,string>={};if(token)headers.Authorization=`Bearer ${token}`;
    await fetch(u,{headers,cache:"no-store"});const x=await fetch(u,{headers,cache:"no-store"});if(!x.ok)throw new Error(String(x.status));const d=await x.json(),row=Array.isArray(d)?d[0]:d,p=num(row?.["31"]);
    return {symbol:r.symbol,assetClass:r.assetClass,region:r.region,price:p,bid:num(row?.["84"]),ask:num(row?.["86"]),previousClose:null,change:num(row?.["82"]),changePct:num(row?.["83"]),volume:num(row?.["87"]),currency:null,marketState:null,observedAt:now(),receivedAt:now(),source:"Interactive Brokers",sourceTier:2,delayed:false,stale:false,confidence:90,available:p!=null};
  }catch(e:any){return nope(r,"IBKR",e?.message||String(e))}
}

async function quote(r:Req):Promise<Quote>{
  const attempts:((r:Req)=>Promise<Quote>)[]=[];
  if(r.providerHint==="ibkr")attempts.push(ibkr);
  if(r.providerHint==="alpaca")attempts.push(alpaca);
  if(r.assetClass==="CRYPTO")attempts.push(binance,alpaca,twelve,ibkr);
  else if(["EQUITY","ETF","OPTION"].includes(r.assetClass)&&r.region==="US")attempts.push(alpaca,ibkr,twelve);
  else if(r.assetClass==="BOND")attempts.push(ibkr,fred);
  else if(r.assetClass==="FUTURE")attempts.push(ibkr,twelve);
  else attempts.push(ibkr,twelve);
  const seen=new Set<any>(),errors:string[]=[];
  for(const fn of attempts){if(seen.has(fn))continue;seen.add(fn);const q=await fn(r);if(q.available)return q;if(q.error)errors.push(q.source+": "+q.error)}
  const q=nope(r,"router",errors.join(" | ")||"No configured provider supports this instrument");return q;
}

const defaults:Req[]=[
  {symbol:"NVDA",assetClass:"EQUITY",region:"US"},
  {symbol:"SPY",assetClass:"ETF",region:"US"},
  {symbol:"VOD.L",assetClass:"EQUITY",region:"UK",providerSymbol:"VOD:LSE"},
  {symbol:"DANGCEM",assetClass:"EQUITY",region:"NG",providerSymbol:"DANGCEM:NGX"},
  {symbol:"GBP/USD",assetClass:"FX",region:"GLOBAL"},
  {symbol:"USD/NGN",assetClass:"FX",region:"NG"},
  {symbol:"BTC/USDT",assetClass:"CRYPTO",region:"GLOBAL",providerSymbol:"BTCUSDT"},
  {symbol:"ETH/USDT",assetClass:"CRYPTO",region:"GLOBAL",providerSymbol:"ETHUSDT"},
  {symbol:"XAU/USD",assetClass:"COMMODITY",region:"GLOBAL"},
  {symbol:"ES",assetClass:"FUTURE",region:"US",providerHint:"ibkr"},
  {symbol:"AAPL OPTION",assetClass:"OPTION",region:"US",providerHint:"alpaca"},
  {symbol:"US10Y",assetClass:"BOND",region:"US",providerHint:"fred",providerSymbol:"DGS10"},
  {symbol:"VFIAX",assetClass:"FUND",region:"US"}
];

export default async function handler(req:any,res:any){
  if(!requireOwner(req,res))return;
  res.setHeader("Cache-Control","no-store, max-age=0");
  const mode=String(req.query?.mode||"quotes");
  if(mode==="providers")return res.status(200).json({generatedAt:now(),providers:[
    {id:"binance",name:"Binance Public Market Data",configured:true,assetClasses:["CRYPTO"],realtime:true},
    {id:"alpaca",name:"Alpaca Market Data",configured:Boolean(process.env.ALPACA_API_KEY||process.env.APCA_API_KEY_ID),assetClasses:["EQUITY","ETF","OPTION","CRYPTO"],realtime:true},
    {id:"twelve-data",name:"Twelve Data",configured:Boolean(process.env.TWELVE_DATA_API_KEY),assetClasses:["EQUITY","ETF","FX","CRYPTO","FUND","COMMODITY"],realtime:true},
    {id:"fred",name:"FRED",configured:Boolean(process.env.FRED_API_KEY),assetClasses:["BOND"],realtime:false},
    {id:"ibkr",name:"Interactive Brokers",configured:Boolean(process.env.IBKR_WEB_API_URL),assetClasses:["EQUITY","ETF","OPTION","FUTURE","FX","CRYPTO","BOND","FUND","COMMODITY"],realtime:true}
  ]});
  if(mode==="quote"){
    const q=req.query||{};if(!q.symbol||!q.assetClass||!q.region)return res.status(400).json({error:"symbol, assetClass and region are required"});
    return res.status(200).json(await quote({symbol:String(q.symbol),assetClass:String(q.assetClass) as AssetClass,region:String(q.region) as Region}));
  }
  return res.status(200).json({generatedAt:now(),quotes:await Promise.all(defaults.map(quote))});
}
