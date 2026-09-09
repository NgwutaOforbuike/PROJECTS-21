import Fastify from "fastify";
import cors from "@fastify/cors";
import { randomUUID } from "node:crypto";
import { MarketSnapshot, Portfolio, RiskLimits, TradeProposal } from "./domain.js";
import { scoreMarket } from "./strategy.js";
import { evaluateRisk } from "./risk.js";
import { PaperBroker } from "./paperBroker.js";
import { providerRoadmap } from "./providers.js";
import { AIServiceClient } from "./aiClient.js";
import { marketDataSources } from "./marketDataSources.js";
import { buildConsensus, MarketObservation } from "./dataFusion.js";

const app=Fastify({logger:true});
await app.register(cors,{origin:true});

const portfolio:Portfolio={
  baseCurrency:"USD",
  cash:150,
  equity:150,
  peakEquity:150,
  positions:[]
};

const limits:RiskLimits={
  maxPositionPct:10,
  maxGrossExposurePct:80,
  maxSingleTradeRiskPct:0.5,
  maxPortfolioDrawdownPct:12,
  maxVolatilityPct:45,
  allowLeverage:false,
  killSwitch:false,
  allowedCountries:["Nigeria","United States","United Kingdom"],
  targetDailyReturnPct:5
};

const proposals=new Map<string,TradeProposal>();
const paper=new PaperBroker();
const ai=new AIServiceClient();

app.get("/health",async()=>({ok:true,service:"global-wealth-trading-os"}));
app.get("/ai/health",async(req,reply)=>{
  try{return await ai.health();}catch(error){return reply.code(503).send({ok:false,error:String(error)});}
});
app.get("/ai/capabilities",async(req,reply)=>{
  try{return await ai.capabilities();}catch(error){return reply.code(503).send({error:String(error)});}
});
app.get("/ai/mandate",async(req,reply)=>{
  try{return await ai.mandate();}catch(error){return reply.code(503).send({error:String(error)});}
});
app.post<{Body:unknown}>("/ai/daily-cycle",async(req,reply)=>{
  try{return await ai.dailyCycle(req.body);}catch(error){return reply.code(503).send({error:String(error)});}
});
app.post<{Body:unknown}>("/ai/monte-carlo",async(req,reply)=>{
  try{return await ai.monteCarlo(req.body);}catch(error){return reply.code(503).send({error:String(error)});}
});
app.get("/portfolio",async()=>portfolio);
app.get("/risk-limits",async()=>limits);
app.get("/providers",async()=>providerRoadmap);
app.get("/market-data/sources",async()=>({
  total:marketDataSources.length,
  tiers:{
    primary:marketDataSources.filter(s=>s.tier===1).length,
    broker:marketDataSources.filter(s=>s.tier===2).length,
    aggregator:marketDataSources.filter(s=>s.tier===3).length,
    fallback:marketDataSources.filter(s=>s.tier===4).length
  },
  sources:marketDataSources
}));
app.post<{Body:{observations:MarketObservation[];maxAgeMs?:number;maxDispersionPct?:number;minimumIndependentSources?:number}}>("/market-data/consensus",async(req)=>{
  return buildConsensus(req.body.observations,{
    maxAgeMs:req.body.maxAgeMs ?? 15000,
    maxDispersionPct:req.body.maxDispersionPct ?? 0.35,
    minimumIndependentSources:req.body.minimumIndependentSources ?? 2
  });
});
app.get("/market-data/health",async()=>({
  status:"CONFIGURED_NOT_FULLY_ENTITLED",
  policy:{
    executionQuoteRequires:["fresh observation","non-delayed feed","confidence >= 70","at least 2 independent sources when available"],
    primarySourcePreferred:true,
    staleFeedQuarantine:true,
    conflictQuarantine:true
  },
  activePublicSources:marketDataSources.filter(s=>s.access==="PUBLIC").map(s=>s.id),
  credentialedSources:marketDataSources.filter(s=>["API_KEY","BROKER_ACCOUNT"].includes(s.access)).map(s=>s.id),
  licensedSources:marketDataSources.filter(s=>s.access==="LICENSED").map(s=>s.id)
}));
app.get("/institutional-capabilities",async()=>({
  marketIntelligence:["multi-market scanner","real-time watchlists","news and research ingestion","technical/fundamental signals","market breadth","liquidity and spread monitoring"],
  portfolioAnalytics:["intraday P&L","performance attribution","factor/sector/country/currency exposures","concentration","cash utilisation","correlation matrix"],
  risk:["pre-trade checks","VaR/CVaR","drawdown controls","stress tests","scenario analysis","what-if portfolio","beta/factor risk","liquidity risk"],
  execution:["limit/stop/stop-limit","bracket orders","conditional orders","VWAP/TWAP/POV adapters","smart-routing hooks","slippage tracking","fill-quality analytics"],
  governance:["audit journal","mandate monitoring","exception alerts","kill switch","owner approval","strategy versioning"],
  research:["thesis notebook","catalyst calendar","earnings/events","macro calendar","sentiment overlays","post-trade review"]
}));
app.get("/proposals",async()=>Array.from(proposals.values()));
app.get("/paper/fills",async()=>paper.fills);

app.post<{Body:MarketSnapshot[]}>("/daily-best",async(req,reply)=>{
  const ranked=req.body
    .map(snapshot=>{
      const signal=scoreMarket(snapshot);
      const risk=evaluateRisk(snapshot,signal,portfolio,limits);
      return {snapshot,signal,risk};
    })
    .filter(x=>x.risk.allowed && x.risk.proposal)
    .sort((a,b)=>{
      const ar=a.snapshot.expectedDailyReturnPct ?? 0;
      const br=b.snapshot.expectedDailyReturnPct ?? 0;
      return (br*0.6+b.signal.score*0.4)-(ar*0.6+a.signal.score*0.4);
    });

  if(!ranked.length){
    return {
      action:"NO_TRADE",
      reason:"No allowed-market setup clears both the 5% modelled return hurdle and the risk governor.",
      riskPerTradePct:limits.maxSingleTradeRiskPct
    };
  }

  const best=ranked[0];
  const p=best.risk.proposal!;
  return {
    action:"BEST_SETUP",
    asset:p.asset,
    expectedDailyReturnPct:best.snapshot.expectedDailyReturnPct,
    confidence:best.signal.confidence,
    entryZone:{
      low:Number((p.referencePrice*0.9975).toFixed(6)),
      high:Number((p.referencePrice*1.0025).toFixed(6))
    },
    stopLoss:p.stopLoss,
    takeProfit:p.takeProfit,
    quantity:p.quantity,
    maxRiskAmount:p.riskAmount,
    riskPerTradePct:limits.maxSingleTradeRiskPct,
    exitRules:[
      "Exit immediately if stop-loss is reached.",
      "Take profit at the configured target unless the strategy has explicitly upgraded the target.",
      "Exit early if the signal falls below BUY or the investment thesis is invalidated.",
      "If neither target nor stop is reached, reassess before the venue closes."
    ],
    reasons:[...best.signal.reasons,...best.risk.reasons]
  };
});

app.post<{Body:MarketSnapshot}>("/scan",async(req,reply)=>{
  const signal=scoreMarket(req.body);
  const risk=evaluateRisk(req.body,signal,portfolio,limits);
  if(!risk.allowed || !risk.proposal){
    return {signal,risk};
  }
  const proposal:TradeProposal={
    ...risk.proposal,
    id:randomUUID(),
    status:"PROPOSED",
    createdAt:new Date().toISOString()
  };
  proposals.set(proposal.id,proposal);
  return {signal,risk,proposal};
});

app.post<{Params:{id:string}}>("/proposals/:id/approve",async(req,reply)=>{
  const proposal=proposals.get(req.params.id);
  if(!proposal) return reply.code(404).send({error:"Proposal not found"});
  if(limits.killSwitch) return reply.code(409).send({error:"Kill switch active"});
  proposal.status="APPROVED";
  return proposal;
});

app.post<{Params:{id:string}}>("/proposals/:id/paper-execute",async(req,reply)=>{
  const proposal=proposals.get(req.params.id);
  if(!proposal) return reply.code(404).send({error:"Proposal not found"});
  const fill=paper.execute(proposal,portfolio);
  proposal.status="PAPER_FILLED";
  return {fill,portfolio};
});

app.post("/risk/kill-switch",async()=>{
  limits.killSwitch=true;
  return {killSwitch:true};
});

app.post("/risk/resume",async()=>{
  limits.killSwitch=false;
  return {killSwitch:false};
});

app.listen({host:"0.0.0.0",port:Number(process.env.PORT||8787)});
