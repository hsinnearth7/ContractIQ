"""Compliance dashboard page."""

import streamlit as st

st.set_page_config(page_title="ContractIQ - Compliance", page_icon="✅", layout="wide")
st.title("✅ Compliance Dashboard")

# Get indexed documents
try:
    from contractiq.indexing.chroma_store import ChromaStore
    store = ChromaStore()
    docs = store.list_documents()
except Exception:
    docs = []

if not docs:
    st.warning("No contracts indexed. Go to **Upload** first.")
    st.stop()

# Settings
with st.sidebar:
    st.header("Compliance Settings")
    severity_filter = st.selectbox(
        "Clause Severity Filter",
        ["All", "critical", "major", "minor"],
    )
    sev = None if severity_filter == "All" else severity_filter

# Document selection
st.subheader("Select Contract(s) to Check")
check_all = st.checkbox("Check all indexed contracts")

if not check_all:
    selected_docs = st.multiselect("Select documents", docs, default=docs[:1])
else:
    selected_docs = docs

# Run compliance check
if selected_docs and st.button("🔍 Run Compliance Check", type="primary"):
    from contractiq.compliance.checker import ComplianceChecker
    from contractiq.compliance.report_generator import risk_level, risk_color
    from contractiq.indexing.index_builder import IndexBuilder

    checker = ComplianceChecker()
    builder = IndexBuilder()

    reports = []
    progress = st.progress(0)

    for i, doc_id in enumerate(selected_docs):
        with st.spinner(f"Checking {doc_id}..."):
            # Retrieve full text from chunks
            result = store._collection.get(
                where={"document_id": doc_id},
                include=["documents"],
            )
            full_text = "\n\n".join(result["documents"]) if result["documents"] else ""

            if not full_text:
                st.warning(f"No text found for {doc_id}")
                continue

            # Get metadata
            meta_result = store._collection.get(
                where={"document_id": doc_id},
                include=["metadatas"],
            )
            meta = meta_result["metadatas"][0] if meta_result["metadatas"] else {}

            report = checker.check(
                contract_text=full_text,
                document_id=doc_id,
                supplier_name=meta.get("supplier_name", ""),
                contract_type=meta.get("contract_type", ""),
                severity_filter=sev,
            )
            reports.append(report)

        progress.progress((i + 1) / len(selected_docs))

    # Display results
    st.subheader("Compliance Results")

    for report in reports:
        level = risk_level(report.risk_score)
        color = risk_color(report.risk_score)

        with st.expander(
            f"{'🟢' if level == 'Low' else '🟡' if level == 'Medium' else '🔴'} "
            f"{report.document_id} — Risk: {level} ({report.risk_score:.0f}/100)",
            expanded=True,
        ):
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Risk Score", f"{report.risk_score:.0f}/100")
            col2.metric("Found", report.clauses_found, delta_color="normal")
            col3.metric("Partial", report.clauses_partial, delta_color="off")
            col4.metric("Missing", report.clauses_missing, delta_color="inverse")

            st.markdown(f"**Supplier:** {report.supplier_name or 'N/A'} | **Type:** {report.contract_type or 'N/A'}")

            # Findings table
            st.markdown("#### Clause Findings")
            for f in report.findings:
                status_icon = {"found": "✅", "partial": "⚠️", "missing": "❌"}.get(f.status, "❓")
                severity_badge = {"critical": "🔴", "major": "🟡", "minor": "🔵"}.get(f.severity, "⚪")

                st.markdown(f"{status_icon} {severity_badge} **{f.clause_name}** ({f.severity})")
                if f.evidence:
                    st.caption(f"Evidence: {f.evidence[:200]}...")
                if f.recommendation and f.status != "found":
                    st.info(f"💡 {f.recommendation}")

    # Summary across all contracts
    if len(reports) > 1:
        st.divider()
        st.subheader("Portfolio Summary")
        avg_risk = sum(r.risk_score for r in reports) / len(reports)
        total_missing = sum(r.clauses_missing for r in reports)

        col1, col2, col3 = st.columns(3)
        col1.metric("Average Risk Score", f"{avg_risk:.0f}/100")
        col2.metric("Total Missing Clauses", total_missing)
        col3.metric("Contracts Checked", len(reports))
