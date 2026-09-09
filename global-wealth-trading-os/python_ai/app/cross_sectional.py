from __future__ import annotations
import pandas as pd


def percentile_ranks(frame:pd.DataFrame,columns:list[str],ascending:bool=True)->pd.DataFrame:
    x=frame.copy()
    for c in columns:
        if c not in x: raise KeyError(c)
        x[f"{c}_pct_rank"]=x[c].rank(pct=True,ascending=ascending)
    return x


def composite_rank(frame:pd.DataFrame,weights:dict[str,float])->pd.Series:
    if not weights: raise ValueError("weights required")
    missing=[c for c in weights if c not in frame]
    if missing: raise KeyError(missing)
    total=sum(abs(v) for v in weights.values())
    if total==0: raise ValueError("weights cannot sum to zero magnitude")
    score=sum(frame[c]*w for c,w in weights.items())/total
    return score.rank(pct=True)
