from __future__ import annotations

from datetime import datetime, timezone
import httpx
from .base import Connector, ConnectorResult
from ..models import Evidence


class SecEdgarConnector(Connector):
    source_id="sec-edgar"
    base="https://data.sec.gov"

    def __init__(self,user_agent:str="GlobalWealthOS research contact@example.com",timeout:float=20.0)->None:
        super().__init__(timeout)
        self.headers={"User-Agent":user_agent,"Accept-Encoding":"gzip, deflate","Host":"data.sec.gov"}

    @staticmethod
    def cik(cik:str|int)->str:
        return str(cik).strip().lstrip("0").zfill(10)

    async def health(self)->dict:
        return {"source_id":self.source_id,"configured":True,"requires_api_key":False}

    async def submissions(self,cik:str|int)->ConnectorResult:
        url=f"{self.base}/submissions/CIK{self.cik(cik)}.json"
        async with httpx.AsyncClient(timeout=self.timeout,follow_redirects=True,headers=self.headers) as c:
            r=await c.get(url); r.raise_for_status()
        return ConnectorResult(self.source_id,r.json(),{"url":url,"retrieved_at":datetime.now(timezone.utc).isoformat()})

    async def companyfacts(self,cik:str|int)->ConnectorResult:
        url=f"{self.base}/api/xbrl/companyfacts/CIK{self.cik(cik)}.json"
        async with httpx.AsyncClient(timeout=self.timeout,follow_redirects=True,headers=self.headers) as c:
            r=await c.get(url); r.raise_for_status()
        return ConnectorResult(self.source_id,r.json(),{"url":url,"retrieved_at":datetime.now(timezone.utc).isoformat()})

    @staticmethod
    def filing_evidence(payload:dict,limit:int=25)->list[Evidence]:
        recent=payload.get("filings",{}).get("recent",{})
        forms=recent.get("form",[])
        accessions=recent.get("accessionNumber",[])
        dates=recent.get("filingDate",[])
        docs=recent.get("primaryDocument",[])
        cik=str(payload.get("cik","")).zfill(10)
        out=[]
        for i,(form,acc,date,doc) in enumerate(zip(forms,accessions,dates,docs)):
            if i>=limit: break
            accession_nodash=acc.replace("-","")
            cik_int=str(int(cik)) if cik else ""
            url=f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_nodash}/{doc}"
            out.append(Evidence(
                source_id="sec-edgar",
                source_name="SEC EDGAR filing",
                source_tier=1,
                url=url,
                published_at=datetime.fromisoformat(date).replace(tzinfo=timezone.utc) if date else None,
                text=f"{form} filing submitted {date}; accession {acc}; primary document {doc}.",
                reliability=0.99,
            ))
        return out

    @staticmethod
    def extract_companyfacts(payload:dict)->dict[str,float]:
        facts=payload.get("facts",{}).get("us-gaap",{})
        candidates={
            "revenue":["RevenueFromContractWithCustomerExcludingAssessedTax","Revenues","SalesRevenueNet"],
            "net_income":["NetIncomeLoss"],
            "assets":["Assets"],
            "liabilities":["Liabilities"],
            "cash":["CashAndCashEquivalentsAtCarryingValue"],
        }
        result={}
        for key,names in candidates.items():
            for name in names:
                units=facts.get(name,{}).get("units",{})
                usd=units.get("USD",[])
                if not usd: continue
                rows=[x for x in usd if x.get("val") is not None]
                if not rows: continue
                rows.sort(key=lambda x:(x.get("filed",""),x.get("fy") or 0,x.get("fp") or ""))
                result[key]=float(rows[-1]["val"])
                break
        return result
