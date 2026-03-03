"""Knowledge Graph visualization page using streamlit-agraph."""

import streamlit as st

st.set_page_config(page_title="ContractIQ - Knowledge Graph", page_icon="🕸️", layout="wide")
st.title("🕸️ Knowledge Graph Explorer")

# Check Neo4j connectivity
try:
    from contractiq.graph.neo4j_client import Neo4jClient
    client = Neo4jClient()
    connected = client.verify_connectivity()
except Exception:
    connected = False

if not connected:
    st.warning(
        "Neo4j is not available. Please ensure Neo4j is running at the configured URI.\n\n"
        "To start Neo4j locally:\n"
        "```\ndocker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest\n```"
    )
    st.stop()

# Sidebar: graph stats
with st.sidebar:
    st.header("Graph Statistics")
    stats = client.get_stats()
    for label, count in stats.items():
        prefix = "🔗 " if label.startswith("rel:") else "🔵 "
        st.metric(prefix + label, count)

# Graph visualization
from contractiq.graph.graph_retriever import GraphRetriever

retriever = GraphRetriever(client)

st.subheader("Interactive Graph")

try:
    from streamlit_agraph import agraph, Node, Edge, Config

    graph_data = retriever.get_all_nodes_edges()

    # Color map for node types
    colors = {
        "Supplier": "#FF6B6B",
        "Buyer": "#4ECDC4",
        "Contract": "#45B7D1",
        "Clause": "#96CEB4",
        "Obligation": "#FFEAA7",
        "Party": "#DDA0DD",
    }

    nodes = []
    for n in graph_data["nodes"]:
        label = n.get("label", "Unknown")
        props = n.get("props", {})
        display_name = props.get("name", props.get("agreement_number", props.get("id", str(n["id"]))))
        nodes.append(Node(
            id=str(n["id"]),
            label=str(display_name)[:30],
            size=25 if label in ("Supplier", "Contract") else 15,
            color=colors.get(label, "#999999"),
            title=f"{label}: {display_name}",
        ))

    edges = []
    for e in graph_data["edges"]:
        edges.append(Edge(
            source=str(e["source"]),
            target=str(e["target"]),
            label=e["type"],
        ))

    config = Config(
        width=1200,
        height=600,
        directed=True,
        physics=True,
        hierarchical=False,
    )

    agraph(nodes=nodes, edges=edges, config=config)

except ImportError:
    st.info("Install `streamlit-agraph` for interactive visualization: `pip install streamlit-agraph`")

# Query interface
st.divider()
st.subheader("Graph Queries")

query_type = st.selectbox("Pre-built Queries", [
    "all_suppliers",
    "supplier_contracts",
    "supplier_clauses",
    "graph_overview",
])

params = {}
if query_type in ("supplier_contracts", "supplier_clauses", "obligations"):
    supplier_name = st.text_input("Supplier Name")
    if supplier_name:
        params["supplier_name"] = supplier_name

if st.button("🔍 Run Query"):
    try:
        results = retriever.query(query_type, params)
        if results:
            st.dataframe(results, use_container_width=True)
        else:
            st.info("No results found.")
    except Exception as e:
        st.error(f"Query error: {e}")

# Custom Cypher
with st.expander("Custom Cypher Query"):
    cypher = st.text_area("Enter Cypher query", "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count")
    if st.button("Execute Cypher"):
        try:
            results = retriever.custom_query(cypher)
            st.dataframe(results, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

client.close()
