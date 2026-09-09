from __future__ import annotations

from dataclasses import dataclass
from .specialist_agents import SPECIALIST_AGENTS


@dataclass(frozen=True)
class AgentDescriptor:
    name:str
    category:str
    veto_capable:bool


_CATEGORIES={
    "fundamental_quality":"fundamental",
    "valuation":"fundamental",
    "earnings_revisions":"fundamental",
    "liquidity_microstructure":"market",
    "volatility":"risk",
    "catalyst":"event",
    "news_credibility":"research",
    "regulatory":"risk",
    "accounting_forensics":"risk",
    "ownership":"fundamental",
    "derivatives":"market",
    "currency":"macro",
    "cross_asset":"macro",
    "portfolio_fit":"portfolio",
    "execution":"execution",
    "alternative_data":"research",
}
_VETO={"regulatory","accounting_forensics","liquidity_microstructure","execution","volatility"}


def descriptors()->list[AgentDescriptor]:
    return [
        AgentDescriptor(a.name,_CATEGORIES.get(a.name,"other"),a.name in _VETO)
        for a in SPECIALIST_AGENTS
    ]
