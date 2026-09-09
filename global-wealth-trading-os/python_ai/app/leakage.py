from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass
class LeakageReport:
    safe:bool
    blockers:list[str]
    warnings:list[str]


FORBIDDEN_FEATURE_PREFIXES=("target_","future_","next_","realised_","realized_")


def audit_temporal_dataset(
    frame:pd.DataFrame,
    feature_columns:list[str],
    target_column:str,
)->LeakageReport:
    blockers=[]; warnings=[]
    if not isinstance(frame.index,pd.DatetimeIndex):
        blockers.append("index is not DatetimeIndex")
    elif not frame.index.is_monotonic_increasing:
        blockers.append("timestamps are not monotonically increasing")
    if frame.index.duplicated().any():
        blockers.append("duplicate timestamps")
    if target_column in feature_columns:
        blockers.append("target column included in features")
    for c in feature_columns:
        if c.lower().startswith(FORBIDDEN_FEATURE_PREFIXES):
            blockers.append(f"feature {c} has a future/target-like name")
    if frame[feature_columns].isna().any(axis=None):
        blockers.append("features contain missing values")
    if frame[target_column].isna().any():
        blockers.append("target contains missing values")
    if len(frame)<100:
        warnings.append("dataset is small; estimates may be unstable")
    return LeakageReport(not blockers,blockers,warnings)


def assert_split_order(train:pd.DataFrame,validation:pd.DataFrame,test:pd.DataFrame)->None:
    if train.empty or validation.empty or test.empty:
        raise ValueError("all splits must be non-empty")
    if train.index.max()>=validation.index.min():
        raise ValueError("train and validation periods overlap or are out of order")
    if validation.index.max()>=test.index.min():
        raise ValueError("validation and test periods overlap or are out of order")
