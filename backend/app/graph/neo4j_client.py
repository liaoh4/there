"""
Neo4j client — v2 stub.
When NEO4J_URL is not set, all operations are no-ops so v1 runs without a graph DB.
"""

import os


class Neo4jClient:
    def __init__(self) -> None:
        self._url = os.getenv("NEO4J_URL")
        self._driver = None

        if self._url:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(
                self._url,
                auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "")),
            )

    @property
    def available(self) -> bool:
        return self._driver is not None

    def close(self) -> None:
        if self._driver:
            self._driver.close()


neo4j_client = Neo4jClient()
