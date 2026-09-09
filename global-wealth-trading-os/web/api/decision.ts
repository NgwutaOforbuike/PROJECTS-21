import {requireOwner} from "../lib/auth";
export default function handler(req:any,res:any){
  if(!requireOwner(req,res))return;
  res.status(200).json({
    action:"NO_TRADE",
    status:"WAITING_FOR_QUALIFIED_LIVE_MARKET_DATA",
    reason:"No entitled live market feed has produced a candidate that can be independently validated and passed through the investment committee and risk governor.",
    entry:null,
    stop:null,
    target:null,
    quantity:null,
    confidence:null,
    maxPlannedLossUsd:0.75,
    minModelledReturnPct:5,
    generatedAt:new Date().toISOString()
  });
}
