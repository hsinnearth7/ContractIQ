"""Generate formatted compliance reports."""

from contractiq.generation.response_models import ComplianceReport


def generate_text_report(report: ComplianceReport) -> str:
    """Generate a human-readable text compliance report."""
    lines = [
        "=" * 60,
        "CONTRACT COMPLIANCE REPORT",
        "=" * 60,
        f"Document: {report.document_id}",
        f"Supplier: {report.supplier_name or 'N/A'}",
        f"Type: {report.contract_type or 'N/A'}",
        f"Risk Score: {report.risk_score:.1f} / 100",
        "",
        f"Summary: {report.summary}",
        "",
        "-" * 60,
        "FINDINGS",
        "-" * 60,
    ]

    for f in report.findings:
        icon = {"found": "[OK]", "partial": "[!!]", "missing": "[XX]"}.get(f.status, "[??]")
        lines.append(f"\n{icon} {f.clause_name} ({f.severity.upper()})")
        lines.append(f"    Status: {f.status}")
        if f.evidence:
            lines.append(f'    Evidence: "{f.evidence[:150]}..."')
        if f.recommendation:
            lines.append(f"    Recommendation: {f.recommendation}")

    lines.extend([
        "",
        "-" * 60,
        "STATISTICS",
        "-" * 60,
        f"Total Clauses Checked: {report.total_clauses_checked}",
        f"Found: {report.clauses_found}",
        f"Partial: {report.clauses_partial}",
        f"Missing: {report.clauses_missing}",
        "=" * 60,
    ])

    return "\n".join(lines)


def risk_level(score: float) -> str:
    """Convert risk score to human-readable level."""
    if score <= 20:
        return "Low"
    elif score <= 50:
        return "Medium"
    elif score <= 75:
        return "High"
    else:
        return "Critical"


def risk_color(score: float) -> str:
    """Return a color name for the risk level (for UI)."""
    if score <= 20:
        return "green"
    elif score <= 50:
        return "orange"
    elif score <= 75:
        return "red"
    else:
        return "darkred"
