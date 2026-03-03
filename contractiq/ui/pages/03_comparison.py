"""Cross-contract comparison page."""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="ContractIQ - Compare", page_icon="⚖️", layout="wide")
st.title("⚖️ Cross-Contract Comparison")

# Get available documents
try:
    from contractiq.indexing.chroma_store import ChromaStore
    store = ChromaStore()
    docs = store.list_documents()
except Exception:
    docs = []

if not docs:
    st.warning("No contracts indexed yet. Go to **Upload** to index documents first.")
    st.stop()

# Supplier selection
st.subheader("Select Suppliers to Compare")

# Extract unique supplier names from metadata
all_results = store._collection.get(include=["metadatas"])
supplier_names = sorted(set(
    m.get("supplier_name", "Unknown")
    for m in all_results["metadatas"]
    if m.get("supplier_name")
))

if not supplier_names:
    supplier_names = docs  # Fallback to document IDs

selected_suppliers = st.multiselect(
    "Choose 2 or more suppliers",
    supplier_names,
    default=supplier_names[:2] if len(supplier_names) >= 2 else supplier_names,
)

# Dimension selection
st.subheader("Comparison Dimensions")
default_dimensions = [
    "Payment Terms",
    "Termination Conditions",
    "Liability Limits",
    "Warranty Period",
    "Confidentiality Duration",
    "Force Majeure",
]

selected_dimensions = st.multiselect(
    "Select dimensions to compare",
    default_dimensions + ["Insurance Requirements", "Data Protection", "SLA / Uptime",
                          "Intellectual Property", "Dispute Resolution"],
    default=default_dimensions[:4],
)

# Run comparison
if len(selected_suppliers) >= 2 and selected_dimensions:
    if st.button("🔍 Run Comparison", type="primary"):
        from contractiq.generation.comparison_chain import ComparisonChain

        with st.spinner("Analyzing contracts..."):
            chain = ComparisonChain()
            result = chain.compare(selected_suppliers, selected_dimensions)

        # Display structured comparison table
        st.subheader("Comparison Results")

        if result.dimensions:
            for dim in result.dimensions:
                st.markdown(f"### {dim.dimension}")

                if dim.values:
                    df = pd.DataFrame([dim.values])
                    st.dataframe(df, use_container_width=True)

                if dim.analysis:
                    st.markdown(f"**Analysis:** {dim.analysis}")

                st.divider()

        # Full summary
        with st.expander("📋 Full Analysis"):
            st.markdown(result.summary)

        # Sources
        if result.sources:
            with st.expander(f"📎 Sources ({len(result.sources)})"):
                for src in result.sources:
                    st.markdown(f"**[Source {src.source_id}]** `{src.document_id}`")
                    st.caption(src.text_excerpt)
elif len(selected_suppliers) < 2:
    st.info("Select at least 2 suppliers to compare.")
