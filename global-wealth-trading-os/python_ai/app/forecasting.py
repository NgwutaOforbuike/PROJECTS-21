from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


@dataclass
class EnsembleForecast:
    prediction: float
    dispersion: float
    confidence: float
    members: dict[str,float]


class ReturnEnsemble:
    def __init__(self,random_state:int=42)->None:
        self.models={
            "ridge":make_pipeline(StandardScaler(),Ridge(alpha=2.0)),
            "random_forest":RandomForestRegressor(n_estimators=200,max_depth=6,min_samples_leaf=5,random_state=random_state,n_jobs=-1),
            "hist_gb":HistGradientBoostingRegressor(max_depth=5,learning_rate=.05,max_iter=200,random_state=random_state),
        }
        self.fitted=False

    def fit(self,X:pd.DataFrame,y:pd.Series)->"ReturnEnsemble":
        mask=X.notna().all(axis=1)&y.notna()
        X2=X.loc[mask]
        y2=y.loc[mask]
        if len(X2)<80:
            raise ValueError("at least 80 clean observations are required")
        for m in self.models.values():
            m.fit(X2,y2)
        self.fitted=True
        return self

    def predict_one(self,row:pd.DataFrame)->EnsembleForecast:
        if not self.fitted:
            raise RuntimeError("ensemble is not fitted")
        if len(row)!=1 or row.isna().any(axis=None):
            raise ValueError("row must contain exactly one complete observation")
        members={name:float(model.predict(row)[0]) for name,model in self.models.items()}
        vals=np.array(list(members.values()))
        pred=float(np.median(vals))
        dispersion=float(vals.std())
        confidence=float(max(0,min(100,90-dispersion*1500)))
        return EnsembleForecast(pred,dispersion,confidence,members)
