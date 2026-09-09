from __future__ import annotations
import pandas as pd


def asof_join_features(
    market:pd.DataFrame,
    exogenous:pd.DataFrame,
    *,
    suffix:str,
    tolerance:pd.Timedelta|None=None,
)->pd.DataFrame:
    """
    Leakage-safe backward as-of join. An exogenous observation can influence a
    market row only if its timestamp is <= the market timestamp.
    """
    if not isinstance(market.index,pd.DatetimeIndex) or not isinstance(exogenous.index,pd.DatetimeIndex):
        raise ValueError("both frames require DatetimeIndex")
    left=market.sort_index().copy()
    right=exogenous.sort_index().copy()
    right=right.rename(columns={c:f"{c}_{suffix}" for c in right.columns})
    joined=pd.merge_asof(
        left.reset_index().rename(columns={left.index.name or "index":"timestamp"}),
        right.reset_index().rename(columns={right.index.name or "index":"timestamp"}),
        on="timestamp",
        direction="backward",
        tolerance=tolerance,
    )
    return joined.set_index("timestamp")


def lag_features(frame:pd.DataFrame,columns:list[str],periods:int=1)->pd.DataFrame:
    if periods<1: raise ValueError("periods must be >=1")
    x=frame.copy()
    for c in columns:
        if c not in x: raise KeyError(c)
        x[f"{c}_lag{periods}"]=x[c].shift(periods)
    return x
