import { MarketSnapshot, Signal } from "./domain.js";

const clamp = (n:number,min=0,max=100)=>Math.max(min,Math.min(max,n));

export function scoreMarket(snapshot: MarketSnapshot): Signal {
  const trend = clamp(50 + snapshot.change20dPct * 2.2);
  const shortMomentum = clamp(50 + snapshot.change1dPct * 4);
  const liquidity = clamp(snapshot.volumeScore);
  const volatilityPenalty = clamp(snapshot.volatility20dPct * 1.8);

  const raw =
    trend * 0.42 +
    shortMomentum * 0.18 +
    liquidity * 0.20 +
    (100 - volatilityPenalty) * 0.20;

  const score = Math.round(clamp(raw));
  const decision =
    score >= 82 ? "STRONG_BUY" :
    score >= 68 ? "BUY" :
    score >= 52 ? "WATCH" :
    score >= 35 ? "AVOID" : "EXIT";

  const reasons = [
    `20-day momentum score: ${Math.round(trend)}`,
    `1-day momentum score: ${Math.round(shortMomentum)}`,
    `liquidity score: ${Math.round(liquidity)}`,
    `volatility penalty: ${Math.round(volatilityPenalty)}`
  ];

  return {
    assetId: snapshot.asset.id,
    score,
    decision,
    reasons,
    confidence: clamp(Math.abs(score - 50) * 1.5)
  };
}
