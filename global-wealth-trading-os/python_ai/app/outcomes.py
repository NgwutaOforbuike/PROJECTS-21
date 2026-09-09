from __future__ import annotations
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from pathlib import Path
import json


@dataclass
class PredictionOutcome:
    id:str
    instrument_id:str
    strategy_version:str
    predicted_return_pct:float
    confidence:float
    entry_price:float
    exit_price:float
    realised_return_pct:float
    thesis_correct:bool
    opened_at:str
    closed_at:str
    regime:str|None=None


class OutcomeStore:
    def __init__(self,path:str="data/outcomes.jsonl")->None:
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)

    def record(self,row:PredictionOutcome)->None:
        with self.path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(asdict(row))+"\n")

    def all(self)->list[PredictionOutcome]:
        if not self.path.exists(): return []
        return [PredictionOutcome(**json.loads(x)) for x in self.path.read_text().splitlines() if x.strip()]

    def by_strategy(self,strategy_version:str)->list[PredictionOutcome]:
        return [x for x in self.all() if x.strategy_version==strategy_version]
