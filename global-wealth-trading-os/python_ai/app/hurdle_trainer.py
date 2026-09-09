from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier,RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,brier_score_loss,precision_score,recall_score,
    roc_auc_score,average_precision_score
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .dataset_builder import add_hurdle_label
from .technical_features import build_technical_features
from .splits import temporal_split
from .leakage import audit_temporal_dataset


@dataclass
class ClassificationMetrics:
    accuracy:float
    precision:float
    recall:float
    roc_auc:float
    average_precision:float
    brier:float
    positives:int
    observations:int


@dataclass
class HurdleTrainingResult:
    winner_name:str
    validation:ClassificationMetrics
    test:ClassificationMetrics
    model:object
    feature_columns:list[str]
    target_column:str


def metrics(y_true:pd.Series,prob:np.ndarray,threshold:float=.5)->ClassificationMetrics:
    y=np.asarray(y_true,dtype=int)
    p=np.asarray(prob,dtype=float)
    pred=(p>=threshold).astype(int)
    auc=float(roc_auc_score(y,p)) if len(np.unique(y))>1 else .5
    ap=float(average_precision_score(y,p)) if y.sum()>0 else 0
    return ClassificationMetrics(
        accuracy=float(accuracy_score(y,pred)),
        precision=float(precision_score(y,pred,zero_division=0)),
        recall=float(recall_score(y,pred,zero_division=0)),
        roc_auc=auc,
        average_precision=ap,
        brier=float(brier_score_loss(y,p)),
        positives=int(y.sum()),
        observations=len(y),
    )


def train_hurdle_classifier(
    raw:pd.DataFrame,
    *,
    hurdle_pct:float=5.0,
    horizon:int=1,
    random_state:int=42,
)->HurdleTrainingResult:
    x=build_technical_features(raw)
    x=add_hurdle_label(x,horizon=horizon,hurdle_pct=hurdle_pct)
    target=f"target_hit_{hurdle_pct:g}pct_{horizon}d"
    excluded={"open","high","low","close","volume"}|{c for c in x if c.startswith("target_")}
    features=[c for c in x.columns if c not in excluded and pd.api.types.is_numeric_dtype(x[c])]
    frame=x[features+[target]].dropna().copy()
    if len(frame)<150: raise ValueError("at least 150 clean observations required")
    if frame[target].nunique()<2: raise ValueError("hurdle label has only one class; cannot train classifier")
    audit=audit_temporal_dataset(frame,features,target)
    if not audit.safe: raise ValueError("unsafe hurdle dataset: "+"; ".join(audit.blockers))

    s=temporal_split(frame)
    models={
        "logistic":make_pipeline(StandardScaler(),LogisticRegression(C=.5,max_iter=1500,class_weight="balanced")),
        "random_forest":RandomForestClassifier(
            n_estimators=300,max_depth=7,min_samples_leaf=5,class_weight="balanced_subsample",
            random_state=random_state,n_jobs=-1
        ),
        "hist_gb":HistGradientBoostingClassifier(
            learning_rate=.04,max_iter=250,max_depth=5,l2_regularization=1.0,
            random_state=random_state
        ),
    }
    vals={}
    for name,m in models.items():
        m.fit(s.train[features],s.train[target].astype(int))
        vals[name]=metrics(s.validation[target],m.predict_proba(s.validation[features])[:,1])
    winner=max(vals,key=lambda n:(vals[n].average_precision,vals[n].roc_auc,-vals[n].brier))
    model=models[winner]
    trainval=pd.concat([s.train,s.validation])
    model.fit(trainval[features],trainval[target].astype(int))
    tm=metrics(s.test[target],model.predict_proba(s.test[features])[:,1])
    return HurdleTrainingResult(winner,vals[winner],tm,model,features,target)
