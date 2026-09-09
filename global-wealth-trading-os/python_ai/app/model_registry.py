from __future__ import annotations
from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json

from .champion_challenger import compare
from .model_artifacts import ModelMetadata


@dataclass
class RegistryEvent:
    timestamp:str
    strategy_name:str
    challenger_id:str
    previous_champion_id:str|None
    promoted:bool
    reasons:list[str]


class ModelRegistry:
    def __init__(self,root:str="data/model_registry")->None:
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self.events_path=self.root/"events.jsonl"

    def _champion_path(self,strategy_name:str)->Path:
        safe=strategy_name.replace("/","_")
        return self.root/f"{safe}.champion.json"

    def champion(self,strategy_name:str)->ModelMetadata|None:
        p=self._champion_path(strategy_name)
        return ModelMetadata(**json.loads(p.read_text())) if p.exists() else None

    def evaluate_challenger(self,challenger:ModelMetadata)->RegistryEvent:
        old=self.champion(challenger.strategy_name)
        decision=compare(old,challenger)
        event=RegistryEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            strategy_name=challenger.strategy_name,
            challenger_id=challenger.model_id,
            previous_champion_id=old.model_id if old else None,
            promoted=decision.promote,
            reasons=decision.reasons,
        )
        if decision.promote:
            promoted=ModelMetadata(**{**asdict(challenger),"status":"CHAMPION"})
            self._champion_path(challenger.strategy_name).write_text(json.dumps(asdict(promoted),indent=2))
        with self.events_path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(asdict(event))+"\n")
        return event
