"""Cross-contract comparison chain."""

import json
from typing import Any

from contractiq.generation.llm_client import LLMClient
from contractiq.generation.prompts import COMPARISON_SYSTEM_PROMPT, COMPARISON_USER_PROMPT
from contractiq.generation.response_models import (
    ComparisonResult,
    ComparisonDimension,
    SourceReference,
)
from contractiq.retrieval.retrieval_pipeline import RetrievalPipeline


DEFAULT_DIMENSIONS = [
    "Payment Terms",
    "Termination Conditions",
    "Liability Limits",
    "Warranty Period",
    "Confidentiality Duration",
    "Service Level (if applicable)",
]


class ComparisonChain:
    """Compares contract terms across multiple suppliers."""

    def __init__(
        self,
        llm: LLMClient | None = None,
        pipeline: RetrievalPipeline | None = None,
    ):
        self.llm = llm or LLMClient()
        self.pipeline = pipeline or RetrievalPipeline()

    def compare(
        self,
        suppliers: list[str],
        dimensions: list[str] | None = None,
    ) -> ComparisonResult:
        """Compare suppliers across specified dimensions.

        Args:
            suppliers: List of supplier names to compare.
            dimensions: Comparison dimensions (uses defaults if not specified).

        Returns:
            ComparisonResult with structured comparison.
        """
        dimensions = dimensions or DEFAULT_DIMENSIONS

        # Retrieve context for each supplier
        all_results: list[dict[str, Any]] = []
        for supplier in suppliers:
            query = f"Contract terms for {supplier}: {', '.join(dimensions)}"
            retrieval = self.pipeline.retrieve(query, use_multi_query=False)
            all_results.extend(retrieval["results"])

        if not all_results:
            return ComparisonResult(
                question=f"Compare {', '.join(suppliers)}",
                suppliers=suppliers,
                summary="No relevant contract data found for the specified suppliers.",
            )

        # Format context
        context_parts = []
        sources = []
        for i, r in enumerate(all_results, 1):
            doc_id = r.get("metadata", {}).get("document_id", "unknown")
            supplier = r.get("metadata", {}).get("supplier_name", "")
            context_parts.append(f"[Source {i}] Supplier: {supplier} | Doc: {doc_id}\n{r['text']}")
            sources.append(SourceReference(
                source_id=i,
                chunk_id=r.get("chunk_id", ""),
                document_id=doc_id,
                text_excerpt=r["text"][:150],
            ))

        context = "\n\n---\n\n".join(context_parts)

        # Generate comparison
        raw = self.llm.chat(
            COMPARISON_SYSTEM_PROMPT,
            COMPARISON_USER_PROMPT.format(
                context=context,
                suppliers=", ".join(suppliers),
                dimensions=", ".join(dimensions),
            ),
            max_tokens=3000,
        )

        # Parse comparison into structured dimensions
        parsed_dimensions = self._parse_dimensions(raw, suppliers, dimensions)

        return ComparisonResult(
            question=f"Compare {', '.join(suppliers)} across {', '.join(dimensions)}",
            suppliers=suppliers,
            dimensions=parsed_dimensions,
            summary=raw,
            sources=sources,
        )

    def _parse_dimensions(
        self,
        raw_text: str,
        suppliers: list[str],
        dimensions: list[str],
    ) -> list[ComparisonDimension]:
        """Attempt to parse LLM output into structured dimensions."""
        # Ask LLM to structure the comparison as JSON
        prompt = f"""\
Convert this comparison into a JSON array. Each element has:
- "dimension": dimension name
- "values": object mapping supplier names to their values
- "analysis": brief analysis

Suppliers: {suppliers}
Dimensions: {dimensions}

Text:
{raw_text}

Return only valid JSON array."""

        try:
            structured = self.llm.chat("Return only valid JSON.", prompt)
            data = json.loads(structured)
            if isinstance(data, list):
                return [
                    ComparisonDimension(
                        dimension=d.get("dimension", ""),
                        values=d.get("values", {}),
                        analysis=d.get("analysis", ""),
                    )
                    for d in data
                ]
        except (json.JSONDecodeError, Exception):
            pass

        # Fallback: return raw text as a single dimension
        return [
            ComparisonDimension(
                dimension="Overall Comparison",
                values={s: "See summary" for s in suppliers},
                analysis=raw_text[:500],
            )
        ]
