from __future__ import annotations
from dataclasses import asdict,dataclass
import pandas as pd

from .dataset_builder import build_supervised_dataset
from .dataset_registry import DatasetRegistry
from .model_artifacts import ModelArtifactStore
from .model_registry import ModelRegistry
from .trainer import train_dataset


@dataclass
class TrainingServiceResult:
    model_id:str
    winner_name:str
    dataset_hash:str
    validation:dict
    test:dict
    promoted_to_champion:bool
    promotion_reasons:list[str]


class TrainingService:
    def __init__(
        self,
        artifacts:ModelArtifactStore|None=None,
        datasets:DatasetRegistry|None=None,
        models:ModelRegistry|None=None,
    )->None:
        self.artifacts=artifacts or ModelArtifactStore()
        self.datasets=datasets or DatasetRegistry()
        self.models=models or ModelRegistry()

    def train_from_frame(
        self,
        frame:pd.DataFrame,
        *,
        instrument_id:str,
        region:str,
        source_ids:list[str],
        target_horizon:int=1,
        strategy_name:str="daily-return",
        version:str="v1",
    )->TrainingServiceResult:
        ds=build_supervised_dataset(
            frame,
            instrument_id=instrument_id,
            region=region,
            source_ids=source_ids,
            target_horizon=target_horizon,
        )
        self.datasets.register(ds.lineage)
        result=train_dataset(ds,strategy_name=strategy_name,version=version,store=self.artifacts)
        event=self.models.evaluate_challenger(result.metadata)
        return TrainingServiceResult(
            model_id=result.model_id,
            winner_name=result.winner_name,
            dataset_hash=ds.lineage.dataset_hash,
            validation=result.validation.__dict__,
            test=result.test.__dict__,
            promoted_to_champion=event.promoted,
            promotion_reasons=event.reasons,
        )
