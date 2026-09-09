from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass
class StrategyVersion:
    name: str
    version: str
    status: str
    min_sharpe: float
    max_drawdown_pct: float
    notes: str = ""


class StrategyRegistry:
    VALID={"DRAFT","BACKTESTED","PAPER","APPROVED","RETIRED"}

    def __init__(self,path:str="data/strategies.json") -> None:
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)

    def _load(self)->list[dict]:
        return json.loads(self.path.read_text()) if self.path.exists() else []

    def save(self,s:StrategyVersion)->None:
        if s.status not in self.VALID: raise ValueError("invalid status")
        rows=[r for r in self._load() if not (r["name"]==s.name and r["version"]==s.version)]
        rows.append(asdict(s))
        self.path.write_text(json.dumps(rows,indent=2))

    def promote(self,name:str,version:str,new_status:str)->StrategyVersion:
        if new_status not in self.VALID: raise ValueError("invalid status")
        rows=self._load()
        for r in rows:
            if r["name"]==name and r["version"]==version:
                r["status"]=new_status
                self.path.write_text(json.dumps(rows,indent=2))
                return StrategyVersion(**r)
        raise KeyError("strategy not found")
