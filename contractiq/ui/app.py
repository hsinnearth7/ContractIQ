"""ContractIQ - Streamlit main application entry point."""

import streamlit as st

st.set_page_config(
    page_title="ContractIQ",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📄 ContractIQ")
st.subheader("Supplier Contract RAG Intelligence Platform")

st.markdown("""
Welcome to **ContractIQ** — an AI-powered platform for analyzing supplier contracts.

### Features

| Feature | Description |
|---------|-------------|
| **Chat Q&A** | Ask questions about your contracts with source citations |
| **Document Upload** | Upload and index PDF/DOCX contracts |
| **Cross-Contract Comparison** | Compare terms across multiple suppliers |
| **Compliance Dashboard** | Automated mandatory clause verification |
| **Knowledge Graph** | Visual exploration of contract relationships |
| **RAG Evaluation** | RAGAS metrics for retrieval quality |

### Getting Started

1. Navigate to **Upload** to index your contracts
2. Use **Chat** to ask questions about indexed contracts
3. Run **Compliance** checks to identify missing clauses
4. Explore relationships in the **Knowledge Graph**

---
*Powered by GPT-4o + ChromaDB + Neo4j + LangChain*
""")

# Sidebar: System status
with st.sidebar:
    st.header("System Status")

    try:
        from contractiq.indexing.chroma_store import ChromaStore
        store = ChromaStore()
        st.metric("Indexed Chunks", store.count)
        docs = store.list_documents()
        st.metric("Documents", len(docs))
    except Exception:
        st.warning("ChromaDB not initialized. Upload documents first.")

    try:
        from contractiq.graph.neo4j_client import Neo4jClient
        client = Neo4jClient()
        if client.verify_connectivity():
            stats = client.get_stats()
            total_nodes = sum(v for k, v in stats.items() if not k.startswith("rel:"))
            st.metric("Graph Nodes", total_nodes)
            st.success("Neo4j Connected")
        else:
            st.info("Neo4j not available")
        client.close()
    except Exception:
        st.info("Neo4j not configured")
