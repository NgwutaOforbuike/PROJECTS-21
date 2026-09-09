import numpy as np
import pandas as pd

from app.feature_join import asof_join_features
from app.hurdle_trainer import train_hurdle_classifier


def volatile_market(n=520):
    rng=np.random.default_rng(12)
    idx=pd.date_range("2023-01-01",periods=n,freq="D",tz="UTC")
    jumps=(rng.random(n)<.10)*rng.uniform(.05,.10,n)
    ret=rng.normal(.0005,.018,n)+jumps-rng.binomial(1,.08,n)*rng.uniform(.03,.07,n)
    close=100*np.cumprod(1+ret)
    open_=close*(1+rng.normal(0,.002,n))
    high=np.maximum(open_,close)*(1+rng.uniform(.002,.07,n))
    low=np.minimum(open_,close)*(1-rng.uniform(.002,.04,n))
    volume=100000+rng.normal(0,12000,n)+jumps*1_000_000
    return pd.DataFrame({"open":open_,"high":high,"low":low,"close":close,"volume":np.maximum(volume,10)},index=idx)


def test_backward_asof_prevents_future_join():
    mi=pd.date_range("2026-01-01",periods=3,freq="D",tz="UTC")
    ei=pd.to_datetime(["2025-12-31","2026-01-02 12:00"],utc=True)
    market=pd.DataFrame({"close":[1,2,3]},index=mi)
    exo=pd.DataFrame({"macro":[10,99]},index=ei)
    x=asof_join_features(market,exo,suffix="m")
    assert x.iloc[1]["macro_m"]==10
    assert x.iloc[2]["macro_m"]==99


def test_hurdle_classifier_trains():
    r=train_hurdle_classifier(volatile_market(),hurdle_pct=5,horizon=1)
    assert r.winner_name
    assert 0<=r.test.roc_auc<=1
    assert r.test.observations>0
