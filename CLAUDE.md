# ContractIQ — Claude Code Guide

## Project Overview
ContractIQ is an AI-powered supplier contract RAG intelligence platform with hybrid retrieval, knowledge graphs, compliance checking, and rigorous evaluation methodology.

## Quick Start
```bash
pip install -r requirements.txt        # Install dependencies
python scripts/seed_demo.py            # Generate contracts + build index
streamlit run contractiq/ui/app.py     # Launch UI
pytest tests/ -v --cov=contractiq      # Run tests (80+)
```

## Architecture (v6.0 / v8.0 / v9.0)
- **Retrieval**: Hybrid (Vector + BM25 + RRF) → Cross-Encoder Reranker → Self-RAG Filter
- **Generation**: LangChain QA/Comparison/Compliance chains with GPT-4o
- **Graph**: Neo4j knowledge graph for entity relationships
- **Evaluation**: RAGAS metrics + 6-layer ablation + Wilcoxon test + 5-fold CV
- **Security**: 3-layer defense (Input Sanitizer + Zero Trust + Output Validator)
- **Resilience**: Circuit Breaker + 4-level Graceful Degradation

## Key Directories
- `contractiq/parsing/` — Document parsers (PDF, DOCX, Docling) + chunking strategies
- `contractiq/indexing/` — ChromaDB vector store + BM25 index
- `contractiq/retrieval/` — Hybrid retriever, reranker, query rewriter, Self-RAG filter
- `contractiq/generation/` — LLM client, QA chain, comparison chain, compliance chain
- `contractiq/compliance/` — Clause registry + compliance checker + report generator
- `contractiq/graph/` — Neo4j client, graph builder, GraphRAG retriever
- `contractiq/evaluation/` — RAGAS evaluator, golden dataset (55 Q), quality gate, ablation study
- `contractiq/security/` — Input sanitizer, output validator, access control
- `contractiq/ui/` — Streamlit app with 6 pages
- `tests/` — 80+ tests across 15 test files

## Configuration
All settings via `CIQ_` env prefix or `.env` file. Key settings:
- `CIQ_OPENAI_API_KEY`: OpenAI API key
- `CIQ_LLM_MODEL`: LLM model (default: gpt-4o)
- `CIQ_CHUNK_STRATEGY`: recursive | semantic | clause_aware
- `CIQ_USE_DOCLING`: Enable Docling parser (default: false)
- `CIQ_GATE_FAITHFULNESS`: Quality gate threshold (default: 0.85)
- `CIQ_ENABLE_INPUT_SANITIZATION`: Security layer 1 (default: true)

## Testing
```bash
pytest tests/ -v                       # All tests
pytest tests/test_golden_dataset.py    # Golden dataset tests
pytest tests/test_ablation.py          # Ablation study tests
pytest tests/test_security.py          # Security tests
pytest tests/test_resilience.py        # Circuit breaker + degradation
pytest tests/test_property_based.py    # Hypothesis property tests
```
