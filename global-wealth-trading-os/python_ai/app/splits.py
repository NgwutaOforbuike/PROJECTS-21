from __future__ import annotations

from dataclasses import dataclass
import pandas as pd
from .leakage import assert_split_order


@dataclass
class TemporalSplits:
    train:pd.DataFrame
    validation:pd.DataFrame
    test:pd.DataFrame


def temporal_split(
    frame:pd.DataFrame,
    train_fraction:float=.65,
    validation_fraction:float=.20,
)->TemporalSplits:
    if not 0<train_fraction<1: raise ValueError("invalid train_fraction")
    if not 0<validation_fraction<1: raise ValueError("invalid validation_fraction")
    if train_fraction+validation_fraction>=1: raise ValueError("test set would be empty")
    x=frame.sort_index()
    n=len(x)
    i=max(1,int(n*train_fraction))
    j=max(i+1,int(n*(train_fraction+validation_fraction)))
    if j>=n: raise ValueError("insufficient rows for temporal split")
    s=TemporalSplits(x.iloc[:i].copy(),x.iloc[i:j].copy(),x.iloc[j:].copy())
    assert_split_order(s.train,s.validation,s.test)
    return s
