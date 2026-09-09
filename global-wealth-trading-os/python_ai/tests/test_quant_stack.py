from app.backtest import evaluate_returns
from app.calibration import ForecastRecord, assess
from app.portfolio import minimum_variance_weights
from app.regime import classify_regime


def test_backtest_metrics():
    m=evaluate_returns([0.01,-0.005,0.02,0.003])
    assert m.trades==4
    assert m.total_return_pct>0


def test_calibration():
    r=assess([ForecastRecord(5,4,80),ForecastRecord(3,-1,60)])
    assert r.count==2
    assert r.mean_absolute_error>0


def test_weights_sum_to_one():
    w=minimum_variance_weights([[0.1,0.02],[0.02,0.08]],max_weight=0.8)
    assert abs(sum(w)-1)<1e-9


def test_regime():
    r=classify_regime(5,12,-25,0,0)
    assert r.label in {"RISK_ON","MIXED","RISK_OFF"}
