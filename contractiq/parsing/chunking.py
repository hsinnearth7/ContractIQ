"""Three chunking strategies: Recursive, Semantic, and ClauseAware."""

import re
import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter

from contractiq.parsing.models import ParsedDocument, DocumentChunk


# --- Clause-aware heading patterns ---
CLAUSE_PATTERNS = [
    re.compile(r"^#{1,3}\s+", re.MULTILINE),  # Markdown headings
    re.compile(r"^ARTICLE\s+\d+", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^Section\s+\d+", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^\d+\.\s+[A-Z][A-Z\s]+$", re.MULTILINE),  # "1. TERM AND TERMINATION"
    re.compile(r"^\d+\.\d+\s+", re.MULTILINE),  # "1.1 Sub-section"
]


def _make_chunk_id(doc_id: str, index: int) -> str:
    raw = f"{doc_id}::{index}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _doc_id(doc: ParsedDocument) -> str:
    return doc.file_name.rsplit(".", 1)[0]


def _build_chunks(
    doc: ParsedDocument,
    texts: list[str],
    strategy: str,
    section_titles: list[str] | None = None,
) -> list[DocumentChunk]:
    """Convert raw text splits into DocumentChunk objects."""
    doc_id = _doc_id(doc)
    section_titles = section_titles or [""] * len(texts)
    chunks: list[DocumentChunk] = []
    offset = 0

    flat_meta = {}
    if doc.metadata:
        m = doc.metadata
        flat_meta = {
            "supplier_name": m.supplier_name,
            "contract_type": m.contract_type.value if m.contract_type else "",
            "agreement_number": m.agreement_number,
            "file_name": doc.file_name,
        }

    for i, text in enumerate(texts):
        if not text.strip():
            continue
        chunk = DocumentChunk(
            chunk_id=_make_chunk_id(doc_id, i),
            document_id=doc_id,
            text=text,
            chunk_index=i,
            total_chunks=len(texts),
            start_char=offset,
            end_char=offset + len(text),
            section_title=section_titles[i] if i < len(section_titles) else "",
            chunk_strategy=strategy,
            metadata=flat_meta,
        )
        chunks.append(chunk)
        offset += len(text)

    return chunks


def chunk_recursive(
    doc: ParsedDocument,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    """Split using LangChain's RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    texts = splitter.split_text(doc.raw_text)
    return _build_chunks(doc, texts, "recursive")


def chunk_semantic(
    doc: ParsedDocument,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    """Semantic chunking using paragraph boundaries with size limits.

    Splits on double newlines (paragraph boundaries) first, then merges
    small paragraphs and splits large ones.
    """
    paragraphs = [p.strip() for p in doc.raw_text.split("\n\n") if p.strip()]

    merged: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                merged.append(current)
            # If single paragraph exceeds chunk_size, split it
            if len(para) > chunk_size:
                sub_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
                merged.extend(sub_splitter.split_text(para))
            else:
                current = para
                continue
            current = ""

    if current:
        merged.append(current)

    return _build_chunks(doc, merged, "semantic")


def chunk_clause_aware(
    doc: ParsedDocument,
    chunk_size: int = 1500,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    """Split on contract clause/article boundaries.

    Detects headings like ARTICLE N, Section N, or markdown headings,
    then keeps each clause as a chunk (splitting if too large).
    """
    text = doc.raw_text
    # Find all clause boundary positions
    boundaries: list[tuple[int, str]] = []

    for pattern in CLAUSE_PATTERNS:
        for match in pattern.finditer(text):
            # Extract section title from the matched line
            line_end = text.find("\n", match.start())
            if line_end == -1:
                line_end = len(text)
            title = text[match.start():line_end].strip().lstrip("#").strip()
            boundaries.append((match.start(), title))

    # Sort by position and deduplicate nearby boundaries
    boundaries.sort(key=lambda x: x[0])
    if not boundaries:
        # No clause boundaries found, fall back to recursive
        return chunk_recursive(doc, chunk_size, chunk_overlap)

    # Split text into sections
    sections: list[str] = []
    section_titles: list[str] = []

    for i, (pos, title) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
        section_text = text[pos:end].strip()
        if section_text:
            sections.append(section_text)
            section_titles.append(title)

    # Add any text before the first boundary
    if boundaries[0][0] > 0:
        preamble = text[:boundaries[0][0]].strip()
        if preamble:
            sections.insert(0, preamble)
            section_titles.insert(0, "Preamble")

    # Split oversized sections
    final_texts: list[str] = []
    final_titles: list[str] = []
    sub_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    for sec_text, sec_title in zip(sections, section_titles):
        if len(sec_text) <= chunk_size:
            final_texts.append(sec_text)
            final_titles.append(sec_title)
        else:
            sub_texts = sub_splitter.split_text(sec_text)
            for j, st in enumerate(sub_texts):
                final_texts.append(st)
                suffix = f" (part {j + 1})" if len(sub_texts) > 1 else ""
                final_titles.append(f"{sec_title}{suffix}")

    return _build_chunks(doc, final_texts, "clause_aware", final_titles)


CHUNKING_STRATEGIES = {
    "recursive": chunk_recursive,
    "semantic": chunk_semantic,
    "clause_aware": chunk_clause_aware,
}


def chunk_document(
    doc: ParsedDocument,
    strategy: str = "recursive",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    """Chunk a document using the specified strategy."""
    fn = CHUNKING_STRATEGIES.get(strategy)
    if fn is None:
        raise ValueError(f"Unknown strategy: {strategy}. Use: {list(CHUNKING_STRATEGIES)}")
    return fn(doc, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
