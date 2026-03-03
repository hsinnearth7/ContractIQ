"""CLI: Build vector and BM25 indices from contract documents."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contractiq.config import get_settings
from contractiq.indexing.index_builder import IndexBuilder


def main():
    settings = get_settings()
    contracts_dir = settings.sample_contracts_dir

    print(f"ContractIQ - Index Builder")
    print(f"Source directory: {contracts_dir}")
    print(f"Chunk strategy: {settings.chunk_strategy}")
    print(f"Chunk size: {settings.chunk_size}")
    print("-" * 50)

    if not Path(contracts_dir).exists():
        print(f"Error: Directory not found: {contracts_dir}")
        print("Run `python scripts/generate_contracts.py` first.")
        sys.exit(1)

    builder = IndexBuilder()
    results = builder.index_directory(
        contracts_dir,
        extract_meta=True,
        chunk_strategy=settings.chunk_strategy,
    )

    print(f"\nIndex Summary:")
    print(f"  ChromaDB chunks: {builder.chroma.count}")
    print(f"  BM25 documents: {builder.bm25.count}")
    print(f"  Embedding tokens: {builder.embedder.total_tokens_used:,}")


if __name__ == "__main__":
    main()
