"""Docling-based multi-format document parser with graceful fallback."""

from __future__ import annotations

import logging
from pathlib import Path

from contractiq.parsing.models import ParsedDocument

logger = logging.getLogger(__name__)

# Supported file extensions that Docling can handle.
_DOCLING_EXTENSIONS: set[str] = {
    ".pdf", ".docx", ".pptx", ".html", ".htm", ".md", ".markdown",
    ".png", ".jpg", ".jpeg", ".tiff", ".bmp",
}


class DoclingParser:
    """Multi-format document parser powered by `Docling <https://github.com/DS4SD/docling>`_.

    If Docling is not installed the parser automatically falls back to the
    existing PyMuPDF / python-docx parsers that ship with ContractIQ.

    Supported formats: PDF, DOCX, PPTX, HTML, Markdown, and images.

    Usage::

        parser = DoclingParser()
        if parser.is_available:
            doc = parser.parse("/path/to/contract.pdf")
        else:
            # Docling not installed — use legacy parsers directly
            ...
    """

    def __init__(self) -> None:
        self._available: bool = False
        self._document_converter_cls: type | None = None

        try:
            from docling.document_converter import DocumentConverter  # type: ignore[import-untyped]

            self._document_converter_cls = DocumentConverter
            self._available = True
            logger.info("Docling is available — multi-format parsing enabled")
        except ImportError:
            logger.warning(
                "Docling is not installed. Install it with "
                "'pip install docling' to enable multi-format parsing. "
                "Falling back to built-in PDF/DOCX parsers."
            )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_available(self) -> bool:
        """Return ``True`` if the Docling library was successfully imported."""
        return self._available

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, file_path: str | Path) -> ParsedDocument:
        """Parse a document file and return a :class:`ParsedDocument`.

        When Docling is installed the file is routed through
        :meth:`_parse_with_docling`.  Otherwise, built-in parsers for PDF
        and DOCX are used via :meth:`_fallback_parse`.

        Parameters
        ----------
        file_path:
            Absolute or relative path to the document.

        Returns
        -------
        ParsedDocument
            The extracted content including text, tables, and metadata.

        Raises
        ------
        FileNotFoundError
            If *file_path* does not exist.
        ValueError
            If the file extension is not supported by any available parser.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        if self._available and path.suffix.lower() in _DOCLING_EXTENSIONS:
            return self._parse_with_docling(path)

        return self._fallback_parse(path)

    # ------------------------------------------------------------------
    # Docling path
    # ------------------------------------------------------------------

    def _parse_with_docling(self, file_path: Path) -> ParsedDocument:
        """Use Docling's ``DocumentConverter`` to parse the file.

        Docling provides a unified conversion pipeline that handles PDF,
        DOCX, PPTX, HTML, Markdown, and image files.
        """
        errors: list[str] = []

        try:
            converter = self._document_converter_cls()  # type: ignore[misc]
            result = converter.convert(str(file_path))

            # Docling returns a ConversionResult whose `.document` has an
            # `export_to_markdown()` method.
            doc = result.document
            raw_text: str = doc.export_to_markdown() if hasattr(doc, "export_to_markdown") else str(doc)

            # Attempt to extract tables if the document exposes them.
            tables: list[list[list[str]]] = []
            if hasattr(doc, "tables"):
                for table in doc.tables:
                    rows: list[list[str]] = []
                    if hasattr(table, "export_to_dataframe"):
                        df = table.export_to_dataframe()
                        # Header row
                        rows.append([str(c) for c in df.columns.tolist()])
                        for _, row in df.iterrows():
                            rows.append([str(v) for v in row.tolist()])
                    if rows:
                        tables.append(rows)

            # Best-effort page count.
            page_count = 0
            if hasattr(doc, "pages"):
                page_count = len(doc.pages)
            elif raw_text:
                # Rough heuristic: ~3000 chars per page.
                page_count = max(1, len(raw_text) // 3000)

            return ParsedDocument(
                file_name=file_path.name,
                file_path=str(file_path),
                file_type=file_path.suffix.lstrip(".").lower(),
                raw_text=raw_text,
                page_count=page_count,
                tables=tables,
                parse_errors=errors,
            )

        except Exception as exc:
            logger.error("Docling parsing failed for %s: %s", file_path, exc)
            errors.append(f"Docling error: {exc}")
            # Fall through to legacy parsers.
            return self._fallback_parse(file_path, extra_errors=errors)

    # ------------------------------------------------------------------
    # Fallback path
    # ------------------------------------------------------------------

    def _fallback_parse(
        self,
        file_path: Path,
        *,
        extra_errors: list[str] | None = None,
    ) -> ParsedDocument:
        """Parse using the built-in PyMuPDF and python-docx parsers.

        Only PDF and DOCX are supported on the fallback path.
        """
        from contractiq.parsing.pdf_parser import parse_pdf
        from contractiq.parsing.docx_parser import parse_docx

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            doc = parse_pdf(file_path)
        elif suffix in {".docx"}:
            doc = parse_docx(file_path)
        else:
            raise ValueError(
                f"Unsupported file type '{suffix}' and Docling is not available. "
                f"Install Docling with 'pip install docling' for {suffix} support."
            )

        if extra_errors:
            doc.parse_errors.extend(extra_errors)

        return doc
