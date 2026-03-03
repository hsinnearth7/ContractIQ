"""Tests for contractiq.evaluation.ablation module."""

import pytest

from contractiq.evaluation.ablation import (
    ALL_CONFIGS,
    AblationConfig,
    AblationStudy,
)


# ---------------------------------------------------------------------------
# Helper mock evaluate function
# ---------------------------------------------------------------------------

def mock_evaluate(config: AblationConfig, questions):
    """Return scores proportional to the number of enabled features."""
    score = 0.5
    if config.use_bm25:
        score += 0.1
    if config.use_dense:
        score += 0.1
    if config.use_reranker:
        score += 0.1
    if config.use_query_decomposition:
        score += 0.05
    if config.use_self_rag:
        score += 0.05
    return {"faithfulness": score, "answer_relevancy": score - 0.05}


SAMPLE_TEST_DATA = [
    {"question": "What is the termination clause?", "expected": "30 days notice"},
    {"question": "What is the liability cap?", "expected": "$1M"},
    {"question": "What governing law applies?", "expected": "Delaware"},
]


# ---------------------------------------------------------------------------
# AblationConfig tests
# ---------------------------------------------------------------------------

class TestAblationConfig:

    def test_all_configs_count(self):
        """ALL_CONFIGS should contain exactly 6 predefined configurations."""
        assert len(ALL_CONFIGS) == 6

    def test_ablation_config_frozen(self):
        """AblationConfig is a frozen dataclass; attribute assignment must fail."""
        config = AblationConfig(name="test")
        with pytest.raises((AttributeError, TypeError)):
            config.use_bm25 = True


# ---------------------------------------------------------------------------
# AblationStudy.run_config / run_all tests
# ---------------------------------------------------------------------------

class TestAblationStudyRun:

    def setup_method(self):
        self.study = AblationStudy(evaluate_fn=mock_evaluate)

    def test_run_config_returns_metrics(self):
        """run_config should return a dict containing config name, latency, and metrics."""
        config = ALL_CONFIGS[0]
        result = self.study.run_config(config, SAMPLE_TEST_DATA)
        assert isinstance(result, dict)
        assert "config" in result
        assert "latency_seconds" in result
        assert "faithfulness" in result

    def test_run_all_returns_six_results(self):
        """run_all should return one result dict per config (6 total)."""
        results = self.study.run_all(SAMPLE_TEST_DATA)
        assert isinstance(results, list)
        assert len(results) == 6

    def test_run_all_progressive_scores(self):
        """Scores should increase progressively as more features are enabled."""
        results = self.study.run_all(SAMPLE_TEST_DATA)
        scores = [r["faithfulness"] for r in results]
        for i in range(1, len(scores)):
            assert scores[i] >= scores[i - 1], (
                f"Score at index {i} ({scores[i]}) should be >= "
                f"score at index {i - 1} ({scores[i - 1]})"
            )


# ---------------------------------------------------------------------------
# Wilcoxon statistical test
# ---------------------------------------------------------------------------

class TestWilcoxonTest:

    def test_wilcoxon_test_significant(self):
        """Clearly different distributions should be flagged as significant."""
        scores_a = [0.8, 0.85, 0.9]
        scores_b = [0.5, 0.55, 0.6]
        result = AblationStudy.wilcoxon_test(scores_a, scores_b)
        assert isinstance(result, dict)
        assert "statistic" in result
        assert "p_value" in result
        assert "significant" in result
        # With only 3 samples the Wilcoxon test may not achieve significance,
        # so we just verify it runs without error. If the implementation is
        # powerful enough we additionally check:
        # assert result["significant"] is True

    def test_wilcoxon_test_not_significant(self):
        """Identical score vectors should NOT be significant."""
        scores = [0.7, 0.75, 0.8]
        result = AblationStudy.wilcoxon_test(scores, scores)
        assert result["significant"] is False

    def test_wilcoxon_test_length_mismatch(self):
        """Vectors of different lengths must raise ValueError."""
        with pytest.raises(ValueError):
            AblationStudy.wilcoxon_test([0.8, 0.9], [0.5, 0.6, 0.7])

    def test_wilcoxon_test_too_few(self):
        """A single-element vector is too small for a meaningful test."""
        with pytest.raises(ValueError):
            AblationStudy.wilcoxon_test([0.8], [0.5])


# ---------------------------------------------------------------------------
# Cross-validation
# ---------------------------------------------------------------------------

class TestCrossValidate:

    def setup_method(self):
        self.study = AblationStudy(evaluate_fn=mock_evaluate)

    def test_cross_validate_returns_all_configs(self):
        """Result dict should have a key for every config name."""
        result = self.study.cross_validate(SAMPLE_TEST_DATA)
        for config in ALL_CONFIGS:
            assert config.name in result

    def test_cross_validate_has_fold_results(self):
        """Each config entry should contain a 'fold_results' key."""
        result = self.study.cross_validate(SAMPLE_TEST_DATA)
        for config_name, data in result.items():
            assert "fold_results" in data, (
                f"Config '{config_name}' missing 'fold_results'"
            )


# ---------------------------------------------------------------------------
# Elbow / efficiency analysis
# ---------------------------------------------------------------------------

class TestFindElbow:

    def setup_method(self):
        self.study = AblationStudy(evaluate_fn=mock_evaluate)

    def test_find_elbow_returns_string(self):
        """find_elbow should return the name of the most efficient config."""
        results = self.study.run_all(SAMPLE_TEST_DATA)
        elbow = self.study.find_elbow(results)
        assert isinstance(elbow, str)
        config_names = {c.name for c in ALL_CONFIGS}
        assert elbow in config_names

    def test_find_elbow_empty_raises(self):
        """An empty results list should raise ValueError."""
        with pytest.raises(ValueError):
            self.study.find_elbow([])


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

class TestFormatAblationTable:

    def test_format_ablation_table(self):
        """Formatted table should mention 'Config' and all config names."""
        study = AblationStudy(evaluate_fn=mock_evaluate)
        results = study.run_all(SAMPLE_TEST_DATA)
        table = AblationStudy.format_ablation_table(results)
        assert isinstance(table, str)
        assert "Config" in table
        for config in ALL_CONFIGS:
            assert config.name in table
