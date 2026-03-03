"""CI/CD Quality Gate for RAG evaluation metrics.

Checks aggregate and per-slice RAGAS metrics against configurable thresholds
and produces structured pass/fail results suitable for CI pipeline gates.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from contractiq.config import get_settings

# ---------------------------------------------------------------------------
# Metric names used throughout the evaluation pipeline
# ---------------------------------------------------------------------------
METRIC_NAMES: list[str] = [
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
]


# ---------------------------------------------------------------------------
# Pydantic result model
# ---------------------------------------------------------------------------
class MetricResult(BaseModel):
    """Outcome for a single metric against its threshold."""

    value: float = Field(description="Observed metric value")
    threshold: float = Field(description="Required minimum value")
    passed: bool = Field(description="Whether the metric met the threshold")


class GateResult(BaseModel):
    """Aggregated quality-gate outcome."""

    passed: bool = Field(description="True if ALL metrics meet their thresholds")
    metric_results: dict[str, MetricResult] = Field(
        default_factory=dict,
        description="Per-metric result keyed by metric name",
    )
    failed_metrics: list[str] = Field(
        default_factory=list,
        description="Names of metrics that did not meet their thresholds",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 timestamp of the gate evaluation",
    )


# ---------------------------------------------------------------------------
# Quality-gate logic
# ---------------------------------------------------------------------------
class QualityGate:
    """Evaluates RAGAS metrics against configurable thresholds.

    Thresholds are loaded from ``contractiq.config`` (``gate_*`` fields) by
    default and can be overridden at construction time.

    Usage::

        gate = QualityGate()
        result = gate.check(aggregate_metrics)
        if not result.passed:
            print(gate.format_report(result))
            sys.exit(1)
    """

    def __init__(
        self,
        thresholds: dict[str, float] | None = None,
    ) -> None:
        settings = get_settings()

        # Default thresholds sourced from config.py gate_* settings
        self._thresholds: dict[str, float] = thresholds or {
            "faithfulness": settings.gate_faithfulness,
            "answer_relevancy": settings.gate_answer_relevancy,
            "context_precision": settings.gate_context_precision,
            "context_recall": settings.gate_context_recall,
        }

    # -- public properties ---------------------------------------------------

    @property
    def thresholds(self) -> dict[str, float]:
        """Return a copy of the current thresholds."""
        return dict(self._thresholds)

    # -- core check ----------------------------------------------------------

    def check(self, metrics: dict[str, float]) -> GateResult:
        """Check aggregate metrics against thresholds.

        Args:
            metrics: Mapping of metric name to observed float value.
                     Keys should match the threshold names (e.g.
                     ``"faithfulness"``, ``"answer_relevancy"``).

        Returns:
            A ``GateResult`` containing per-metric verdicts and overall
            pass/fail status.
        """
        metric_results: dict[str, MetricResult] = {}
        failed_metrics: list[str] = []

        for name, threshold in self._thresholds.items():
            value = metrics.get(name, 0.0)
            passed = value >= threshold
            metric_results[name] = MetricResult(
                value=value,
                threshold=threshold,
                passed=passed,
            )
            if not passed:
                failed_metrics.append(name)

        return GateResult(
            passed=len(failed_metrics) == 0,
            metric_results=metric_results,
            failed_metrics=failed_metrics,
        )

    # -- per-slice check -----------------------------------------------------

    def check_slices(
        self,
        slice_results: dict[str, dict[str, float]],
    ) -> dict[str, GateResult]:
        """Evaluate per-slice metrics independently.

        Args:
            slice_results: Mapping of slice label (e.g. ``"factual"``,
                ``"comparison"``) to a metrics dict.

        Returns:
            Mapping of slice label to its ``GateResult``.
        """
        return {
            slice_name: self.check(slice_metrics)
            for slice_name, slice_metrics in slice_results.items()
        }

    # -- report formatting ---------------------------------------------------

    @staticmethod
    def format_report(result: GateResult) -> str:
        """Format a ``GateResult`` as human-readable text for CI logs.

        Example output::

            ╔══════════════════════════════════════════╗
            ║       QUALITY GATE: PASSED               ║
            ╚══════════════════════════════════════════╝
            Metric               Value   Threshold  Status
            ─────────────────────────────────────────────
            faithfulness         0.9100  >= 0.8500  PASS
            answer_relevancy     0.8700  >= 0.8000  PASS
            ...
        """
        status_label = "PASSED" if result.passed else "FAILED"

        border = "=" * 46
        lines: list[str] = [
            f"+{border}+",
            f"|{'QUALITY GATE: ' + status_label:^46s}|",
            f"+{border}+",
            "",
            f"  Timestamp: {result.timestamp}",
            "",
            f"  {'Metric':<24s} {'Value':>7s}  {'Threshold':>10s}  {'Status':>6s}",
            f"  {'-' * 55}",
        ]

        for name, mr in result.metric_results.items():
            tag = "PASS" if mr.passed else "FAIL"
            lines.append(
                f"  {name:<24s} {mr.value:>7.4f}  >= {mr.threshold:>7.4f}  {tag:>6s}"
            )

        lines.append(f"  {'-' * 55}")

        if result.failed_metrics:
            lines.append("")
            lines.append(
                f"  Failed metrics ({len(result.failed_metrics)}): "
                + ", ".join(result.failed_metrics)
            )

        lines.append("")
        lines.append(f"  Overall: {'PASS' if result.passed else 'FAIL'}")
        lines.append("")

        return "\n".join(lines)
