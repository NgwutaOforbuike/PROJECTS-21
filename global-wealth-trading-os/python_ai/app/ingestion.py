from __future__ import annotations

from dataclasses import dataclass
from .knowledge import KnowledgeBase
from .feature_store import FeatureStore
from .models import Evidence


@dataclass
class IngestionReport:
    source_id:str
    evidence_stored:int
    features_written:int
    instrument_id:str|None


class ResearchIngestionPipeline:
    def __init__(self,kb:KnowledgeBase|None=None,features:FeatureStore|None=None)->None:
        self.kb=kb or KnowledgeBase()
        self.features=features or FeatureStore()

    def ingest_evidence(
        self,
        source_id:str,
        evidence:list[Evidence],
        *,
        instrument_id:str|None=None,
        region:str|None=None,
        topic:str="research",
        tags:list[str]|None=None,
    )->IngestionReport:
        for e in evidence:
            self.kb.remember(topic,e,instrument_id,region,tags or [])
        return IngestionReport(source_id,len(evidence),0,instrument_id)

    def ingest_features(
        self,
        source_id:str,
        features:dict[str,float],
        *,
        instrument_id:str,
        version:str="v1"
    )->IngestionReport:
        self.features.put(instrument_id,features,version)
        return IngestionReport(source_id,0,len(features),instrument_id)
