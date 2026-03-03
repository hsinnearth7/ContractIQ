"""Chat Q&A page with source highlighting and GraphRAG toggle."""

import streamlit as st

st.set_page_config(page_title="ContractIQ - Chat", page_icon="💬", layout="wide")
st.title("💬 Contract Q&A")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar controls
with st.sidebar:
    st.header("Chat Settings")

    use_graph_rag = st.toggle("Enable GraphRAG", value=False,
                               help="Enhance answers with knowledge graph context")
    use_rewrite = st.toggle("Query Rewriting", value=True)
    use_multi_query = st.toggle("Multi-Query", value=True)
    use_rerank = st.toggle("Cross-Encoder Reranking", value=True)

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"📎 Sources ({len(msg['sources'])})"):
                for src in msg["sources"]:
                    st.markdown(
                        f"**[Source {src.source_id}]** `{src.document_id}`\n\n"
                        f"> {src.text_excerpt}..."
                    )

# Chat input
if question := st.chat_input("Ask about your contracts..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing contracts..."):
            try:
                if use_graph_rag:
                    from contractiq.graph.graph_enhanced_rag import GraphEnhancedRAG
                    chain = GraphEnhancedRAG()
                    response = chain.answer(question)
                else:
                    from contractiq.generation.qa_chain import QAChain
                    chain = QAChain()
                    response = chain.answer(
                        question,
                        use_rewrite=use_rewrite,
                        use_multi_query=use_multi_query,
                        use_rerank=use_rerank,
                    )

                st.markdown(response.answer)

                # Confidence indicator
                col1, col2 = st.columns([1, 4])
                with col1:
                    confidence_color = (
                        "green" if response.confidence > 0.8
                        else "orange" if response.confidence > 0.5
                        else "red"
                    )
                    st.markdown(
                        f"Confidence: :{confidence_color}[**{response.confidence:.0%}**]"
                    )

                # Sources
                if response.sources:
                    with st.expander(f"📎 Sources ({len(response.sources)})"):
                        for src in response.sources:
                            st.markdown(
                                f"**[Source {src.source_id}]** `{src.document_id}`\n\n"
                                f"> {src.text_excerpt}..."
                            )
                            st.divider()

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.answer,
                    "sources": response.sources,
                })

            except Exception as e:
                error_msg = f"Error: {e}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })
