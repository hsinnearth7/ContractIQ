"""Self-RAG (Self-Reflective Retrieval-Augmented Generation) module.

Implements a reflection step that verifies whether each retrieved chunk is
actually relevant to the user query before it is passed to the generation
stage.  When an LLM client is available the check is performed via a
structured prompt; otherwise a lightweight keyword-overlap heuristic is used
as a fallback (mock mode).
"""

from __future__ import annotations

import logging
import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums & data models
# ---------------------------------------------------------------------------

class RelevanceVerdict(Enum):
    """Verdict returned by the Self-RAG relevance check."""

    RELEVANT = "RELEVANT"
    PARTIALLY_RELEVANT = "PARTIALLY_RELEVANT"
    NOT_RELEVANT = "NOT_RELEVANT"

    # Allow ordering so that thresholds can be compared with >=
    def _rank(self) -> int:
        return {
            RelevanceVerdict.NOT_RELEVANT: 0,
            RelevanceVerdict.PARTIALLY_RELEVANT: 1,
            RelevanceVerdict.RELEVANT: 2,
        }[self]

    def __ge__(self, other: RelevanceVerdict) -> bool:  # type: ignore[override]
        if not isinstance(other, RelevanceVerdict):
            return NotImplemented
        return self._rank() >= other._rank()

    def __gt__(self, other: RelevanceVerdict) -> bool:  # type: ignore[override]
        if not isinstance(other, RelevanceVerdict):
            return NotImplemented
        return self._rank() > other._rank()

    def __le__(self, other: RelevanceVerdict) -> bool:  # type: ignore[override]
        if not isinstance(other, RelevanceVerdict):
            return NotImplemented
        return self._rank() <= other._rank()

    def __lt__(self, other: RelevanceVerdict) -> bool:  # type: ignore[override]
        if not isinstance(other, RelevanceVerdict):
            return NotImplemented
        return self._rank() < other._rank()


class SelfRAGResult(BaseModel):
    """Result of a Self-RAG filtering pass over retrieval results."""

    original_results: list[dict[str, Any]] = Field(
        description="The unfiltered retrieval results that were provided as input.",
    )
    filtered_results: list[dict[str, Any]] = Field(
        description="Results that passed the relevance threshold.",
    )
    reflections: list[dict[str, Any]] = Field(
        description=(
            "Per-chunk reflection records.  Each dict contains 'chunk_id', "
            "'verdict' (RelevanceVerdict value), and 'reasoning'."
        ),
    )
    filter_rate: float = Field(
        description=(
            "Fraction of original results that were filtered out "
            "(0.0 = nothing removed, 1.0 = everything removed)."
        ),
    )


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

_RELEVANCE_SYSTEM_PROMPT = (
    "You are a relevance judge for a Retrieval-Augmented Generation system.  "
    "Given a user question and a retrieved context chunk, decide whether the "
    "context is useful for answering the question."
)

_RELEVANCE_USER_PROMPT = (
    "Question: {query}\n\n"
    "Context:\n{chunk_text}\n\n"
    "Is the following context relevant to answering the question? "
    "Respond with RELEVANT, PARTIALLY_RELEVANT, or NOT_RELEVANT, "
    "followed by a brief reasoning."
)


# ---------------------------------------------------------------------------
# SelfRAGFilter
# ---------------------------------------------------------------------------

class SelfRAGFilter:
    """Filters retrieval results via LLM-based relevance reflection.

    If no *llm_client* is supplied the filter falls back to a simple
    keyword-overlap heuristic (useful for testing or offline environments).

    Parameters
    ----------
    llm_client:
        An instance of :class:`contractiq.generation.llm_client.LLMClient`
        (or any object that exposes a compatible ``chat(system_prompt,
        user_prompt)`` method).  When *None*, keyword-based mock mode is
        used.
    """

    def __init__(self, llm_client: Any | None = None) -> None:
        self._llm = llm_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def verify_relevance(self, query: str, chunk_text: str) -> RelevanceVerdict:
        """Judge whether *chunk_text* is relevant to *query*.

        Uses the LLM when available; otherwise falls back to keyword
        overlap.

        Parameters
        ----------
        query:
            The user question.
        chunk_text:
            The text content of a retrieved chunk.

        Returns
        -------
        RelevanceVerdict
            The relevance verdict for this chunk.
        """
        if self._llm is None:
            return self._fallback_keyword_check(query, chunk_text)

        try:
            user_prompt = _RELEVANCE_USER_PROMPT.format(
                query=query,
                chunk_text=chunk_text,
            )
            response: str = self._llm.chat(
                system_prompt=_RELEVANCE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.0,
                max_tokens=256,
            )
            return self._parse_verdict(response)
        except Exception:
            logger.warning(
                "LLM relevance check failed; falling back to keyword heuristic.",
                exc_info=True,
            )
            return self._fallback_keyword_check(query, chunk_text)

    def filter_results(
        self,
        query: str,
        results: list[dict[str, Any]],
        threshold: RelevanceVerdict = RelevanceVerdict.PARTIALLY_RELEVANT,
    ) -> SelfRAGResult:
        """Filter *results* by checking each chunk against *query*.

        Parameters
        ----------
        query:
            The user question.
        results:
            List of retrieval result dicts.  Each dict is expected to
            contain at least ``chunk_id`` and ``text`` keys.
        threshold:
            Minimum verdict required for a result to be kept.  Defaults
            to ``PARTIALLY_RELEVANT`` (i.e. ``NOT_RELEVANT`` results are
            dropped).

        Returns
        -------
        SelfRAGResult
            Aggregated filtering outcome including per-chunk reflections.
        """
        reflections: list[dict[str, Any]] = []
        filtered: list[dict[str, Any]] = []

        for result in results:
            chunk_id = result.get("chunk_id", "unknown")
            text = result.get("text", "")

            verdict = self.verify_relevance(query, text)
            reasoning = self._build_reasoning(verdict, query, text)

            reflections.append(
                {
                    "chunk_id": chunk_id,
                    "verdict": verdict.value,
                    "reasoning": reasoning,
                }
            )

            if verdict >= threshold:
                filtered.append(result)

        total = len(results)
        removed = total - len(filtered)
        filter_rate = removed / total if total > 0 else 0.0

        logger.info(
            "Self-RAG filter: %d/%d results kept (filter rate %.1f%%).",
            len(filtered),
            total,
            filter_rate * 100,
        )

        return SelfRAGResult(
            original_results=results,
            filtered_results=filtered,
            reflections=reflections,
            filter_rate=filter_rate,
        )

    # ------------------------------------------------------------------
    # Fallback / mock mode
    # ------------------------------------------------------------------

    @staticmethod
    def _fallback_keyword_check(query: str, text: str) -> RelevanceVerdict:
        """Simple keyword-overlap heuristic used when no LLM is available.

        Tokenises both *query* and *text* into lowercase alphanumeric
        words, computes the fraction of query tokens present in the text
        and maps the overlap ratio to a verdict.

        Parameters
        ----------
        query:
            The user question.
        text:
            The chunk text.

        Returns
        -------
        RelevanceVerdict
        """
        query_tokens = set(re.findall(r"\w+", query.lower()))
        text_tokens = set(re.findall(r"\w+", text.lower()))

        if not query_tokens:
            return RelevanceVerdict.NOT_RELEVANT

        overlap = len(query_tokens & text_tokens) / len(query_tokens)

        if overlap >= 0.6:
            return RelevanceVerdict.RELEVANT
        if overlap >= 0.3:
            return RelevanceVerdict.PARTIALLY_RELEVANT
        return RelevanceVerdict.NOT_RELEVANT

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_verdict(response: str) -> RelevanceVerdict:
        """Extract a ``RelevanceVerdict`` from the LLM response string."""
        upper = response.strip().upper()
        # Try exact prefix match in order of specificity
        if upper.startswith("PARTIALLY_RELEVANT") or upper.startswith("PARTIALLY RELEVANT"):
            return RelevanceVerdict.PARTIALLY_RELEVANT
        if upper.startswith("NOT_RELEVANT") or upper.startswith("NOT RELEVANT"):
            return RelevanceVerdict.NOT_RELEVANT
        if upper.startswith("RELEVANT"):
            return RelevanceVerdict.RELEVANT

        # Fallback: search for the verdict anywhere in the response
        if "PARTIALLY_RELEVANT" in upper or "PARTIALLY RELEVANT" in upper:
            return RelevanceVerdict.PARTIALLY_RELEVANT
        if "NOT_RELEVANT" in upper or "NOT RELEVANT" in upper:
            return RelevanceVerdict.NOT_RELEVANT
        if "RELEVANT" in upper:
            return RelevanceVerdict.RELEVANT

        logger.warning(
            "Could not parse relevance verdict from LLM response: %s",
            response[:120],
        )
        return RelevanceVerdict.NOT_RELEVANT

    @staticmethod
    def _build_reasoning(
        verdict: RelevanceVerdict,
        query: str,
        text: str,
    ) -> str:
        """Build a short human-readable reasoning string.

        When the LLM is used, the reasoning is embedded in the LLM
        response itself; this helper produces a deterministic explanation
        for the keyword-fallback path.
        """
        query_tokens = set(re.findall(r"\w+", query.lower()))
        text_tokens = set(re.findall(r"\w+", text.lower()))
        shared = query_tokens & text_tokens
        overlap = len(shared) / len(query_tokens) if query_tokens else 0.0

        return (
            f"Verdict {verdict.value}: keyword overlap {overlap:.0%} "
            f"(shared tokens: {', '.join(sorted(shared)[:10]) or 'none'})."
        )
