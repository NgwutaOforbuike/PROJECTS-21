from app.drift import detect_drift
from app.transaction_costs import estimate_costs
from app.reconciliation import Position,reconcile_positions
from app.alerts import AlertEngine
from app.database import init_db


def test_drift_detector_flags_large_shift():
    r=detect_drift([.001,-.001,.002,-.002]*10,[.04,.05,.03,.06]*3)
    assert r.drifted


def test_transaction_costs():
    r=estimate_costs(100,spread_bps=10,market_impact_bps=2,commission=.1)
    assert r.total_cost>0


def test_reconciliation():
    x=reconcile_positions([Position("A",1,10)],[Position("A",.5,10)])
    assert len(x)==1


def test_alerts():
    a=AlertEngine().evaluate(drawdown_pct=12,data_confidence=50,stale=True,drifted=True,reconciliation_issues=1)
    assert any(x.severity=="CRITICAL" for x in a)


def test_database_init(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_URL",f"sqlite:///{tmp_path/'x.db'}")
    assert init_db() is not None
