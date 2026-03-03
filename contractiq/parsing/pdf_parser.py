"""PDF parsing using PyMuPDF4LLM (primary) with pdfplumber table fallback."""

from pathlib import Path

import pymupdf4llm
import pdfplumber

from contractiq.parsing.models import ParsedDocument


def parse_pdf(file_path: str | Path) -> ParsedDocument:
    """Parse a PDF file and extract text + tables.

    Uses PyMuPDF4LLM for markdown-formatted text extraction and
    pdfplumber as fallback for table extraction.
    """
    file_path = Path(file_path)
    errors: list[str] = []

    # --- Primary: PyMuPDF4LLM for text ---
    try:
        md_text = pymupdf4llm.to_markdown(str(file_path))
    except Exception as e:
        md_text = ""
        errors.append(f"PyMuPDF4LLM error: {e}")

    # --- Get page count ---
    page_count = 0
    try:
        import pymupdf
        doc = pymupdf.open(str(file_path))
        page_count = len(doc)
        doc.close()
    except Exception:
        pass

    # --- Fallback: pdfplumber for tables ---
    tables: list[list[list[str]]] = []
    try:
        with pdfplumber.open(str(file_path)) as pdf:
            if page_count == 0:
                page_count = len(pdf.pages)
            for page in pdf.pages:
                page_tables = page.extract_tables()
                for table in page_tables:
                    cleaned = [
                        [cell if cell else "" for cell in row]
                        for row in table
                        if any(cell for cell in row)
                    ]
                    if cleaned:
                        tables.append(cleaned)

            # If pymupdf4llm failed, use pdfplumber text
            if not md_text:
                text_parts = []
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
                md_text = "\n\n".join(text_parts)
    except Exception as e:
        errors.append(f"pdfplumber error: {e}")

    return ParsedDocument(
        file_name=file_path.name,
        file_path=str(file_path),
        file_type="pdf",
        raw_text=md_text,
        page_count=page_count,
        tables=tables,
        parse_errors=errors,
    )
