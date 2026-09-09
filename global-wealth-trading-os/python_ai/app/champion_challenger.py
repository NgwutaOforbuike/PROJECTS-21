from __future__ import annotations

from dataclasses import dataclass
from .model_artifacts import ModelMetadata


@dataclass
class ChallengeDecision:
    promote:bool
    reasons:list[str]


def _metric(m:ModelMetadata,name:str)->float:
    return float(m.metrics.get("test",{}).get(name,0))


def compare(
    champion:ModelMetadata|None,
    challenger:ModelMetadata,
    *,
    minimum_directional_accuracy:float=52.0,
    minimum_improvement_pct:float=2.0,
)->ChallengeDecision:
    reasons=[]
    cda=_metric(challenger,"directional_accuracy_pct")
    if cda<minimum_directional_accuracy:
        return ChallengeDecision(False,[f"challenger directional accuracy {cda:.2f}% below {minimum_directional_accuracy:.2f}%"])
    if champion is None:
        return ChallengeDecision(True,["no existing champion and challenger clears minimum validation gate"])
    old=_metric(champion,"directional_accuracy_pct")
    if cda<old+minimum_improvement_pct:
        reasons.append(f"directional accuracy improvement {cda-old:.2f}pp below required {minimum_improvement_pct:.2f}pp")
    new_mae=_metric(challenger,"mae")
    old_mae=_metric(champion,"mae")
    if old_mae>0 and new_mae>old_mae*1.05:
        reasons.append("challenger MAE is more than 5% worse than champion")
    return ChallengeDecision(not reasons,reasons or ["challenger materially improves validated performance"])
