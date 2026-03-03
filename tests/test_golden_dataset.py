"""Tests for contractiq.evaluation.golden_dataset module."""

import pytest

from contractiq.evaluation.golden_dataset import (
    GOLDEN_DATASET,
    get_by_difficulty,
    get_by_slice,
    get_slices,
)

REQUIRED_KEYS = {"id", "question", "expected_answer", "expected_context", "difficulty", "slice"}


class TestGoldenDatasetStructure:
    """Tests for the structure and content of the golden dataset."""

    def test_golden_dataset_has_55_questions(self):
        assert len(GOLDEN_DATASET) == 55

    def test_golden_dataset_unique_ids(self):
        ids = [entry["id"] for entry in GOLDEN_DATASET]
        assert len(ids) == len(set(ids)), "Duplicate IDs found in golden dataset"

    def test_golden_dataset_required_keys(self):
        for entry in GOLDEN_DATASET:
            assert set(entry.keys()) >= REQUIRED_KEYS, (
                f"Entry {entry.get('id', '?')} is missing keys: "
                f"{REQUIRED_KEYS - set(entry.keys())}"
            )

    def test_difficulty_distribution(self):
        difficulties = [entry["difficulty"] for entry in GOLDEN_DATASET]
        easy_count = difficulties.count("easy")
        medium_count = difficulties.count("medium")
        hard_count = difficulties.count("hard")

        assert easy_count >= 14, f"Expected at least 14 easy, got {easy_count}"
        assert medium_count >= 18, f"Expected at least 18 medium, got {medium_count}"
        assert hard_count >= 14, f"Expected at least 14 hard, got {hard_count}"
        assert easy_count + medium_count + hard_count == 55

    def test_slice_distribution(self):
        slices = [entry["slice"] for entry in GOLDEN_DATASET]
        assert slices.count("single_contract") == 20
        assert slices.count("cross_contract") == 15
        assert slices.count("numerical") == 10
        assert slices.count("temporal") == 10

    def test_questions_have_nonempty_fields(self):
        for entry in GOLDEN_DATASET:
            assert isinstance(entry["question"], str) and len(entry["question"]) > 0, (
                f"Entry {entry['id']} has empty or non-string question"
            )
            assert isinstance(entry["expected_answer"], str) and len(entry["expected_answer"]) > 0, (
                f"Entry {entry['id']} has empty or non-string expected_answer"
            )
            assert isinstance(entry["expected_context"], str) and len(entry["expected_context"]) > 0, (
                f"Entry {entry['id']} has empty or non-string expected_context"
            )


class TestGetByDifficulty:
    """Tests for the get_by_difficulty function."""

    def test_get_by_difficulty_easy(self):
        results = get_by_difficulty("easy")
        assert len(results) > 0, "Expected non-empty list for easy difficulty"
        assert all(entry["difficulty"] == "easy" for entry in results)

    def test_get_by_difficulty_hard(self):
        results = get_by_difficulty("hard")
        assert len(results) > 0, "Expected non-empty list for hard difficulty"
        assert all(entry["difficulty"] == "hard" for entry in results)

    def test_get_by_difficulty_invalid(self):
        with pytest.raises(ValueError):
            get_by_difficulty("invalid")


class TestGetBySlice:
    """Tests for the get_by_slice function."""

    def test_get_by_slice_single_contract(self):
        results = get_by_slice("single_contract")
        assert len(results) == 20, f"Expected 20 single_contract items, got {len(results)}"
        assert all(entry["slice"] == "single_contract" for entry in results)

    def test_get_by_slice_invalid(self):
        with pytest.raises(ValueError):
            get_by_slice("unknown")


class TestGetSlices:
    """Tests for the get_slices function."""

    def test_get_slices_returns_four_slices(self):
        slices = get_slices()
        assert isinstance(slices, dict)
        expected_keys = {"single_contract", "cross_contract", "numerical", "temporal"}
        assert set(slices.keys()) == expected_keys
