# ADR: Why Self-RAG Was Not Included in the Recommended Pipeline

**Status:** Accepted
**Date:** 2026-03-02
**Decision Maker:** Ablation Study Framework (v8.0)

## Context

Self-RAG (Self-Reflective Retrieval-Augmented Generation) adds an LLM-based relevance verification step between retrieval and generation. Each retrieved chunk is evaluated for relevance before being passed to the answer generation stage.

During the v8.0 ablation study, we compared 6 progressive pipeline configurations:

| Layer | Configuration | Components Added |
|-------|--------------|-----------------|
| 1 | BM25_ONLY | BM25 keyword search |
| 2 | DENSE_ONLY | Vector embedding search |
| 3 | HYBRID | BM25 + Dense + RRF fusion |
| 4 | HYBRID_RERANKER | + Cross-encoder reranking |
| 5 | HYBRID_RERANKER_QD | + Query decomposition |
| 6 | FULL_WITH_SELF_RAG | + Self-RAG filtering |

## Decision

The recommended production pipeline is **HYBRID_RERANKER_QD** (Layer 5), excluding Self-RAG.

## Rationale

### 1. Marginal Accuracy Gain

The Wilcoxon signed-rank test between Layer 5 (HYBRID_RERANKER_QD) and Layer 6 (FULL_WITH_SELF_RAG) showed:
- The accuracy improvement from Self-RAG is statistically insignificant (p > 0.05)
- The cross-encoder reranker already filters out most irrelevant chunks
- Query decomposition handles multi-hop questions effectively

### 2. Latency Cost

Self-RAG requires an additional LLM call per retrieved chunk:
- With `top_k=5` chunks, this adds 5 extra LLM calls per query
- Estimated latency increase: 2-5 seconds per query
- The efficiency ratio (accuracy / (1 + latency)) drops significantly

### 3. Cost Implications

Each Self-RAG verification call consumes tokens:
- ~200 tokens per chunk (prompt + response)
- 5 chunks x 200 tokens = 1,000 extra tokens per query
- At scale (1000 queries/day), this adds ~$15-30/day in API costs

### 4. Occam's Razor (Elbow Analysis)

The `find_elbow()` analysis identifies Layer 5 as the optimal complexity point:
- Maximum accuracy-per-unit-latency ratio
- Adding Self-RAG crosses the diminishing returns threshold

## Consequences

- Self-RAG remains implemented in `contractiq/retrieval/self_rag.py` for research and optional use
- The ablation framework can re-evaluate if future LLM models reduce Self-RAG latency
- Users can enable Self-RAG via the ablation configuration for specific use cases
- The decision is data-driven and reproducible via `contractiq/evaluation/ablation.py`

## Alternatives Considered

1. **Lightweight Self-RAG (keyword-based):** The fallback keyword heuristic is fast but less accurate than the cross-encoder reranker already in the pipeline.
2. **Batched Self-RAG:** Sending all chunks in a single LLM call reduces latency but changes the evaluation semantics.
3. **Cached Self-RAG:** Caching relevance judgments reduces cost but introduces staleness for dynamic queries.

## References

- Asai et al. (2023). "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection." arXiv:2310.11511
- ContractIQ Ablation Study: `contractiq/evaluation/ablation.py`
- Golden Dataset: `contractiq/evaluation/golden_dataset.py` (55 questions, 3 difficulty levels)
