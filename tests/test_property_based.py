"""Property-based tests using Hypothesis for ContractIQ components."""

from hypothesis import given, settings, strategies as st

from contractiq.security.input_sanitizer import InputSanitizer
from contractiq.security.output_validator import OutputValidator
from contractiq.evaluation.quality_gate import QualityGate


# ---------------------------------------------------------------------------
# Input Sanitizer property tests
# ---------------------------------------------------------------------------

class TestInputSanitizerProperties:
    @given(user_input=st.text(min_size=0, max_size=500))
    @settings(max_examples=50)
    def test_sanitize_always_returns_result(self, user_input: str):
        """Sanitizer never crashes, always returns a valid result."""
        sanitizer = InputSanitizer()
        result = sanitizer.sanitize(user_input)
        assert isinstance(result.is_safe, bool)
        assert 0.0 <= result.risk_score <= 1.0
        assert isinstance(result.threats_detected, list)
        assert isinstance(result.sanitized_input, str)

    @given(user_input=st.text(min_size=0, max_size=500))
    @settings(max_examples=50)
    def test_sanitize_preserves_original(self, user_input: str):
        """Original input is always preserved in the result."""
        sanitizer = InputSanitizer()
        result = sanitizer.sanitize(user_input)
        assert result.original_input == user_input

    @given(user_input=st.text(min_size=0, max_size=500))
    @settings(max_examples=50)
    def test_risk_score_zero_when_no_threats(self, user_input: str):
        """Risk score is 0 when no threats are detected."""
        sanitizer = InputSanitizer()
        result = sanitizer.sanitize(user_input)
        if len(result.threats_detected) == 0:
            assert result.risk_score == 0.0


# ---------------------------------------------------------------------------
# Output Validator property tests
# ---------------------------------------------------------------------------

class TestOutputValidatorProperties:
    @given(answer=st.text(min_size=0, max_size=1000))
    @settings(max_examples=50)
    def test_validate_always_returns_result(self, answer: str):
        """Validator never crashes, always returns a valid result."""
        validator = OutputValidator()
        result = validator.validate(answer)
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.has_citations, bool)
        assert result.citation_count >= 0
        assert isinstance(result.issues, list)

    @given(answer=st.text(min_size=0, max_size=1000))
    @settings(max_examples=50)
    def test_citation_count_consistency(self, answer: str):
        """Citation count is consistent with has_citations flag."""
        validator = OutputValidator()
        result = validator.validate(answer)
        if result.citation_count > 0:
            assert result.has_citations is True
        if not result.has_citations:
            assert result.citation_count == 0


# ---------------------------------------------------------------------------
# Quality Gate property tests
# ---------------------------------------------------------------------------

class TestQualityGateProperties:
    @given(
        faithfulness=st.floats(min_value=0.0, max_value=1.0),
        answer_relevancy=st.floats(min_value=0.0, max_value=1.0),
        context_precision=st.floats(min_value=0.0, max_value=1.0),
        context_recall=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=50)
    def test_check_always_returns_gate_result(
        self,
        faithfulness: float,
        answer_relevancy: float,
        context_precision: float,
        context_recall: float,
    ):
        """Quality gate check never crashes for valid float inputs."""
        gate = QualityGate(thresholds={
            "faithfulness": 0.85,
            "answer_relevancy": 0.80,
            "context_precision": 0.75,
            "context_recall": 0.80,
        })
        metrics = {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "context_precision": context_precision,
            "context_recall": context_recall,
        }
        result = gate.check(metrics)
        assert isinstance(result.passed, bool)
        assert isinstance(result.failed_metrics, list)

    @given(
        value=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=30)
    def test_all_above_threshold_passes(self, value: float):
        """When all metrics exceed thresholds, the gate passes."""
        threshold = 0.5
        gate = QualityGate(thresholds={
            "faithfulness": threshold,
            "answer_relevancy": threshold,
        })
        metrics = {
            "faithfulness": max(value, threshold),
            "answer_relevancy": max(value, threshold),
        }
        result = gate.check(metrics)
        assert result.passed is True
        assert len(result.failed_metrics) == 0
