from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .models import Evidence


@dataclass
class KnowledgeRecord:
    id: str
    topic: str
    instrument_id: str | None
    region: str | None
    evidence: Evidence
    tags: list[str]
    created_at: str


class KnowledgeBase:
    """
    Append-only research memory.

    Production target: PostgreSQL + pgvector/object storage.
    Portable development mode: JSONL so the knowledge-building behaviour can be
    tested without cloud infrastructure.
    """

    def __init__(self, path: str = "data/knowledge.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _fingerprint(topic: str, evidence: Evidence, instrument_id: str | None) -> str:
        raw = json.dumps(
            {
                "topic": topic,
                "instrument": instrument_id,
                "source": evidence.source_id,
                "text": evidence.text.strip(),
                "observed": evidence.observed_at.isoformat(),
            },
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def remember(
        self,
        topic: str,
        evidence: Evidence,
        instrument_id: str | None = None,
        region: str | None = None,
        tags: Iterable[str] = (),
    ) -> KnowledgeRecord:
        record = KnowledgeRecord(
            id=self._fingerprint(topic, evidence, instrument_id),
            topic=topic,
            instrument_id=instrument_id,
            region=region,
            evidence=evidence,
            tags=sorted(set(tags)),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        existing = {r.id for r in self.all()}
        if record.id not in existing:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(self._to_dict(record), ensure_ascii=False) + "\n")
        return record

    def all(self) -> list[KnowledgeRecord]:
        if not self.path.exists():
            return []
        rows: list[KnowledgeRecord] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            d["evidence"] = Evidence.model_validate(d["evidence"])
            rows.append(KnowledgeRecord(**d))
        return rows

    def query(
        self,
        *,
        instrument_id: str | None = None,
        topic: str | None = None,
        limit: int = 50,
    ) -> list[KnowledgeRecord]:
        rows = self.all()
        if instrument_id:
            rows = [r for r in rows if r.instrument_id == instrument_id]
        if topic:
            t = topic.lower()
            rows = [r for r in rows if t in r.topic.lower() or t in r.evidence.text.lower()]
        rows.sort(key=lambda r: r.created_at, reverse=True)
        return rows[:limit]

    @staticmethod
    def _to_dict(record: KnowledgeRecord) -> dict:
        return {
            "id": record.id,
            "topic": record.topic,
            "instrument_id": record.instrument_id,
            "region": record.region,
            "evidence": record.evidence.model_dump(mode="json"),
            "tags": record.tags,
            "created_at": record.created_at,
        }
