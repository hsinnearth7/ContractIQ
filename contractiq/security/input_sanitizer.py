"""Layer 1: Input Sanitization — detect and neutralize prompt injection attempts."""

from __future__ import annotations

import logging
import re

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

class SanitizationResult(BaseModel):
    """Outcome of sanitizing a single user input string."""

    original_input: str = Field(description="The raw user input before sanitization")
    sanitized_input: str = Field(description="The cleaned user input after sanitization")
    is_safe: bool = Field(description="Whether the input is considered safe")
    threats_detected: list[str] = Field(
        default_factory=list,
        description="Names of detected threat patterns",
    )
    risk_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall risk score from 0 (safe) to 1 (dangerous)",
    )


# ---------------------------------------------------------------------------
# Sanitizer
# ---------------------------------------------------------------------------

class InputSanitizer:
    """Scans user input for prompt-injection patterns and returns a risk assessment.

    Usage::

        sanitizer = InputSanitizer()
        result = sanitizer.sanitize("Tell me about clause 4.2")
        if not result.is_safe:
            raise SecurityError(result.threats_detected)
    """

    # Each tuple is (pattern_name, compiled_regex).  Patterns are evaluated
    # case-insensitively against the full input string.
    INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
        (
            "ignore_previous_instructions",
            re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
        ),
        (
            "forget_instructions",
            re.compile(r"forget\s+(all\s+)?(your\s+)?instructions", re.IGNORECASE),
        ),
        (
            "identity_override",
            re.compile(r"you\s+are\s+now\b", re.IGNORECASE),
        ),
        (
            "system_prompt_leak",
            re.compile(r"system\s*prompt\s*:", re.IGNORECASE),
        ),
        (
            "role_hijack",
            re.compile(r"\bact\s+as\b", re.IGNORECASE),
        ),
        (
            "prompt_reveal",
            re.compile(r"reveal\s+(your\s+)?prompt", re.IGNORECASE),
        ),
        (
            "override_attempt",
            re.compile(r"\boverride\b", re.IGNORECASE),
        ),
        (
            "instruction_injection",
            re.compile(r"\[INST\]|\[/INST\]|<<SYS>>|<\|im_start\|>", re.IGNORECASE),
        ),
        (
            "delimiter_injection",
            re.compile(r"```\s*system\b|###\s*system\b", re.IGNORECASE),
        ),
        (
            "do_anything_now",
            re.compile(r"\bDAN\b|do\s+anything\s+now", re.IGNORECASE),
        ),
    ]

    # Weights allow certain threat categories to contribute more to the risk
    # score.  Patterns not listed here default to a weight of 1.0.
    _THREAT_WEIGHTS: dict[str, float] = {
        "ignore_previous_instructions": 1.5,
        "system_prompt_leak": 1.5,
        "instruction_injection": 2.0,
        "identity_override": 1.3,
        "do_anything_now": 1.8,
    }

    # If the cumulative risk score meets or exceeds this threshold the input
    # is flagged as unsafe.
    RISK_THRESHOLD: float = 0.3

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sanitize(self, user_input: str) -> SanitizationResult:
        """Check *user_input* against known injection patterns.

        Returns a :class:`SanitizationResult` containing the sanitized text,
        detected threats, risk score, and an ``is_safe`` flag.
        """
        threats = self._detect_threats(user_input)
        risk = self._calculate_risk(threats)
        sanitized = self._strip_dangerous_tokens(user_input) if threats else user_input
        is_safe = risk < self.RISK_THRESHOLD

        if not is_safe:
            logger.warning(
                "Prompt injection detected (risk=%.2f): %s",
                risk,
                threats,
            )

        return SanitizationResult(
            original_input=user_input,
            sanitized_input=sanitized,
            is_safe=is_safe,
            threats_detected=threats,
            risk_score=risk,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _detect_threats(self, text: str) -> list[str]:
        """Return a list of threat-pattern names that matched *text*."""
        detected: list[str] = []
        for name, pattern in self.INJECTION_PATTERNS:
            if pattern.search(text):
                detected.append(name)
        return detected

    def _calculate_risk(self, threats: list[str]) -> float:
        """Compute a 0-1 risk score from the list of detected threat names.

        The score is the weighted sum of matched threats divided by the
        theoretical maximum (sum of all weights), clamped to [0, 1].
        """
        if not threats:
            return 0.0

        weighted_sum = sum(
            self._THREAT_WEIGHTS.get(t, 1.0) for t in threats
        )
        max_possible = sum(
            w for _, w in self._THREAT_WEIGHTS.items()
        ) + max(0, len(self.INJECTION_PATTERNS) - len(self._THREAT_WEIGHTS))

        return min(weighted_sum / max_possible, 1.0)

    @staticmethod
    def _strip_dangerous_tokens(text: str) -> str:
        """Remove control-style tokens that could be interpreted by an LLM."""
        cleaned = re.sub(
            r"\[INST\]|\[/INST\]|<<SYS>>|<\|im_start\|>|<\|im_end\|>",
            "",
            text,
            flags=re.IGNORECASE,
        )
        # Collapse multiple whitespace runs introduced by removal
        cleaned = re.sub(r"  +", " ", cleaned).strip()
        return cleaned
