import {requireOwner} from "../lib/auth";

export default function handler(req:any,res:any){
  if(!requireOwner(req,res))return;
  const mode=String(req.query?.mode||"mandate");
  res.setHeader("Cache-Control","no-store, max-age=0");
  if(mode==="mandate") return res.status(200).json({
    startingEquityUsd:150,cashUsd:150,
    allowedMarkets:["Nigeria","United States","United Kingdom"],
    maxRiskPerTradePct:0.5,minModelledReturnPct:5,
    leverage:false,liveExecution:false,forcedTrades:false
  });
  if(mode==="decision") return res.status(200).json({
    action:"NO_TRADE",status:"LIVE_MARKET_ENGINE_ACTIVE",
    reason:"Live market data is now collected where providers are configured. A trade is only surfaced after data-quality, specialist-agent, 5% hurdle and 0.5% risk gates all pass.",
    entry:null,stop:null,target:null,quantity:null,confidence:null,
    maxPlannedLossUsd:0.75,minModelledReturnPct:5,generatedAt:new Date().toISOString()
  });
  if(mode==="portfolio") return res.status(200).json({
    equityUsd:150,cashUsd:150,investedUsd:0,positions:[],
    grossExposurePct:0,drawdownPct:0,updatedAt:new Date().toISOString()
  });
  if(mode==="risk") return res.status(200).json({
    maxRiskPerTradePct:0.5,maxPlannedLossUsd:0.75,maxDrawdownPct:12,
    leverage:false,liveExecution:false,killSwitch:true,dataConfidenceRequired:70,
    updatedAt:new Date().toISOString()
  });
  return res.status(400).json({error:"Unknown mode"});
}
