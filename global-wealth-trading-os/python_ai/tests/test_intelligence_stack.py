import numpy as np
import pandas as pd
from app.technical_features import build_technical_features
from app.data_quality import assess_market_frame
from app.monte_carlo import simulate
from app.correlation import correlation_alerts
from app.promotion import can_promote_to_paper
from app.backtest import evaluate_returns


def sample_frame(n=180):
    idx=pd.date_range("2025-01-01",periods=n,freq="D",tz="UTC")
    close=pd.Series(np.linspace(100,130,n)+np.sin(np.arange(n)/5),index=idx)
    return pd.DataFrame({
        "close":close,
        "high":close*1.01,
        "low":close*.99,
        "volume":np.linspace(1000,2000,n)
    },index=idx)


def test_technical_features_are_created():
    x=build_technical_features(sample_frame())
    assert {"rsi_14","macd","atr_pct","volume_z20"}.issubset(x.columns)


def test_data_quality_clean_frame():
    r=assess_market_frame(sample_frame(),max_staleness_seconds=None)
    assert r.score>90


def test_monte_carlo():
    r=simulate(150,[.01,-.005,.004,.002,-.001,.006,.003,-.002,.004,.005],horizon_days=5,simulations=200)
    assert r.p95_terminal>=r.p05_terminal


def test_correlation_alerts():
    x=pd.DataFrame({"a":[1,2,3,4],"b":[2,4,6,8],"c":[4,1,3,2]})
    alerts=correlation_alerts(x,.9)
    assert any({a.a,a.b}=={"a","b"} for a in alerts)


def test_promotion_gate():
    m=evaluate_returns([.01,-.005,.012,.004]*20)
    d=can_promote_to_paper(m,min_trades=50)
    assert isinstance(d.allowed,bool)
