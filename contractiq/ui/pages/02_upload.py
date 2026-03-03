"""Document upload and indexing page."""

import tempfile
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="ContractIQ - Upload", page_icon="📤", layout="wide")
st.title("📤 Contract Upload & Indexing")

# Sidebar: index status
with st.sidebar:
    st.header("Index Status")
    try:
        from contractiq.indexing.chroma_store import ChromaStore
        store = ChromaStore()
        st.metric("Total Chunks", store.count)
        docs = store.list_documents()
        st.metric("Documents Indexed", len(docs))
        if docs:
            st.markdown("**Indexed Documents:**")
            for d in docs:
                st.markdown(f"- `{d}`")
    except Exception:
        st.info("No index found yet.")

# Chunking settings
with st.sidebar:
    st.header("Indexing Settings")
    chunk_strategy = st.selectbox(
        "Chunking Strategy",
        ["recursive", "semantic", "clause_aware"],
        index=0,
    )
    extract_meta = st.checkbox("Extract Metadata (GPT-4o)", value=True)

# File upload
st.subheader("Upload Contracts")
uploaded_files = st.file_uploader(
    "Upload PDF or DOCX files",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)

# Process uploaded files
if uploaded_files:
    if st.button("🔨 Index Uploaded Files", type="primary"):
        from contractiq.indexing.index_builder import IndexBuilder

        builder = IndexBuilder()
        progress = st.progress(0)
        status = st.empty()

        results = []
        for i, uploaded in enumerate(uploaded_files):
            status.text(f"Processing {uploaded.name}...")

            # Save to temp file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(uploaded.name).suffix,
            ) as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name

            try:
                result = builder.index_document(
                    tmp_path,
                    extract_meta=extract_meta,
                    chunk_strategy=chunk_strategy,
                )
                results.append(result)
            except Exception as e:
                results.append({"file": uploaded.name, "chunks": 0, "status": f"error: {e}"})

            progress.progress((i + 1) / len(uploaded_files))

        status.text("Done!")

        # Show results
        st.subheader("Indexing Results")
        for r in results:
            if r["status"] == "indexed":
                st.success(
                    f"**{r['file']}**: {r['chunks']} chunks | "
                    f"Supplier: {r.get('supplier', 'N/A')} | "
                    f"Type: {r.get('contract_type', 'N/A')}"
                )
            else:
                st.error(f"**{r['file']}**: {r['status']}")

# Index sample contracts
st.divider()
st.subheader("Index Sample Contracts")
st.markdown("Generate and index the included sample contracts for demo purposes.")

col1, col2 = st.columns(2)

with col1:
    if st.button("📝 Generate Sample Contracts"):
        from contractiq.data.synthetic_generator import generate_contracts
        from contractiq.config import get_settings
        settings = get_settings()
        with st.spinner("Generating contracts..."):
            files = generate_contracts(settings.sample_contracts_dir, count=20)
            st.success(f"Generated {len(files)} sample contracts.")

with col2:
    if st.button("🔨 Index Sample Directory"):
        from contractiq.indexing.index_builder import IndexBuilder
        from contractiq.config import get_settings
        settings = get_settings()
        with st.spinner("Indexing sample contracts..."):
            builder = IndexBuilder()
            results = builder.index_directory(
                settings.sample_contracts_dir,
                extract_meta=extract_meta,
                chunk_strategy=chunk_strategy,
            )
            total = sum(r["chunks"] for r in results)
            st.success(f"Indexed {len(results)} documents with {total} total chunks.")

# Reset index
st.divider()
with st.expander("⚠️ Danger Zone"):
    if st.button("🗑️ Reset All Indices", type="secondary"):
        try:
            from contractiq.indexing.index_builder import IndexBuilder
            builder = IndexBuilder()
            builder.reset_all()
            st.warning("All indices have been cleared.")
        except Exception as e:
            st.error(f"Reset failed: {e}")
