from __future__ import annotations

PUBLIC_OFFICIAL_CONNECTORS={
    "sec-edgar":{
        "region":"US",
        "domains":["filings","xbrl fundamentals"],
        "credential":"none",
        "status":"implemented"
    },
    "bls":{
        "region":"US",
        "domains":["inflation","employment","wages","labour"],
        "credential":"optional registration key for higher limits",
        "status":"implemented"
    },
}

CREDENTIALED_OFFICIAL_CONNECTORS={
    "companies-house":{
        "region":"UK",
        "domains":["company profile","filing history"],
        "credential":"API key",
        "status":"implemented"
    }
}

NEXT_CONNECTORS=[
    "Bank of England time-series database",
    "ONS API",
    "Federal Reserve/FRED",
    "BEA",
    "U.S. Treasury",
    "CBN official FX/monetary datasets",
    "NBS Nigeria",
    "DMO Nigeria",
    "SEC Nigeria",
    "NGX licensed market feed",
    "FMDQ licensed market feed",
    "LSE licensed market feed",
    "NYSE/Nasdaq licensed market feeds",
    "IBKR",
    "Alpaca",
    "Databento",
    "Massive",
]
