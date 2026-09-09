from __future__ import annotations
from dataclasses import dataclass
from .backtest import BacktestMetrics


@dataclass
class PromotionDecision:
    allowed:bool
    reasons:list[str]


def can_promote_to_paper(metrics:BacktestMetrics,min_trades:int=50,min_sharpe:float=.8,max_drawdown_pct:float=15)->PromotionDecision:
    reasons=[]
    if metrics.trades<min_trades: reasons.append(f"needs at least {min_trades} trades")
    if metrics.sharpe<min_sharpe: reasons.append(f"Sharpe below {min_sharpe}")
    if abs(metrics.max_drawdown_pct)>max_drawdown_pct: reasons.append(f"drawdown exceeds {max_drawdown_pct}%")
    if metrics.profit_factor<1.1: reasons.append("profit factor below 1.1")
    return PromotionDecision(not reasons,reasons)


def can_promote_to_live(*args,**kwargs)->PromotionDecision:
    return PromotionDecision(False,["Live strategy promotion requires explicit owner approval and an external permission gate."])
