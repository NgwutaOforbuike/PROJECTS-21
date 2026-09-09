import numpy as np
import pandas as pd

from app.dataset_registry import DatasetRegistry
from app.model_artifacts import ModelArtifactStore
from app.model_registry import ModelRegistry
from app.training_service import TrainingService


def sample(n=420):
    rng=np.random.default_rng(9)
    idx=pd.date_range("2024-01-01",periods=n,freq="D",tz="UTC")
    signal=np.sin(np.arange(n)/13)*.006
    ret=.0005+signal+rng.normal(0,.007,n)
    close=50*np.cumprod(1+ret)
    open_=close*(1+rng.normal(0,.001,n))
    high=np.maximum(open_,close)*(1+rng.uniform(.001,.008,n))
    low=np.minimum(open_,close)*(1-rng.uniform(.001,.008,n))
    volume=50000+rng.normal(0,5000,n)+np.abs(signal)*1_000_000
    return pd.DataFrame({"open":open_,"high":high,"low":low,"close":close,"volume":np.maximum(volume,10)},index=idx)


def test_training_service_registers_model_and_dataset(tmp_path):
    svc=TrainingService(
        ModelArtifactStore(str(tmp_path/"models")),
        DatasetRegistry(str(tmp_path/"datasets.json")),
        ModelRegistry(str(tmp_path/"registry")),
    )
    result=svc.train_from_frame(sample(),instrument_id="TEST",region="US",source_ids=["ci"],strategy_name="ci-strategy")
    assert result.model_id
    assert result.dataset_hash
    assert len(svc.datasets.all())==1
