from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json


@dataclass
class FeatureVector:
    instrument_id: str
    timestamp: str
    features: dict[str, float]
    version: str = "v1"


class FeatureStore:
    def __init__(self, path: str = "data/features.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def put(self, instrument_id: str, features: dict[str, float], version: str = "v1") -> FeatureVector:
        row = FeatureVector(
            instrument_id=instrument_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            features=features,
            version=version,
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(row)) + "\n")
        return row

    def latest(self, instrument_id: str, version: str | None = None) -> FeatureVector | None:
        if not self.path.exists():
            return None
        rows=[]
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            d=json.loads(line)
            if d["instrument_id"] != instrument_id: continue
            if version and d["version"] != version: continue
            rows.append(FeatureVector(**d))
        return rows[-1] if rows else None
