"""Load and manage mandatory clause definitions from YAML."""

from pathlib import Path
from typing import Any

import yaml

from contractiq.config import get_settings


class ClauseRegistry:
    """Registry of mandatory contract clauses loaded from YAML config."""

    def __init__(self, yaml_path: str | None = None):
        settings = get_settings()
        self._path = Path(yaml_path or settings.mandatory_clauses_path)
        self._clauses: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load clause definitions from YAML file."""
        if not self._path.exists():
            raise FileNotFoundError(f"Mandatory clauses file not found: {self._path}")

        with open(self._path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self._clauses = data.get("clauses", [])

    @property
    def all_clauses(self) -> list[dict[str, Any]]:
        return self._clauses

    def get_by_severity(self, severity: str) -> list[dict[str, Any]]:
        """Get clauses filtered by severity level."""
        return [c for c in self._clauses if c.get("severity") == severity]

    @property
    def critical(self) -> list[dict[str, Any]]:
        return self.get_by_severity("critical")

    @property
    def major(self) -> list[dict[str, Any]]:
        return self.get_by_severity("major")

    @property
    def minor(self) -> list[dict[str, Any]]:
        return self.get_by_severity("minor")

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        """Find a clause by name (case-insensitive)."""
        for c in self._clauses:
            if c["name"].lower() == name.lower():
                return c
        return None
