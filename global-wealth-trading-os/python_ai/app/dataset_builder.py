from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import pandas as pd

from .technical_features import build_technical_features


@dataclass
class DatasetLineage:
    instrument_id:str
    region:str
    source_ids:list[str]
    feature_version:str
    label_version:str
    rows:int
    first_timestamp:str
    last_timestamp:str
    dataset_hash:str


@dataclass
class BuiltDataset:
    frame:pd.DataFrame
    feature_columns:list[str]
    target_column:str
    lineage:DatasetLineage


def _hash_frame(frame:pd.DataFrame)->str:
    payload=frame.to_csv(index=True).encode()
    return sha256(payload).hexdigest()


def add_forward_return_labels(frame:pd.DataFrame,horizons:tuple[int,...]=(1,5,20))->pd.DataFrame:
    x=frame.copy()
    for h in horizons:
        x[f"target_return_{h}d"]=x["close"].shift(-h)/x["close"]-1
        x[f"target_up_{h}d"]=(x[f"target_return_{h}d"]>0).astype(float)
    return x


def add_hurdle_label(frame:pd.DataFrame,horizon:int=1,hurdle_pct:float=5.0)->pd.DataFrame:
    x=frame.copy()
    future_high=x["high"].shift(-1).rolling(horizon).max().shift(-(horizon-1)) if horizon>1 else x["high"].shift(-1)
    x[f"target_hit_{hurdle_pct:g}pct_{horizon}d"]=(
        future_high/x["close"]-1 >= hurdle_pct/100
    ).astype(float)
    return x


def build_supervised_dataset(
    raw:pd.DataFrame,
    *,
    instrument_id:str,
    region:str,
    source_ids:list[str],
    target_horizon:int=1,
    feature_version:str="technical-v1",
    label_version:str="forward-return-v1",
)->BuiltDataset:
    if not isinstance(raw.index,pd.DatetimeIndex):
        raise ValueError("raw data index must be a DatetimeIndex")
    if not raw.index.is_monotonic_increasing:
        raw=raw.sort_index()
    if raw.index.duplicated().any():
        raise ValueError("duplicate timestamps are not allowed")
    required={"open","high","low","close","volume"}
    missing=required-set(raw.columns)
    if missing:
        raise ValueError(f"missing OHLCV columns: {sorted(missing)}")

    x=build_technical_features(raw)
    x=add_forward_return_labels(x,(1,5,20))
    target=f"target_return_{target_horizon}d"

    excluded=set(required)|{c for c in x.columns if c.startswith("target_")}
    feature_cols=[c for c in x.columns if c not in excluded and pd.api.types.is_numeric_dtype(x[c])]
    clean=x[feature_cols+[target]].dropna().copy()
    if len(clean)<100:
        raise ValueError("at least 100 clean labelled observations are required")

    lineage=DatasetLineage(
        instrument_id=instrument_id,
        region=region,
        source_ids=sorted(set(source_ids)),
        feature_version=feature_version,
        label_version=label_version,
        rows=len(clean),
        first_timestamp=clean.index.min().isoformat(),
        last_timestamp=clean.index.max().isoformat(),
        dataset_hash=_hash_frame(clean),
    )
    return BuiltDataset(clean,feature_cols,target,lineage)
