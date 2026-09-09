from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass
class PaperOrder:
    id: str
    symbol: str
    side: str
    quantity: float
    requested_price: float
    fill_price: float
    slippage_bps: float
    created_at: str


class PaperExecutionEngine:
    def execute(self,symbol:str,side:str,quantity:float,reference_price:float,spread_bps:float=5.0,impact_bps:float=2.0)->PaperOrder:
        direction=1 if side.upper()=="BUY" else -1
        slip=(spread_bps/2+impact_bps)/10000
        fill=reference_price*(1+direction*slip)
        return PaperOrder(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side.upper(),
            quantity=quantity,
            requested_price=reference_price,
            fill_price=round(fill,6),
            slippage_bps=round((fill/reference_price-1)*10000*direction,4),
            created_at=datetime.now(timezone.utc).isoformat()
        )
