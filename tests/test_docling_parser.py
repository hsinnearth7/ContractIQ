"""Tests for contractiq.parsing.docling_parser module."""

import tempfile
from pathlib import Path

import pytest

from contractiq.parsing.docling_parser import DoclingParser
from contractiq.parsing.models import ParsedDocument


class TestDoclingParser:
    """Tests for the DoclingParser class."""

    def setup_method(self):
        self.parser = DoclingParser()

    def test_docling_parser_init(self):
        assert isinstance(self.parser, DoclingParser)
        assert isinstance(self.parser.is_available, bool)

    def test_parse_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            self.parser.parse("/nonexistent/file.pdf")

    def test_unsupported_extension_raises(self):
        if self.parser.is_available:
            pytest.skip("Docling is installed; unsupported-extension fallback does not apply")
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"Some plain text content")
            tmp_path = tmp.name
        try:
            with pytest.raises(ValueError):
                self.parser.parse(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_is_available_property(self):
        # Depending on whether docling is installed, either True or False is valid.
        result = self.parser.is_available
        assert result is True or result is False
