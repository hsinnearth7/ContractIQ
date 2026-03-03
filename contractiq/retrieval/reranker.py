"""Cross-encoder re-ranking using sentence-transformers."""

from typing import Any

from sentence_transformers import CrossEncoder

from contractiq.config import get_settings


class CrossEncoderReranker:
    """Re-ranks retrieval results using a cross-encoder model."""

    def __init__(self, model_name: str | None = None):
        settings = get_settings()
        self._model_name = model_name or settings.reranker_model
        self._model: CrossEncoder | None = None

    def _load_model(self) -> CrossEncoder:
        if self._model is None:
            self._model = CrossEncoder(self._model_name)
        return self._model

    def rerank(
        self,
        query: str,
        results: list[dict[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """Re-rank results using cross-encoder scores.

        Args:
            query: Original query.
            results: Retrieval results with 'text' field.
            top_k: Number of results to return after re-ranking.

        Returns:
            Re-ranked results with 'rerank_score' field.
        """
        if not results:
            return []

        settings = get_settings()
        top_k = top_k or settings.rerank_top_k
        model = self._load_model()

        # Prepare query-document pairs
        pairs = [(query, r["text"]) for r in results]
        scores = model.predict(pairs)

        # Attach scores and sort
        for result, score in zip(results, scores):
            result["rerank_score"] = float(score)

        reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]
