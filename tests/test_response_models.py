"""Tests for response models."""

from contractiq.generation.response_models import (
    QAResponse,
    SourceReference,
    ComparisonResult,
    ComparisonDimension,
    ComplianceReport,
    ClauseFinding,
)


def test_qa_response():
    response = QAResponse(
        question="What are the payment terms?",
        answer="Net 30 days.",
        sources=[
            SourceReference(source_id=1, document_id="doc1", text_excerpt="Payment..."),
        ],
        confidence=0.9,
    )
    assert response.confidence == 0.9
    assert len(response.sources) == 1


def test_comparison_result():
    result = ComparisonResult(
        question="Compare suppliers",
        suppliers=["Acme", "NexGen"],
        dimensions=[
            ComparisonDimension(
                dimension="Payment Terms",
                values={"Acme": "Net 30", "NexGen": "Net 45"},
                analysis="Acme has shorter payment terms.",
            )
        ],
    )
    assert len(result.dimensions) == 1
    assert result.dimensions[0].values["Acme"] == "Net 30"


def test_compliance_report_risk_bounds():
    report = ComplianceReport(
        document_id="test",
        risk_score=0.0,
    )
    assert report.risk_score >= 0.0

    report2 = ComplianceReport(
        document_id="test",
        risk_score=100.0,
    )
    assert report2.risk_score <= 100.0
