"""Complete retrieval pipeline: rewrite → filter → retrieve → rerank."""

from typing import Any

from contractiq.config import get_settings
from contractiq.retrieval.hybrid_retriever import HybridRetriever
from contractiq.retrieval.reranker import CrossEncoderReranker
from contractiq.retrieval.query_rewriter import QueryRewriter
from contractiq.retrieval.multi_query import MultiQueryDecomposer
from contractiq.retrieval.metadata_filter import MetadataFilter
from contractiq.retrieval.hybrid_retriever import reciprocal_rank_fusion


class RetrievalPipeline:
    """End-to-end retrieval pipeline orchestrator.

    Pipeline:
    1. (Optional) Query rewriting for better retrieval
    2. (Optional) Multi-query decomposition for complex questions
    3. Metadata filter extraction from query intent
    4. Hybrid retrieval (vector + BM25 + RRF)
    5. Cross-encoder re-ranking
    """

    def __init__(
        self,
        retriever: HybridRetriever | None = None,
        reranker: CrossEncoderReranker | None = None,
        query_rewriter: QueryRewriter | None = None,
        multi_query: MultiQueryDecomposer | None = None,
        metadata_filter: MetadataFilter | None = None,
    ):
        self.retriever = retriever or HybridRetriever()
        self.reranker = reranker or CrossEncoderReranker()
        self.query_rewriter = query_rewriter or QueryRewriter()
        self.multi_query = multi_query or MultiQueryDecomposer()
        self.metadata_filter = metadata_filter or MetadataFilter()

    def retrieve(
        self,
        query: str,
        use_rewrite: bool = True,
        use_multi_query: bool = True,
        use_rerank: bool = True,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        """Run the full retrieval pipeline.

        Args:
            query: User query.
            use_rewrite: Enable query rewriting.
            use_multi_query: Enable multi-query decomposition.
            use_rerank: Enable cross-encoder reranking.
            top_k: Final number of results.

        Returns:
            Dict with keys: results, original_query, rewritten_query,
            sub_queries, metadata_filter.
        """
        settings = get_settings()
        final_k = top_k or settings.rerank_top_k

        # 1. Extract metadata filter
        where_filter = self.metadata_filter.parse(query)

        # 2. Query rewriting
        rewritten = self.query_rewriter.rewrite(query) if use_rewrite else query

        # 3. Multi-query decomposition
        if use_multi_query and self.multi_query.is_complex(query):
            sub_queries = self.multi_query.decompose(query)
        else:
            sub_queries = [rewritten]

        # 4. Retrieve for each sub-query and fuse
        all_result_lists = []
        for sq in sub_queries:
            results = self.retriever.retrieve(
                sq, top_k=settings.retrieval_top_k, where=where_filter
            )
            all_result_lists.append(results)

        # Fuse across sub-queries if multiple
        if len(all_result_lists) > 1:
            fused = reciprocal_rank_fusion(all_result_lists)
        else:
            fused = all_result_lists[0]

        # 5. Re-rank
        if use_rerank and fused:
            final_results = self.reranker.rerank(query, fused, top_k=final_k)
        else:
            final_results = fused[:final_k]

        return {
            "results": final_results,
            "original_query": query,
            "rewritten_query": rewritten,
            "sub_queries": sub_queries,
            "metadata_filter": where_filter,
        }
