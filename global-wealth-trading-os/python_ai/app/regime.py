from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Regime:
    label: str
    confidence: float
    reasons: list[str]


def classify_regime(
    equity_trend_pct: float,
    volatility_pct: float,
    policy_rate_change_bps: float,
    inflation_change_pct: float,
    usd_trend_pct: float,
) -> Regime:
    score=0.0
    reasons=[]
    if equity_trend_pct > 3:
        score += 2; reasons.append("equity trend positive")
    elif equity_trend_pct < -3:
        score -= 2; reasons.append("equity trend negative")

    if volatility_pct > 25:
        score -= 2; reasons.append("high volatility")
    elif volatility_pct < 15:
        score += 1; reasons.append("low volatility")

    if policy_rate_change_bps < 0:
        score += 1; reasons.append("policy easing")
    elif policy_rate_change_bps > 50:
        score -= 1; reasons.append("policy tightening")

    if inflation_change_pct > 0.5:
        score -= 1; reasons.append("inflation accelerating")

    if usd_trend_pct > 3:
        reasons.append("USD strengthening")

    if score >= 3:
        label="RISK_ON"
    elif score <= -3:
        label="RISK_OFF"
    else:
        label="MIXED"

    confidence=min(95.0, 55.0 + abs(score)*10)
    return Regime(label,confidence,reasons)
