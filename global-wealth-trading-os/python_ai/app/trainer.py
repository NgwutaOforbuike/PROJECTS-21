from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime,timezone
import json
import uuid
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor,RandomForestRegressor,ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .dataset_builder import BuiltDataset
from .leakage import audit_temporal_dataset
from .splits import temporal_split
from .model_artifacts import ModelArtifactStore,ModelMetadata


@dataclass
class RegressionMetrics:
    mae:float
    rmse:float
    r2:float
    directional_accuracy_pct:float
    correlation:float
    observations:int


@dataclass
class TrainingResult:
    model_id:str
    winner_name:str
    validation:RegressionMetrics
    test:RegressionMetrics
    metadata:ModelMetadata
    leaderboard:dict[str,dict]


def regression_metrics(y_true:pd.Series,pred:np.ndarray)->RegressionMetrics:
    y=np.asarray(y_true,dtype=float)
    p=np.asarray(pred,dtype=float)
    directional=float(((y>=0)==(p>=0)).mean()*100)
    corr=float(np.corrcoef(y,p)[0,1]) if len(y)>1 and np.std(y)>0 and np.std(p)>0 else 0.0
    return RegressionMetrics(
        mae=float(mean_absolute_error(y,p)),
        rmse=float(mean_squared_error(y,p)**.5),
        r2=float(r2_score(y,p)),
        directional_accuracy_pct=directional,
        correlation=corr,
        observations=len(y),
    )


def default_candidates(random_state:int=42):
    return {
        "ridge":make_pipeline(StandardScaler(),Ridge(alpha=3.0)),
        "random_forest":RandomForestRegressor(
            n_estimators=300,max_depth=7,min_samples_leaf=5,
            max_features=.8,random_state=random_state,n_jobs=-1
        ),
        "extra_trees":ExtraTreesRegressor(
            n_estimators=300,max_depth=8,min_samples_leaf=4,
            max_features=.9,random_state=random_state,n_jobs=-1
        ),
        "hist_gb":HistGradientBoostingRegressor(
            learning_rate=.04,max_iter=250,max_depth=5,l2_regularization=1.0,
            random_state=random_state
        ),
    }


def _selection_score(m:RegressionMetrics)->float:
    return m.directional_accuracy_pct*.6 + max(-20,min(20,m.correlation*20)) - m.mae*1000*.02


def train_dataset(
    dataset:BuiltDataset,
    *,
    strategy_name:str="daily-return-ensemble",
    version:str="v1",
    store:ModelArtifactStore|None=None,
)->TrainingResult:
    audit=audit_temporal_dataset(dataset.frame,dataset.feature_columns,dataset.target_column)
    if not audit.safe:
        raise ValueError("unsafe training dataset: "+"; ".join(audit.blockers))

    splits=temporal_split(dataset.frame)
    Xtr=splits.train[dataset.feature_columns]; ytr=splits.train[dataset.target_column]
    Xv=splits.validation[dataset.feature_columns]; yv=splits.validation[dataset.target_column]
    Xt=splits.test[dataset.feature_columns]; yt=splits.test[dataset.target_column]

    leaderboard={}
    fitted={}
    for name,model in default_candidates().items():
        model.fit(Xtr,ytr)
        vm=regression_metrics(yv,model.predict(Xv))
        leaderboard[name]={"validation":vm.__dict__}
        fitted[name]=model

    winner=max(fitted,key=lambda n:_selection_score(RegressionMetrics(**leaderboard[n]["validation"])))
    final_model=default_candidates()[winner]
    trainval=pd.concat([splits.train,splits.validation])
    final_model.fit(trainval[dataset.feature_columns],trainval[dataset.target_column])
    test_metrics=regression_metrics(yt,final_model.predict(Xt))
    validation_metrics=RegressionMetrics(**leaderboard[winner]["validation"])

    model_id=f"{strategy_name}-{version}-{uuid.uuid4().hex[:10]}"
    metadata=ModelMetadata(
        model_id=model_id,
        strategy_name=strategy_name,
        version=version,
        trained_at=datetime.now(timezone.utc).isoformat(),
        dataset_hash=dataset.lineage.dataset_hash,
        feature_columns=dataset.feature_columns,
        target_column=dataset.target_column,
        metrics={"validation":validation_metrics.__dict__,"test":test_metrics.__dict__},
        parameters={"winner":winner},
    )
    store=store or ModelArtifactStore()
    metadata=store.save(final_model,metadata)
    return TrainingResult(model_id,winner,validation_metrics,test_metrics,metadata,leaderboard)
