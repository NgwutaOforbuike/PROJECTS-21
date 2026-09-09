from __future__ import annotations
import numpy as np
import pandas as pd


def _rsi(close: pd.Series, window:int=14)->pd.Series:
    delta=close.diff()
    gain=delta.clip(lower=0).rolling(window).mean()
    loss=(-delta.clip(upper=0)).rolling(window).mean()
    rs=gain/loss.replace(0,np.nan)
    return 100-(100/(1+rs))


def build_technical_features(frame:pd.DataFrame)->pd.DataFrame:
    required={"close","high","low","volume"}
    missing=required-set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    x=frame.copy().sort_index()
    c=x["close"].astype(float)
    x["ret_1"]=c.pct_change()
    x["ret_5"]=c.pct_change(5)
    x["ret_20"]=c.pct_change(20)
    x["vol_20"]=x["ret_1"].rolling(20).std()*np.sqrt(252)
    x["sma_10_ratio"]=c/c.rolling(10).mean()-1
    x["sma_20_ratio"]=c/c.rolling(20).mean()-1
    x["ema_12"]=c.ewm(span=12,adjust=False).mean()
    x["ema_26"]=c.ewm(span=26,adjust=False).mean()
    x["macd"]=x["ema_12"]-x["ema_26"]
    x["macd_signal"]=x["macd"].ewm(span=9,adjust=False).mean()
    x["rsi_14"]=_rsi(c,14)
    tr=pd.concat([
        x["high"]-x["low"],
        (x["high"]-c.shift()).abs(),
        (x["low"]-c.shift()).abs()
    ],axis=1).max(axis=1)
    x["atr_14"]=tr.rolling(14).mean()
    x["atr_pct"]=x["atr_14"]/c
    x["volume_z20"]=(x["volume"]-x["volume"].rolling(20).mean())/x["volume"].rolling(20).std().replace(0,np.nan)
    rolling_high=c.rolling(20).max()
    rolling_low=c.rolling(20).min()
    x["range_position_20"]=(c-rolling_low)/(rolling_high-rolling_low).replace(0,np.nan)
    return x.replace([np.inf,-np.inf],np.nan)
