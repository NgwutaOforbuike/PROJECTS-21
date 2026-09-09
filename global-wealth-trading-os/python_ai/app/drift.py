from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class DriftReport:
    drifted:bool
    mean_shift_z:float
    volatility_ratio:float
    reasons:list[str]


def detect_drift(reference:list[float],recent:list[float],mean_z_threshold:float=2.5,vol_ratio_threshold:float=1.75)->DriftReport:
    a=np.asarray(reference,dtype=float); b=np.asarray(recent,dtype=float)
    if len(a)<20 or len(b)<10: return DriftReport(True,0,0,["insufficient observations for stable drift test"])
    std=float(a.std(ddof=1))
    z=abs(float(b.mean()-a.mean()))/(std/np.sqrt(len(b))) if std else 0
    av=float(a.std(ddof=1)); bv=float(b.std(ddof=1))
    ratio=max(bv/av,av/bv) if av>0 and bv>0 else float("inf") if av!=bv else 1
    reasons=[]
    if z>mean_z_threshold: reasons.append("return distribution mean shifted materially")
    if ratio>vol_ratio_threshold: reasons.append("volatility regime changed materially")
    return DriftReport(bool(reasons),z,ratio,reasons)
