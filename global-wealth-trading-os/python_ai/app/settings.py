from __future__ import annotations
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    environment:str=os.getenv("GW_ENV","development")
    sec_user_agent:str=os.getenv("SEC_USER_AGENT","GlobalWealthOS research contact@example.com")
    fred_api_key:str=os.getenv("FRED_API_KEY","")
    bea_api_key:str=os.getenv("BEA_API_KEY","")
    bls_registration_key:str=os.getenv("BLS_REGISTRATION_KEY","")
    companies_house_api_key:str=os.getenv("COMPANIES_HOUSE_API_KEY","")
    live_execution_enabled:bool=False


settings=Settings()
