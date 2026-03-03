"""Tests for synthetic contract generation."""

import tempfile
from pathlib import Path

from contractiq.data.synthetic_generator import generate_contracts
from contractiq.data.clause_library import CLAUSE_LIBRARY, CLAUSE_NAMES


def test_clause_library_completeness():
    assert len(CLAUSE_NAMES) >= 15
    for name in CLAUSE_NAMES:
        variants = CLAUSE_LIBRARY[name]
        assert len(variants) >= 1, f"{name} should have at least 1 variant"


def test_generate_contracts():
    with tempfile.TemporaryDirectory() as tmpdir:
        files = generate_contracts(tmpdir, count=5, seed=42)
        assert len(files) == 5
        assert all(Path(f).exists() for f in files)

        # Check file types
        extensions = {f.suffix for f in files}
        assert ".pdf" in extensions or ".docx" in extensions


def test_generate_contracts_reproducible():
    with tempfile.TemporaryDirectory() as tmpdir1:
        files1 = generate_contracts(tmpdir1, count=3, seed=42)
        names1 = [f.name for f in files1]

    with tempfile.TemporaryDirectory() as tmpdir2:
        files2 = generate_contracts(tmpdir2, count=3, seed=42)
        names2 = [f.name for f in files2]

    assert names1 == names2, "Same seed should produce same filenames"
