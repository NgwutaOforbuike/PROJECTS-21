from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import json

from .dataset_builder import DatasetLineage


class DatasetRegistry:
    def __init__(self,path:str="data/datasets.json")->None:
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)

    def _load(self)->list[dict]:
        if not self.path.exists(): return []
        return json.loads(self.path.read_text())

    def register(self,lineage:DatasetLineage)->None:
        rows=[r for r in self._load() if r.get("dataset_hash")!=lineage.dataset_hash]
        rows.append(asdict(lineage))
        self.path.write_text(json.dumps(rows,indent=2))

    def all(self)->list[DatasetLineage]:
        return [DatasetLineage(**r) for r in self._load()]
