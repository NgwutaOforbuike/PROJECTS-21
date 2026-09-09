export default function handler(req:any,res:any){
  res.status(200).json({
    startingEquityUsd:150,
    cashUsd:150,
    allowedMarkets:["Nigeria","United States","United Kingdom"],
    maxRiskPerTradePct:0.5,
    minModelledReturnPct:5,
    leverage:false,
    liveExecution:false,
    forcedTrades:false
  });
}
