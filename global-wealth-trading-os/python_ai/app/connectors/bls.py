from __future__ import annotations

from datetime import datetime, timezone
import httpx
from .base import Connector, ConnectorResult
from ..models import Evidence


class BlsConnector(Connector):
    source_id="bls"
    base="https://api.bls.gov/publicAPI/v2/timeseries/data/"

    async def health(self)->dict:
        return {"source_id":self.source_id,"configured":True,"registration_recommended":True}

    async def series(self,series_ids:list[str],start_year:int|None=None,end_year:int|None=None,registration_key:str|None=None)->ConnectorResult:
        payload={"seriesid":series_ids}
        if start_year is not None: payload["startyear"]=str(start_year)
        if end_year is not None: payload["endyear"]=str(end_year)
        if registration_key: payload["registrationkey"]=registration_key
        async with httpx.AsyncClient(timeout=self.timeout,follow_redirects=True) as c:
            r=await c.post(self.base,json=payload); r.raise_for_status()
        data=r.json()
        return ConnectorResult(self.source_id,data,{"retrieved_at":datetime.now(timezone.utc).isoformat(),"series_ids":series_ids})

    @staticmethod
    def latest_values(payload:dict)->dict[str,float]:
        out={}
        series=payload.get("Results",{}).get("series",[])
        for s in series:
            points=s.get("data",[])
            if not points: continue
            p=points[0]
            try: out[s["seriesID"]]=float(str(p["value"]).replace(",",""))
            except Exception: continue
        return out

    @staticmethod
    def evidence(payload:dict)->list[Evidence]:
        out=[]
        for s in payload.get("Results",{}).get("series",[]):
            sid=s.get("seriesID","")
            for p in s.get("data",[])[:12]:
                out.append(Evidence(
                    source_id="bls",
                    source_name="U.S. Bureau of Labor Statistics",
                    source_tier=1,
                    url="https://www.bls.gov/developers/",
                    text=f"BLS series {sid}: {p.get('year')} {p.get('periodName',p.get('period'))} = {p.get('value')}.",
                    reliability=0.99,
                ))
        return out
