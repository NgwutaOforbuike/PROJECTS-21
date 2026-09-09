from app.connectors.sec_edgar import SecEdgarConnector
from app.connectors.bls import BlsConnector
from app.connectors.companies_house import CompaniesHouseConnector


def test_sec_cik_padding():
    assert SecEdgarConnector.cik("320193")=="0000320193"


def test_sec_companyfacts_normalization():
    payload={"facts":{"us-gaap":{"Assets":{"units":{"USD":[
        {"val":100,"filed":"2025-01-01"},
        {"val":125,"filed":"2026-01-01"}
    ]}}}}}
    assert SecEdgarConnector.extract_companyfacts(payload)["assets"]==125


def test_bls_latest():
    payload={"Results":{"series":[{"seriesID":"X","data":[{"value":"123.4"}]}]}}
    assert BlsConnector.latest_values(payload)=={"X":123.4}


def test_companies_house_health_requires_key():
    c=CompaniesHouseConnector("")
    assert c.api_key==""
