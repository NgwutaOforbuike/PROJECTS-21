from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from .knowledge import KnowledgeBase
from .models import Evidence, Mandate, MarketState, PortfolioState
from .orchestrator import AutonomousInvestmentOrchestrator
from .connectors import SecEdgarConnector, BlsConnector, CompaniesHouseConnector
from .ingestion import ResearchIngestionPipeline

app = FastAPI(title="Global Wealth AI", version="0.1.0")
kb = KnowledgeBase()
orchestrator = AutonomousInvestmentOrchestrator(Mandate())
ingestion = ResearchIngestionPipeline(kb=kb)


class DailyBestRequest(BaseModel):
    universe: list[MarketState]
    portfolio: PortfolioState = PortfolioState()


class RememberRequest(BaseModel):
    topic: str
    evidence: Evidence
    instrument_id: str | None = None
    region: str | None = None
    tags: list[str] = []


@app.get("/health")
async def health() -> dict:
    return {
        "ok": True,
        "service": "global-wealth-ai",
        "mode": "AUTONOMOUS_ANALYSIS_PAPER_EXECUTION_ONLY",
        "live_execution": False,
    }


@app.get("/mandate")
async def mandate() -> dict:
    return orchestrator.mandate.model_dump(mode="json")


@app.post("/knowledge/remember")
async def remember(req: RememberRequest) -> dict:
    r = kb.remember(req.topic, req.evidence, req.instrument_id, req.region, req.tags)
    return {"id": r.id, "stored": True}


@app.get("/knowledge/query")
async def query(instrument_id: str | None = None, topic: str | None = None, limit: int = 50) -> list[dict]:
    return [KnowledgeBase._to_dict(r) for r in kb.query(instrument_id=instrument_id, topic=topic, limit=limit)]


@app.post("/decisions/daily-best")
async def daily_best(req: DailyBestRequest) -> dict:
    result = await orchestrator.daily_best(req.universe, req.portfolio)
    if result is None:
        return {
            "action": "NO_TRADE",
            "reason": "No candidate cleared market-data, committee, return-hurdle and risk requirements.",
        }
    return {
        "action": "BEST_SETUP",
        "market_state": result.state.model_dump(mode="json"),
        "opinions": [o.model_dump(mode="json") for o in result.opinions],
        "plan": result.plan.model_dump(mode="json"),
    }


class SecIngestRequest(BaseModel):
    cik: str
    instrument_id: str | None = None
    region: str = "US"


class BlsIngestRequest(BaseModel):
    series_ids: list[str]
    start_year: int | None = None
    end_year: int | None = None
    registration_key: str | None = None


class CompaniesHouseIngestRequest(BaseModel):
    company_number: str
    instrument_id: str | None = None


@app.get("/sources/health")
async def sources_health() -> dict:
    sec = SecEdgarConnector()
    bls = BlsConnector()
    ch_key = os.getenv("COMPANIES_HOUSE_API_KEY", "")
    ch = CompaniesHouseConnector(ch_key)
    return {
        "sec_edgar": await sec.health(),
        "bls": await bls.health(),
        "companies_house": await ch.health(),
    }


@app.post("/sources/sec-edgar/ingest")
async def ingest_sec(req: SecIngestRequest) -> dict:
    connector = SecEdgarConnector(
        user_agent=os.getenv(
            "SEC_USER_AGENT",
            "GlobalWealthOS research contact@example.com",
        )
    )
    try:
        submissions = await connector.submissions(req.cik)
        facts = await connector.companyfacts(req.cik)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"SEC EDGAR ingestion failed: {exc}") from exc

    evidence = connector.filing_evidence(submissions.payload)
    report = ingestion.ingest_evidence(
        connector.source_id,
        evidence,
        instrument_id=req.instrument_id,
        region=req.region,
        topic="SEC filings",
        tags=["filings", "fundamentals", "official"],
    )
    features = connector.extract_companyfacts(facts.payload)
    feature_report = None
    if req.instrument_id and features:
        feature_report = ingestion.ingest_features(
            connector.source_id,
            features,
            instrument_id=req.instrument_id,
            version="sec-companyfacts-v1",
        )
    return {
        "evidence_report": report.__dict__,
        "feature_report": feature_report.__dict__ if feature_report else None,
        "features": features,
    }


@app.post("/sources/bls/ingest")
async def ingest_bls(req: BlsIngestRequest) -> dict:
    connector = BlsConnector()
    try:
        result = await connector.series(
            req.series_ids,
            start_year=req.start_year,
            end_year=req.end_year,
            registration_key=req.registration_key or os.getenv("BLS_REGISTRATION_KEY"),
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"BLS ingestion failed: {exc}") from exc

    evidence = connector.evidence(result.payload)
    report = ingestion.ingest_evidence(
        connector.source_id,
        evidence,
        region="US",
        topic="US macro",
        tags=["macro", "official", "bls"],
    )
    return {
        "report": report.__dict__,
        "latest_values": connector.latest_values(result.payload),
    }


@app.post("/sources/companies-house/ingest")
async def ingest_companies_house(req: CompaniesHouseIngestRequest) -> dict:
    key = os.getenv("COMPANIES_HOUSE_API_KEY", "")
    if not key:
        raise HTTPException(status_code=503, detail="COMPANIES_HOUSE_API_KEY is not configured.")
    connector = CompaniesHouseConnector(key)
    try:
        profile = await connector.company_profile(req.company_number)
        history = await connector.filing_history(req.company_number)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Companies House ingestion failed: {exc}") from exc

    evidence = connector.filing_evidence(history.payload)
    report = ingestion.ingest_evidence(
        connector.source_id,
        evidence,
        instrument_id=req.instrument_id,
        region="UK",
        topic="UK company filings",
        tags=["filings", "official", "companies-house"],
    )
    return {
        "report": report.__dict__,
        "profile": profile.payload,
    }
