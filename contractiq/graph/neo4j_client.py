"""Neo4j connection management."""

from typing import Any

from neo4j import GraphDatabase

from contractiq.config import get_settings
from contractiq.graph.schema import SCHEMA_CONSTRAINTS, SCHEMA_INDEXES


class Neo4jClient:
    """Manages Neo4j driver lifecycle and query execution."""

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ):
        settings = get_settings()
        self._uri = uri or settings.neo4j_uri
        self._username = username or settings.neo4j_username
        self._password = password or settings.neo4j_password
        self._database = database or settings.neo4j_database
        self._driver = None

    def _get_driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=(self._username, self._password),
            )
        return self._driver

    def verify_connectivity(self) -> bool:
        """Test if Neo4j is reachable."""
        try:
            driver = self._get_driver()
            driver.verify_connectivity()
            return True
        except Exception:
            return False

    def run_query(
        self,
        cypher: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results.

        Args:
            cypher: Cypher query string.
            parameters: Query parameters.

        Returns:
            List of result records as dicts.
        """
        driver = self._get_driver()
        with driver.session(database=self._database) as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

    def run_write(
        self,
        cypher: str,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        """Execute a write Cypher query."""
        driver = self._get_driver()
        with driver.session(database=self._database) as session:
            session.run(cypher, parameters or {})

    def init_schema(self) -> None:
        """Create constraints and indexes."""
        for stmt in SCHEMA_CONSTRAINTS + SCHEMA_INDEXES:
            try:
                self.run_write(stmt)
            except Exception as e:
                print(f"Schema init warning: {e}")

    def clear_all(self) -> None:
        """Delete all nodes and relationships (use with caution)."""
        self.run_write("MATCH (n) DETACH DELETE n")

    def get_stats(self) -> dict[str, int]:
        """Get node and relationship counts."""
        result = self.run_query(
            "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count"
        )
        stats = {r["label"]: r["count"] for r in result}

        rel_result = self.run_query(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count"
        )
        for r in rel_result:
            stats[f"rel:{r['type']}"] = r["count"]

        return stats

    def close(self) -> None:
        if self._driver:
            self._driver.close()
            self._driver = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
