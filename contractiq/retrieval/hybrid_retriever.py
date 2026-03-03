"""Hybrid retriever combining ChromaDB vector search + BM25 with Reciprocal Rank Fusion."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from contractiq.indexing.embedder import OpenAIEmbedder
    from contractiq.indexing.chroma_store import ChromaStore
    from contractiq.indexing.bm25_store import BM25Store


def reciprocal_rank_fusion(
    result_lists: list[list[dict[str, Any]]],
    k: int = 60,
) -> list[dict[str, Any]]:
    """Combine multiple ranked lists using Reciprocal Rank Fusion.

    RRF score = sum(1 / (k + rank)) across all lists.
    """
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for results in result_lists:
        for rank, item in enumerate(results):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
            if cid not in items:
                items[cid] = item

    # Sort by RRF score descending
    ranked_ids = sorted(scores, key=lambda x: scores[x], reverse=True)

    output = []
    for cid in ranked_ids:
        item = items[cid].copy()
        item["rrf_score"] = scores[cid]
        output.append(item)

    return output


class HybridRetriever:
    """Combines vector similarity (ChromaDB) and keyword (BM25) retrieval."""

    def __init__(
        self,
        embedder: OpenAIEmbedder | None = None,
        chroma_store: ChromaStore | None = None,
        bm25_store: BM25Store | None = None,
        alpha: float | None = None,
    ):
        from contractiq.config import get_settings
        from contractiq.indexing.embedder import OpenAIEmbedder
        from contractiq.indexing.chroma_store import ChromaStore
        from contractiq.indexing.bm25_store import BM25Store

        settings = get_settings()
        self.embedder = embedder or OpenAIEmbedder()
        self.chroma = chroma_store or ChromaStore()
        self.bm25 = bm25_store or BM25Store()
        self.alpha = alpha if alpha is not None else settings.hybrid_alpha

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve using hybrid vector + BM25 search with RRF fusion.

        Args:
            query: User query string.
            top_k: Number of results to return.
            where: ChromaDB metadata filter.

        Returns:
            List of ranked results with rrf_score.
        """
        from contractiq.config import get_settings

        settings = get_settings()
        top_k = top_k or settings.retrieval_top_k
        fetch_k = top_k * 2  # Over-fetch for better fusion

        # Vector search
        query_embedding = self.embedder.embed_query(query)
        vector_results = self.chroma.search(
            query_embedding, top_k=fetch_k, where=where
        )

        # BM25 search
        bm25_results = self.bm25.search(query, top_k=fetch_k)

        # Fuse with RRF
        fused = reciprocal_rank_fusion([vector_results, bm25_results])

        return fused[:top_k]
