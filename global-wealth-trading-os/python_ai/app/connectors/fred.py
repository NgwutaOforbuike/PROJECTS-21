from __future__ import annotations
from datetime import datetime, timezone
import httpx
from .base import Connector, ConnectorResult
from ..models import Evidence


class FredConnector(Connector):
    source_id="fred"
    base="https://api.stlouisfed.org/fred"

    def __init__(self,api_key:str,timeout:float=20.0)->None:
        super().__init__(timeout)
        self.api_key=api_key

    async def health(self)->dict:
        return {"source_id":self.source_id,"configured":bool(self.api_key),"requires_api_key":True}

    async def observations(self,series_id:str,observation_start:str|None=None,observation_end:str|None=None)->ConnectorResult:
        if not self.api_key: raise RuntimeError("FRED_API_KEY is required")
        params={"series_id":series_id,"api_key":self.api_key,"file_type":"json","sort_order":"asc"}
        if observation_start: params["observation_start"]=observation_start
        if observation_end: params["observation_end"]=observation_end
        url=f"{self.base}/series/observations"
        async with httpx.AsyncClient(timeout=self.timeout,follow_redirects=True) as c:
            r=await c.get(url,params=params); r.raise_for_status()
        return ConnectorResult(self.source_id,r.json(),{"series_id":series_id,"retrieved_at":datetime.now(timezone.utc).isoformat()})

    @staticmethod
    def numeric_observations(payload:dict)->list[tuple[str,float]]:
        out=[]
        for row in payload.get("observations",[]):
            v=row.get("value")
            if v in {None,"."}: continue
            try: out.append((row["date"],float(v)))
            except Exception: continue
        return out

    @staticmethod
    def evidence(series_id:str,payload:dict,limit:int=24)->list[Evidence]:
        rows=FredConnector.numeric_observations(payload)[-limit:]
        return [Evidence(
            source_id="fred",source_name="Federal Reserve Bank of St. Louis FRED",
            source_tier=1,url="https://fred.stlouisfed.org/",
            text=f"FRED series {series_id}: {date} = {value}.",reliability=.97
        ) for date,value in rows]
