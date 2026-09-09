import numpy as np
import pandas as pd

from app.dataset_builder import build_supervised_dataset
from app.leakage import audit_temporal_dataset
from app.trainer import train_dataset
from app.model_artifacts import ModelArtifactStore
from app.champion_challenger import compare


def synthetic_market(n=420):
    rng=np.random.default_rng(7)
    idx=pd.date_range("2024-01-01",periods=n,freq="D",tz="UTC")
    seasonal=np.sin(np.arange(n)/11)*.004
    ret=.0008+seasonal+rng.normal(0,.009,n)
    close=100*np.cumprod(1+ret)
    open_=close*(1+rng.normal(0,.001,n))
    high=np.maximum(open_,close)*(1+rng.uniform(.001,.012,n))
    low=np.minimum(open_,close)*(1-rng.uniform(.001,.012,n))
    volume=100000*(1+np.abs(seasonal)*20)+rng.normal(0,8000,n)
    return pd.DataFrame({"open":open_,"high":high,"low":low,"close":close,"volume":np.maximum(volume,100)},index=idx)


def test_training_save_reload(tmp_path):
    ds=build_supervised_dataset(
        synthetic_market(),instrument_id="TEST",region="US",source_ids=["synthetic-ci"],target_horizon=1
    )
    audit=audit_temporal_dataset(ds.frame,ds.feature_columns,ds.target_column)
    assert audit.safe
    store=ModelArtifactStore(str(tmp_path/"models"))
    result=train_dataset(ds,strategy_name="smoke",version="v1",store=store)
    model,meta=store.load(result.model_id)
    assert meta.artifact_sha256
    row=ds.frame[ds.feature_columns].iloc[[-1]]
    pred=float(model.predict(row)[0])
    assert np.isfinite(pred)


def test_champion_challenger_gate(tmp_path):
    ds=build_supervised_dataset(
        synthetic_market(),instrument_id="TEST",region="US",source_ids=["synthetic-ci"],target_horizon=1
    )
    store=ModelArtifactStore(str(tmp_path/"models"))
    challenger=train_dataset(ds,strategy_name="smoke",version="v1",store=store).metadata
    decision=compare(None,challenger,minimum_directional_accuracy=0)
    assert decision.promote
