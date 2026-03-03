"""RAGAS evaluation dashboard."""

import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="ContractIQ - Evaluation", page_icon="📊", layout="wide")
st.title("📊 RAG Evaluation Dashboard")

EVAL_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "evaluation"

# Load existing results
results_path = EVAL_DIR / "evaluation_results.json"
if results_path.exists():
    with open(results_path) as f:
        eval_data = json.load(f)
else:
    eval_data = None

# Overall metrics
st.subheader("RAGAS Metrics")

if eval_data:
    metrics = eval_data.get("aggregate_metrics", {})

    col1, col2, col3, col4 = st.columns(4)

    faithfulness = metrics.get("faithfulness", 0)
    relevancy = metrics.get("answer_relevancy", 0)
    precision = metrics.get("context_precision", 0)
    recall = metrics.get("context_recall", 0)

    col1.metric(
        "Faithfulness",
        f"{faithfulness:.2f}",
        delta="Pass" if faithfulness > 0.85 else "Below target",
        delta_color="normal" if faithfulness > 0.85 else "inverse",
    )
    col2.metric(
        "Answer Relevancy",
        f"{relevancy:.2f}",
        delta="Pass" if relevancy > 0.80 else "Below target",
        delta_color="normal" if relevancy > 0.80 else "inverse",
    )
    col3.metric(
        "Context Precision",
        f"{precision:.2f}",
    )
    col4.metric(
        "Context Recall",
        f"{recall:.2f}",
    )

    # Targets
    st.markdown("""
    **Targets:** Faithfulness > 0.85 | Answer Relevancy > 0.80
    """)

    # Per-question details
    st.divider()
    st.subheader("Per-Question Results")

    details = eval_data.get("per_question", [])
    if details:
        for i, item in enumerate(details):
            with st.expander(f"Q{i+1}: {item.get('question', 'N/A')[:80]}..."):
                st.markdown(f"**Answer:** {item.get('answer', 'N/A')[:300]}...")

                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Faithfulness", f"{item.get('faithfulness', 0):.2f}")
                m_col2.metric("Relevancy", f"{item.get('answer_relevancy', 0):.2f}")
                m_col3.metric("Precision", f"{item.get('context_precision', 0):.2f}")
                m_col4.metric("Recall", f"{item.get('context_recall', 0):.2f}")

                if item.get("contexts"):
                    st.markdown("**Retrieved Contexts:**")
                    for ctx in item["contexts"][:3]:
                        st.caption(ctx[:200] + "...")

    # Evaluation metadata
    st.divider()
    st.caption(
        f"Evaluation run: {eval_data.get('timestamp', 'N/A')} | "
        f"Questions: {eval_data.get('total_questions', 'N/A')} | "
        f"Model: {eval_data.get('model', 'N/A')}"
    )

else:
    st.info(
        "No evaluation results found. Run evaluation first:\n\n"
        "```\npython scripts/run_evaluation.py\n```"
    )

# Run new evaluation
st.divider()
st.subheader("Run New Evaluation")

if st.button("🚀 Run RAGAS Evaluation", type="primary"):
    with st.spinner("Running evaluation (this may take several minutes)..."):
        try:
            from contractiq.evaluation.evaluator import RAGASEvaluator
            evaluator = RAGASEvaluator()
            results = evaluator.run()

            # Save results
            EVAL_DIR.mkdir(parents=True, exist_ok=True)
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)

            st.success("Evaluation complete! Refresh the page to see results.")
            st.rerun()
        except Exception as e:
            st.error(f"Evaluation failed: {e}")
