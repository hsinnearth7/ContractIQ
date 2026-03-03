"""Tests for contractiq.evaluation.quality_gate module."""

import pytest

from contractiq.evaluation.quality_gate import (
    GateResult,
    MetricResult,
    QualityGate,
)

DEFAULT_THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.80,
    "context_precision": 0.75,
    "context_recall": 0.80,
}

ALL_PASSING_METRICS = {
    "faithfulness": 0.95,
    "answer_relevancy": 0.90,
    "context_precision": 0.85,
    "context_recall": 0.90,
}


class TestQualityGateInit:
    """Tests for QualityGate initialization and thresholds."""

    def test_quality_gate_default_thresholds(self):
        gate = QualityGate()
        thresholds = gate.thresholds
        assert thresholds["faithfulness"] == 0.85
        assert thresholds["answer_relevancy"] == 0.80
        assert thresholds["context_precision"] == 0.75
        assert thresholds["context_recall"] == 0.80
        assert len(thresholds) == 4

    def test_quality_gate_custom_thresholds(self):
        custom = {"faithfulness": 0.9}
        gate = QualityGate(thresholds=custom)
        assert gate.thresholds == {"faithfulness": 0.9}


class TestQualityGateCheck:
    """Tests for QualityGate.check method."""

    def test_check_all_pass(self):
        gate = QualityGate()
        result = gate.check(ALL_PASSING_METRICS)
        assert result.passed is True
        assert len(result.failed_metrics) == 0

    def test_check_partial_fail(self):
        gate = QualityGate()
        metrics = {
            "faithfulness": 0.5,
            "answer_relevancy": 0.90,
            "context_precision": 0.85,
            "context_recall": 0.90,
        }
        result = gate.check(metrics)
        assert result.passed is False
        assert "faithfulness" in result.failed_metrics

    def test_check_all_fail(self):
        gate = QualityGate()
        metrics = {
            "faithfulness": 0.0,
            "answer_relevancy": 0.0,
            "context_precision": 0.0,
            "context_recall": 0.0,
        }
        result = gate.check(metrics)
        assert result.passed is False
        assert len(result.failed_metrics) == 4

    def test_check_missing_metric_defaults_to_zero(self):
        gate = QualityGate()
        result = gate.check({})
        assert result.passed is False
        assert len(result.failed_metrics) == 4

    def test_metric_result_structure(self):
        gate = QualityGate()
        result = gate.check(ALL_PASSING_METRICS)
        for name, metric_result in result.metric_results.items():
            assert isinstance(metric_result, MetricResult)
            assert hasattr(metric_result, "value")
            assert hasattr(metric_result, "threshold")
            assert hasattr(metric_result, "passed")


class TestCheckSlices:
    """Tests for QualityGate.check_slices method."""

    def test_check_slices(self):
        gate = QualityGate()
        slice_results = {
            "factual": ALL_PASSING_METRICS,
            "comparison": ALL_PASSING_METRICS,
        }
        results = gate.check_slices(slice_results)
        assert isinstance(results, dict)
        assert "factual" in results
        assert "comparison" in results
        assert isinstance(results["factual"], GateResult)
        assert isinstance(results["comparison"], GateResult)


class TestFormatReport:
    """Tests for QualityGate.format_report static/class method."""

    def test_format_report_passed(self):
        gate = QualityGate()
        result = gate.check(ALL_PASSING_METRICS)
        report = QualityGate.format_report(result)
        assert "PASSED" in report

    def test_format_report_failed(self):
        gate = QualityGate()
        result = gate.check({"faithfulness": 0.0})
        report = QualityGate.format_report(result)
        assert "FAILED" in report


class TestGateResultTimestamp:
    """Tests for GateResult timestamp field."""

    def test_gate_result_has_timestamp(self):
        gate = QualityGate()
        result = gate.check(ALL_PASSING_METRICS)
        assert isinstance(result.timestamp, str)
        assert len(result.timestamp) > 0
