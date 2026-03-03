"""Zero Trust Access Control — re-verify permissions on every query."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class DocumentClassification(str, Enum):
    """Sensitivity classification for contract documents."""

    PUBLIC = "PUBLIC"
    CONFIDENTIAL = "CONFIDENTIAL"
    HIGHLY_CONFIDENTIAL = "HIGHLY_CONFIDENTIAL"


class UserRole(str, Enum):
    """Roles available within the ContractIQ platform."""

    VIEWER = "VIEWER"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"


# ---------------------------------------------------------------------------
# Access Control
# ---------------------------------------------------------------------------

class AccessControl:
    """Zero Trust access-control layer.

    Design principle: **never cache authorisation decisions**.  Every call to
    :meth:`check_access` or :meth:`filter_results` re-evaluates permissions
    from scratch so that role changes take effect immediately.

    Usage::

        ac = AccessControl()
        if ac.check_access(UserRole.ANALYST, DocumentClassification.CONFIDENTIAL):
            ...  # proceed

        safe_results = ac.filter_results(raw_results, user_role=UserRole.VIEWER)
    """

    # Maps each role to the set of document classifications it may access.
    ROLE_PERMISSIONS: dict[UserRole, set[DocumentClassification]] = {
        UserRole.VIEWER: {
            DocumentClassification.PUBLIC,
        },
        UserRole.ANALYST: {
            DocumentClassification.PUBLIC,
            DocumentClassification.CONFIDENTIAL,
        },
        UserRole.ADMIN: {
            DocumentClassification.PUBLIC,
            DocumentClassification.CONFIDENTIAL,
            DocumentClassification.HIGHLY_CONFIDENTIAL,
        },
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_access(
        self,
        user_role: UserRole,
        document_classification: DocumentClassification,
    ) -> bool:
        """Return ``True`` if *user_role* is permitted to view documents
        classified as *document_classification*.

        This method is intentionally stateless — it re-evaluates the
        permission mapping on every call (Zero Trust).
        """
        allowed = self.ROLE_PERMISSIONS.get(user_role, set())
        granted = document_classification in allowed

        if not granted:
            logger.info(
                "Access denied: role=%s cannot access classification=%s",
                user_role.value,
                document_classification.value,
            )

        return granted

    def filter_results(
        self,
        results: list[Any],
        user_role: UserRole,
    ) -> list[Any]:
        """Return only those *results* the *user_role* is allowed to see.

        Each result is expected to carry a ``metadata`` attribute (or behave
        as a dict) with an optional ``"classification"`` key whose value is
        either a :class:`DocumentClassification` member or its string name.

        Results lacking a classification are treated as
        :attr:`DocumentClassification.HIGHLY_CONFIDENTIAL` (deny by default).

        Parameters
        ----------
        results:
            Iterable of retrieval results (Pydantic models, dicts, or any
            object exposing a ``metadata`` mapping).
        user_role:
            The role of the user making the request.

        Returns
        -------
        list
            A filtered copy of *results* containing only permitted items.
        """
        permitted: list[Any] = []

        for result in results:
            classification = self._extract_classification(result)
            if self.check_access(user_role, classification):
                permitted.append(result)

        removed = len(results) - len(permitted)
        if removed:
            logger.info(
                "Filtered %d result(s) for role=%s",
                removed,
                user_role.value,
            )

        return permitted

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_classification(result: Any) -> DocumentClassification:
        """Best-effort extraction of a :class:`DocumentClassification` from *result*.

        Falls back to ``HIGHLY_CONFIDENTIAL`` when the classification cannot
        be determined (deny by default).
        """
        metadata: dict[str, Any] | None = None

        # Support dict-like results
        if isinstance(result, dict):
            metadata = result.get("metadata", result)
        # Support objects with a .metadata attribute (e.g., Pydantic models)
        elif hasattr(result, "metadata"):
            meta_attr = getattr(result, "metadata")
            if isinstance(meta_attr, dict):
                metadata = meta_attr
            elif hasattr(meta_attr, "get"):
                metadata = meta_attr  # type: ignore[assignment]

        if metadata is None:
            return DocumentClassification.HIGHLY_CONFIDENTIAL

        raw = metadata.get("classification")
        if raw is None:
            return DocumentClassification.HIGHLY_CONFIDENTIAL

        if isinstance(raw, DocumentClassification):
            return raw

        # Accept string values (e.g., "CONFIDENTIAL")
        try:
            return DocumentClassification(str(raw).upper())
        except ValueError:
            logger.warning(
                "Unknown classification value %r — defaulting to HIGHLY_CONFIDENTIAL",
                raw,
            )
            return DocumentClassification.HIGHLY_CONFIDENTIAL
