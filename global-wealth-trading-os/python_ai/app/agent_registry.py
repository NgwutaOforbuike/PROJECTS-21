from __future__ import annotations

from dataclasses import dataclass
from .specialist_agents import SPECIALIST_AGENTS
from .advanced_specialist_agents import ADVANCED_AGENTS


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
    "factor_exposure":"factor",
    "corporate_actions":"event",
    "dividend":"fundamental",
    "crowding_short_interest":"market",
    "tax_friction":"execution",
    "management_quality":"fundamental",
    "supply_chain":"fundamental",
    "geopolitical":"macro",
    "capital_structure":"risk",
    "trend_persistence":"technical",
    "mean_reversion":"technical",
    "tail_risk":"risk",
}
_VETO={"regulatory","accounting_forensics","liquidity_microstructure","execution","volatility","tail_risk","capital_structure"}


def descriptors()->list[AgentDescriptor]:
    return [
        AgentDescriptor(a.name,_CATEGORIES.get(a.name,"other"),a.name in _VETO)
        for a in (SPECIALIST_AGENTS+ADVANCED_AGENTS)
    ]
