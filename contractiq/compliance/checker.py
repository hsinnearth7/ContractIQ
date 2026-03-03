"""Two-stage compliance checker: keyword pre-screening + LLM semantic check."""

from typing import Any

from contractiq.compliance.clause_registry import ClauseRegistry
from contractiq.generation.compliance_chain import ComplianceChain
from contractiq.generation.llm_client import LLMClient
from contractiq.generation.response_models import ComplianceReport


class ComplianceChecker:
    """Orchestrates compliance checking with keyword pre-screening + LLM verification."""

    def __init__(
        self,
        registry: ClauseRegistry | None = None,
        chain: ComplianceChain | None = None,
    ):
        self.registry = registry or ClauseRegistry()
        self.chain = chain or ComplianceChain()

    def check(
        self,
        contract_text: str,
        document_id: str,
        supplier_name: str = "",
        contract_type: str = "",
        severity_filter: str | None = None,
    ) -> ComplianceReport:
        """Run compliance check on a contract.

        Args:
            contract_text: Full contract text.
            document_id: Document identifier.
            supplier_name: Supplier name.
            contract_type: Contract type.
            severity_filter: Only check clauses of this severity.

        Returns:
            ComplianceReport with findings and risk score.
        """
        if severity_filter:
            clauses = self.registry.get_by_severity(severity_filter)
        else:
            clauses = self.registry.all_clauses

        return self.chain.check_contract(
            contract_text=contract_text,
            document_id=document_id,
            mandatory_clauses=clauses,
            supplier_name=supplier_name,
            contract_type=contract_type,
        )
