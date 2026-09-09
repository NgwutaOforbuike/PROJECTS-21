from __future__ import annotations

from pydantic import BaseModel, Field
from .models import MarketState, PortfolioState


class InvestmentContext(BaseModel):
    market: MarketState
    portfolio: PortfolioState = PortfolioState()

    fundamentals: dict[str,float|int|str|bool|None] = {}
    valuation: dict[str,float|int|str|bool|None] = {}
    earnings: dict[str,float|int|str|bool|None] = {}
    macro: dict[str,float|int|str|bool|None] = {}
    events: list[dict] = []
    news: list[dict] = []
    ownership: dict[str,float|int|str|bool|None] = {}
    derivatives: dict[str,float|int|str|bool|None] = {}
    cross_asset: dict[str,float|int|str|bool|None] = {}
    currency: dict[str,float|int|str|bool|None] = {}
    execution: dict[str,float|int|str|bool|None] = {}
    regulatory: dict[str,float|int|str|bool|None] = {}
    accounting: dict[str,float|int|str|bool|None] = {}
    alternative: dict[str,float|int|str|bool|None] = {}
    metadata: dict[str,str|float|int|bool|None] = {}


def num(d:dict,key:str,default:float|None=None)->float|None:
    v=d.get(key,default)
    if v is None: return None
    try: return float(v)
    except Exception: return default
