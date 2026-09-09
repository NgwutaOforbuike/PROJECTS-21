from __future__ import annotations

import numpy as np


def minimum_variance_weights(covariance: list[list[float]], max_weight: float = 0.35) -> list[float]:
    cov=np.asarray(covariance,dtype=float)
    n=cov.shape[0]
    if cov.shape!=(n,n) or n==0:
        raise ValueError("covariance must be square")
    inv=np.linalg.pinv(cov)
    ones=np.ones(n)
    raw=inv@ones
    if float(ones@raw)==0:
        return [1/n]*n
    w=raw/float(ones@raw)
    w=np.clip(w,0,max_weight)
    if w.sum()==0:
        w=np.ones(n)/n
    else:
        w=w/w.sum()
    return [float(x) for x in w]


def risk_contributions(weights: list[float], covariance: list[list[float]]) -> list[float]:
    w=np.asarray(weights,dtype=float)
    cov=np.asarray(covariance,dtype=float)
    port_var=float(w@cov@w)
    if port_var<=0:
        return [0.0]*len(w)
    marginal=cov@w
    contrib=w*marginal/port_var
    return [float(x) for x in contrib]
