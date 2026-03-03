"""BM25 sparse keyword index with pickle persistence."""

import pickle
import re
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

from contractiq.config import get_settings
from contractiq.parsing.models import DocumentChunk


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer."""
    text = text.lower()
    tokens = re.findall(r"\b\w+\b", text)
    return tokens


class BM25Store:
    """BM25 keyword index with pickle persistence."""

    def __init__(self, index_path: str | None = None):
        settings = get_settings()
        self._index_path = Path(index_path or settings.bm25_index_path)
        self._chunks: list[DocumentChunk] = []
        self._corpus: list[list[str]] = []
        self._bm25: BM25Okapi | None = None

        if self._index_path.exists() and self._index_path.stat().st_size > 0:
            self._load()

    def _build_index(self) -> None:
        """Rebuild BM25 index from corpus."""
        if self._corpus:
            self._bm25 = BM25Okapi(self._corpus)
        else:
            self._bm25 = None

    def _save(self) -> None:
        """Persist index to disk."""
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "chunks": self._chunks,
            "corpus": self._corpus,
        }
        with open(self._index_path, "wb") as f:
            pickle.dump(data, f)

    def _load(self) -> None:
        """Load index from disk."""
        with open(self._index_path, "rb") as f:
            data = pickle.load(f)
        self._chunks = data["chunks"]
        self._corpus = data["corpus"]
        self._build_index()

    @property
    def count(self) -> int:
        return len(self._chunks)

    def add(self, chunks: list[DocumentChunk]) -> None:
        """Add chunks to the BM25 index."""
        for chunk in chunks:
            self._chunks.append(chunk)
            self._corpus.append(_tokenize(chunk.text))

        self._build_index()
        self._save()

    def search(self, query: str, top_k: int = 20) -> list[dict[str, Any]]:
        """Search using BM25 scoring.

        Returns:
            List of dicts with keys: chunk_id, text, score, metadata.
        """
        if self._bm25 is None or not self._chunks:
            return []

        tokens = _tokenize(query)
        scores = self._bm25.get_scores(tokens)

        # Get top-k indices
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in ranked:
            if scores[idx] > 0:
                chunk = self._chunks[idx]
                results.append({
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "score": float(scores[idx]),
                    "metadata": chunk.to_vector_metadata(),
                })
        return results

    def delete_by_document(self, document_id: str) -> None:
        """Remove chunks for a specific document and rebuild."""
        filtered = [
            (c, t)
            for c, t in zip(self._chunks, self._corpus)
            if c.document_id != document_id
        ]
        if filtered:
            self._chunks, self._corpus = zip(*filtered)
            self._chunks = list(self._chunks)
            self._corpus = list(self._corpus)
        else:
            self._chunks = []
            self._corpus = []
        self._build_index()
        self._save()

    def reset(self) -> None:
        """Clear all data."""
        self._chunks = []
        self._corpus = []
        self._bm25 = None
        if self._index_path.exists():
            self._index_path.unlink()
