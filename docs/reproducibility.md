# Reproducibility Guide

## Overview

All evaluation results in ContractIQ are designed to be reproducible. This document describes how to replicate the key experiments.

## Golden Dataset

The golden dataset (`contractiq/evaluation/golden_dataset.py`) contains 55 fixed questions with ground-truth answers, organized by:
- **Difficulty:** easy (18), medium (21), hard (16)
- **Slice:** single_contract (20), cross_contract (15), numerical (10), temporal (10)

To verify the dataset:
```python
from contractiq.evaluation.golden_dataset import GOLDEN_DATASET, get_slices
assert len(GOLDEN_DATASET) == 55
slices = get_slices()
assert len(slices["single_contract"]) == 20
```

## Ablation Study

### Running the Full Study

```python
from contractiq.evaluation.ablation import AblationStudy, ALL_CONFIGS

study = AblationStudy(evaluate_fn=your_evaluate_fn)
results = study.run_all(test_data)
print(AblationStudy.format_ablation_table(results))
```

### Cross-Validation

```python
cv_results = study.cross_validate(test_data, n_folds=5)
for config_name, metrics in cv_results.items():
    print(f"{config_name}: faith_mean={metrics['faithfulness_mean']:.4f} +/- {metrics['faithfulness_std']:.4f}")
```

### Statistical Significance

```python
# Compare adjacent layers
wilcoxon = AblationStudy.wilcoxon_test(
    scores_layer_5,  # HYBRID_RERANKER_QD per-question scores
    scores_layer_6,  # FULL_WITH_SELF_RAG per-question scores
)
print(f"p-value: {wilcoxon['p_value']:.4f}, significant: {wilcoxon['significant']}")
```

### Elbow Analysis

```python
recommended = study.find_elbow(results)
print(f"Recommended config (Occam's razor): {recommended}")
```

## Quality Gate

### Running the Gate

```python
from contractiq.evaluation.quality_gate import QualityGate

gate = QualityGate()  # Uses default thresholds from config
result = gate.check(aggregate_metrics)
print(gate.format_report(result))
```

### Per-Slice Evaluation

```python
slice_results = gate.check_slices({
    "single_contract": {...},
    "cross_contract": {...},
    "numerical": {...},
    "temporal": {...},
})
```

### CI/CD Integration

```python
import sys
result = gate.check(metrics)
if not result.passed:
    print(gate.format_report(result))
    sys.exit(1)
```

## Synthetic Contract Generation

Contracts are generated with a fixed seed for reproducibility:

```bash
python scripts/generate_contracts.py --seed 42 --count 20
```

## Environment

Key dependencies for reproducible results:
- Python 3.11+
- `scipy >= 1.11.0` (Wilcoxon test)
- `hypothesis` (property-based tests)
- `ragas >= 0.2.0` (evaluation metrics)

All configuration is managed via `CIQ_` environment variables (see `contractiq/config.py`).
