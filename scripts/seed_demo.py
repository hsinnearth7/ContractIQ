"""CLI: One-click demo setup — generate contracts, build index, optionally build graph."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    print("=" * 60)
    print("ContractIQ - Demo Setup")
    print("=" * 60)

    # Step 1: Generate contracts
    print("\n[1/3] Generating synthetic contracts...")
    from contractiq.config import get_settings
    from contractiq.data.synthetic_generator import generate_contracts

    settings = get_settings()
    files = generate_contracts(settings.sample_contracts_dir, count=20)
    print(f"  Generated {len(files)} contracts.")

    # Step 2: Build index
    print("\n[2/3] Building search index...")
    from contractiq.indexing.index_builder import IndexBuilder

    builder = IndexBuilder()
    results = builder.index_directory(
        settings.sample_contracts_dir,
        extract_meta=True,
        chunk_strategy="clause_aware",
    )
    total_chunks = sum(r["chunks"] for r in results)
    print(f"  Indexed {len(results)} documents with {total_chunks} chunks.")

    # Step 3: Build graph (optional - requires Neo4j)
    print("\n[3/3] Building knowledge graph...")
    try:
        from contractiq.graph.neo4j_client import Neo4jClient
        client = Neo4jClient()
        if client.verify_connectivity():
            from contractiq.graph.graph_builder import GraphBuilder
            graph_builder = GraphBuilder(client)
            graph_builder.init_schema()

            for f in sorted(Path(settings.sample_contracts_dir).iterdir()):
                if f.suffix.lower() in (".pdf", ".docx"):
                    try:
                        doc = builder.parse_file(f)
                        from contractiq.parsing.metadata_extractor import extract_metadata
                        doc.metadata = extract_metadata(doc.raw_text)
                        graph_builder.build_from_document(doc)
                    except Exception:
                        pass

            stats = client.get_stats()
            print(f"  Graph built: {stats}")
            client.close()
        else:
            print("  Neo4j not available — skipping graph build.")
    except Exception as e:
        print(f"  Neo4j not available — skipping graph build. ({e})")

    # Done
    print("\n" + "=" * 60)
    print("Demo setup complete!")
    print(f"\nTo start the app:")
    print(f"  streamlit run contractiq/ui/app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
