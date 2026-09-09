from __future__ import annotations
from dataclasses import dataclass
import pandas as pd


@dataclass
class CorrelationAlert:
    a:str
    b:str
    correlation:float
    severity:str


def correlation_alerts(returns:pd.DataFrame,threshold:float=.75)->list[CorrelationAlert]:
    corr=returns.corr()
    cols=list(corr.columns)
    out=[]
    for i,a in enumerate(cols):
        for b in cols[i+1:]:
            v=float(corr.loc[a,b])
            if abs(v)>=threshold:
                out.append(CorrelationAlert(a,b,v,"HIGH" if abs(v)>=.9 else "MEDIUM"))
    return sorted(out,key=lambda x:abs(x.correlation),reverse=True)
