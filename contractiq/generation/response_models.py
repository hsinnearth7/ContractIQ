"""Response models for LLM generation outputs."""

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """A reference to a source chunk used in generating an answer."""
    source_id: int = Field(description="Source number [1], [2], etc.")
    chunk_id: str = Field(default="")
    document_id: str = Field(default="")
    text_excerpt: str = Field(default="", description="Relevant excerpt from the chunk")
    relevance: str = Field(default="", description="Why this source is relevant")


class QAResponse(BaseModel):
    """Response from the QA chain."""
    question: str
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ComparisonDimension(BaseModel):
    """One comparison dimension across multiple suppliers."""
    dimension: str = Field(description="e.g., Payment Terms, Liability Limit")
    values: dict[str, str] = Field(
        description="Supplier name → value mapping"
    )
    analysis: str = Field(default="", description="Brief comparative analysis")


class ComparisonResult(BaseModel):
    """Result of cross-contract comparison."""
    question: str
    suppliers: list[str]
    dimensions: list[ComparisonDimension] = Field(default_factory=list)
    summary: str = Field(default="")
    sources: list[SourceReference] = Field(default_factory=list)


class ClauseFinding(BaseModel):
    """Finding for a single mandatory clause check."""
    clause_name: str
    status: str = Field(description="found | missing | partial")
    severity: str = Field(description="critical | major | minor")
    evidence: str = Field(default="", description="Supporting text if found")
    recommendation: str = Field(default="")


class ComplianceReport(BaseModel):
    """Full compliance report for a contract."""
    document_id: str
    supplier_name: str = ""
    contract_type: str = ""
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    findings: list[ClauseFinding] = Field(default_factory=list)
    summary: str = ""
    total_clauses_checked: int = 0
    clauses_found: int = 0
    clauses_missing: int = 0
    clauses_partial: int = 0
