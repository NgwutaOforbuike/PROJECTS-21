from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime,timezone
from .drift import DriftReport


@dataclass
class RetrainingDecision:
    retrain:bool
    reasons:list[str]


def should_retrain(
    *,
    last_trained_at:str,
    new_clean_observations:int,
    drift:DriftReport|None,
    days_threshold:int=14,
    observation_threshold:int=50,
)->RetrainingDecision:
    reasons=[]
    last=datetime.fromisoformat(last_trained_at.replace("Z","+00:00"))
    age=(datetime.now(timezone.utc)-last).total_seconds()/86400
    if age>=days_threshold: reasons.append(f"model age {age:.1f} days exceeds {days_threshold}")
    if new_clean_observations>=observation_threshold: reasons.append(f"{new_clean_observations} new clean observations available")
    if drift and drift.drifted: reasons.append("model/data drift detected")
    return RetrainingDecision(bool(reasons),reasons)
