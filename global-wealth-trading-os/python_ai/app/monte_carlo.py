from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class MonteCarloResult:
    median_terminal:float
    p05_terminal:float
    p95_terminal:float
    probability_of_loss_pct:float
    expected_max_drawdown_pct:float


def simulate(
    initial_equity:float,
    daily_returns:list[float],
    *,
    horizon_days:int=20,
    simulations:int=5000,
    seed:int=42
)->MonteCarloResult:
    if initial_equity<=0: raise ValueError("initial equity must be positive")
    r=np.asarray(daily_returns,dtype=float)
    if len(r)<10: raise ValueError("at least 10 return observations required")
    rng=np.random.default_rng(seed)
    sampled=rng.choice(r,size=(simulations,horizon_days),replace=True)
    curves=initial_equity*np.cumprod(1+sampled,axis=1)
    terminal=curves[:,-1]
    peaks=np.maximum.accumulate(curves,axis=1)
    dds=(curves-peaks)/peaks
    max_dd=dds.min(axis=1)
    return MonteCarloResult(
        median_terminal=float(np.median(terminal)),
        p05_terminal=float(np.quantile(terminal,.05)),
        p95_terminal=float(np.quantile(terminal,.95)),
        probability_of_loss_pct=float((terminal<initial_equity).mean()*100),
        expected_max_drawdown_pct=float(abs(max_dd.mean())*100)
    )
