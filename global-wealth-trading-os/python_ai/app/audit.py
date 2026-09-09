from __future__ import annotations
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json


@dataclass
class AuditEvent:
    timestamp:str
    event_type:str
    actor:str
    payload:dict
    previous_hash:str
    hash:str


class AuditLedger:
    def __init__(self,path:str="data/audit.jsonl")->None:
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)

    def _last_hash(self)->str:
        if not self.path.exists(): return "GENESIS"
        lines=[x for x in self.path.read_text().splitlines() if x.strip()]
        return json.loads(lines[-1])["hash"] if lines else "GENESIS"

    def append(self,event_type:str,actor:str,payload:dict)->AuditEvent:
        ts=datetime.now(timezone.utc).isoformat()
        prev=self._last_hash()
        raw=json.dumps({"timestamp":ts,"event_type":event_type,"actor":actor,"payload":payload,"previous_hash":prev},sort_keys=True,default=str)
        h=hashlib.sha256(raw.encode()).hexdigest()
        row=AuditEvent(ts,event_type,actor,payload,prev,h)
        with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(asdict(row),default=str)+"\n")
        return row
