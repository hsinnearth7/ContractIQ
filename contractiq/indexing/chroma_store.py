"""ChromaDB vector store for contract chunks."""

from pathlib import Path
from typing import Any

import chromadb

from contractiq.config import get_settings
from contractiq.parsing.models import DocumentChunk


class ChromaStore:
    """ChromaDB-backed vector store with metadata filtering."""

    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str | None = None,
    ):
        settings = get_settings()
        self._persist_dir = persist_dir or settings.chroma_persist_dir
        self._collection_name = collection_name or settings.chroma_collection_name

        Path(self._persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=self._persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def count(self) -> int:
        return self._collection.count()

    def add(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Add chunks with their embeddings to the store."""
        if not chunks:
            return

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [c.to_vector_metadata() for c in chunks]

        # ChromaDB requires string/int/float/bool metadata values
        clean_metas = []
        for m in metadatas:
            clean = {}
            for k, v in m.items():
                if isinstance(v, (str, int, float, bool)):
                    clean[k] = v
                elif v is not None:
                    clean[k] = str(v)
            clean_metas.append(clean)

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=clean_metas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 20,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar chunks.

        Returns:
            List of dicts with keys: chunk_id, text, score, metadata.
        """
        kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = self._collection.query(**kwargs)

        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "score": 1.0 - results["distances"][0][i],  # cosine distance to similarity
                "metadata": results["metadatas"][0][i],
            })
        return output

    def delete_by_document(self, document_id: str) -> None:
        """Delete all chunks belonging to a document."""
        self._collection.delete(where={"document_id": document_id})

    def list_documents(self) -> list[str]:
        """List unique document IDs in the store."""
        result = self._collection.get(include=["metadatas"])
        doc_ids = set()
        for m in result["metadatas"]:
            if "document_id" in m:
                doc_ids.add(m["document_id"])
        return sorted(doc_ids)

    def reset(self) -> None:
        """Delete and recreate the collection."""
        self._client.delete_collection(self._collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
