from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class MarketDataFile:
    path:str
    instrument_id:str
    region:str
    source_ids:list[str]


def load_ohlcv_csv(spec:MarketDataFile)->pd.DataFrame:
    p=Path(spec.path)
    if not p.exists(): raise FileNotFoundError(p)
    df=pd.read_csv(p)
    timestamp=None
    for candidate in ["timestamp","date","datetime","time"]:
        if candidate in df.columns:
            timestamp=candidate; break
    if timestamp is None: raise ValueError("CSV requires timestamp/date/datetime/time column")
    df[timestamp]=pd.to_datetime(df[timestamp],utc=True,errors="raise")
    df=df.set_index(timestamp).sort_index()
    rename={c:c.lower() for c in df.columns}
    df=df.rename(columns=rename)
    required=["open","high","low","close","volume"]
    missing=[c for c in required if c not in df]
    if missing: raise ValueError(f"missing OHLCV columns: {missing}")
    return df[required].astype(float)
