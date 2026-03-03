"""IndexBuilder: orchestrates parse → chunk → embed → store pipeline."""

from pathlib import Path

from tqdm import tqdm

from contractiq.config import get_settings
from contractiq.parsing import parse_pdf, parse_docx, chunk_document, extract_metadata
from contractiq.parsing.models import ParsedDocument, DocumentChunk
from contractiq.indexing.embedder import OpenAIEmbedder
from contractiq.indexing.chroma_store import ChromaStore
from contractiq.indexing.bm25_store import BM25Store


class IndexBuilder:
    """Orchestrates the full document indexing pipeline.

    Pipeline: parse file → extract metadata → chunk → embed → store (vector + BM25).
    """

    def __init__(
        self,
        embedder: OpenAIEmbedder | None = None,
        chroma_store: ChromaStore | None = None,
        bm25_store: BM25Store | None = None,
    ):
        self.embedder = embedder or OpenAIEmbedder()
        self.chroma = chroma_store or ChromaStore()
        self.bm25 = bm25_store or BM25Store()
        self._settings = get_settings()

    def parse_file(self, file_path: str | Path) -> ParsedDocument:
        """Parse a single file based on extension."""
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            return parse_pdf(file_path)
        elif ext in (".docx", ".doc"):
            return parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def index_document(
        self,
        file_path: str | Path,
        extract_meta: bool = True,
        chunk_strategy: str | None = None,
    ) -> dict:
        """Index a single document through the full pipeline.

        Args:
            file_path: Path to PDF or DOCX file.
            extract_meta: Whether to use GPT-4o for metadata extraction.
            chunk_strategy: Override chunking strategy.

        Returns:
            Dict with indexing stats.
        """
        file_path = Path(file_path)
        strategy = chunk_strategy or self._settings.chunk_strategy

        # 1. Parse
        doc = self.parse_file(file_path)

        # 2. Extract metadata
        if extract_meta and doc.raw_text:
            doc.metadata = extract_metadata(doc.raw_text)

        # 3. Chunk
        chunks = chunk_document(
            doc,
            strategy=strategy,
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
        )

        if not chunks:
            return {"file": file_path.name, "chunks": 0, "status": "no_chunks"}

        # 4. Embed
        texts = [c.text for c in chunks]
        embeddings = self.embedder.embed_texts(texts)

        # 5. Store in ChromaDB
        self.chroma.add(chunks, embeddings)

        # 6. Store in BM25
        self.bm25.add(chunks)

        return {
            "file": file_path.name,
            "chunks": len(chunks),
            "strategy": strategy,
            "supplier": doc.metadata.supplier_name,
            "contract_type": doc.metadata.contract_type.value,
            "status": "indexed",
        }

    def index_directory(
        self,
        directory: str | Path,
        extract_meta: bool = True,
        chunk_strategy: str | None = None,
    ) -> list[dict]:
        """Index all PDF/DOCX files in a directory.

        Returns:
            List of indexing stats per file.
        """
        directory = Path(directory)
        files = sorted(
            [f for f in directory.iterdir()
             if f.suffix.lower() in (".pdf", ".docx", ".doc")]
        )

        results = []
        for f in tqdm(files, desc="Indexing documents"):
            try:
                result = self.index_document(
                    f, extract_meta=extract_meta, chunk_strategy=chunk_strategy
                )
                results.append(result)
                print(f"  ✓ {result['file']}: {result['chunks']} chunks ({result['status']})")
            except Exception as e:
                results.append({"file": f.name, "chunks": 0, "status": f"error: {e}"})
                print(f"  ✗ {f.name}: {e}")

        print(f"\nTotal: {sum(r['chunks'] for r in results)} chunks from {len(results)} files")
        print(f"Embedding tokens used: {self.embedder.total_tokens_used:,}")
        return results

    def delete_document(self, document_id: str) -> None:
        """Remove a document from all indices."""
        self.chroma.delete_by_document(document_id)
        self.bm25.delete_by_document(document_id)

    def reset_all(self) -> None:
        """Clear all indices."""
        self.chroma.reset()
        self.bm25.reset()
