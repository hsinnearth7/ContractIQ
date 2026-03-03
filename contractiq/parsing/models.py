"""Data models for document parsing pipeline."""

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ContractType(str, Enum):
    MSA = "MSA"
    PO = "PO"
    NDA = "NDA"
    SLA = "SLA"
    OTHER = "OTHER"


class ContractMetadata(BaseModel):
    """Structured metadata extracted from a contract by GPT-4o."""

    supplier_name: str = Field(default="", description="Supplier/vendor name")
    buyer_name: str = Field(default="", description="Buyer/client name")
    contract_type: ContractType = Field(default=ContractType.OTHER)
    agreement_number: str = Field(default="", description="Contract/agreement ID")
    effective_date: str = Field(default="", description="Contract start date")
    expiration_date: str = Field(default="", description="Contract end date")
    contract_value: str = Field(default="", description="Total contract value")
    currency: str = Field(default="USD")
    governing_law: str = Field(default="", description="Jurisdiction / governing law")
    key_terms: list[str] = Field(default_factory=list, description="Key terms summary")


class ParsedDocument(BaseModel):
    """Result of parsing a single document file."""

    file_name: str
    file_path: str
    file_type: str  # "pdf" or "docx"
    raw_text: str
    page_count: int = 0
    tables: list[list[list[str]]] = Field(
        default_factory=list, description="Extracted tables"
    )
    metadata: ContractMetadata = Field(default_factory=ContractMetadata)
    parse_errors: list[str] = Field(default_factory=list)


class DocumentChunk(BaseModel):
    """A chunk of text from a parsed document, ready for embedding."""

    chunk_id: str = Field(description="Unique chunk identifier")
    document_id: str = Field(description="Source document identifier")
    text: str = Field(description="Chunk text content")
    chunk_index: int = Field(description="Position in document")
    total_chunks: int = Field(default=0)
    start_char: int = Field(default=0)
    end_char: int = Field(default=0)
    page_number: int | None = Field(default=None)
    section_title: str = Field(default="")
    chunk_strategy: str = Field(default="recursive")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Flattened metadata for vector store filtering",
    )

    def to_vector_metadata(self) -> dict[str, Any]:
        """Flatten metadata for ChromaDB storage."""
        m = {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "chunk_strategy": self.chunk_strategy,
            "section_title": self.section_title,
        }
        if self.page_number is not None:
            m["page_number"] = self.page_number
        m.update(self.metadata)
        return m
