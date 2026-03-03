"""Build knowledge graph from contract documents using LLMGraphTransformer."""

from typing import Any

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer

from contractiq.config import get_settings
from contractiq.graph.neo4j_client import Neo4jClient
from contractiq.graph import schema as S
from contractiq.parsing.models import ParsedDocument


class GraphBuilder:
    """Builds a knowledge graph in Neo4j from contract documents."""

    def __init__(self, neo4j_client: Neo4jClient | None = None):
        settings = get_settings()
        self.client = neo4j_client or Neo4jClient()

        llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )

        self.transformer = LLMGraphTransformer(
            llm=llm,
            allowed_nodes=[
                S.SUPPLIER, S.BUYER, S.CONTRACT, S.CLAUSE,
                S.OBLIGATION, S.PARTY,
            ],
            allowed_relationships=[
                S.SUPPLIES_TO, S.HAS_CONTRACT, S.HAS_CLAUSE,
                S.OBLIGATES, S.SIGNED_BY, S.PARTIES_TO,
            ],
        )

    def build_from_document(self, doc: ParsedDocument) -> dict[str, int]:
        """Extract entities and relationships from a parsed document and store in Neo4j.

        Args:
            doc: Parsed contract document.

        Returns:
            Dict with counts of nodes and relationships created.
        """
        # First, create the core contract node from metadata
        self._create_contract_node(doc)

        # Split text into chunks for LLMGraphTransformer
        text = doc.raw_text
        chunk_size = 4000
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        total_nodes = 0
        total_rels = 0

        for chunk in chunks:
            lc_doc = Document(
                page_content=chunk,
                metadata={"source": doc.file_name},
            )

            try:
                graph_docs = self.transformer.convert_to_graph_documents([lc_doc])

                for gd in graph_docs:
                    for node in gd.nodes:
                        self._merge_node(node.type, node.id, node.properties)
                        total_nodes += 1

                    for rel in gd.relationships:
                        self._merge_relationship(
                            rel.source.type, rel.source.id,
                            rel.type,
                            rel.target.type, rel.target.id,
                            rel.properties,
                        )
                        total_rels += 1
            except Exception as e:
                print(f"  Warning: graph extraction error for chunk: {e}")

        return {"nodes": total_nodes, "relationships": total_rels}

    def _create_contract_node(self, doc: ParsedDocument) -> None:
        """Create core contract node from document metadata."""
        m = doc.metadata
        params: dict[str, Any] = {
            "agreement_number": m.agreement_number or doc.file_name,
            "contract_type": m.contract_type.value,
            "effective_date": m.effective_date,
            "contract_value": m.contract_value,
            "supplier_name": m.supplier_name,
            "buyer_name": m.buyer_name,
        }

        # MERGE Supplier
        if m.supplier_name:
            self.client.run_write(
                "MERGE (s:Supplier {name: $name})",
                {"name": m.supplier_name},
            )

        # MERGE Buyer
        if m.buyer_name:
            self.client.run_write(
                "MERGE (b:Buyer {name: $name})",
                {"name": m.buyer_name},
            )

        # MERGE Contract
        self.client.run_write(
            """
            MERGE (c:Contract {agreement_number: $agreement_number})
            SET c.contract_type = $contract_type,
                c.effective_date = $effective_date,
                c.contract_value = $contract_value
            """,
            params,
        )

        # Link Supplier → Contract
        if m.supplier_name:
            self.client.run_write(
                """
                MATCH (s:Supplier {name: $supplier_name})
                MATCH (c:Contract {agreement_number: $agreement_number})
                MERGE (s)-[:HAS_CONTRACT]->(c)
                """,
                params,
            )

        # Link Supplier → Buyer
        if m.supplier_name and m.buyer_name:
            self.client.run_write(
                """
                MATCH (s:Supplier {name: $supplier_name})
                MATCH (b:Buyer {name: $buyer_name})
                MERGE (s)-[:SUPPLIES_TO]->(b)
                """,
                params,
            )

    def _merge_node(self, label: str, node_id: str, properties: dict) -> None:
        """MERGE a node with deduplication."""
        props = {k: v for k, v in properties.items() if v is not None}
        set_clause = ", ".join(f"n.{k} = ${k}" for k in props)
        set_stmt = f"SET {set_clause}" if set_clause else ""

        cypher = f"MERGE (n:{label} {{id: $node_id}}) {set_stmt}"
        self.client.run_write(cypher, {"node_id": node_id, **props})

    def _merge_relationship(
        self,
        src_label: str, src_id: str,
        rel_type: str,
        tgt_label: str, tgt_id: str,
        properties: dict,
    ) -> None:
        """MERGE a relationship."""
        cypher = f"""
        MERGE (a:{src_label} {{id: $src_id}})
        MERGE (b:{tgt_label} {{id: $tgt_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        """
        self.client.run_write(cypher, {"src_id": src_id, "tgt_id": tgt_id})

    def init_schema(self) -> None:
        """Initialize graph constraints and indexes."""
        self.client.init_schema()
