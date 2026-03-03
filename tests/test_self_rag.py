"""Tests for contractiq.retrieval.self_rag module."""

import pytest

from contractiq.retrieval.self_rag import (
    RelevanceVerdict,
    SelfRAGFilter,
    SelfRAGResult,
)


class TestRelevanceVerdict:
    """Tests for the RelevanceVerdict enum ordering."""

    def test_relevance_verdict_ordering(self):
        assert RelevanceVerdict.RELEVANT > RelevanceVerdict.PARTIALLY_RELEVANT
        assert RelevanceVerdict.PARTIALLY_RELEVANT > RelevanceVerdict.NOT_RELEVANT
        assert RelevanceVerdict.RELEVANT > RelevanceVerdict.NOT_RELEVANT


class TestSelfRAGFilter:
    """Tests for the SelfRAGFilter keyword-fallback behaviour."""

    def setup_method(self):
        # No LLM client — uses keyword-based fallback logic.
        self.rag = SelfRAGFilter()

    # ------------------------------------------------------------------
    # verify_relevance
    # ------------------------------------------------------------------

    def test_verify_relevance_high_overlap(self):
        verdict = self.rag.verify_relevance(
            "payment terms",
            "Payment terms are net 30 days from invoice",
        )
        assert verdict == RelevanceVerdict.RELEVANT

    def test_verify_relevance_no_overlap(self):
        verdict = self.rag.verify_relevance(
            "payment terms",
            "The weather is sunny today",
        )
        assert verdict == RelevanceVerdict.NOT_RELEVANT

    def test_verify_relevance_partial_overlap(self):
        verdict = self.rag.verify_relevance(
            "What are the payment terms for Acme",
            "Acme Technologies provides enterprise solutions and consulting",
        )
        assert verdict in (
            RelevanceVerdict.PARTIALLY_RELEVANT,
            RelevanceVerdict.NOT_RELEVANT,
        )

    # ------------------------------------------------------------------
    # filter_results
    # ------------------------------------------------------------------

    def test_filter_results_keeps_relevant(self):
        results = [
            {"chunk_id": "1", "text": "Payment terms are net 30 days from invoice date."},
            {"chunk_id": "2", "text": "The weather is sunny today with clear skies."},
            {"chunk_id": "3", "text": "Invoice payment is due within 30 days of receipt."},
        ]
        outcome = self.rag.filter_results("payment terms", results)
        # Only relevant/partially-relevant chunks should survive.
        filtered_ids = [r["chunk_id"] for r in outcome.filtered_results]
        assert "1" in filtered_ids
        assert "2" not in filtered_ids

    def test_filter_results_returns_selfrag_result(self):
        results = [
            {"chunk_id": "1", "text": "Payment terms are net 30 days."},
        ]
        outcome = self.rag.filter_results("payment terms", results)
        assert isinstance(outcome, SelfRAGResult)

    def test_filter_rate_calculation(self):
        results = [
            {"chunk_id": "1", "text": "Payment terms are net 30 days from invoice date."},
            {"chunk_id": "2", "text": "The weather is sunny today with clear skies."},
            {"chunk_id": "3", "text": "Invoice payment is due within 30 days of receipt."},
        ]
        outcome = self.rag.filter_results("payment terms", results)
        # Expect chunk 2 to be removed (1 of 3), so filter_rate ~ 0.33.
        assert pytest.approx(outcome.filter_rate, abs=0.1) == 1 / 3

    def test_reflections_have_correct_structure(self):
        results = [
            {"chunk_id": "1", "text": "Payment terms are net 30 days."},
            {"chunk_id": "2", "text": "The weather is sunny today."},
        ]
        outcome = self.rag.filter_results("payment terms", results)
        for reflection in outcome.reflections:
            assert "chunk_id" in reflection
            assert "verdict" in reflection
            assert "reasoning" in reflection

    def test_empty_results(self):
        outcome = self.rag.filter_results("payment terms", [])
        assert outcome.filtered_results == []
        assert outcome.filter_rate == 0.0

    def test_all_relevant_none_filtered(self):
        results = [
            {"chunk_id": "1", "text": "Payment terms are net 30 days from invoice date."},
            {"chunk_id": "2", "text": "Net 30 payment terms apply to all invoices."},
        ]
        outcome = self.rag.filter_results("payment terms", results)
        assert outcome.filter_rate == 0.0
        assert len(outcome.filtered_results) == len(results)
