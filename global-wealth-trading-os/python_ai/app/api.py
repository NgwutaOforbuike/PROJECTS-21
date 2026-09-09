from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
from .knowledge import KnowledgeBase
from .models import Evidence, Mandate, MarketState, PortfolioState
from .orchestrator import AutonomousInvestmentOrchestrator
from .connectors import SecEdgarConnector, BlsConnector, CompaniesHouseConnector, FredConnector, BeaConnector, OfficialWebConnector
from .ingestion import ResearchIngestionPipeline
from .daily_cycle import DailyInvestmentCycle
from .monte_carlo import simulate as monte_carlo_simulate
from .research_score import score_evidence
from .audit import AuditLedger
from .drift import detect_drift
from .transaction_costs import estimate_costs
from .alerts import AlertEngine
from .database import init_db
from .training_service import TrainingService
from .model_artifacts import ModelArtifactStore
from .model_registry import ModelRegistry
from .dataset_registry import DatasetRegistry
from .retraining import should_retrain
from .learning_cycle import LearningCycle
from .investment_engine import AutonomousInvestmentEngine
from .agent_context import InvestmentContext
from .security import posture as security_posture

app = FastAPI(title="Global Wealth AI", version="0.1.0")
kb = KnowledgeBase()
orchestrator = AutonomousInvestmentOrchestrator(Mandate())
ingestion = ResearchIngestionPipeline(kb=kb)
daily_cycle_engine = DailyInvestmentCycle(orchestrator=orchestrator, kb=kb)
audit = AuditLedger()
training_service = TrainingService()
model_artifacts = ModelArtifactStore()
model_registry = ModelRegistry()
dataset_registry = DatasetRegistry()
learning_cycle_engine = LearningCycle(training=training_service)
investment_engine = AutonomousInvestmentEngine()


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


class FredIngestRequest(BaseModel):
    series_id: str
    observation_start: str | None = None
    observation_end: str | None = None


class BeaRequest(BaseModel):
    dataset: str
    params: dict[str, str]


class OfficialWebIngestRequest(BaseModel):
    url: str
    source_name: str
    topic: str = "official research"
    region: str | None = None
    instrument_id: str | None = None


class MonteCarloRequest(BaseModel):
    initial_equity: float = 150.0
    daily_returns: list[float]
    horizon_days: int = 20
    simulations: int = 5000


@app.get("/system/capabilities")
async def system_capabilities() -> dict:
    return {
        "knowledge_memory": "ACTIVE",
        "feature_store": "ACTIVE",
        "market_data_consensus": "ACTIVE_IN_TYPESCRIPT_SERVICE",
        "official_filings_ingestion": "ACTIVE",
        "macro_ingestion": "ACTIVE",
        "technical_features": "ACTIVE",
        "ensemble_forecasting": "ACTIVE",
        "walk_forward_validation": "ACTIVE",
        "data_quality_gates": "ACTIVE",
        "investment_committee": "ACTIVE",
        "risk_governor": "ACTIVE",
        "monte_carlo": "ACTIVE",
        "portfolio_optimisation": "ACTIVE",
        "paper_execution": "ACTIVE",
        "prediction_outcomes": "ACTIVE",
        "strategy_promotion_gate": "ACTIVE",
        "audit_ledger": "ACTIVE",
        "model_drift_detection": "ACTIVE",
        "transaction_cost_model": "ACTIVE",
        "portfolio_reconciliation": "ACTIVE",
        "operational_alerts": "ACTIVE",
        "sql_persistence": "ACTIVE",
        "dataset_lineage_registry": "ACTIVE",
        "temporal_leakage_guard": "ACTIVE",
        "model_training_pipeline": "ACTIVE",
        "champion_challenger_registry": "ACTIVE",
        "artifact_hash_verification": "ACTIVE",
        "retraining_policy": "ACTIVE",
        "champion_inference": "ACTIVE",
        "continuous_learning_cycle": "ACTIVE",
        "live_execution": "LOCKED",
    }


@app.post("/decisions/daily-cycle")
async def daily_cycle(req: DailyBestRequest) -> dict:
    report = await daily_cycle_engine.run(req.universe, req.portfolio)
    row = audit.append("DAILY_CYCLE", "autonomous-investment-orchestrator", report.__dict__)
    return {"report": report.__dict__, "audit_hash": row.hash}


@app.post("/analysis/monte-carlo")
async def monte_carlo(req: MonteCarloRequest) -> dict:
    try:
        result = monte_carlo_simulate(
            req.initial_equity,
            req.daily_returns,
            horizon_days=req.horizon_days,
            simulations=req.simulations,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.__dict__


@app.get("/research/evidence-score")
async def evidence_score(instrument_id: str | None = None, topic: str | None = None) -> dict:
    records = kb.query(instrument_id=instrument_id, topic=topic, limit=200)
    result = score_evidence([r.evidence for r in records])
    return result.__dict__


@app.post("/sources/fred/ingest")
async def ingest_fred(req: FredIngestRequest) -> dict:
    key = os.getenv("FRED_API_KEY", "")
    if not key:
        raise HTTPException(status_code=503, detail="FRED_API_KEY is not configured.")
    connector = FredConnector(key)
    try:
        result = await connector.observations(req.series_id, req.observation_start, req.observation_end)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"FRED ingestion failed: {exc}") from exc
    evidence = connector.evidence(req.series_id, result.payload)
    report = ingestion.ingest_evidence(
        connector.source_id, evidence, region="US", topic="US macro",
        tags=["macro","official","fred",req.series_id]
    )
    audit.append("INGEST_FRED","research-pipeline",{"series_id":req.series_id,"count":len(evidence)})
    return {"report":report.__dict__,"observations":connector.numeric_observations(result.payload)[-24:]}


@app.post("/sources/bea/query")
async def query_bea(req: BeaRequest) -> dict:
    key = os.getenv("BEA_API_KEY", "")
    if not key:
        raise HTTPException(status_code=503, detail="BEA_API_KEY is not configured.")
    connector = BeaConnector(key)
    try:
        result = await connector.request(req.dataset, req.params)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"BEA query failed: {exc}") from exc
    audit.append("QUERY_BEA","research-pipeline",{"dataset":req.dataset})
    return result.payload


@app.post("/sources/official-web/ingest")
async def ingest_official_web(req: OfficialWebIngestRequest) -> dict:
    connector = OfficialWebConnector()
    try:
        result = await connector.fetch(req.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Official-source ingestion failed: {exc}") from exc
    evidence = connector.evidence(req.source_name, result)
    report = ingestion.ingest_evidence(
        connector.source_id,[evidence],instrument_id=req.instrument_id,
        region=req.region,topic=req.topic,tags=["official","web-snapshot"]
    )
    audit.append("INGEST_OFFICIAL_WEB","research-pipeline",{"url":req.url,"sha256":result.payload["sha256"]})
    return {"report":report.__dict__,"sha256":result.payload["sha256"],"url":result.metadata.get("url")}


class DriftRequest(BaseModel):
    reference: list[float]
    recent: list[float]


class CostRequest(BaseModel):
    notional: float
    spread_bps: float
    market_impact_bps: float
    commission: float = 0.0
    fx_bps: float = 0.0


class AlertRequest(BaseModel):
    drawdown_pct: float
    data_confidence: float
    stale: bool
    drifted: bool
    reconciliation_issues: int = 0


@app.post("/ops/drift")
async def drift(req: DriftRequest) -> dict:
    return detect_drift(req.reference, req.recent).__dict__


@app.post("/ops/transaction-costs")
async def transaction_costs(req: CostRequest) -> dict:
    try:
        return estimate_costs(
            req.notional,
            spread_bps=req.spread_bps,
            market_impact_bps=req.market_impact_bps,
            commission=req.commission,
            fx_bps=req.fx_bps,
        ).__dict__
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/ops/alerts")
async def alerts(req: AlertRequest) -> list[dict]:
    rows = AlertEngine().evaluate(
        drawdown_pct=req.drawdown_pct,
        data_confidence=req.data_confidence,
        stale=req.stale,
        drifted=req.drifted,
        reconciliation_issues=req.reconciliation_issues,
    )
    return [x.__dict__ for x in rows]


@app.post("/ops/database/init")
async def database_init() -> dict:
    try:
        init_db()
        return {"ok": True}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database initialisation failed: {exc}") from exc


class OHLCVPoint(BaseModel):
    timestamp: str
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)


class TrainModelRequest(BaseModel):
    instrument_id: str
    region: str
    source_ids: list[str]
    observations: list[OHLCVPoint]
    target_horizon: int = Field(default=1, ge=1, le=20)
    strategy_name: str = "daily-return"
    version: str = "v1"


class RetrainingCheckRequest(BaseModel):
    last_trained_at: str
    new_clean_observations: int = 0
    drifted: bool = False
    mean_shift_z: float = 0.0
    volatility_ratio: float = 1.0


@app.post("/training/train")
async def train_model(req: TrainModelRequest) -> dict:
    if req.region not in {"NG","US","UK"}:
        raise HTTPException(status_code=400, detail="region must be NG, US or UK")
    if not req.source_ids:
        raise HTTPException(status_code=400, detail="at least one source_id is required")
    if len(req.observations) < 140:
        raise HTTPException(status_code=400, detail="at least 140 OHLCV observations are required for training")
    try:
        import pandas as pd
        rows=[o.model_dump() for o in req.observations]
        frame=pd.DataFrame(rows)
        frame["timestamp"]=pd.to_datetime(frame["timestamp"],utc=True,errors="raise")
        frame=frame.set_index("timestamp").sort_index()
        result=training_service.train_from_frame(
            frame[["open","high","low","close","volume"]],
            instrument_id=req.instrument_id,
            region=req.region,
            source_ids=req.source_ids,
            target_horizon=req.target_horizon,
            strategy_name=req.strategy_name,
            version=req.version,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Training failed: {exc}") from exc
    audit.append(
        "MODEL_TRAINED","training-service",
        {"model_id":result.model_id,"dataset_hash":result.dataset_hash,
         "strategy_name":req.strategy_name,"promoted":result.promoted_to_champion}
    )
    return result.__dict__


@app.get("/training/models")
async def list_models() -> list[dict]:
    return [m.__dict__ for m in model_artifacts.list_metadata()]


@app.get("/training/champion/{strategy_name}")
async def get_champion(strategy_name: str) -> dict:
    champion=model_registry.champion(strategy_name)
    if champion is None:
        raise HTTPException(status_code=404, detail="No champion model registered for strategy.")
    return champion.__dict__


@app.get("/training/datasets")
async def list_datasets() -> list[dict]:
    return [d.__dict__ for d in dataset_registry.all()]


@app.post("/training/retraining-check")
async def retraining_check(req: RetrainingCheckRequest) -> dict:
    from .drift import DriftReport
    drift=DriftReport(req.drifted,req.mean_shift_z,req.volatility_ratio,["provided drift signal"] if req.drifted else [])
    decision=should_retrain(
        last_trained_at=req.last_trained_at,
        new_clean_observations=req.new_clean_observations,
        drift=drift,
    )
    return decision.__dict__


class LearningCycleRequest(BaseModel):
    instrument_id: str
    region: str
    source_ids: list[str]
    observations: list[OHLCVPoint]
    strategy_name: str = "daily-return"
    version: str = "v1"
    new_clean_observations: int | None = None


@app.post("/learning/cycle")
async def learning_cycle(req: LearningCycleRequest) -> dict:
    if req.region not in {"NG","US","UK"}:
        raise HTTPException(status_code=400, detail="region must be NG, US or UK")
    if len(req.observations) < 160:
        raise HTTPException(status_code=400, detail="at least 160 OHLCV observations are required")
    if not req.source_ids:
        raise HTTPException(status_code=400, detail="at least one source_id is required")
    try:
        import pandas as pd
        frame=pd.DataFrame([o.model_dump() for o in req.observations])
        frame["timestamp"]=pd.to_datetime(frame["timestamp"],utc=True,errors="raise")
        frame=frame.set_index("timestamp").sort_index()
        result=learning_cycle_engine.run(
            frame[["open","high","low","close","volume"]],
            instrument_id=req.instrument_id,
            region=req.region,
            source_ids=req.source_ids,
            strategy_name=req.strategy_name,
            version=req.version,
            new_clean_observations=req.new_clean_observations,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Learning cycle failed: {exc}") from exc
    payload={
        "strategy_name":result.strategy_name,
        "retrained":result.retrained,
        "retraining_reasons":result.retraining_reasons,
        "trained_model_id":result.trained_model_id,
        "promoted_to_champion":result.promoted_to_champion,
        "forecast":result.forecast.__dict__ if result.forecast else None,
        "ran_at":result.ran_at,
    }
    audit.append("LEARNING_CYCLE","learning-engine",payload)
    return payload


@app.post("/investment/decide")
async def investment_decide(ctx: InvestmentContext) -> dict:
    result = await investment_engine.decide(ctx)
    payload = {
        "action": result.action,
        "committee": {
            "score": result.committee.score,
            "confidence": result.committee.confidence,
            "buy_votes": result.committee.buy_votes,
            "avoid_votes": result.committee.avoid_votes,
            "vetoes": result.committee.vetoes,
            "decision": result.committee.decision,
            "reasons": result.committee.reasons,
        },
        "trade_plan": result.trade_plan.model_dump(mode="json") if result.trade_plan else None,
        "blockers": result.blockers,
    }
    audit.append("INVESTMENT_DECISION","autonomous-investment-engine",payload)
    return payload


@app.get("/security/posture")
async def security_posture_endpoint() -> dict:
    return security_posture().__dict__
