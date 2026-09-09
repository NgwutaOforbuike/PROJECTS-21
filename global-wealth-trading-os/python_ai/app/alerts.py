from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime,timezone


@dataclass
class Alert:
    severity:str
    code:str
    message:str
    created_at:str


class AlertEngine:
    def evaluate(
        self,
        *,
        drawdown_pct:float,
        data_confidence:float,
        stale:bool,
        drifted:bool,
        reconciliation_issues:int,
    )->list[Alert]:
        now=datetime.now(timezone.utc).isoformat()
        out=[]
        def add(sev,code,msg): out.append(Alert(sev,code,msg,now))
        if drawdown_pct>=12: add("CRITICAL","DRAWDOWN_LIMIT","Portfolio drawdown limit reached; block new trades.")
        elif drawdown_pct>=8: add("HIGH","DRAWDOWN_WARNING","Portfolio drawdown is approaching the hard limit.")
        if data_confidence<70: add("HIGH","LOW_DATA_CONFIDENCE","Market data confidence is below decision threshold.")
        if stale: add("HIGH","STALE_DATA","Market data is stale.")
        if drifted: add("MEDIUM","MODEL_DRIFT","Recent data distribution differs from model reference regime.")
        if reconciliation_issues: add("CRITICAL","POSITION_MISMATCH",f"{reconciliation_issues} portfolio reconciliation issue(s) detected.")
        return out
