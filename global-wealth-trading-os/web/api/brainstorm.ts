import {requireOwner} from "../lib/auth";
type Message={role:"user"|"assistant";content:string};
function fallbackAnswer(message:string):string{return [`Working question: ${message}`,"","Separate the investment thesis from the evidence needed to prove it. Define the instrument, jurisdiction, time horizon, expected return driver and maximum acceptable loss.","","Test company fundamentals, valuation, macroeconomic conditions and market positioning. Identify what would invalidate the thesis, what data is missing and whether transaction costs, liquidity, tax or regulation change the result.","","Next research step: compare official filings and point-in-time market data for Nigeria, the United Kingdom and the United States where relevant. Do not trade until the evidence, risk limits and paper-trading gates are satisfied."].join("\n")}
export default async function handler(req:any,res:any){
  res.setHeader("Cache-Control","no-store, max-age=0");res.setHeader("X-Content-Type-Options","nosniff");
  if(!requireOwner(req,res))return;
  if(req.method!=="POST"){res.setHeader("Allow","POST");return res.status(405).json({error:"Method not allowed"})}
  const message=String(req.body?.message||"").trim();if(!message||message.length>4000)return res.status(400).json({error:"Message must contain 1–4,000 characters"});
  const history=(Array.isArray(req.body?.history)?req.body.history:[]).slice(-10).filter((m:any)=>m&&(m.role==="user"||m.role==="assistant")&&typeof m.content==="string").map((m:any):Message=>({role:m.role,content:m.content.slice(0,4000)}));
  const endpoint=process.env.BRAINSTORM_API_URL;const token=process.env.BRAINSTORM_API_TOKEN;
  if(endpoint){const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),15000);try{const upstream=await fetch(endpoint,{method:"POST",headers:{"content-type":"application/json",...(token?{authorization:`Bearer ${token}`}:{})},body:JSON.stringify({message,history,jurisdictions:["Nigeria","United Kingdom","United States"],execution_mode:"ANALYSIS_ONLY"}),signal:controller.signal});if(upstream.ok){const data:any=await upstream.json();const answer=String(data.answer||data.message||"").trim();if(answer)return res.status(200).json({answer,sources:Array.isArray(data.sources)?data.sources:[],mode:"CONNECTED"})}}catch{/* Safe local fallback. */}finally{clearTimeout(timer)}}
  return res.status(200).json({answer:fallbackAnswer(message),sources:[],mode:"LOCAL_ZERO_COST"})
}
