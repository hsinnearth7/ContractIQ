"""Tests for configuration."""

from contractiq.config import Settings, get_settings, PROJECT_ROOT


def test_default_settings():
    settings = Settings(openai_api_key="test-key")
    assert settings.llm_model == "gpt-4o"
    assert settings.embedding_model == "text-embedding-3-small"
    assert settings.chunk_size == 1000
    assert settings.chunk_overlap == 200
    assert settings.retrieval_top_k == 20
    assert settings.rerank_top_k == 5
    assert settings.hybrid_alpha == 0.5


def test_project_root():
    assert PROJECT_ROOT.exists()
    assert (PROJECT_ROOT / "contractiq").exists()


def test_env_prefix():
    # Verify CIQ_ prefix is configured
    assert Settings.model_config["env_prefix"] == "CIQ_"
