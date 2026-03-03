"""Tests for contractiq.resilience module."""

import pytest

from contractiq.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    DegradationLevel,
    GracefulDegradation,
    StructuredError,
    handle_llm_error,
)


# ---------------------------------------------------------------------------
# CircuitBreaker tests
# ---------------------------------------------------------------------------

class TestCircuitBreaker:

    def test_circuit_breaker_starts_closed(self):
        """A new CircuitBreaker should start in the CLOSED state."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_success_stays_closed(self):
        """A successful call should keep the breaker CLOSED."""
        cb = CircuitBreaker()
        result = cb.call(lambda: 42)
        assert result == 42
        assert cb.state == CircuitState.CLOSED

    def test_circuit_breaker_failure_increments(self):
        """Each failed call should increment the failure count."""
        cb = CircuitBreaker(failure_threshold=5)
        initial = cb.failure_count

        with pytest.raises(ValueError):
            cb.call(_raise_value_error)

        assert cb.failure_count == initial + 1

    def test_circuit_breaker_opens_after_threshold(self):
        """After reaching the failure threshold the breaker should OPEN."""
        cb = CircuitBreaker(failure_threshold=3)

        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(_raise_value_error)

        # Use _state to avoid auto-transition logic in .state property
        assert cb._state == CircuitState.OPEN

    def test_circuit_open_error_raised(self):
        """Calling through an OPEN breaker must raise CircuitOpenError."""
        cb = CircuitBreaker(failure_threshold=3)

        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(_raise_value_error)

        with pytest.raises(CircuitOpenError):
            cb.call(lambda: "should not run")

    def test_circuit_breaker_half_open_after_timeout(self):
        """With recovery_timeout=0.0 the breaker should transition to HALF_OPEN."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.0)

        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(_raise_value_error)

        # .state should auto-transition from OPEN to HALF_OPEN since timeout
        # has already elapsed (recovery_timeout=0.0)
        assert cb.state == CircuitState.HALF_OPEN

    def test_circuit_breaker_reset(self):
        """reset() should restore CLOSED state and zero the failure count."""
        cb = CircuitBreaker(failure_threshold=3)

        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(_raise_value_error)

        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_breaker_half_open_success_closes(self):
        """A successful call while HALF_OPEN should transition back to CLOSED."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.0)

        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(_raise_value_error)

        # Should now be HALF_OPEN (recovery_timeout=0.0)
        assert cb.state == CircuitState.HALF_OPEN

        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.state == CircuitState.CLOSED


# ---------------------------------------------------------------------------
# GracefulDegradation tests
# ---------------------------------------------------------------------------

class TestGracefulDegradation:

    def test_degradation_starts_full(self):
        """Default degradation level should be FULL and not degraded."""
        gd = GracefulDegradation()
        assert gd.level == DegradationLevel.FULL
        assert gd.is_degraded is False

    def test_degradation_degrade_steps(self):
        """Successive degrade() calls should walk through all levels."""
        gd = GracefulDegradation()
        assert gd.level == DegradationLevel.FULL

        gd.degrade()
        assert gd.level == DegradationLevel.LLM_PARTIAL

        gd.degrade()
        assert gd.level == DegradationLevel.RULE_BASED

        gd.degrade()
        assert gd.level == DegradationLevel.HUMAN

    def test_degradation_recover_steps(self):
        """Successive recover() calls should walk back up to FULL."""
        gd = GracefulDegradation(initial_level=DegradationLevel.HUMAN)

        gd.recover()
        assert gd.level == DegradationLevel.RULE_BASED

        gd.recover()
        assert gd.level == DegradationLevel.LLM_PARTIAL

        gd.recover()
        assert gd.level == DegradationLevel.FULL

    def test_degradation_degrade_at_bottom(self):
        """Degrading past HUMAN should stay at HUMAN."""
        gd = GracefulDegradation(initial_level=DegradationLevel.HUMAN)
        gd.degrade()
        assert gd.level == DegradationLevel.HUMAN

    def test_degradation_recover_at_top(self):
        """Recovering past FULL should stay at FULL."""
        gd = GracefulDegradation()
        gd.recover()
        assert gd.level == DegradationLevel.FULL

    def test_degradation_set_level(self):
        """set_level should jump directly to the specified level."""
        gd = GracefulDegradation()
        gd.set_level(DegradationLevel.RULE_BASED)
        assert gd.level == DegradationLevel.RULE_BASED

    def test_degradation_level_ordering(self):
        """DegradationLevel should support ordering: FULL > ... > HUMAN."""
        assert DegradationLevel.FULL > DegradationLevel.LLM_PARTIAL
        assert DegradationLevel.LLM_PARTIAL > DegradationLevel.RULE_BASED
        assert DegradationLevel.RULE_BASED > DegradationLevel.HUMAN


# ---------------------------------------------------------------------------
# StructuredError & handle_llm_error tests
# ---------------------------------------------------------------------------

class TestStructuredError:

    def test_structured_error_creation(self):
        """StructuredError should store all provided fields."""
        import time

        ts = time.time()
        err = StructuredError(
            error_type="TestError",
            message="something went wrong",
            component="test_component",
            timestamp=ts,
            recoverable=False,
            context={"detail": "extra info"},
        )
        assert err.error_type == "TestError"
        assert err.message == "something went wrong"
        assert err.component == "test_component"
        assert err.recoverable is False
        assert err.timestamp == ts
        assert err.context == {"detail": "extra info"}


class TestHandleLlmError:

    def test_handle_llm_error_recoverable(self):
        """handle_llm_error with a plain Exception should set recoverable=False."""
        error = Exception("generic failure")
        result = handle_llm_error(error, component="retriever")
        assert isinstance(result, StructuredError)
        assert result.recoverable is False

    def test_handle_llm_error_returns_structured(self):
        """Return value should be a StructuredError with the correct component."""
        error = RuntimeError("something broke")
        result = handle_llm_error(error, component="generator")
        assert isinstance(result, StructuredError)
        assert result.component == "generator"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _raise_value_error():
    """Simple callable that always raises ValueError."""
    raise ValueError("intentional test failure")
