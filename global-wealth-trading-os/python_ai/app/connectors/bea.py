from __future__ import annotations
from datetime import datetime,timezone
import httpx
from .base import Connector,ConnectorResult


class BeaConnector(Connector):
    source_id="bea"
    base="https://apps.bea.gov/api/data"

    def __init__(self,api_key:str,timeout:float=20.0)->None:
        super().__init__(timeout); self.api_key=api_key

    async def health(self)->dict:
        return {"source_id":self.source_id,"configured":bool(self.api_key),"requires_api_key":True}

    async def request(self,dataset:str,params:dict[str,str])->ConnectorResult:
        if not self.api_key: raise RuntimeError("BEA_API_KEY is required")
        q={"UserID":self.api_key,"method":"GetData","datasetname":dataset,"ResultFormat":"JSON",**params}
        async with httpx.AsyncClient(timeout=self.timeout,follow_redirects=True) as c:
            r=await c.get(self.base,params=q); r.raise_for_status()
        return ConnectorResult(self.source_id,r.json(),{"dataset":dataset,"retrieved_at":datetime.now(timezone.utc).isoformat()})
