from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CostEstimate:
    spread_cost:float
    impact_cost:float
    commission:float
    fx_cost:float
    total_cost:float
    total_cost_pct_notional:float


def estimate_costs(
    notional:float,
    *,
    spread_bps:float,
    market_impact_bps:float,
    commission:float=0.0,
    fx_bps:float=0.0
)->CostEstimate:
    if notional<0: raise ValueError("notional cannot be negative")
    spread=notional*(spread_bps/2)/10000
    impact=notional*market_impact_bps/10000
    fx=notional*fx_bps/10000
    total=spread+impact+commission+fx
    pct=(total/notional*100) if notional else 0
    return CostEstimate(spread,impact,commission,fx,total,pct)
