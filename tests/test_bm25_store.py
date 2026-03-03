"""Tests for BM25 store."""

import tempfile
from pathlib import Path

from contractiq.parsing.models import DocumentChunk
from contractiq.indexing.bm25_store import BM25Store, _tokenize


def _make_chunk(chunk_id: str, text: str, doc_id: str = "test") -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=doc_id,
        text=text,
        chunk_index=0,
    )


def test_tokenize():
    tokens = _tokenize("Hello World! This is a test.")
    assert "hello" in tokens
    assert "world" in tokens
    assert "!" not in tokens


def test_bm25_add_and_search():
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        idx_path = f.name

    try:
        store = BM25Store(index_path=idx_path)
        store.add([
            _make_chunk("1", "Payment terms are net thirty days from invoice receipt."),
            _make_chunk("2", "Force majeure covers natural disasters and pandemics."),
            _make_chunk("3", "The agreement shall be governed by New York law."),
        ])

        results = store.search("payment terms invoice", top_k=2)
        assert len(results) >= 1
        assert results[0]["chunk_id"] == "1"

        assert store.count == 3
    finally:
        Path(idx_path).unlink(missing_ok=True)


def test_bm25_persistence():
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        idx_path = f.name

    try:
        # Write
        store1 = BM25Store(index_path=idx_path)
        store1.add([_make_chunk("1", "Test document content")])
        assert store1.count == 1

        # Read
        store2 = BM25Store(index_path=idx_path)
        assert store2.count == 1
    finally:
        Path(idx_path).unlink(missing_ok=True)


def test_bm25_delete_by_document():
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        idx_path = f.name

    try:
        store = BM25Store(index_path=idx_path)
        store.add([
            _make_chunk("1", "Doc A content", doc_id="doc_a"),
            _make_chunk("2", "Doc B content", doc_id="doc_b"),
        ])
        assert store.count == 2

        store.delete_by_document("doc_a")
        assert store.count == 1
    finally:
        Path(idx_path).unlink(missing_ok=True)
