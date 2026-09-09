from __future__ import annotations

from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
import joblib


@dataclass
class ModelMetadata:
    model_id:str
    strategy_name:str
    version:str
    trained_at:str
    dataset_hash:str
    feature_columns:list[str]
    target_column:str
    metrics:dict
    parameters:dict
    artifact_sha256:str|None=None
    status:str="CHALLENGER"


class ModelArtifactStore:
    def __init__(self,root:str="data/models")->None:
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)

    def save(self,model,metadata:ModelMetadata)->ModelMetadata:
        model_dir=self.root/metadata.model_id
        model_dir.mkdir(parents=True,exist_ok=True)
        artifact=model_dir/"model.joblib"
        joblib.dump(model,artifact)
        metadata.artifact_sha256=sha256(artifact.read_bytes()).hexdigest()
        (model_dir/"metadata.json").write_text(json.dumps(asdict(metadata),indent=2,default=str))
        return metadata

    def load(self,model_id:str):
        model_dir=self.root/model_id
        metadata=json.loads((model_dir/"metadata.json").read_text())
        artifact=model_dir/"model.joblib"
        digest=sha256(artifact.read_bytes()).hexdigest()
        if digest!=metadata.get("artifact_sha256"):
            raise RuntimeError("model artifact hash mismatch")
        return joblib.load(artifact),ModelMetadata(**metadata)

    def list_metadata(self)->list[ModelMetadata]:
        rows=[]
        for p in self.root.glob("*/metadata.json"):
            try: rows.append(ModelMetadata(**json.loads(p.read_text())))
            except Exception: continue
        return sorted(rows,key=lambda x:x.trained_at,reverse=True)
