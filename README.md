# ContractIQ

**AI-Powered Supplier Contract RAG Intelligence Platform** — v6.0

A platform for analyzing supplier contracts using RAG (Retrieval-Augmented Generation), knowledge graphs, automated compliance checking, and rigorous evaluation methodology.

## v6.0 / v8.0 / v9.0 Highlights

| Version | Capability | Details |
|---------|-----------|---------|
| v6.0 | Golden Dataset | 55 questions x 3 difficulty x 4 evaluation slices |
| v6.0 | CI/CD Quality Gate | RAGAS threshold enforcement (faithfulness >= 0.85) |
| v6.0 | Docling Multi-Format | IBM Research-grade document parsing (PDF/DOCX/PPTX/HTML/images) |
| v6.0 | Resilience | Circuit Breaker + 4-level Graceful Degradation |
| v8.0 | 6-Layer Ablation | BM25 -> Dense -> Hybrid -> Reranker -> QD -> Self-RAG |
| v8.0 | Statistical Testing | Wilcoxon signed-rank + 5-fold CV + Occam's razor elbow |
| v9.0 | 3-Layer Security | Input sanitization + context isolation + output validation |
| v9.0 | Zero Trust | Role-based access control with deny-by-default classification |
| v9.0 | Self-RAG | LLM-based relevance verification with keyword fallback |

## Features

- **Intelligent Q&A** — Ask questions about contracts with source citations
- **Hybrid Retrieval** — Vector (ChromaDB) + BM25 keyword search with RRF fusion
- **Cross-Encoder Reranking** — ms-marco-MiniLM-L-6-v2 for precision
- **Self-RAG Filtering** — LLM-based relevance verification before generation
- **Cross-Contract Comparison** — Compare terms across multiple suppliers
- **Compliance Dashboard** — Automated mandatory clause verification with risk scoring
- **Knowledge Graph (GraphRAG)** — Neo4j-powered entity relationship exploration
- **RAGAS Evaluation** — Quantitative RAG quality assessment with quality gates
- **Ablation Study** — 6-layer progressive pipeline analysis with statistical significance testing
- **Security Architecture** — 3-layer prompt injection defense + Zero Trust access control

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | OpenAI GPT-4o |
| Embedding | text-embedding-3-small (1536-dim) |
| Vector DB | ChromaDB (local) |
| Keyword Search | BM25 (rank_bm25) |
| Re-ranking | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| RAG Framework | LangChain |
| Knowledge Graph | Neo4j |
| Document Parsing | PyMuPDF4LLM + pdfplumber + python-docx + Docling (optional) |
| Evaluation | RAGAS + Wilcoxon signed-rank test |
| Statistical | scipy (ablation study, 5-fold CV) |
| Security | 3-layer defense (input/context/output) |
| Frontend | Streamlit |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 3. One-click demo setup (generate contracts + build index)
python scripts/seed_demo.py

# 4. Launch the app
streamlit run contractiq/ui/app.py
```

## Docker

```bash
docker compose up --build
```

## CLI Scripts

```bash
python scripts/generate_contracts.py   # Generate 20 sample contracts
python scripts/build_index.py          # Build vector + BM25 index
python scripts/build_graph.py          # Build Neo4j knowledge graph
python scripts/run_evaluation.py       # Run RAGAS evaluation
python scripts/seed_demo.py            # One-click demo setup
```

## Testing

```bash
pytest tests/ -v --cov=contractiq      # Full test suite (80+ tests)
pytest tests/test_ablation.py -v       # Ablation study tests
pytest tests/test_security.py -v       # Security tests
pytest tests/test_resilience.py -v     # Resilience tests
pytest tests/test_property_based.py -v # Property-based tests (Hypothesis)
```

## Architecture

```
User Query
    |
    v
Input Sanitizer (Layer 1: prompt injection defense)
    |
    v
Query Rewriter --> Multi-Query Decomposer
                          |
              +-----------+-----------+
              |                       |
     Vector Search (ChromaDB)    BM25 Search
              |                       |
              +-----------+-----------+
                          |
                    RRF Fusion (Reciprocal Rank)
                          |
                 Cross-Encoder Reranker
                          |
                   Self-RAG Filter (relevance verification)
                          |
             +--- Access Control (Zero Trust) ---+
             |                                   |
      Document Context                   Graph Context (Neo4j)
             |                                   |
             +-------- GPT-4o QA Chain ----------+
                          |
                 Output Validator (Layer 3: citation + grounding check)
                          |
                    Answer + Sources
```

## Ablation Study (v8.0)

The 6-layer ablation framework evaluates each pipeline component's contribution:

| Layer | Configuration | Components |
|-------|--------------|------------|
| 1 | BM25_ONLY | BM25 keyword search |
| 2 | DENSE_ONLY | Vector embedding search |
| 3 | HYBRID | BM25 + Dense + RRF fusion |
| 4 | HYBRID_RERANKER | + Cross-encoder reranking |
| 5 | HYBRID_RERANKER_QD | + Query decomposition |
| 6 | FULL_WITH_SELF_RAG | + Self-RAG filtering |

Statistical validation: Wilcoxon signed-rank test (alpha=0.05) between adjacent layers, 5-fold cross-validation for variance estimation, and Occam's razor elbow analysis for optimal complexity selection.

## Security Architecture (v9.0)

```
Layer 1: Input Sanitization
  - 10 regex patterns for prompt injection detection
  - Weighted risk scoring (threshold: 0.3)
  - Dangerous token stripping ([INST], <<SYS>>, etc.)

Layer 2: Context Isolation (Zero Trust)
  - Document classification: PUBLIC / CONFIDENTIAL / HIGHLY_CONFIDENTIAL
  - Role-based access: VIEWER / ANALYST / ADMIN
  - Deny-by-default for unclassified documents

Layer 3: Output Validation
  - Citation presence verification
  - Hallucination marker detection
  - No-access phrase filtering
```

## Resilience (v6.0)

```
Circuit Breaker: CLOSED --> OPEN --> HALF_OPEN --> CLOSED
  - Failure threshold: 3 consecutive failures
  - Recovery timeout: 60 seconds
  - Automatic state transitions

Graceful Degradation: FULL --> LLM_PARTIAL --> RULE_BASED --> HUMAN
  - Progressive capability reduction
  - Per-level behavior adaptation
```

## Quality Gate (v6.0)

CI/CD quality gate enforces minimum RAGAS metrics:

| Metric | Threshold |
|--------|-----------|
| Faithfulness | >= 0.85 |
| Answer Relevancy | >= 0.80 |
| Context Precision | >= 0.75 |
| Context Recall | >= 0.80 |

## Neo4j Setup (Optional)

```bash
docker run -d -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

## License

MIT
