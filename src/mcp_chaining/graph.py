#!/usr/bin/env python3
"""graph_engine.py — Portable NetworkX Tool Graph for Tool Chaining.

Provides semantic relationship queries (friends, opponents, pipelines),
path routing, and automatic semantic onboarding for any user tool.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .db import get_db_path, init_db

try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None


class SimpleMultiDiGraph:
    """Zero-dependency pure-Python fallback for NetworkX MultiDiGraph."""

    def __init__(self):
        self._nodes: dict[str, dict[str, Any]] = {}
        self._adj: dict[str, list[tuple[str, str, dict[str, Any]]]] = {}
        self._edges_count = 0

    def clear(self):
        self._nodes.clear()
        self._adj.clear()
        self._edges_count = 0

    def add_node(self, node_for_adding: str, **attr):
        self._nodes[node_for_adding] = attr
        if node_for_adding not in self._adj:
            self._adj[node_for_adding] = []

    def add_edge(self, u_for_edge: str, v_for_edge: str, key: str | None = None, **attr):
        if u_for_edge not in self._nodes:
            self.add_node(u_for_edge)
        if v_for_edge not in self._nodes:
            self.add_node(v_for_edge)
        self._adj[u_for_edge].append((u_for_edge, v_for_edge, attr))
        self._edges_count += 1

    def out_edges(self, nbunch: str, data: bool = False):
        edges = self._adj.get(nbunch, [])
        if data:
            return [(u, v, d) for u, v, d in edges]
        return [(u, v) for u, v, _ in edges]

    @property
    def nodes(self):
        class NodeView:
            def __init__(self, nodes_dict: dict[str, dict[str, Any]]):
                self._d = nodes_dict

            def get(self, k: str, default: Any = None) -> Any:
                return self._d.get(k, default)

            def __call__(self, data: bool = False):
                if data:
                    return list(self._d.items())
                return list(self._d.keys())

            def __contains__(self, k: str) -> bool:
                return k in self._d

            def __iter__(self):
                return iter(self._d)

        return NodeView(self._nodes)

    def edges(self, data: bool = False):
        all_edges = []
        for out in self._adj.values():
            for u, v, d in out:
                if data:
                    all_edges.append((u, v, d))
                else:
                    all_edges.append((u, v))
        return all_edges

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def number_of_edges(self) -> int:
        return self._edges_count

    def __contains__(self, n: str) -> bool:
        return n in self._nodes


class PortableToolGraph:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_db_path()
        if not self.db_path.exists():
            init_db(self.db_path)
        self.graph = (
            nx.MultiDiGraph() if (HAS_NETWORKX and nx is not None) else SimpleMultiDiGraph()
        )
        self.load()

    def get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def load(self):
        self.graph.clear()
        conn = self.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, server_name, tool_name, category, description, read_only, sandbox_safe, capability_weight FROM tools"
            )
            for row in cur.fetchall():
                self.graph.add_node(
                    row[0],
                    server_name=row[1],
                    tool_name=row[2],
                    category=row[3],
                    description=row[4],
                    read_only=bool(row[5]),
                    sandbox_safe=bool(row[6]),
                    capability_weight=row[7],
                )

            cur.execute(
                "SELECT source_tool_id, target_tool_id, relationship_type, weight, rationale FROM tool_relationships"
            )
            for row in cur.fetchall():
                self.graph.add_edge(
                    row[0],
                    row[1],
                    key=row[2],
                    relationship_type=row[2],
                    weight=row[3],
                    rationale=row[4],
                )
        finally:
            conn.close()

    def get_friends(self, tool_id: str) -> list[dict[str, Any]]:
        """Return tools that complement or ingest from the target tool."""
        friends = []
        if tool_id in self.graph:
            for _, target, data in self.graph.out_edges(tool_id, data=True):
                if data.get("relationship_type") in ("COMPLEMENTS", "PIPES_TO"):
                    target_data = self.graph.nodes.get(target, {})
                    friends.append(
                        {
                            "target_tool": target,
                            "relationship": data.get("relationship_type"),
                            "weight": data.get("weight"),
                            "rationale": data.get("rationale"),
                            "category": target_data.get("category", "unknown"),
                        }
                    )
        return friends

    def get_opponents(self, tool_id: str) -> list[dict[str, Any]]:
        """Return tools that act as adversarial critics or quality gates."""
        opponents = []
        if tool_id in self.graph:
            for _, target, data in self.graph.out_edges(tool_id, data=True):
                if data.get("relationship_type") == "OPPOSES":
                    target_data = self.graph.nodes.get(target, {})
                    opponents.append(
                        {
                            "target_tool": target,
                            "relationship": "OPPOSES",
                            "weight": data.get("weight"),
                            "rationale": data.get("rationale"),
                            "category": target_data.get("category", "unknown"),
                        }
                    )
        return opponents

    def onboard_tool(
        self,
        tool_id: str,
        server_name: str,
        tool_name: str,
        category: str,
        description: str,
        read_only: bool = True,
        sandbox_safe: bool = True,
        capability_weight: float = 1.0,
    ) -> dict[str, Any]:
        """Automatically register a new tool and infer its semantic relationships."""
        if not tool_id or len(tool_id) > 128:
            raise ValueError("Invalid tool_id: must be non-empty and <= 128 characters")
        if capability_weight <= 0.0:
            raise ValueError("capability_weight must be strictly positive")

        conn = self.get_conn()
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT OR REPLACE INTO tools (id, server_name, tool_name, category, description, read_only, sandbox_safe, capability_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tool_id,
                        server_name,
                        tool_name,
                        category,
                        description,
                        int(read_only),
                        int(sandbox_safe),
                        float(capability_weight),
                    ),
                )

                relationships_added = []
                category_lower = category.lower()

                # Inferred relationships
                if "compute" in category_lower or "code" in category_lower:
                    relationships_added.append(
                        (
                            tool_id,
                            "security/osvScanner",
                            "OPPOSES",
                            1.9,
                            "Automated vulnerability check on generated code",
                        )
                    )
                    relationships_added.append(
                        (
                            tool_id,
                            "clean_code/refactor_gate",
                            "OPPOSES",
                            1.8,
                            "Clean code review blocks premature abstractions",
                        )
                    )
                elif "docs" in category_lower or "search" in category_lower:
                    relationships_added.append(
                        (
                            tool_id,
                            "context-mode/ctx_execute",
                            "COMPLEMENTS",
                            1.7,
                            "Supplies signatures directly to sandbox execution",
                        )
                    )
                elif "security" in category_lower:
                    relationships_added.append(
                        (
                            tool_id,
                            "mempalace/checkpoint",
                            "COMPLEMENTS",
                            1.6,
                            "Persists security audit sign-offs to memory",
                        )
                    )

                for rel in relationships_added:
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO tool_relationships (source_tool_id, target_tool_id, relationship_type, weight, rationale)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        rel,
                    )
        finally:
            conn.close()

        self.load()
        return {
            "status": "ONBOARDED",
            "tool_id": tool_id,
            "category": category,
            "relationships_inferred": len(relationships_added),
        }

    def summary(self) -> dict[str, Any]:
        categories: dict[str, int] = {}
        for _, data in self.graph.nodes(data=True):
            cat = data.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        rel_types: dict[str, int] = {}
        for _, _, data in self.graph.edges(data=True):
            rt = data.get("relationship_type", "unknown")
            rel_types[rt] = rel_types.get(rt, 0) + 1

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "categories": categories,
            "relationship_types": rel_types,
            "db_path": str(self.db_path),
        }
