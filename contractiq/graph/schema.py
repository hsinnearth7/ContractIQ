"""Knowledge graph schema definitions."""

from pathlib import Path
from typing import Any

import yaml

from contractiq.config import get_settings


# Node labels
SUPPLIER = "Supplier"
BUYER = "Buyer"
CONTRACT = "Contract"
CLAUSE = "Clause"
OBLIGATION = "Obligation"
PARTY = "Party"

# Relationship types
SUPPLIES_TO = "SUPPLIES_TO"
HAS_CONTRACT = "HAS_CONTRACT"
HAS_CLAUSE = "HAS_CLAUSE"
OBLIGATES = "OBLIGATES"
SIGNED_BY = "SIGNED_BY"
PARTIES_TO = "PARTIES_TO"
SIMILAR_CLAUSE = "SIMILAR_CLAUSE"


def load_graph_schema(path: str | None = None) -> dict[str, Any]:
    """Load graph schema from YAML config."""
    settings = get_settings()
    schema_path = Path(path or settings.graph_schema_path)

    if not schema_path.exists():
        return {"nodes": [], "relationships": []}

    with open(schema_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Cypher constraint statements for schema enforcement
SCHEMA_CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Supplier) REQUIRE s.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (b:Buyer) REQUIRE b.name IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Contract) REQUIRE c.agreement_number IS UNIQUE",
]

# Index statements for query performance
SCHEMA_INDEXES = [
    "CREATE INDEX IF NOT EXISTS FOR (c:Clause) ON (c.clause_type)",
    "CREATE INDEX IF NOT EXISTS FOR (c:Contract) ON (c.contract_type)",
    "CREATE INDEX IF NOT EXISTS FOR (o:Obligation) ON (o.obligation_type)",
]
