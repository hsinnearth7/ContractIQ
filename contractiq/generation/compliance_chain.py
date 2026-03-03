"""Compliance checking chain using LLM for semantic clause verification."""

from typing import Any

from contractiq.generation.llm_client import LLMClient
from contractiq.generation.prompts import COMPLIANCE_SYSTEM_PROMPT, COMPLIANCE_USER_PROMPT
from contractiq.generation.response_models import ComplianceReport, ClauseFinding


class ComplianceChain:
    """Checks contract compliance against mandatory clauses using LLM."""

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    def check_clause(
        self,
        contract_text: str,
        clause_name: str,
        clause_description: str,
        keywords: list[str],
        severity: str = "major",
    ) -> ClauseFinding:
        """Check if a specific clause is present in the contract text.

        Args:
            contract_text: Full or relevant contract text.
            clause_name: Name of the clause to check.
            clause_description: Description of what the clause should cover.
            keywords: Keywords for quick pre-screening.
            severity: Clause severity (critical/major/minor).

        Returns:
            ClauseFinding with status and evidence.
        """
        # Phase 1: Keyword pre-screening
        text_lower = contract_text.lower()
        keyword_hits = sum(1 for kw in keywords if kw.lower() in text_lower)

        if keyword_hits == 0:
            # No keywords found - likely missing, but verify with LLM
            # Use truncated text to save tokens
            check_text = contract_text[:4000]
        else:
            check_text = contract_text[:6000]

        # Phase 2: LLM semantic verification
        response = self.llm.chat(
            COMPLIANCE_SYSTEM_PROMPT,
            COMPLIANCE_USER_PROMPT.format(
                context=check_text,
                clause_name=clause_name,
                clause_description=clause_description,
                keywords=", ".join(keywords),
            ),
        )

        # Parse LLM response
        response_lower = response.lower()
        if '"found"' in response_lower or "status: found" in response_lower:
            status = "found"
        elif '"partial"' in response_lower or "status: partial" in response_lower:
            status = "partial"
        else:
            status = "missing"

        # Extract evidence and recommendation
        evidence = ""
        recommendation = ""
        lines = response.split("\n")
        for line in lines:
            if "evidence" in line.lower() and ":" in line:
                evidence = line.split(":", 1)[1].strip().strip('"')
            elif "recommend" in line.lower() and ":" in line:
                recommendation = line.split(":", 1)[1].strip().strip('"')

        if not recommendation and status != "found":
            recommendation = f"Consider adding a {clause_name} clause to the contract."

        return ClauseFinding(
            clause_name=clause_name,
            status=status,
            severity=severity,
            evidence=evidence,
            recommendation=recommendation,
        )

    def check_contract(
        self,
        contract_text: str,
        document_id: str,
        mandatory_clauses: list[dict[str, Any]],
        supplier_name: str = "",
        contract_type: str = "",
    ) -> ComplianceReport:
        """Run full compliance check against all mandatory clauses.

        Args:
            contract_text: Full contract text.
            document_id: Document identifier.
            mandatory_clauses: List of clause definitions from YAML.
            supplier_name: Supplier name for the report.
            contract_type: Contract type for the report.

        Returns:
            ComplianceReport with all findings and risk score.
        """
        findings: list[ClauseFinding] = []

        for clause_def in mandatory_clauses:
            finding = self.check_clause(
                contract_text=contract_text,
                clause_name=clause_def["name"],
                clause_description=clause_def["description"],
                keywords=clause_def.get("keywords", []),
                severity=clause_def.get("severity", "major"),
            )
            findings.append(finding)

        # Calculate risk score
        risk_score = self._calculate_risk(findings)

        found = sum(1 for f in findings if f.status == "found")
        missing = sum(1 for f in findings if f.status == "missing")
        partial = sum(1 for f in findings if f.status == "partial")

        summary = (
            f"Checked {len(findings)} mandatory clauses: "
            f"{found} found, {partial} partial, {missing} missing. "
            f"Risk score: {risk_score:.1f}/100."
        )

        return ComplianceReport(
            document_id=document_id,
            supplier_name=supplier_name,
            contract_type=contract_type,
            risk_score=risk_score,
            findings=findings,
            summary=summary,
            total_clauses_checked=len(findings),
            clauses_found=found,
            clauses_missing=missing,
            clauses_partial=partial,
        )

    def _calculate_risk(self, findings: list[ClauseFinding]) -> float:
        """Calculate risk score 0-100 (100 = highest risk)."""
        if not findings:
            return 0.0

        severity_weights = {"critical": 15, "major": 8, "minor": 3}
        status_multipliers = {"found": 0.0, "partial": 0.5, "missing": 1.0}

        total_risk = 0.0
        max_possible = 0.0

        for f in findings:
            weight = severity_weights.get(f.severity, 5)
            multiplier = status_multipliers.get(f.status, 1.0)
            total_risk += weight * multiplier
            max_possible += weight

        if max_possible == 0:
            return 0.0

        return min(100.0, (total_risk / max_possible) * 100)
