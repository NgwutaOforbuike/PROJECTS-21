import {getQuotes} from "../../lib/market/router";
import type {InstrumentRequest} from "../../lib/market/types";

const DEFAULTS:InstrumentRequest[]=[
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
  if(req.method!=="GET"&&req.method!=="POST") return res.status(405).json({error:"Method not allowed"});
  let requests:InstrumentRequest[]=DEFAULTS;
  if(req.method==="POST"){
    const body=typeof req.body==="string"?JSON.parse(req.body):req.body;
    if(Array.isArray(body?.requests)&&body.requests.length){
      requests=body.requests.slice(0,50);
    }
  }
  const quotes=await getQuotes(requests);
  res.setHeader("Cache-Control","no-store, max-age=0");
  res.status(200).json({
    generatedAt:new Date().toISOString(),
    quotes
  });
}
