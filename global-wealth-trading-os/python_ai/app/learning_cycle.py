from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime,timezone
import pandas as pd

from .drift import detect_drift
from .inference import ChampionInference,ModelForecast
from .model_registry import ModelRegistry
from .training_service import TrainingService
from .retraining import should_retrain


@dataclass
class LearningCycleReport:
    strategy_name:str
    retrained:bool
    retraining_reasons:list[str]
    trained_model_id:str|None
    promoted_to_champion:bool|None
    forecast:ModelForecast|None
    ran_at:str


class LearningCycle:
    def __init__(
        self,
        training:TrainingService|None=None,
        inference:ChampionInference|None=None,
        registry:ModelRegistry|None=None,
    )->None:
        self.training=training or TrainingService()
        self.inference=inference or ChampionInference()
        self.registry=registry or ModelRegistry()

    def run(
        self,
        history:pd.DataFrame,
        *,
        instrument_id:str,
        region:str,
        source_ids:list[str],
        strategy_name:str="daily-return",
        version:str="v1",
        new_clean_observations:int|None=None,
    )->LearningCycleReport:
        champion=self.registry.champion(strategy_name)
        retrain=True
        reasons=["no champion model exists"]
        if champion:
            returns=history["close"].pct_change().dropna()
            split=max(20,int(len(returns)*.75))
            reference=returns.iloc[:split].tolist()
            recent=returns.iloc[split:].tolist()
            drift=detect_drift(reference,recent) if len(reference)>=20 and len(recent)>=10 else None
            decision=should_retrain(
                last_trained_at=champion.trained_at,
                new_clean_observations=new_clean_observations or len(recent),
                drift=drift,
            )
            retrain=decision.retrain
            reasons=decision.reasons

        trained_id=None
        promoted=None
        if retrain:
            result=self.training.train_from_frame(
                history,
                instrument_id=instrument_id,
                region=region,
                source_ids=source_ids,
                strategy_name=strategy_name,
                version=version,
            )
            trained_id=result.model_id
            promoted=result.promoted_to_champion

        forecast=None
        if self.registry.champion(strategy_name):
            forecast=self.inference.forecast(strategy_name,history)

        return LearningCycleReport(
            strategy_name=strategy_name,
            retrained=retrain,
            retraining_reasons=reasons,
            trained_model_id=trained_id,
            promoted_to_champion=promoted,
            forecast=forecast,
            ran_at=datetime.now(timezone.utc).isoformat(),
        )
