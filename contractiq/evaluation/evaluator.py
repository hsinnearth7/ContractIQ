"""RAGAS evaluation executor for RAG pipeline quality assessment."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from datasets import Dataset

from contractiq.config import get_settings
from contractiq.evaluation.test_dataset import load_test_dataset
from contractiq.generation.qa_chain import QAChain


class RAGASEvaluator:
    """Runs RAGAS evaluation against the RAG pipeline."""

    def __init__(self, qa_chain: QAChain | None = None):
        self.qa_chain = qa_chain or QAChain()
        self._settings = get_settings()

    def run(
        self,
        test_data: list[dict[str, Any]] | None = None,
        max_questions: int | None = None,
    ) -> dict[str, Any]:
        """Run RAGAS evaluation on the test dataset.

        Args:
            test_data: Custom test data (uses built-in if None).
            max_questions: Limit number of questions to evaluate.

        Returns:
            Dict with aggregate_metrics and per_question results.
        """
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        )

        data = test_data or load_test_dataset()
        if max_questions:
            data = data[:max_questions]

        # Generate answers for all questions
        questions = []
        answers = []
        contexts = []
        ground_truths = []

        for item in data:
            q = item["question"]
            print(f"  Evaluating: {q[:60]}...")

            try:
                response = self.qa_chain.answer(q)
                questions.append(q)
                answers.append(response.answer)
                contexts.append([s.text_excerpt for s in response.sources])
                ground_truths.append(item.get("ground_truth", ""))
            except Exception as e:
                print(f"  Error: {e}")
                questions.append(q)
                answers.append(f"Error: {e}")
                contexts.append([])
                ground_truths.append(item.get("ground_truth", ""))

        # Build RAGAS dataset
        eval_dataset = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        })

        # Run RAGAS evaluation
        result = evaluate(
            eval_dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
        )

        # Build output
        aggregate = {
            "faithfulness": float(result["faithfulness"]),
            "answer_relevancy": float(result["answer_relevancy"]),
            "context_precision": float(result["context_precision"]),
            "context_recall": float(result["context_recall"]),
        }

        per_question = []
        result_df = result.to_pandas()
        for i, row in result_df.iterrows():
            per_question.append({
                "question": questions[i],
                "answer": answers[i][:300],
                "contexts": contexts[i][:3],
                "ground_truth": ground_truths[i],
                "faithfulness": float(row.get("faithfulness", 0)),
                "answer_relevancy": float(row.get("answer_relevancy", 0)),
                "context_precision": float(row.get("context_precision", 0)),
                "context_recall": float(row.get("context_recall", 0)),
            })

        output = {
            "timestamp": datetime.now().isoformat(),
            "model": self._settings.llm_model,
            "total_questions": len(questions),
            "aggregate_metrics": aggregate,
            "per_question": per_question,
        }

        # Save results
        eval_dir = Path(self._settings.evaluation_dir)
        eval_dir.mkdir(parents=True, exist_ok=True)
        with open(eval_dir / "evaluation_results.json", "w") as f:
            json.dump(output, f, indent=2)

        print(f"\nRAGAS Evaluation Results:")
        for metric, value in aggregate.items():
            status = "PASS" if value > 0.80 else "BELOW TARGET"
            print(f"  {metric}: {value:.4f} [{status}]")

        return output
