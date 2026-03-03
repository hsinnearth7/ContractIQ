"""Test dataset management for RAGAS evaluation."""

import json
from pathlib import Path
from typing import Any

from contractiq.config import get_settings

# Pre-built test Q&A pairs for contract domain
TEST_QUESTIONS: list[dict[str, Any]] = [
    {
        "question": "What are the payment terms for Acme Technologies?",
        "ground_truth": "Payment terms include Net 30, Net 45, or Net 60 day invoice periods with late payment interest rates.",
        "category": "factual",
    },
    {
        "question": "What is the force majeure clause in the GlobalLogistics contract?",
        "ground_truth": "Force majeure covers acts of God, war, terrorism, pandemic, earthquake, flood, fire, and governmental actions.",
        "category": "factual",
    },
    {
        "question": "What are the termination conditions across all MSA contracts?",
        "ground_truth": "Termination can be for convenience (30-90 days notice) or for cause (breach with 30-45 day cure period).",
        "category": "comparison",
    },
    {
        "question": "Compare the liability limits between Acme Technologies and NexGen Cloud Services.",
        "ground_truth": "Liability is typically capped at 1-2x the total contract value, with exclusions for indirect damages.",
        "category": "comparison",
    },
    {
        "question": "Which contracts are missing data protection clauses?",
        "ground_truth": "Contracts with intentional omissions for compliance testing may be missing data protection clauses.",
        "category": "compliance",
    },
    {
        "question": "What is the confidentiality survival period in the NDA contracts?",
        "ground_truth": "Confidentiality obligations typically survive for 3 to 7 years after termination.",
        "category": "factual",
    },
    {
        "question": "What insurance requirements does Pinnacle Manufacturing have?",
        "ground_truth": "Insurance typically includes General Liability ($1-2M), Professional Liability ($2-5M), and Cyber Liability ($1-3M).",
        "category": "factual",
    },
    {
        "question": "What are the SLA uptime guarantees across all service agreements?",
        "ground_truth": "SLA uptime guarantees range from 99.5% to 99.95% measured monthly or quarterly.",
        "category": "comparison",
    },
    {
        "question": "What dispute resolution mechanisms are specified in the contracts?",
        "ground_truth": "Dispute resolution typically follows: negotiation (15-30 days), mediation (30 days), then binding arbitration.",
        "category": "factual",
    },
    {
        "question": "Which governing law jurisdictions are used across the contract portfolio?",
        "ground_truth": "Common jurisdictions include New York, California, with courts in New York County or Santa Clara County.",
        "category": "comparison",
    },
    {
        "question": "What is the warranty period for goods in Purchase Order agreements?",
        "ground_truth": "Warranty periods range from 90 days to 12 months for defects in materials and workmanship.",
        "category": "factual",
    },
    {
        "question": "What are the indemnification obligations of suppliers?",
        "ground_truth": "Suppliers indemnify buyers against claims from breaches, negligence, willful misconduct, and IP infringement.",
        "category": "factual",
    },
    {
        "question": "What are the P1 incident response times in the SLA contracts?",
        "ground_truth": "P1 (Critical) incidents require 15 minutes response time and 4 hours resolution.",
        "category": "factual",
    },
    {
        "question": "What are the intellectual property ownership terms?",
        "ground_truth": "Deliverables created for buyer are owned by buyer upon full payment. Supplier retains pre-existing IP with a perpetual license.",
        "category": "factual",
    },
    {
        "question": "How do assignment clauses differ across the contracts?",
        "ground_truth": "Assignment requires prior written consent, with exceptions for affiliates, mergers, or acquisitions.",
        "category": "comparison",
    },
    {
        "question": "What data breach notification timelines are specified?",
        "ground_truth": "Data breach notification is required within 48-72 hours of discovery.",
        "category": "factual",
    },
    {
        "question": "What are the service credit tiers for SLA violations?",
        "ground_truth": "Service credits: 5% for <99.9% uptime, 10% for <99.5%, 20% for <99.0%, capped at 30% of monthly fees.",
        "category": "factual",
    },
    {
        "question": "Which suppliers have the highest contract values?",
        "ground_truth": "Contract values range from $50,000 to $5,000,000 depending on supplier and contract type.",
        "category": "analytical",
    },
    {
        "question": "Are there any contracts expiring in the next 6 months?",
        "ground_truth": "Contract expiration depends on effective dates and term lengths specified in each agreement.",
        "category": "analytical",
    },
    {
        "question": "What are the early payment discount terms available?",
        "ground_truth": "Some contracts offer a 2% early payment discount for invoices paid within 10 days.",
        "category": "factual",
    },
]


def load_test_dataset(path: str | None = None) -> list[dict[str, Any]]:
    """Load test dataset from file or return built-in questions."""
    if path:
        p = Path(path)
        if p.exists():
            with open(p) as f:
                return json.load(f)

    settings = get_settings()
    dataset_path = Path(settings.evaluation_dir) / "test_dataset.json"
    if dataset_path.exists():
        with open(dataset_path) as f:
            return json.load(f)

    return TEST_QUESTIONS


def save_test_dataset(
    questions: list[dict[str, Any]],
    path: str | None = None,
) -> Path:
    """Save test dataset to file."""
    settings = get_settings()
    output = Path(path or settings.evaluation_dir) / "test_dataset.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(questions, f, indent=2)

    return output
