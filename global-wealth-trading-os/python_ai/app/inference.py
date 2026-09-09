from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

from .technical_features import build_technical_features
from .model_artifacts import ModelArtifactStore
from .model_registry import ModelRegistry


@dataclass
class ModelForecast:
    strategy_name:str
    model_id:str
    prediction_return_pct:float
    artifact_sha256:str
    feature_timestamp:str


class ChampionInference:
    def __init__(
        self,
        artifacts:ModelArtifactStore|None=None,
        registry:ModelRegistry|None=None,
    )->None:
        self.artifacts=artifacts or ModelArtifactStore()
        self.registry=registry or ModelRegistry()

    def forecast(self,strategy_name:str,history:pd.DataFrame)->ModelForecast:
        champion=self.registry.champion(strategy_name)
        if champion is None:
            raise RuntimeError(f"no champion registered for strategy {strategy_name}")
        model,metadata=self.artifacts.load(champion.model_id)
        features=build_technical_features(history)
        missing=[c for c in metadata.feature_columns if c not in features]
        if missing: raise RuntimeError(f"missing inference features: {missing}")
        row=features[metadata.feature_columns].dropna().iloc[[-1]]
        pred=float(model.predict(row)[0])
        return ModelForecast(
            strategy_name=strategy_name,
            model_id=champion.model_id,
            prediction_return_pct=pred*100,
            artifact_sha256=metadata.artifact_sha256 or "",
            feature_timestamp=row.index[-1].isoformat(),
        )
