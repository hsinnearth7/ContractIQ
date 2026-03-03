"""Graph-enhanced RAG: combines vector retrieval with knowledge graph context."""

from typing import Any

from contractiq.generation.llm_client import LLMClient
from contractiq.generation.prompts import GRAPH_QA_SYSTEM_PROMPT, GRAPH_QA_USER_PROMPT
from contractiq.generation.response_models import QAResponse, SourceReference
from contractiq.retrieval.retrieval_pipeline import RetrievalPipeline
from contractiq.graph.graph_retriever import GraphRetriever


class GraphEnhancedRAG:
    """Combines vector retrieval results with graph neighborhood context."""

    def __init__(
        self,
        llm: LLMClient | None = None,
        pipeline: RetrievalPipeline | None = None,
        graph_retriever: GraphRetriever | None = None,
    ):
        self.llm = llm or LLMClient()
        self.pipeline = pipeline or RetrievalPipeline()
        self.graph_retriever = graph_retriever or GraphRetriever()

    def answer(self, question: str) -> QAResponse:
        """Answer a question using both vector search and knowledge graph.

        Args:
            question: User's question.

        Returns:
            QAResponse with graph-enhanced answer.
        """
        # 1. Standard vector retrieval
        retrieval = self.pipeline.retrieve(question)
        results = retrieval["results"]

        # 2. Extract entities from results to query graph
        suppliers = set()
        contracts = set()
        for r in results:
            meta = r.get("metadata", {})
            if meta.get("supplier_name"):
                suppliers.add(meta["supplier_name"])
            if meta.get("agreement_number"):
                contracts.add(meta["agreement_number"])

        # 3. Get graph context for related entities
        graph_contexts = []
        for supplier in list(suppliers)[:3]:
            try:
                ctx = self.graph_retriever.get_supplier_context(supplier)
                if ctx:
                    graph_contexts.append(ctx)
            except Exception:
                pass

        for contract in list(contracts)[:3]:
            try:
                ctx = self.graph_retriever.get_contract_context(contract)
                if ctx:
                    graph_contexts.append(ctx)
            except Exception:
                pass

        # 4. Format contexts
        doc_context_parts = []
        sources = []
        for i, r in enumerate(results, 1):
            doc_id = r.get("metadata", {}).get("document_id", "unknown")
            supplier = r.get("metadata", {}).get("supplier_name", "")
            doc_context_parts.append(
                f"[Source {i}] Doc: {doc_id} | Supplier: {supplier}\n{r['text']}"
            )
            sources.append(SourceReference(
                source_id=i,
                chunk_id=r.get("chunk_id", ""),
                document_id=doc_id,
                text_excerpt=r["text"][:200],
            ))

        document_context = "\n\n---\n\n".join(doc_context_parts)
        graph_context = "\n\n".join(graph_contexts) if graph_contexts else "No graph context available."

        # 5. Generate answer with both contexts
        raw_answer = self.llm.chat(
            GRAPH_QA_SYSTEM_PROMPT,
            GRAPH_QA_USER_PROMPT.format(
                document_context=document_context,
                graph_context=graph_context,
                question=question,
            ),
        )

        return QAResponse(
            question=question,
            answer=raw_answer,
            sources=sources,
            confidence=0.85,
        )
