from __future__ import annotations
from datetime import datetime,timezone
from html.parser import HTMLParser
from urllib.parse import urlparse
import hashlib
import httpx
from .base import Connector,ConnectorResult
from ..models import Evidence


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]
    def handle_data(self,data):
        t=" ".join(data.split())
        if t: self.parts.append(t)


class OfficialWebConnector(Connector):
    source_id="official-web"
    ALLOWED={
        "cbn.gov.ng","www.cbn.gov.ng",
        "nigerianstat.gov.ng","www.nigerianstat.gov.ng",
        "dmo.gov.ng","www.dmo.gov.ng",
        "sec.gov.ng","www.sec.gov.ng",
        "bankofengland.co.uk","www.bankofengland.co.uk",
        "ons.gov.uk","www.ons.gov.uk",
        "fca.org.uk","www.fca.org.uk",
    }

    async def health(self)->dict:
        return {"source_id":self.source_id,"configured":True,"allowlisted_domains":sorted(self.ALLOWED)}

    async def fetch(self,url:str)->ConnectorResult:
        host=urlparse(url).hostname or ""
        if host not in self.ALLOWED: raise ValueError("domain is not in official-source allowlist")
        async with httpx.AsyncClient(timeout=self.timeout,follow_redirects=True,headers={"User-Agent":"GlobalWealthOS/0.1 research"}) as c:
            r=await c.get(url); r.raise_for_status()
        parser=_Text(); parser.feed(r.text)
        text=" ".join(parser.parts)
        digest=hashlib.sha256(r.content).hexdigest()
        return ConnectorResult(self.source_id,{"text":text,"sha256":digest},{"url":str(r.url),"retrieved_at":datetime.now(timezone.utc).isoformat(),"status_code":r.status_code})

    @staticmethod
    def evidence(name:str,result:ConnectorResult,max_chars:int=12000)->Evidence:
        return Evidence(
            source_id="official-web",source_name=name,source_tier=1,
            url=result.metadata.get("url"),text=result.payload["text"][:max_chars],
            reliability=.96,observed_at=datetime.now(timezone.utc)
        )
