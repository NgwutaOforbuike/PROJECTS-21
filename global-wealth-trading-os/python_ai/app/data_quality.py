from __future__ import annotations
from dataclasses import dataclass
import math
import pandas as pd


@dataclass
class DataQualityReport:
    score:float
    missing_pct:float
    duplicate_rows:int
    stale:bool
    impossible_prices:int
    extreme_returns:int
    blockers:list[str]


def assess_market_frame(frame:pd.DataFrame,max_staleness_seconds:int|None=None)->DataQualityReport:
    if frame.empty:
        return DataQualityReport(0,100,0,True,0,0,["empty dataset"])
    blockers=[]
    missing=float(frame.isna().sum().sum()/max(1,frame.size)*100)
    duplicate=int(frame.index.duplicated().sum())
    impossible=0
    if "close" in frame:
        impossible=int((frame["close"]<=0).sum())
    extreme=0
    if "close" in frame:
        r=frame["close"].pct_change()
        extreme=int((r.abs()>0.50).sum())
    stale=False
    if max_staleness_seconds is not None and isinstance(frame.index,pd.DatetimeIndex):
        now=pd.Timestamp.now(tz="UTC")
        last=frame.index.max()
        if last.tz is None: last=last.tz_localize("UTC")
        stale=(now-last).total_seconds()>max_staleness_seconds
    if missing>5: blockers.append("missing data exceeds 5%")
    if duplicate: blockers.append("duplicate timestamps present")
    if impossible: blockers.append("non-positive prices present")
    if stale: blockers.append("dataset is stale")
    penalty=min(100,missing*4+duplicate*2+impossible*10+extreme*1+(30 if stale else 0))
    return DataQualityReport(max(0,100-penalty),missing,duplicate,stale,impossible,extreme,blockers)
