import numpy as np
import pandas as pd

from app.dataset_registry import DatasetRegistry
from app.inference import ChampionInference
from app.learning_cycle import LearningCycle
from app.model_artifacts import ModelArtifactStore
from app.model_registry import ModelRegistry
from app.training_service import TrainingService


def market(n=430):
    rng=np.random.default_rng(44)
    idx=pd.date_range("2024-01-01",periods=n,freq="D",tz="UTC")
    cyc=np.sin(np.arange(n)/9)*.004
    ret=.0007+cyc+rng.normal(0,.006,n)
    close=80*np.cumprod(1+ret)
    open_=close*(1+rng.normal(0,.001,n))
    high=np.maximum(open_,close)*(1+rng.uniform(.001,.009,n))
    low=np.minimum(open_,close)*(1-rng.uniform(.001,.009,n))
    volume=80000+np.abs(cyc)*1_000_000+rng.normal(0,5000,n)
    return pd.DataFrame({"open":open_,"high":high,"low":low,"close":close,"volume":np.maximum(volume,100)},index=idx)


def test_learning_cycle_trains_and_forecasts(tmp_path):
    artifacts=ModelArtifactStore(str(tmp_path/"models"))
    registry=ModelRegistry(str(tmp_path/"registry"))
    training=TrainingService(artifacts,DatasetRegistry(str(tmp_path/"datasets.json")),registry)
    inference=ChampionInference(artifacts,registry)
    cycle=LearningCycle(training,inference,registry)
    result=cycle.run(market(),instrument_id="TEST",region="US",source_ids=["ci"],strategy_name="learn",version="v1")
    assert result.retrained
    champion=registry.champion("learn")
    if champion is not None:
        assert result.forecast is not None
        assert np.isfinite(result.forecast.prediction_return_pct)
