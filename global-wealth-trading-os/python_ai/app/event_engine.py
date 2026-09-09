from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class MarketEvent:
    region: str
    category: str
    title: str
    scheduled_at: datetime
    importance: int
    source_id: str


def event_risk(events:list[MarketEvent], now:datetime|None=None, horizon_hours:int=24)->list[MarketEvent]:
    now=now or datetime.now(timezone.utc)
    out=[]
    for e in events:
        delta=(e.scheduled_at-now).total_seconds()/3600
        if 0<=delta<=horizon_hours and e.importance>=2:
            out.append(e)
    return sorted(out,key=lambda e:e.scheduled_at)
