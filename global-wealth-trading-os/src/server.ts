import Fastify from "fastify";
import cors from "@fastify/cors";
import { randomUUID } from "node:crypto";
import { MarketSnapshot, Portfolio, RiskLimits, TradeProposal } from "./domain.js";
import { scoreMarket } from "./strategy.js";
import { evaluateRisk } from "./risk.js";
import { PaperBroker } from "./paperBroker.js";
import { providerRoadmap } from "./providers.js";

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
  maxSingleTradeRiskPct:0.75,
  maxPortfolioDrawdownPct:12,
  maxVolatilityPct:45,
  allowLeverage:false,
  killSwitch:false,
  allowedCountries:["Nigeria","United States","United Kingdom"],
  targetDailyReturnPct:15
};

const proposals=new Map<string,TradeProposal>();
const paper=new PaperBroker();

app.get("/health",async()=>({ok:true,service:"global-wealth-trading-os"}));
app.get("/portfolio",async()=>portfolio);
app.get("/risk-limits",async()=>limits);
app.get("/providers",async()=>providerRoadmap);
app.get("/proposals",async()=>Array.from(proposals.values()));
app.get("/paper/fills",async()=>paper.fills);

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
