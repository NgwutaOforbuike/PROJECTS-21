import { MarketSnapshot, Portfolio, RiskLimits, Signal, TradeProposal } from "./domain.js";

export interface RiskDecision {
  allowed: boolean;
  reasons: string[];
  proposal?: Omit<TradeProposal, "id" | "createdAt" | "status">;
}

export function evaluateRisk(
  snapshot: MarketSnapshot,
  signal: Signal,
  portfolio: Portfolio,
  limits: RiskLimits
): RiskDecision {
  const reasons:string[] = [];
  if (limits.killSwitch) return { allowed:false, reasons:["Global kill switch is active."] };

  const country = snapshot.asset.country ?? "";
  if (!limits.allowedCountries.includes(country)) {
    return { allowed:false, reasons:[`Asset country ${country || "UNKNOWN"} is outside the Nigeria/US/UK mandate.`] };
  }

  if (snapshot.expectedDailyReturnPct === undefined) {
    return { allowed:false, reasons:[`No verified expected daily return estimate is available; the ${limits.targetDailyReturnPct}% target hurdle cannot be tested.`] };
  }

  if (snapshot.expectedDailyReturnPct < limits.targetDailyReturnPct) {
    return { allowed:false, reasons:[`Expected daily return ${snapshot.expectedDailyReturnPct.toFixed(2)}% is below the configured ${limits.targetDailyReturnPct}% target hurdle.`] };
  }

  const drawdownPct = portfolio.peakEquity <= 0
    ? 0
    : ((portfolio.peakEquity - portfolio.equity) / portfolio.peakEquity) * 100;

  if (drawdownPct >= limits.maxPortfolioDrawdownPct) {
    return { allowed:false, reasons:[`Portfolio drawdown ${drawdownPct.toFixed(2)}% exceeds limit.`] };
  }

  if (snapshot.volatility20dPct > limits.maxVolatilityPct) {
    return { allowed:false, reasons:["Asset volatility exceeds configured limit."] };
  }

  if (!["BUY","STRONG_BUY"].includes(signal.decision)) {
    return { allowed:false, reasons:[`Signal is ${signal.decision}, not a buy instruction.`] };
  }

  const maxPositionValue = portfolio.equity * (limits.maxPositionPct / 100);
  const riskBudget = portfolio.equity * (limits.maxSingleTradeRiskPct / 100);

  const stopDistancePct = Math.max(2, Math.min(12, snapshot.volatility20dPct * 0.65));
  const stopDistance = snapshot.price * (stopDistancePct / 100);
  const quantityByRisk = stopDistance > 0 ? riskBudget / stopDistance : 0;
  const quantityByPosition = maxPositionValue / snapshot.price;
  const rawQuantity = Math.max(0, Math.min(quantityByRisk, quantityByPosition));
  const quantity = Number(rawQuantity.toFixed(4));

  if (quantity <= 0) return { allowed:false, reasons:["Risk budget is too small for the current asset price."] };

  const positionValue = quantity * snapshot.price;
  const currentGross = portfolio.positions.reduce((s,p)=>s + Math.abs(p.quantity*p.currentPrice),0);
  const projectedGrossPct = portfolio.equity <= 0 ? 1000 : ((currentGross + positionValue) / portfolio.equity) * 100;

  if (projectedGrossPct > limits.maxGrossExposurePct) {
    return { allowed:false, reasons:["Projected gross exposure exceeds configured portfolio limit."] };
  }

  reasons.push(
    `Position capped at ${limits.maxPositionPct}% of portfolio equity.`,
    `Single-trade risk capped at ${limits.maxSingleTradeRiskPct}% of equity.`,
    `Stop distance derived from volatility: ${stopDistancePct.toFixed(2)}%.`
  );

  return {
    allowed:true,
    reasons,
    proposal:{
      asset:snapshot.asset,
      side:"BUY",
      orderType:"LIMIT",
      quantity,
      referencePrice:snapshot.price,
      limitPrice:snapshot.price,
      stopLoss:Number((snapshot.price-stopDistance).toFixed(6)),
      takeProfit:Number((snapshot.price * (1 + Math.max(limits.targetDailyReturnPct, stopDistancePct*2)/100)).toFixed(6)),
      riskAmount:Number((quantity*stopDistance).toFixed(2)),
      signal
    }
  };
}
