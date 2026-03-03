"""CLI: Build Neo4j knowledge graph from parsed contracts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contractiq.config import get_settings
from contractiq.graph.neo4j_client import Neo4jClient
from contractiq.graph.graph_builder import GraphBuilder
from contractiq.indexing.index_builder import IndexBuilder


def main():
    settings = get_settings()
    contracts_dir = settings.sample_contracts_dir

    print(f"ContractIQ - Knowledge Graph Builder")
    print(f"Source directory: {contracts_dir}")
    print(f"Neo4j URI: {settings.neo4j_uri}")
    print("-" * 50)

    # Verify Neo4j connectivity
    client = Neo4jClient()
    if not client.verify_connectivity():
        print("Error: Cannot connect to Neo4j.")
        print(f"Please ensure Neo4j is running at {settings.neo4j_uri}")
        sys.exit(1)

    print("Neo4j connected.")

    # Initialize schema
    graph_builder = GraphBuilder(client)
    graph_builder.init_schema()
    print("Schema initialized.")

    # Parse and build graph
    file_builder = IndexBuilder()
    contract_files = sorted(
        Path(contracts_dir).glob("*.pdf")
    ) + sorted(
        Path(contracts_dir).glob("*.docx")
    )

    if not contract_files:
        print(f"No contract files found in {contracts_dir}")
        print("Run `python scripts/generate_contracts.py` first.")
        sys.exit(1)

    for f in contract_files:
        print(f"\nProcessing: {f.name}")
        try:
            doc = file_builder.parse_file(f)
            from contractiq.parsing.metadata_extractor import extract_metadata
            doc.metadata = extract_metadata(doc.raw_text)

            stats = graph_builder.build_from_document(doc)
            print(f"  Nodes: {stats['nodes']}, Relationships: {stats['relationships']}")
        except Exception as e:
            print(f"  Error: {e}")

    # Print final stats
    graph_stats = client.get_stats()
    print(f"\nGraph Statistics:")
    for label, count in graph_stats.items():
        print(f"  {label}: {count}")

    client.close()


if __name__ == "__main__":
    main()
