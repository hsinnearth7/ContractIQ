"""Cypher-based knowledge graph retriever."""

from typing import Any

from contractiq.graph.neo4j_client import Neo4jClient


# Pre-built Cypher query templates
QUERIES = {
    "supplier_clauses": """
        MATCH (s:Supplier {name: $supplier_name})-[:HAS_CONTRACT]->(c:Contract)-[:HAS_CLAUSE]->(cl:Clause)
        RETURN s.name AS supplier, c.agreement_number AS contract,
               cl.clause_type AS clause_type, cl.title AS title, cl.text_summary AS summary
        ORDER BY cl.clause_type
    """,
    "supplier_contracts": """
        MATCH (s:Supplier {name: $supplier_name})-[:HAS_CONTRACT]->(c:Contract)
        RETURN s.name AS supplier, c.agreement_number AS contract,
               c.contract_type AS type, c.effective_date AS date, c.contract_value AS value
    """,
    "contract_details": """
        MATCH (c:Contract {agreement_number: $agreement_number})
        OPTIONAL MATCH (s:Supplier)-[:HAS_CONTRACT]->(c)
        OPTIONAL MATCH (c)-[:HAS_CLAUSE]->(cl:Clause)
        OPTIONAL MATCH (c)<-[:PARTIES_TO]-(p:Party)
        RETURN c, s.name AS supplier,
               collect(DISTINCT cl.title) AS clauses,
               collect(DISTINCT p.name) AS parties
    """,
    "all_suppliers": """
        MATCH (s:Supplier)
        OPTIONAL MATCH (s)-[:HAS_CONTRACT]->(c:Contract)
        RETURN s.name AS supplier, count(c) AS contract_count
        ORDER BY contract_count DESC
    """,
    "obligations": """
        MATCH (s:Supplier {name: $supplier_name})-[:HAS_CONTRACT]->(c:Contract)
              -[:HAS_CLAUSE]->(cl:Clause)-[:OBLIGATES]->(o:Obligation)
        RETURN s.name AS supplier, c.agreement_number AS contract,
               o.description AS obligation, o.due_date AS due_date, o.status AS status
    """,
    "related_contracts": """
        MATCH (c1:Contract {agreement_number: $agreement_number})<-[:HAS_CONTRACT]-(s:Supplier)
              -[:HAS_CONTRACT]->(c2:Contract)
        WHERE c1 <> c2
        RETURN s.name AS supplier, c2.agreement_number AS related_contract,
               c2.contract_type AS type, c2.contract_value AS value
    """,
    "graph_overview": """
        MATCH (n)
        WITH labels(n)[0] AS label, count(n) AS count
        RETURN label, count
        ORDER BY count DESC
    """,
}


class GraphRetriever:
    """Retrieves structured data from the knowledge graph using Cypher queries."""

    def __init__(self, client: Neo4jClient | None = None):
        self.client = client or Neo4jClient()

    def query(self, query_name: str, params: dict[str, Any] | None = None) -> list[dict]:
        """Run a named query from the pre-built templates.

        Args:
            query_name: Key in QUERIES dict.
            params: Cypher parameters.

        Returns:
            List of result records.
        """
        cypher = QUERIES.get(query_name)
        if not cypher:
            raise ValueError(f"Unknown query: {query_name}. Available: {list(QUERIES)}")
        return self.client.run_query(cypher, params or {})

    def custom_query(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict]:
        """Run a custom Cypher query."""
        return self.client.run_query(cypher, params or {})

    def get_supplier_context(self, supplier_name: str) -> str:
        """Get a text summary of graph context for a supplier."""
        contracts = self.query("supplier_contracts", {"supplier_name": supplier_name})
        clauses = self.query("supplier_clauses", {"supplier_name": supplier_name})

        lines = [f"Knowledge Graph context for {supplier_name}:"]

        if contracts:
            lines.append(f"\nContracts ({len(contracts)}):")
            for c in contracts:
                lines.append(f"  - {c['contract']} ({c.get('type','')}) Value: {c.get('value','N/A')}")

        if clauses:
            lines.append(f"\nClauses ({len(clauses)}):")
            for cl in clauses:
                lines.append(f"  - [{cl.get('clause_type','')}] {cl.get('title','')}")

        return "\n".join(lines)

    def get_contract_context(self, agreement_number: str) -> str:
        """Get a text summary of graph context for a contract."""
        details = self.query("contract_details", {"agreement_number": agreement_number})
        related = self.query("related_contracts", {"agreement_number": agreement_number})

        lines = [f"Knowledge Graph context for {agreement_number}:"]

        if details:
            d = details[0]
            lines.append(f"  Supplier: {d.get('supplier', 'N/A')}")
            lines.append(f"  Clauses: {', '.join(d.get('clauses', []))}")
            lines.append(f"  Parties: {', '.join(d.get('parties', []))}")

        if related:
            lines.append(f"\nRelated contracts ({len(related)}):")
            for r in related:
                lines.append(f"  - {r['related_contract']} ({r.get('type','')}) Value: {r.get('value','N/A')}")

        return "\n".join(lines)

    def get_all_nodes_edges(self) -> dict[str, Any]:
        """Get all nodes and edges for visualization."""
        nodes = self.client.run_query(
            "MATCH (n) RETURN id(n) AS id, labels(n)[0] AS label, properties(n) AS props"
        )
        edges = self.client.run_query(
            "MATCH (a)-[r]->(b) RETURN id(a) AS source, id(b) AS target, type(r) AS type"
        )
        return {"nodes": nodes, "edges": edges}
