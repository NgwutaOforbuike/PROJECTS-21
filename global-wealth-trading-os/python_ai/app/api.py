from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from .knowledge import KnowledgeBase
from .models import Evidence, Mandate, MarketState, PortfolioState
from .orchestrator import AutonomousInvestmentOrchestrator

app = FastAPI(title="Global Wealth AI", version="0.1.0")
kb = KnowledgeBase()
orchestrator = AutonomousInvestmentOrchestrator(Mandate())


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
