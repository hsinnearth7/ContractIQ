"""Question-answering chain with source citations."""

import re
from typing import Any

from contractiq.generation.llm_client import LLMClient
from contractiq.generation.prompts import QA_SYSTEM_PROMPT, QA_USER_PROMPT
from contractiq.generation.response_models import QAResponse, SourceReference
from contractiq.retrieval.retrieval_pipeline import RetrievalPipeline


def _format_context(results: list[dict[str, Any]]) -> tuple[str, list[SourceReference]]:
    """Format retrieval results into context string with source refs."""
    context_parts = []
    sources = []

    for i, r in enumerate(results, 1):
        doc_id = r.get("metadata", {}).get("document_id", "unknown")
        section = r.get("metadata", {}).get("section_title", "")
        supplier = r.get("metadata", {}).get("supplier_name", "")

        header = f"[Source {i}] Document: {doc_id}"
        if supplier:
            header += f" | Supplier: {supplier}"
        if section:
            header += f" | Section: {section}"

        context_parts.append(f"{header}\n{r['text']}")

        sources.append(SourceReference(
            source_id=i,
            chunk_id=r.get("chunk_id", ""),
            document_id=doc_id,
            text_excerpt=r["text"][:200],
        ))

    return "\n\n---\n\n".join(context_parts), sources


def _extract_confidence(answer: str) -> tuple[str, float]:
    """Extract confidence from answer text."""
    confidence = 0.8  # default
    patterns = [
        r"[Cc]onfidence[:\s]*([01]?\.\d+)",
        r"([01]?\.\d+)\s*confidence",
    ]
    for p in patterns:
        match = re.search(p, answer)
        if match:
            try:
                confidence = float(match.group(1))
                # Remove confidence statement from answer
                answer = re.sub(r"\n*[Cc]onfidence.*$", "", answer, flags=re.MULTILINE).strip()
            except ValueError:
                pass
            break
    return answer, confidence


class QAChain:
    """Question-answering chain with retrieval and source citations."""

    def __init__(
        self,
        llm: LLMClient | None = None,
        pipeline: RetrievalPipeline | None = None,
    ):
        self.llm = llm or LLMClient()
        self.pipeline = pipeline or RetrievalPipeline()

    def answer(
        self,
        question: str,
        use_rewrite: bool = True,
        use_multi_query: bool = True,
        use_rerank: bool = True,
    ) -> QAResponse:
        """Answer a question using RAG pipeline.

        Args:
            question: User's question.
            use_rewrite: Enable query rewriting.
            use_multi_query: Enable multi-query decomposition.
            use_rerank: Enable cross-encoder reranking.

        Returns:
            QAResponse with answer and source citations.
        """
        # Retrieve relevant chunks
        retrieval = self.pipeline.retrieve(
            question,
            use_rewrite=use_rewrite,
            use_multi_query=use_multi_query,
            use_rerank=use_rerank,
        )

        results = retrieval["results"]
        if not results:
            return QAResponse(
                question=question,
                answer="I couldn't find any relevant information in the indexed contracts.",
                confidence=0.0,
            )

        # Format context
        context, sources = _format_context(results)

        # Generate answer
        raw_answer = self.llm.chat(
            QA_SYSTEM_PROMPT,
            QA_USER_PROMPT.format(context=context, question=question),
        )

        answer, confidence = _extract_confidence(raw_answer)

        return QAResponse(
            question=question,
            answer=answer,
            sources=sources,
            confidence=confidence,
        )
