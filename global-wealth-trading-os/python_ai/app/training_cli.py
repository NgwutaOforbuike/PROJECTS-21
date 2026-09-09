from __future__ import annotations

import argparse
import json

from .training_data import MarketDataFile,load_ohlcv_csv
from .dataset_builder import build_supervised_dataset
from .trainer import train_dataset


def main()->None:
    p=argparse.ArgumentParser(description="Train Global Wealth OS return model from provenance-labelled OHLCV data.")
    p.add_argument("--csv",required=True)
    p.add_argument("--instrument",required=True)
    p.add_argument("--region",required=True,choices=["NG","US","UK"])
    p.add_argument("--source",action="append",required=True)
    p.add_argument("--horizon",type=int,default=1)
    p.add_argument("--strategy",default="daily-return")
    p.add_argument("--version",default="v1")
    args=p.parse_args()

    raw=load_ohlcv_csv(MarketDataFile(args.csv,args.instrument,args.region,args.source))
    dataset=build_supervised_dataset(
        raw,instrument_id=args.instrument,region=args.region,source_ids=args.source,target_horizon=args.horizon
    )
    result=train_dataset(dataset,strategy_name=args.strategy,version=args.version)
    print(json.dumps({
        "model_id":result.model_id,
        "winner":result.winner_name,
        "validation":result.validation.__dict__,
        "test":result.test.__dict__,
        "dataset_hash":dataset.lineage.dataset_hash,
        "artifact_sha256":result.metadata.artifact_sha256,
    },indent=2))


if __name__=="__main__":
    main()
