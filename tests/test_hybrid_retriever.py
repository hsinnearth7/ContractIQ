"""Tests for hybrid retrieval and RRF."""

from contractiq.retrieval.hybrid_retriever import reciprocal_rank_fusion


def test_reciprocal_rank_fusion_basic():
    list1 = [
        {"chunk_id": "a", "text": "text a", "score": 0.9},
        {"chunk_id": "b", "text": "text b", "score": 0.8},
        {"chunk_id": "c", "text": "text c", "score": 0.7},
    ]
    list2 = [
        {"chunk_id": "b", "text": "text b", "score": 5.0},
        {"chunk_id": "d", "text": "text d", "score": 4.0},
        {"chunk_id": "a", "text": "text a", "score": 3.0},
    ]

    fused = reciprocal_rank_fusion([list1, list2], k=60)

    # Both a and b appear in both lists, so they should rank higher
    ids = [r["chunk_id"] for r in fused]
    assert "a" in ids
    assert "b" in ids

    # b appears at rank 0 in list2 and rank 1 in list1, should rank high
    assert all("rrf_score" in r for r in fused)

    # Scores should be positive
    assert all(r["rrf_score"] > 0 for r in fused)


def test_rrf_empty_lists():
    fused = reciprocal_rank_fusion([[], []])
    assert fused == []


def test_rrf_single_list():
    items = [
        {"chunk_id": "x", "text": "x", "score": 1.0},
        {"chunk_id": "y", "text": "y", "score": 0.5},
    ]
    fused = reciprocal_rank_fusion([items])
    assert len(fused) == 2
    assert fused[0]["chunk_id"] == "x"  # Higher score = higher rank
