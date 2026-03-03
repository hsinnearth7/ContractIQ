"""Tests for chunking strategies."""

from contractiq.parsing.models import ParsedDocument
from contractiq.parsing.chunking import (
    chunk_recursive,
    chunk_semantic,
    chunk_clause_aware,
    chunk_document,
)


def _make_doc(text: str) -> ParsedDocument:
    return ParsedDocument(
        file_name="test.pdf",
        file_path="/tmp/test.pdf",
        file_type="pdf",
        raw_text=text,
    )


SAMPLE_TEXT = """MASTER SERVICE AGREEMENT

ARTICLE 1 - SCOPE OF SERVICES

The supplier shall provide software development services including design,
implementation, testing, and maintenance of enterprise applications.

ARTICLE 2 - PAYMENT TERMS

Payment shall be made within thirty (30) days of receipt of invoice.
Late payments shall accrue interest at 1.5% per month.

ARTICLE 3 - TERMINATION

Either party may terminate this agreement with 60 days written notice.
Termination for cause requires 30 days to cure.

ARTICLE 4 - CONFIDENTIALITY

All proprietary information shared between parties shall be kept confidential
for a period of five (5) years following termination of this agreement.
"""


def test_chunk_recursive():
    doc = _make_doc(SAMPLE_TEXT)
    chunks = chunk_recursive(doc, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    assert all(c.chunk_strategy == "recursive" for c in chunks)
    assert all(c.document_id == "test" for c in chunks)


def test_chunk_semantic():
    doc = _make_doc(SAMPLE_TEXT)
    chunks = chunk_semantic(doc, chunk_size=300, chunk_overlap=50)
    assert len(chunks) >= 1
    assert all(c.chunk_strategy == "semantic" for c in chunks)


def test_chunk_clause_aware():
    doc = _make_doc(SAMPLE_TEXT)
    chunks = chunk_clause_aware(doc, chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= 1
    assert all(c.chunk_strategy == "clause_aware" for c in chunks)

    # Should have detected ARTICLE headings
    titles = [c.section_title for c in chunks if c.section_title]
    assert any("SCOPE" in t.upper() or "PAYMENT" in t.upper() for t in titles)


def test_chunk_document_dispatcher():
    doc = _make_doc(SAMPLE_TEXT)

    r_chunks = chunk_document(doc, strategy="recursive", chunk_size=200)
    assert len(r_chunks) > 0

    s_chunks = chunk_document(doc, strategy="semantic", chunk_size=300)
    assert len(s_chunks) > 0

    c_chunks = chunk_document(doc, strategy="clause_aware", chunk_size=500)
    assert len(c_chunks) > 0


def test_chunk_ids_unique():
    doc = _make_doc(SAMPLE_TEXT)
    chunks = chunk_recursive(doc, chunk_size=200, chunk_overlap=50)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids)), "Chunk IDs should be unique"
