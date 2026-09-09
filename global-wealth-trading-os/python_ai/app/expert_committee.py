from __future__ import annotations

import asyncio
from dataclasses import dataclass
from statistics import mean

from .agent_context import InvestmentContext
from .models import AgentOpinion
from .specialist_agents import SPECIALIST_AGENTS,SpecialistAgent
from .advanced_specialist_agents import ADVANCED_AGENTS


@dataclass
class ExpertCommitteeResult:
    opinions:list[AgentOpinion]
    score:float
    confidence:float
    buy_votes:int
    avoid_votes:int
    vetoes:list[str]
    decision:str
    reasons:list[str]


VETO_AGENTS={"regulatory","accounting_forensics","liquidity_microstructure","execution","volatility"}


class ExpertInvestmentCommittee:
    def __init__(self,agents:list[SpecialistAgent]|None=None)->None:
        self.agents=agents or (SPECIALIST_AGENTS+ADVANCED_AGENTS)

    async def evaluate(self,ctx:InvestmentContext)->ExpertCommitteeResult:
        opinions=await asyncio.gather(*(a.evaluate(ctx) for a in self.agents))
        weighted=[]
        confidences=[]
        buy_votes=0; avoid_votes=0; vetoes=[]
        for o in opinions:
            w=max(.10,o.confidence/100)
            weighted.append(o.score*w)
            confidences.append(o.confidence)
            if o.action in {"BUY","STRONG_BUY"}:buy_votes+=1
            if o.action in {"AVOID","EXIT"}:avoid_votes+=1
            if o.agent in VETO_AGENTS and o.score<30 and o.confidence>=60:
                vetoes.append(o.agent)
        score=sum(weighted)/sum(max(.10,o.confidence/100) for o in opinions)
        confidence=mean(confidences)
        if vetoes:
            decision="AVOID"
            reasons=[f"Specialist veto: {', '.join(vetoes)}"]
        elif score>=70 and buy_votes>=6:
            decision="BUY"
            reasons=[f"Expert committee score {score:.1f}; {buy_votes} positive specialist votes."]
        elif score>=58:
            decision="WATCH"
            reasons=[f"Committee score {score:.1f}; evidence is not strong enough for BUY."]
        else:
            decision="AVOID"
            reasons=[f"Committee score {score:.1f} below decision threshold."]
        return ExpertCommitteeResult(opinions,score,confidence,buy_votes,avoid_votes,vetoes,decision,reasons)
