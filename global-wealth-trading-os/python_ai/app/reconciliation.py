from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Position:
    symbol:str
    quantity:float
    price:float


@dataclass
class ReconciliationIssue:
    symbol:str
    expected_quantity:float
    actual_quantity:float
    difference:float


def reconcile_positions(expected:list[Position],actual:list[Position],tolerance:float=1e-6)->list[ReconciliationIssue]:
    e={p.symbol:p.quantity for p in expected}
    a={p.symbol:p.quantity for p in actual}
    issues=[]
    for symbol in sorted(set(e)|set(a)):
        diff=a.get(symbol,0)-e.get(symbol,0)
        if abs(diff)>tolerance:
            issues.append(ReconciliationIssue(symbol,e.get(symbol,0),a.get(symbol,0),diff))
    return issues
