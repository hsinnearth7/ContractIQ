"""CLI: Run RAGAS evaluation on the RAG pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contractiq.evaluation.evaluator import RAGASEvaluator


def main():
    print("ContractIQ - RAGAS Evaluation")
    print("-" * 50)

    evaluator = RAGASEvaluator()
    results = evaluator.run()

    print(f"\nResults saved to: data/evaluation/evaluation_results.json")
    print(f"\nTargets:")
    print(f"  Faithfulness > 0.85: {'PASS' if results['aggregate_metrics']['faithfulness'] > 0.85 else 'FAIL'}")
    print(f"  Relevancy > 0.80: {'PASS' if results['aggregate_metrics']['answer_relevancy'] > 0.80 else 'FAIL'}")


if __name__ == "__main__":
    main()
