from __future__ import annotations
from dataclasses import dataclass
from statistics import mean
import pandas as pd
from .forecasting import ReturnEnsemble


@dataclass
class WalkForwardResult:
    predictions:list[float]
    actuals:list[float]
    mae:float
    directional_accuracy_pct:float
    folds:int


def validate(
    X:pd.DataFrame,
    y:pd.Series,
    *,
    min_train:int=120,
    test_size:int=20,
    step:int=20
)->WalkForwardResult:
    preds=[]; actuals=[]; folds=0
    end=min_train
    while end+test_size<=len(X):
        train_X=X.iloc[:end]
        train_y=y.iloc[:end]
        test_X=X.iloc[end:end+test_size]
        test_y=y.iloc[end:end+test_size]
        model=ReturnEnsemble()
        try:
            model.fit(train_X,train_y)
        except ValueError:
            end+=step
            continue
        for i in range(len(test_X)):
            row=test_X.iloc[[i]]
            if row.isna().any(axis=None) or pd.isna(test_y.iloc[i]):
                continue
            f=model.predict_one(row)
            preds.append(f.prediction)
            actuals.append(float(test_y.iloc[i]))
        folds+=1
        end+=step
    if not preds:
        return WalkForwardResult([],[],0,0,folds)
    errors=[abs(a-p) for a,p in zip(actuals,preds)]
    dirs=[1 if (a>=0)==(p>=0) else 0 for a,p in zip(actuals,preds)]
    return WalkForwardResult(preds,actuals,mean(errors),mean(dirs)*100,folds)
