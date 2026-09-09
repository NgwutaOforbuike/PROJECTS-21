export default function handler(req:any,res:any){
  res.status(200).json({
    maxRiskPerTradePct:0.5,
    maxPlannedLossUsd:0.75,
    maxDrawdownPct:12,
    leverage:false,
    liveExecution:false,
    killSwitch:true,
    dataConfidenceRequired:70,
    updatedAt:new Date().toISOString()
  });
}
