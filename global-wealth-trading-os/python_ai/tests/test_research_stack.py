from app.connectors.fred import FredConnector
from app.research_score import score_evidence
from app.models import Evidence
from app.audit import AuditLedger


def test_fred_parser_ignores_missing():
    p={"observations":[{"date":"2026-01-01","value":"."},{"date":"2026-02-01","value":"4.2"}]}
    assert FredConnector.numeric_observations(p)==[("2026-02-01",4.2)]


def test_evidence_score_rewards_primary():
    rows=[Evidence(source_id="a",source_name="A",source_tier=1,text="x",reliability=.99),
          Evidence(source_id="b",source_name="B",source_tier=1,text="y",reliability=.98)]
    r=score_evidence(rows)
    assert r.score>90
    assert not r.blockers


def test_audit_chain(tmp_path):
    a=AuditLedger(str(tmp_path/"audit.jsonl"))
    x=a.append("TEST","system",{"a":1})
    y=a.append("TEST2","system",{"b":2})
    assert y.previous_hash==x.hash
