"""RAG Pipeline Ablation Study framework.

Provides a structured way to evaluate how each component of the retrieval
pipeline (BM25, dense retrieval, reranker, query decomposition, self-RAG)
contributes to overall quality.  Designed to work **without** real LLM calls
by accepting a callable ``evaluate_fn`` that maps (config, questions) to a
metrics dict.
"""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from scipy.stats import wilcoxon as scipy_wilcoxon


# ---------------------------------------------------------------------------
# Ablation configuration
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AblationConfig:
    """Feature-flag configuration for a single ablation experiment."""

    name: str
    use_bm25: bool = False
    use_dense: bool = False
    use_reranker: bool = False
    use_query_decomposition: bool = False
    use_self_rag: bool = False


# ---------------------------------------------------------------------------
# Predefined configurations (progressive pipeline build-up)
# ---------------------------------------------------------------------------
BM25_ONLY = AblationConfig(
    name="BM25_ONLY",
    use_bm25=True,
)

DENSE_ONLY = AblationConfig(
    name="DENSE_ONLY",
    use_dense=True,
)

HYBRID = AblationConfig(
    name="HYBRID",
    use_bm25=True,
    use_dense=True,
)

HYBRID_RERANKER = AblationConfig(
    name="HYBRID_RERANKER",
    use_bm25=True,
    use_dense=True,
    use_reranker=True,
)

HYBRID_RERANKER_QD = AblationConfig(
    name="HYBRID_RERANKER_QD",
    use_bm25=True,
    use_dense=True,
    use_reranker=True,
    use_query_decomposition=True,
)

FULL_WITH_SELF_RAG = AblationConfig(
    name="FULL_WITH_SELF_RAG",
    use_bm25=True,
    use_dense=True,
    use_reranker=True,
    use_query_decomposition=True,
    use_self_rag=True,
)

ALL_CONFIGS: list[AblationConfig] = [
    BM25_ONLY,
    DENSE_ONLY,
    HYBRID,
    HYBRID_RERANKER,
    HYBRID_RERANKER_QD,
    FULL_WITH_SELF_RAG,
]

# Metric used as the primary accuracy score for elbow analysis
_PRIMARY_METRIC = "faithfulness"
# Metric used to represent latency
_LATENCY_KEY = "latency_seconds"


# ---------------------------------------------------------------------------
# Type alias for the evaluation callback
# ---------------------------------------------------------------------------
EvaluateFn = Callable[[AblationConfig, list[dict[str, Any]]], dict[str, Any]]
"""Signature: (config, questions) -> {"faithfulness": ..., ...}"""


# ---------------------------------------------------------------------------
# Ablation study runner
# ---------------------------------------------------------------------------
class AblationStudy:
    """Orchestrates ablation experiments across pipeline configurations.

    Args:
        evaluate_fn: A callable with signature
            ``(config: AblationConfig, questions: list[dict]) -> dict``
            that returns a metrics dictionary (e.g.
            ``{"faithfulness": 0.91, "answer_relevancy": 0.88, ...}``).
            This abstraction keeps the study independent of any LLM or
            retrieval backend.
        configs: Override the set of configs to study (defaults to all six
            predefined configurations).
    """

    def __init__(
        self,
        evaluate_fn: EvaluateFn,
        configs: list[AblationConfig] | None = None,
    ) -> None:
        self._evaluate_fn = evaluate_fn
        self._configs = configs or list(ALL_CONFIGS)

    # -- single config -------------------------------------------------------

    def run_config(
        self,
        config: AblationConfig,
        test_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Evaluate a single ablation configuration.

        Args:
            config: The pipeline configuration to test.
            test_data: List of test-question dicts (same schema as
                ``test_dataset.TEST_QUESTIONS``).

        Returns:
            Dict containing ``"config"`` (name), all metrics produced by
            ``evaluate_fn``, and ``"latency_seconds"``.
        """
        start = time.perf_counter()
        metrics = self._evaluate_fn(config, test_data)
        elapsed = time.perf_counter() - start

        return {
            "config": config.name,
            _LATENCY_KEY: round(elapsed, 4),
            **metrics,
        }

    # -- run all -------------------------------------------------------------

    def run_all(
        self,
        test_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Run all configured ablation experiments sequentially.

        Args:
            test_data: Shared test dataset passed to every configuration.

        Returns:
            List of result dicts (one per configuration), each containing
            the config name, latency, and all evaluation metrics.
        """
        return [self.run_config(cfg, test_data) for cfg in self._configs]

    # -- statistical testing -------------------------------------------------

    @staticmethod
    def wilcoxon_test(
        scores_a: Sequence[float],
        scores_b: Sequence[float],
        alpha: float = 0.05,
    ) -> dict[str, Any]:
        """Perform a Wilcoxon signed-rank test on paired score vectors.

        This is a non-parametric test that determines whether the *median*
        difference between two paired samples is significantly different
        from zero.

        Args:
            scores_a: Per-question scores from configuration A.
            scores_b: Per-question scores from configuration B.
            alpha: Significance level (default 0.05).

        Returns:
            Dict with ``"statistic"``, ``"p_value"``, and ``"significant"``
            (bool, ``True`` when ``p_value < alpha``).

        Raises:
            ValueError: If the input sequences have different lengths or
                contain fewer than two observations.
        """
        if len(scores_a) != len(scores_b):
            raise ValueError(
                f"Score vectors must have the same length, "
                f"got {len(scores_a)} and {len(scores_b)}"
            )
        if len(scores_a) < 2:
            raise ValueError(
                "At least two paired observations are required for the "
                "Wilcoxon signed-rank test"
            )

        # If all differences are zero, scipy raises -- handle gracefully.
        diffs = [a - b for a, b in zip(scores_a, scores_b)]
        if all(d == 0.0 for d in diffs):
            return {
                "statistic": 0.0,
                "p_value": 1.0,
                "significant": False,
            }

        result = scipy_wilcoxon(scores_a, scores_b)

        return {
            "statistic": float(result.statistic),
            "p_value": float(result.pvalue),
            "significant": float(result.pvalue) < alpha,
        }

    # -- cross-validation ----------------------------------------------------

    def cross_validate(
        self,
        test_data: list[dict[str, Any]],
        n_folds: int = 5,
    ) -> dict[str, dict[str, Any]]:
        """Run stratified k-fold cross-validation over question splits.

        Each fold uses ``(n_folds - 1) / n_folds`` of the questions as the
        evaluation set (simulating different data slices).  Metrics are
        averaged across folds to estimate variance.

        Args:
            test_data: Full test dataset.
            n_folds: Number of folds (default 5).

        Returns:
            Mapping of config name to a dict containing ``"mean"``,
            ``"std"``, and ``"fold_results"`` for each metric.
        """
        if n_folds < 2:
            raise ValueError("n_folds must be >= 2")

        # Build fold indices (simple round-robin assignment)
        fold_indices: list[list[int]] = [[] for _ in range(n_folds)]
        for idx in range(len(test_data)):
            fold_indices[idx % n_folds].append(idx)

        results_by_config: dict[str, dict[str, Any]] = {}

        for cfg in self._configs:
            fold_metrics_list: list[dict[str, Any]] = []

            for fold_idx in range(n_folds):
                # Use all folds *except* the held-out fold as the eval set
                eval_indices: list[int] = []
                for other_fold in range(n_folds):
                    if other_fold != fold_idx:
                        eval_indices.extend(fold_indices[other_fold])

                fold_data = [test_data[i] for i in sorted(eval_indices)]
                metrics = self._evaluate_fn(cfg, fold_data)
                fold_metrics_list.append(metrics)

            # Aggregate across folds
            all_metric_names = {
                k for fm in fold_metrics_list for k in fm if isinstance(fm[k], (int, float))
            }
            aggregated: dict[str, Any] = {"fold_results": fold_metrics_list}

            for metric_name in sorted(all_metric_names):
                values = [
                    fm[metric_name]
                    for fm in fold_metrics_list
                    if metric_name in fm
                ]
                aggregated[f"{metric_name}_mean"] = (
                    statistics.mean(values) if values else 0.0
                )
                aggregated[f"{metric_name}_std"] = (
                    statistics.stdev(values) if len(values) >= 2 else 0.0
                )

            results_by_config[cfg.name] = aggregated

        return results_by_config

    # -- elbow / Occam's razor -----------------------------------------------

    def find_elbow(
        self,
        results: list[dict[str, Any]],
        accuracy_key: str = _PRIMARY_METRIC,
        latency_key: str = _LATENCY_KEY,
    ) -> str:
        """Identify the optimal configuration using an elbow heuristic.

        The "elbow" is the configuration that provides the best
        accuracy-per-unit-latency tradeoff (Occam's razor: prefer the
        simplest model that is *good enough*).

        The algorithm scores each configuration as::

            efficiency = accuracy / (1 + latency)

        and returns the name of the config with the highest efficiency.
        When two configs are tied, the one appearing earlier in the list
        (i.e. simpler) wins.

        Args:
            results: Output of ``run_all`` -- list of result dicts.
            accuracy_key: Metric name used as the accuracy proxy.
            latency_key: Key holding the latency in seconds.

        Returns:
            Name of the recommended configuration.

        Raises:
            ValueError: If *results* is empty or the required keys are
                missing from every entry.
        """
        if not results:
            raise ValueError("results list must not be empty")

        best_name: str = results[0]["config"]
        best_efficiency: float = -1.0

        for entry in results:
            accuracy = entry.get(accuracy_key, 0.0)
            latency = entry.get(latency_key, 0.0)
            efficiency = accuracy / (1.0 + latency)

            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_name = entry["config"]

        return best_name

    # -- pretty table --------------------------------------------------------

    @staticmethod
    def format_ablation_table(results: list[dict[str, Any]]) -> str:
        """Format ablation results as a readable comparison table.

        Example output::

            Config                faith.  ans_rel  ctx_pre  ctx_rec  latency
            ---------------------------------------------------------------
            BM25_ONLY             0.7200  0.6800   0.6500   0.7000   0.12s
            DENSE_ONLY            0.8000  0.7500   0.7200   0.7800   0.15s
            ...

        Args:
            results: Output from ``run_all``.

        Returns:
            Multi-line formatted string.
        """
        if not results:
            return "(no results)"

        # Determine which metric columns are present
        metric_keys = [
            k
            for k in results[0]
            if k not in ("config", _LATENCY_KEY)
            and isinstance(results[0][k], (int, float))
        ]

        # Column widths
        name_w = max(len(r["config"]) for r in results)
        name_w = max(name_w, len("Config"))
        col_w = 9  # width per metric column

        # Header
        header_parts = [f"{'Config':<{name_w}s}"]
        for mk in metric_keys:
            label = mk[:col_w]
            header_parts.append(f"{label:>{col_w}s}")
        header_parts.append(f"{'latency':>{col_w}s}")
        header = "  ".join(header_parts)

        separator = "-" * len(header)

        lines: list[str] = [header, separator]

        for entry in results:
            parts = [f"{entry['config']:<{name_w}s}"]
            for mk in metric_keys:
                val = entry.get(mk, 0.0)
                parts.append(f"{val:>{col_w}.4f}")
            latency = entry.get(_LATENCY_KEY, 0.0)
            parts.append(f"{latency:>{col_w - 1}.2f}s")
            lines.append("  ".join(parts))

        # Elbow recommendation (if enough data)
        if len(results) >= 2:
            lines.append(separator)
            try:
                study = AblationStudy(evaluate_fn=lambda *_: {})
                elbow = study.find_elbow(results)
                lines.append(f"  Recommended (elbow): {elbow}")
            except ValueError:
                pass

        lines.append("")
        return "\n".join(lines)
