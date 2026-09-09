from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timezone
from .models import MarketState,PortfolioState
from .orchestrator import AutonomousInvestmentOrchestrator
from .knowledge import KnowledgeBase


@dataclass
class DailyCycleReport:
    ran_at:str
    candidates:int
    action:str
    selected_symbol:str|None
    confidence:float|None
    rationale:list[str]


class DailyInvestmentCycle:
    def __init__(self,orchestrator:AutonomousInvestmentOrchestrator|None=None,kb:KnowledgeBase|None=None)->None:
        self.orchestrator=orchestrator or AutonomousInvestmentOrchestrator()
        self.kb=kb or KnowledgeBase()

    async def run(self,universe:list[MarketState],portfolio:PortfolioState)->DailyCycleReport:
        best=await self.orchestrator.daily_best(universe,portfolio)
        now=datetime.now(timezone.utc).isoformat()
        if best is None:
            return DailyCycleReport(now,len(universe),"NO_TRADE",None,None,["No candidate cleared all mandate gates."])
        p=best.plan
        return DailyCycleReport(
            now,len(universe),"BEST_SETUP",best.state.symbol,p.confidence,p.rationale
        )
