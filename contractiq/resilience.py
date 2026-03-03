"""Resilience module — Circuit Breaker and Graceful Degradation.

Provides fault-tolerance primitives for the ContractIQ platform:

* **CircuitBreaker** — prevents cascading failures by short-circuiting calls
  to an unhealthy dependency (e.g. the OpenAI API) once a configurable
  failure threshold has been reached.
* **GracefulDegradation** — tracks the current degradation level of the
  system and allows other components to adapt their behaviour accordingly.
* **StructuredError / handle_llm_error** — converts raw exceptions into
  structured, Pydantic-serialisable error objects that can be surfaced in
  the UI or logged consistently.
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------

class CircuitState(Enum):
    """State of a circuit breaker."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(Exception):
    """Raised when a call is attempted while the circuit is OPEN."""

    def __init__(self, breaker_name: str, remaining_seconds: float) -> None:
        self.breaker_name = breaker_name
        self.remaining_seconds = remaining_seconds
        super().__init__(
            f"Circuit breaker '{breaker_name}' is OPEN.  "
            f"Recovery in {remaining_seconds:.1f}s."
        )


class CircuitBreaker:
    """Synchronous circuit breaker for protecting external calls.

    The breaker starts in the **CLOSED** state.  After
    *failure_threshold* consecutive failures it transitions to **OPEN**
    and rejects all calls with :class:`CircuitOpenError`.  Once
    *recovery_timeout* seconds have elapsed the state becomes
    **HALF_OPEN** and the next call is allowed through as a probe.  A
    successful probe resets the breaker to CLOSED; a failed probe
    re-opens the circuit.

    Parameters
    ----------
    failure_threshold:
        Number of consecutive failures before opening the circuit.
    recovery_timeout:
        Seconds to wait in the OPEN state before transitioning to
        HALF_OPEN.
    name:
        Human-readable name for logging and error messages.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,
        name: str = "default",
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._name = name

        self._state = CircuitState.CLOSED
        self._failure_count: int = 0
        self._last_failure_time: float = 0.0
        self._success_count: int = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Human-readable name of this breaker."""
        return self._name

    @property
    def state(self) -> CircuitState:
        """Current state, with automatic OPEN -> HALF_OPEN transition.

        If the breaker is OPEN and *recovery_timeout* has elapsed since
        the last failure, the state is promoted to HALF_OPEN so that
        the next :meth:`call` is allowed through as a probe.
        """
        if self._state is CircuitState.OPEN:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self._recovery_timeout:
                logger.info(
                    "Circuit '%s': OPEN -> HALF_OPEN after %.1fs.",
                    self._name,
                    elapsed,
                )
                self._state = CircuitState.HALF_OPEN
        return self._state

    @property
    def failure_count(self) -> int:
        """Number of consecutive failures recorded so far."""
        return self._failure_count

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute *func* through the circuit breaker.

        Parameters
        ----------
        func:
            The callable to protect.
        *args, **kwargs:
            Positional and keyword arguments forwarded to *func*.

        Returns
        -------
        T
            The return value of *func*.

        Raises
        ------
        CircuitOpenError
            If the circuit is currently OPEN and the recovery timeout
            has not yet elapsed.
        """
        current = self.state  # triggers auto OPEN->HALF_OPEN

        if current is CircuitState.OPEN:
            remaining = self._recovery_timeout - (
                time.monotonic() - self._last_failure_time
            )
            raise CircuitOpenError(self._name, max(remaining, 0.0))

        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            self._on_failure()
            raise exc  # noqa: TRY201 — re-raise original exception
        else:
            self._on_success()
            return result

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def _on_success(self) -> None:
        """Record a successful call and reset the breaker to CLOSED."""
        if self._state is CircuitState.HALF_OPEN:
            logger.info("Circuit '%s': HALF_OPEN -> CLOSED (probe succeeded).", self._name)
        self._failure_count = 0
        self._success_count += 1
        self._state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        """Record a failed call and potentially open the circuit."""
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self._state is CircuitState.HALF_OPEN:
            logger.warning(
                "Circuit '%s': HALF_OPEN -> OPEN (probe failed).", self._name,
            )
            self._state = CircuitState.OPEN
        elif self._failure_count >= self._failure_threshold:
            logger.warning(
                "Circuit '%s': CLOSED -> OPEN after %d consecutive failures.",
                self._name,
                self._failure_count,
            )
            self._state = CircuitState.OPEN

    def reset(self) -> None:
        """Manually reset the breaker to CLOSED with zero failures."""
        logger.info("Circuit '%s': manual reset -> CLOSED.", self._name)
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0


# ---------------------------------------------------------------------------
# Graceful Degradation
# ---------------------------------------------------------------------------

class DegradationLevel(Enum):
    """Ordered degradation levels for the ContractIQ platform.

    The levels (from highest capability to lowest) are:

    * **FULL** — all features available (LLM + retrieval + graph).
    * **LLM_PARTIAL** — LLM features degraded (e.g. using a smaller
      model or cached responses); retrieval still works.
    * **RULE_BASED** — no LLM at all; answers generated via
      deterministic rules / keyword matching.
    * **HUMAN** — system cannot answer automatically; requests are
      queued for human review.
    """

    FULL = "full"
    LLM_PARTIAL = "llm_partial"
    RULE_BASED = "rule_based"
    HUMAN = "human"

    def _rank(self) -> int:
        return {
            DegradationLevel.FULL: 3,
            DegradationLevel.LLM_PARTIAL: 2,
            DegradationLevel.RULE_BASED: 1,
            DegradationLevel.HUMAN: 0,
        }[self]

    def __ge__(self, other: DegradationLevel) -> bool:  # type: ignore[override]
        if not isinstance(other, DegradationLevel):
            return NotImplemented
        return self._rank() >= other._rank()

    def __gt__(self, other: DegradationLevel) -> bool:  # type: ignore[override]
        if not isinstance(other, DegradationLevel):
            return NotImplemented
        return self._rank() > other._rank()

    def __le__(self, other: DegradationLevel) -> bool:  # type: ignore[override]
        if not isinstance(other, DegradationLevel):
            return NotImplemented
        return self._rank() <= other._rank()

    def __lt__(self, other: DegradationLevel) -> bool:  # type: ignore[override]
        if not isinstance(other, DegradationLevel):
            return NotImplemented
        return self._rank() < other._rank()


# Ordered sequence used by degrade() / recover()
_DEGRADATION_ORDER: list[DegradationLevel] = [
    DegradationLevel.FULL,
    DegradationLevel.LLM_PARTIAL,
    DegradationLevel.RULE_BASED,
    DegradationLevel.HUMAN,
]


class GracefulDegradation:
    """Tracks and manages the current degradation level.

    Components can query :attr:`level` and :attr:`is_degraded` to adapt
    their behaviour.  The level can be adjusted manually with
    :meth:`set_level`, or moved one step at a time via :meth:`degrade`
    and :meth:`recover`.
    """

    def __init__(self, initial_level: DegradationLevel = DegradationLevel.FULL) -> None:
        self._level = initial_level

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def level(self) -> DegradationLevel:
        """Current degradation level."""
        return self._level

    @property
    def is_degraded(self) -> bool:
        """``True`` when the system is not running at full capacity."""
        return self._level is not DegradationLevel.FULL

    # ------------------------------------------------------------------
    # Transitions
    # ------------------------------------------------------------------

    def degrade(self) -> DegradationLevel:
        """Move one step down the degradation ladder.

        Returns the new level.  If already at the lowest level
        (``HUMAN``), the level remains unchanged.
        """
        idx = _DEGRADATION_ORDER.index(self._level)
        if idx < len(_DEGRADATION_ORDER) - 1:
            self._level = _DEGRADATION_ORDER[idx + 1]
            logger.warning(
                "Degradation level lowered to %s.", self._level.value,
            )
        else:
            logger.warning(
                "Already at lowest degradation level (%s).", self._level.value,
            )
        return self._level

    def recover(self) -> DegradationLevel:
        """Move one step up the degradation ladder.

        Returns the new level.  If already at ``FULL``, the level
        remains unchanged.
        """
        idx = _DEGRADATION_ORDER.index(self._level)
        if idx > 0:
            self._level = _DEGRADATION_ORDER[idx - 1]
            logger.info("Degradation level raised to %s.", self._level.value)
        else:
            logger.info(
                "Already at highest degradation level (%s).", self._level.value,
            )
        return self._level

    def set_level(self, level: DegradationLevel) -> None:
        """Explicitly set the degradation level.

        Parameters
        ----------
        level:
            The new degradation level.
        """
        previous = self._level
        self._level = level
        if previous is not level:
            logger.info(
                "Degradation level changed: %s -> %s.",
                previous.value,
                level.value,
            )


# ---------------------------------------------------------------------------
# Structured Error Handling
# ---------------------------------------------------------------------------

class StructuredError(BaseModel):
    """A structured, serialisable error object.

    Used to wrap raw exceptions into a consistent format that can be
    logged, returned via API, or rendered in the Streamlit UI.
    """

    error_type: str = Field(description="The class name of the original exception.")
    message: str = Field(description="Human-readable error description.")
    component: str = Field(description="ContractIQ component that raised the error.")
    timestamp: float = Field(description="Unix timestamp when the error was captured.")
    recoverable: bool = Field(
        description="Whether the system can potentially recover from this error.",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary extra context (e.g. model name, retry count).",
    )


def handle_llm_error(error: Exception, component: str) -> StructuredError:
    """Convert a raw exception from an LLM call into a :class:`StructuredError`.

    Parameters
    ----------
    error:
        The exception that was caught.
    component:
        The ContractIQ component where the error originated (e.g.
        ``"qa_chain"``, ``"compliance_chain"``).

    Returns
    -------
    StructuredError
        A structured representation of the error.
    """
    error_type = type(error).__name__

    # Classify recoverability by exception type
    recoverable_types = (
        "APITimeoutError",
        "RateLimitError",
        "APIConnectionError",
        "InternalServerError",
        "ServiceUnavailableError",
        "Timeout",
        "ConnectionError",
    )
    recoverable = error_type in recoverable_types

    context: dict[str, Any] = {}
    # Capture HTTP status code when available (e.g. openai.APIStatusError)
    if hasattr(error, "status_code"):
        context["status_code"] = getattr(error, "status_code")
    if hasattr(error, "response"):
        resp = getattr(error, "response", None)
        if resp is not None and hasattr(resp, "status_code"):
            context["http_status"] = resp.status_code

    structured = StructuredError(
        error_type=error_type,
        message=str(error),
        component=component,
        timestamp=time.time(),
        recoverable=recoverable,
        context=context,
    )

    logger.error(
        "Structured error in '%s': [%s] %s (recoverable=%s)",
        component,
        error_type,
        error,
        recoverable,
    )

    return structured
