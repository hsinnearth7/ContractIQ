"""Tests for data models."""

from contractiq.parsing.models import (
    ContractMetadata,
    ContractType,
    ParsedDocument,
    DocumentChunk,
)


def test_contract_metadata_defaults():
    meta = ContractMetadata()
    assert meta.supplier_name == ""
    assert meta.contract_type == ContractType.OTHER
    assert meta.currency == "USD"


def test_parsed_document_creation():
    doc = ParsedDocument(
        file_name="test.pdf",
        file_path="/tmp/test.pdf",
        file_type="pdf",
        raw_text="This is a test contract.",
    )
    assert doc.file_name == "test.pdf"
    assert doc.page_count == 0
    assert doc.tables == []


def test_document_chunk_vector_metadata():
    chunk = DocumentChunk(
        chunk_id="abc123",
        document_id="test_contract",
        text="Sample text",
        chunk_index=0,
        section_title="Preamble",
        metadata={"supplier_name": "Acme", "contract_type": "MSA"},
    )
    vm = chunk.to_vector_metadata()
    assert vm["chunk_id"] == "abc123"
    assert vm["document_id"] == "test_contract"
    assert vm["supplier_name"] == "Acme"
    assert vm["section_title"] == "Preamble"
