"""Tests for compliance module."""

from contractiq.compliance.clause_registry import ClauseRegistry
from contractiq.compliance.report_generator import risk_level, risk_color
from contractiq.generation.response_models import ComplianceReport, ClauseFinding


def test_clause_registry_loads():
    registry = ClauseRegistry()
    assert len(registry.all_clauses) >= 15

    critical = registry.critical
    assert len(critical) >= 5

    major = registry.major
    assert len(major) >= 3

    minor = registry.minor
    assert len(minor) >= 3


def test_clause_registry_by_name():
    registry = ClauseRegistry()

    fm = registry.get_by_name("Force Majeure")
    assert fm is not None
    assert fm["severity"] == "critical"
    assert "force majeure" in fm["keywords"]

    missing = registry.get_by_name("nonexistent")
    assert missing is None


def test_risk_level():
    assert risk_level(10) == "Low"
    assert risk_level(30) == "Medium"
    assert risk_level(60) == "High"
    assert risk_level(85) == "Critical"


def test_risk_color():
    assert risk_color(10) == "green"
    assert risk_color(30) == "orange"
    assert risk_color(60) == "red"
    assert risk_color(85) == "darkred"


def test_compliance_report_model():
    findings = [
        ClauseFinding(
            clause_name="Force Majeure",
            status="found",
            severity="critical",
            evidence="Force Majeure clause found in Article 5",
        ),
        ClauseFinding(
            clause_name="Data Protection",
            status="missing",
            severity="critical",
            recommendation="Add a data protection clause.",
        ),
    ]

    report = ComplianceReport(
        document_id="test-001",
        supplier_name="Acme",
        contract_type="MSA",
        risk_score=50.0,
        findings=findings,
        summary="1 found, 1 missing",
        total_clauses_checked=2,
        clauses_found=1,
        clauses_missing=1,
        clauses_partial=0,
    )

    assert report.risk_score == 50.0
    assert len(report.findings) == 2
    assert report.clauses_found == 1
