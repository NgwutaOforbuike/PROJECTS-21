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
    brier_score: float = 0.0
    expected_calibration_error_pct: float = 0.0


def _direction_probability(record: ForecastRecord) -> float:
    confidence = min(100.0, max(0.0, record.confidence)) / 100.0
    return confidence if record.predicted_return_pct > 0 else 1.0 - confidence


def _expected_calibration_error(records: list[ForecastRecord], bins: int = 10) -> float:
    if not records:
        return 0.0
    weighted_gap = 0.0
    total = len(records)
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        bucket = [
            record
            for record in records
            if lower <= _direction_probability(record) < upper
            or (index == bins - 1 and _direction_probability(record) == 1.0)
        ]
        if not bucket:
            continue
        predicted = mean(_direction_probability(record) for record in bucket)
        realized = mean(1.0 if record.realized_return_pct > 0 else 0.0 for record in bucket)
        weighted_gap += (len(bucket) / total) * abs(predicted - realized)
    return weighted_gap * 100.0


def assess(records: list[ForecastRecord]) -> CalibrationReport:
    if not records:
        return CalibrationReport(0, 0, 0, 0, 0, 0, 0)
    errors = [r.realized_return_pct - r.predicted_return_pct for r in records]
    mae = mean(abs(e) for e in errors)
    bias = mean(errors)
    hits = mean(
        1.0 if (r.predicted_return_pct > 0) == (r.realized_return_pct > 0) else 0.0
        for r in records
    )
    weights = [max(0.01, min(1.0, max(0.0, r.confidence) / 100)) for r in records]
    cwe = sum(abs(e) * w for e, w in zip(errors, weights)) / sum(weights)

    probabilities = [_direction_probability(record) for record in records]
    outcomes = [1.0 if record.realized_return_pct > 0 else 0.0 for record in records]
    brier = mean((probability - outcome) ** 2 for probability, outcome in zip(probabilities, outcomes))
    ece = _expected_calibration_error(records)

    return CalibrationReport(
        len(records),
        mae,
        bias,
        hits * 100,
        cwe,
        brier,
        ece,
    )
