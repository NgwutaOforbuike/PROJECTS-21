from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass
class ForecastRecord:
    predicted_return_pct: float
    realized_return_pct: float
    confidence: float


@dataclass
class CalibrationReport:
    count: int
    mean_absolute_error: float
    bias: float
    hit_rate: float
    confidence_weighted_error: float


def assess(records: list[ForecastRecord]) -> CalibrationReport:
    if not records:
        return CalibrationReport(0,0,0,0,0)
    errors=[r.realized_return_pct-r.predicted_return_pct for r in records]
    mae=mean(abs(e) for e in errors)
    bias=mean(errors)
    hits=mean(1.0 if (r.predicted_return_pct>0)==(r.realized_return_pct>0) else 0.0 for r in records)
    weights=[max(0.01,r.confidence/100) for r in records]
    cwe=sum(abs(e)*w for e,w in zip(errors,weights))/sum(weights)
    return CalibrationReport(len(records),mae,bias,hits*100,cwe)
