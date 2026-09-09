import {getQuote} from "../../lib/market/router";
import type {AssetClass,Region} from "../../lib/market/types";
import {requireOwner} from "../../lib/auth";

export default async function handler(req:any,res:any){
  if(!requireOwner(req,res))return;
  if(req.method!=="GET") return res.status(405).json({error:"Method not allowed"});
  const {symbol,assetClass,region,providerHint,providerSymbol}=req.query||{};
  if(!symbol||!assetClass||!region) return res.status(400).json({error:"symbol, assetClass and region are required"});
  const quote=await getQuote({
    symbol:String(symbol),
    assetClass:String(assetClass) as AssetClass,
    region:String(region) as Region,
    providerHint:providerHint?String(providerHint):undefined,
    providerSymbol:providerSymbol?String(providerSymbol):undefined,
  });
  res.setHeader("Cache-Control","no-store, max-age=0");
  res.status(200).json(quote);
}
