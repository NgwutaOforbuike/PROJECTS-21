from __future__ import annotations

from datetime import datetime, timezone
import httpx
from .base import Connector, ConnectorResult
from ..models import Evidence


class CompaniesHouseConnector(Connector):
    source_id="companies-house"
    base="https://api.company-information.service.gov.uk"

    def __init__(self,api_key:str,timeout:float=20.0)->None:
        super().__init__(timeout)
        self.api_key=api_key

    async def health(self)->dict:
        return {"source_id":self.source_id,"configured":bool(self.api_key),"requires_api_key":True}

    async def company_profile(self,company_number:str)->ConnectorResult:
        url=f"{self.base}/company/{company_number}"
        async with httpx.AsyncClient(timeout=self.timeout,follow_redirects=True,auth=(self.api_key,"")) as c:
            r=await c.get(url); r.raise_for_status()
        return ConnectorResult(self.source_id,r.json(),{"url":url,"retrieved_at":datetime.now(timezone.utc).isoformat()})

    async def filing_history(self,company_number:str,items_per_page:int=100)->ConnectorResult:
        url=f"{self.base}/company/{company_number}/filing-history"
        async with httpx.AsyncClient(timeout=self.timeout,follow_redirects=True,auth=(self.api_key,"")) as c:
            r=await c.get(url,params={"items_per_page":items_per_page}); r.raise_for_status()
        return ConnectorResult(self.source_id,r.json(),{"url":url,"retrieved_at":datetime.now(timezone.utc).isoformat()})

    @staticmethod
    def filing_evidence(payload:dict)->list[Evidence]:
        out=[]
        for item in payload.get("items",[])[:50]:
            date=item.get("date")
            desc=item.get("description","filing")
            tx=item.get("transaction_id")
            out.append(Evidence(
                source_id="companies-house",
                source_name="Companies House filing",
                source_tier=1,
                published_at=datetime.fromisoformat(date).replace(tzinfo=timezone.utc) if date else None,
                text=f"Companies House filing: {desc}; transaction {tx}; date {date}.",
                reliability=0.98,
            ))
        return out
