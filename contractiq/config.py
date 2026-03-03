"""ContractIQ configuration management using Pydantic Settings."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"


class Settings(BaseSettings):
    """Central configuration loaded from .env with CIQ_ prefix."""

    model_config = SettingsConfigDict(
        env_prefix="CIQ_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- OpenAI ---
    openai_api_key: str = Field(default="", description="OpenAI API key")
    llm_model: str = Field(default="gpt-4o", description="LLM model name")
    embedding_model: str = Field(
        default="text-embedding-3-small", description="Embedding model"
    )
    embedding_dimensions: int = Field(default=1536)
    llm_temperature: float = Field(default=0.0)
    llm_max_tokens: int = Field(default=2048)

    # --- ChromaDB ---
    chroma_persist_dir: str = Field(
        default=str(DATA_DIR / "chroma_db"),
        description="ChromaDB persistence directory",
    )
    chroma_collection_name: str = Field(default="contracts")

    # --- BM25 ---
    bm25_index_path: str = Field(
        default=str(DATA_DIR / "bm25_index.pkl"),
        description="BM25 index pickle path",
    )

    # --- Neo4j ---
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_username: str = Field(default="neo4j")
    neo4j_password: str = Field(default="password")
    neo4j_database: str = Field(default="neo4j")

    # --- Retrieval ---
    retrieval_top_k: int = Field(default=20, description="Initial retrieval count")
    rerank_top_k: int = Field(default=5, description="After re-ranking count")
    hybrid_alpha: float = Field(
        default=0.5, description="Vector vs BM25 weight (0=BM25 only, 1=vector only)"
    )
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Cross-encoder model for reranking",
    )

    # --- Chunking ---
    chunk_strategy: Literal["recursive", "semantic", "clause_aware"] = Field(
        default="recursive"
    )
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)

    # --- Paths ---
    contracts_dir: str = Field(default=str(DATA_DIR / "contracts"))
    sample_contracts_dir: str = Field(default=str(DATA_DIR / "contracts" / "sample"))
    evaluation_dir: str = Field(default=str(DATA_DIR / "evaluation"))
    mandatory_clauses_path: str = Field(
        default=str(CONFIG_DIR / "mandatory_clauses.yaml")
    )
    graph_schema_path: str = Field(default=str(CONFIG_DIR / "graph_schema.yaml"))

    # --- Streamlit ---
    page_title: str = Field(default="ContractIQ")
    page_icon: str = Field(default="📄")

    # --- Logging ---
    log_level: str = Field(default="INFO")

    # --- v6.0: Evaluation Quality Gate thresholds ---
    gate_faithfulness: float = Field(default=0.85)
    gate_answer_relevancy: float = Field(default=0.80)
    gate_context_precision: float = Field(default=0.75)
    gate_context_recall: float = Field(default=0.80)

    # --- v6.0: Docling ---
    use_docling: bool = Field(default=False, description="Use Docling for parsing")

    # --- v6.0: Resilience ---
    circuit_breaker_failure_threshold: int = Field(default=3)
    circuit_breaker_recovery_timeout: float = Field(default=60.0)
    degradation_level: str = Field(default="full")

    # --- v9.0: Security ---
    enable_input_sanitization: bool = Field(default=True)
    enable_output_validation: bool = Field(default=True)
    document_classification_default: str = Field(default="confidential")


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
