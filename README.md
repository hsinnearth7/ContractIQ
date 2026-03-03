<div align="center">

# ContractIQ — AI-Powered Supplier Contract RAG Intelligence Platform

**Hybrid retrieval (Vector + BM25 + RRF), cross-encoder reranking, Self-RAG filtering, Neo4j knowledge graph, compliance checking, and rigorous evaluation methodology for supplier contract analysis**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests: 80+](https://img.shields.io/badge/tests-80+-blue.svg)](tests/)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED.svg)](docker-compose.yml)

</div>

> ContractIQ is an AI-powered platform that enables intelligent Q&A, cross-contract comparison, and automated compliance checking for supplier contracts. The system uses a hybrid retrieval pipeline (ChromaDB vector + BM25 keyword + RRF fusion), cross-encoder reranking (ms-marco-MiniLM-L-6-v2), and Self-RAG filtering for high-quality retrieval. A 6-layer ablation framework evaluates each pipeline component's contribution with Wilcoxon signed-rank tests and 5-fold cross-validation. The platform includes a Neo4j knowledge graph for entity relationships, 3-layer security defense (input sanitization + zero trust + output validation), circuit breaker resilience with 4-level graceful degradation, and CI/CD quality gates enforcing RAGAS metric thresholds.

---

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

---

## Features

- **Intelligent Q&A** — Ask questions about contracts with source citations
- **Hybrid Retrieval** — Vector (ChromaDB) + BM25 keyword search with RRF fusion
- **Cross-Encoder Reranking** — ms-marco-MiniLM-L-6-v2 for precision
- **Self-RAG Filtering** — LLM-based relevance verification before generation
- **Cross-Contract Comparison** — Compare terms across multiple suppliers
- **Compliance Dashboard** — Automated mandatory clause verification with risk scoring
- **Knowledge Graph (GraphRAG)** — Neo4j-powered entity relationship exploration
- **RAGAS Evaluation** — Quantitative RAG quality assessment with quality gates
- **6-Layer Ablation Study** — Progressive pipeline analysis with Wilcoxon signed-rank tests and 5-fold CV
- **3-Layer Security** — Input sanitization + context isolation (Zero Trust) + output validation
- **Circuit Breaker Resilience** — 4-level graceful degradation (FULL → LLM_PARTIAL → RULE_BASED → HUMAN)
- **Docling Multi-Format** — IBM Research-grade document parsing (PDF/DOCX/PPTX/HTML/images)

---

## Ablation Study

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

---

## Quality Gate

CI/CD quality gate enforces minimum RAGAS metrics:

| Metric | Threshold |
|--------|-----------|
| Faithfulness | >= 0.85 |
| Answer Relevancy | >= 0.80 |
| Context Precision | >= 0.75 |
| Context Recall | >= 0.80 |

---

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

### Docker

```bash
docker compose up --build
```

---

## Technical Approach

### Hybrid Retrieval Pipeline

The retrieval pipeline combines three search strategies with Reciprocal Rank Fusion:

1. **Vector Search (ChromaDB)** — text-embedding-3-small (1536-dim) for semantic similarity
2. **BM25 Keyword Search** — rank_bm25 for exact term matching
3. **RRF Fusion** — Reciprocal rank fusion merges results from both strategies
4. **Cross-Encoder Reranker** — ms-marco-MiniLM-L-6-v2 re-scores top candidates for precision
5. **Self-RAG Filter** — LLM-based relevance verification with keyword fallback removes irrelevant chunks

### Security Architecture — 3-Layer Defense

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

### Resilience — Circuit Breaker + Graceful Degradation

```
Circuit Breaker: CLOSED --> OPEN --> HALF_OPEN --> CLOSED
  - Failure threshold: 3 consecutive failures
  - Recovery timeout: 60 seconds
  - Automatic state transitions

Graceful Degradation: FULL --> LLM_PARTIAL --> RULE_BASED --> HUMAN
  - Progressive capability reduction
  - Per-level behavior adaptation
```

---

## Project Structure

```
ContractIQ/
├── contractiq/
│   ├── parsing/                       # Document parsers (PDF, DOCX, Docling) + chunking
│   ├── indexing/                       # ChromaDB vector store + BM25 index
│   ├── retrieval/                      # Hybrid retriever, reranker, query rewriter, Self-RAG
│   ├── generation/                     # LLM client, QA/comparison/compliance chains
│   ├── compliance/                     # Clause registry + compliance checker + report
│   ├── graph/                          # Neo4j client, graph builder, GraphRAG retriever
│   ├── evaluation/                     # RAGAS evaluator, golden dataset (55 Q), ablation
│   ├── security/                       # Input sanitizer, output validator, access control
│   ├── ui/                             # Streamlit app with 6 pages
│   └── resilience.py                   # Circuit breaker + graceful degradation
├── config/
│   ├── graph_schema.yaml               # Neo4j graph schema
│   └── mandatory_clauses.yaml          # Compliance clause definitions
├── tests/                              # 80+ tests across 15 test files
├── scripts/                            # CLI tools (seed, build, evaluate)
├── docs/                               # ADR + reproducibility docs
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## CLI Scripts

```bash
python scripts/generate_contracts.py   # Generate 20 sample contracts
python scripts/build_index.py          # Build vector + BM25 index
python scripts/build_graph.py          # Build Neo4j knowledge graph
python scripts/run_evaluation.py       # Run RAGAS evaluation
python scripts/seed_demo.py            # One-click demo setup
```

---

## Testing

**80+ tests** across 15 test files:

```bash
pytest tests/ -v --cov=contractiq      # Full test suite
pytest tests/test_ablation.py -v       # Ablation study tests
pytest tests/test_security.py -v       # Security tests
pytest tests/test_resilience.py -v     # Resilience tests
pytest tests/test_property_based.py -v # Property-based tests (Hypothesis)
```

---

## Neo4j Setup (Optional)

```bash
docker run -d -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **LLM** | OpenAI GPT-4o |
| **Embedding** | text-embedding-3-small (1536-dim) |
| **Vector DB** | ChromaDB (local) |
| **Keyword Search** | BM25 (rank_bm25) |
| **Re-ranking** | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| **RAG Framework** | LangChain |
| **Knowledge Graph** | Neo4j |
| **Document Parsing** | PyMuPDF4LLM, pdfplumber, python-docx, Docling (optional) |
| **Evaluation** | RAGAS, Wilcoxon signed-rank test, scipy (5-fold CV) |
| **Security** | 3-layer defense (input/context/output) |
| **Frontend** | Streamlit |
| **Infrastructure** | Docker, docker-compose |
| **Testing** | pytest, Hypothesis (property-based) |

---

## License

MIT

---

<div align="center">

**Hybrid RAG · 6-Layer Ablation · 3-Layer Security · Zero Trust**

*Built with statistical rigor. Designed for contract intelligence.*

</div>
