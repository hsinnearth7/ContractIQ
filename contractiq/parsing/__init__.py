"""Document parsing pipeline."""

from contractiq.parsing.pdf_parser import parse_pdf
from contractiq.parsing.docx_parser import parse_docx
from contractiq.parsing.chunking import chunk_document, CHUNKING_STRATEGIES
from contractiq.parsing.metadata_extractor import extract_metadata
from contractiq.parsing.models import (
    ParsedDocument,
    DocumentChunk,
    ContractMetadata,
    ContractType,
)

__all__ = [
    "parse_pdf",
    "parse_docx",
    "chunk_document",
    "extract_metadata",
    "CHUNKING_STRATEGIES",
    "ParsedDocument",
    "DocumentChunk",
    "ContractMetadata",
    "ContractType",
]
