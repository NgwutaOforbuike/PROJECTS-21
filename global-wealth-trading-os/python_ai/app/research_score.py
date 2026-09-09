from __future__ import annotations
from dataclasses import dataclass
from .models import Evidence


@dataclass
class EvidenceScore:
    score:float
    primary_ratio:float
    freshness_ratio:float
    independent_sources:int
    blockers:list[str]


def score_evidence(evidence:list[Evidence],min_sources:int=2)->EvidenceScore:
    if not evidence: return EvidenceScore(0,0,0,0,["no evidence"])
    unique=len({e.source_id for e in evidence})
    primary=sum(e.source_tier==1 for e in evidence)/len(evidence)
    fresh=sum(not e.stale for e in evidence)/len(evidence)
    reliability=sum(e.reliability for e in evidence)/len(evidence)
    score=(primary*.35+fresh*.2+reliability*.3+min(1,unique/min_sources)*.15)*100
    blockers=[]
    if unique<min_sources: blockers.append("insufficient independent sources")
    if primary<.5: blockers.append("less than half of evidence is primary")
    if fresh<.8: blockers.append("too much stale evidence")
    return EvidenceScore(round(score,2),primary,fresh,unique,blockers)
