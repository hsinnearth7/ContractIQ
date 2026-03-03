"""Layer 3: Output Validation — ensure generated answers are grounded and cited."""

from __future__ import annotations

import logging
import re

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

class ValidationResult(BaseModel):
    """Outcome of validating a single generated answer."""

    is_valid: bool = Field(description="Whether the answer passed all validation checks")
    has_citations: bool = Field(description="Whether the answer contains source citations")
    citation_count: int = Field(
        default=0,
        description="Number of distinct citations found in the answer",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Human-readable descriptions of validation failures",
    )


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class OutputValidator:
    """Validate that LLM-generated answers are grounded in retrieved sources.

    Checks performed:

    1. The answer must reference at least one source via Section / Contract /
       Clause citations.
    2. The answer must not contain phrases that signal the model lacks access
       to the underlying documents.
    3. The answer should be free of hedging phrases that often indicate
       hallucination.

    Usage::

        validator = OutputValidator()
        result = validator.validate(answer_text, source_chunks)
        if not result.is_valid:
            # re-generate or warn user
            ...
    """

    # Regex patterns that count as valid source citations.
    _CITATION_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"\bSection\s+\d+", re.IGNORECASE),
        re.compile(r"\bClause\s+\d+", re.IGNORECASE),
        re.compile(r"\bArticle\s+\d+", re.IGNORECASE),
        re.compile(r"\bContract\s+#?\w+", re.IGNORECASE),
        re.compile(r"\bAgreement\s+#?\w+", re.IGNORECASE),
        re.compile(r"\bSchedule\s+[A-Z0-9]", re.IGNORECASE),
        re.compile(r"\bExhibit\s+[A-Z0-9]", re.IGNORECASE),
        re.compile(r"\bAppendix\s+[A-Z0-9]", re.IGNORECASE),
        # Bracket-style references such as [Source 1] or [1]
        re.compile(r"\[Source\s+\d+\]", re.IGNORECASE),
        re.compile(r"\[\d+\]"),
    ]

    # Phrases that indicate the model is admitting it cannot answer.
    _NO_ACCESS_PHRASES: list[str] = [
        "I don't have access",
        "I do not have access",
        "I cannot access",
        "I'm unable to access",
        "I am unable to access",
        "not available to me",
        "outside my knowledge",
    ]

    # Hedging phrases that often signal hallucination.
    _HALLUCINATION_MARKERS: list[str] = [
        "I believe",
        "I think",
        "it is possible that",
        "it might be",
        "I'm not sure",
        "I am not sure",
        "this may not be accurate",
        "I cannot verify",
        "I can not verify",
        "to the best of my knowledge",
        "hypothetically",
    ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, answer: str, sources: list[object] | None = None) -> ValidationResult:
        """Validate *answer* against the provided *sources*.

        Parameters
        ----------
        answer:
            The LLM-generated answer text.
        sources:
            List of source chunks / documents used for retrieval.  When the
            list is empty or ``None`` the answer is expected to at least
            contain inline citations.

        Returns
        -------
        ValidationResult
            A structured validation outcome.
        """
        issues: list[str] = []

        # --- Citation check ---
        has_citations = self._check_citations(answer)
        citation_count = self._count_citations(answer)

        if not has_citations:
            issues.append("Answer lacks source citations")

        # --- No-access phrases ---
        answer_lower = answer.lower()
        for phrase in self._NO_ACCESS_PHRASES:
            if phrase.lower() in answer_lower:
                issues.append(f"Answer contains no-access phrase: \"{phrase}\"")
                break  # one match is enough

        # --- Hallucination markers ---
        hallucination_issues = self._check_hallucination_markers(answer)
        if hallucination_issues:
            issues.extend(hallucination_issues)

        # --- Source cross-reference ---
        if sources is not None and len(sources) > 0 and not has_citations:
            issues.append(
                "Sources were provided but the answer does not reference any of them"
            )

        is_valid = len(issues) == 0

        if not is_valid:
            logger.warning("Output validation failed: %s", issues)

        return ValidationResult(
            is_valid=is_valid,
            has_citations=has_citations,
            citation_count=citation_count,
            issues=issues,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_citations(self, answer: str) -> bool:
        """Return ``True`` if *answer* contains at least one citation reference."""
        return any(p.search(answer) for p in self._CITATION_PATTERNS)

    def _count_citations(self, answer: str) -> int:
        """Count the total number of distinct citation matches in *answer*."""
        matches: set[str] = set()
        for pattern in self._CITATION_PATTERNS:
            for m in pattern.finditer(answer):
                matches.add(m.group())
        return len(matches)

    def _check_hallucination_markers(self, answer: str) -> list[str]:
        """Return a list of issue strings for any hedging phrases found in *answer*."""
        issues: list[str] = []
        answer_lower = answer.lower()
        for marker in self._HALLUCINATION_MARKERS:
            if marker.lower() in answer_lower:
                issues.append(f"Possible hallucination marker detected: \"{marker}\"")
        return issues
