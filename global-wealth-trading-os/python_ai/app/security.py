from __future__ import annotations
from dataclasses import dataclass
import os


SECRET_NAMES={
    "FRED_API_KEY","BEA_API_KEY","BLS_REGISTRATION_KEY",
    "COMPANIES_HOUSE_API_KEY","DATABASE_URL",
    "IBKR_TOKEN","ALPACA_API_KEY","ALPACA_SECRET_KEY",
}


@dataclass
class SecurityPosture:
    live_execution_locked:bool
    secrets_from_environment:bool
    configured_secret_names:list[str]
    missing_required_for_live:list[str]


def posture()->SecurityPosture:
    configured=sorted(k for k in SECRET_NAMES if os.getenv(k))
    return SecurityPosture(
        live_execution_locked=True,
        secrets_from_environment=True,
        configured_secret_names=configured,
        missing_required_for_live=["explicit owner approval","broker permission gate","production risk certification"],
    )
