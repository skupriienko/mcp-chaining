#!/usr/bin/env python3
"""mesh_db.py — Portable SQLite FTS5 Mesh Registry for Tool Chaining.

Stores tools, full-text FTS5 index, topological relationships, and golden sequences.
Works 100% standalone out-of-the-box in any project repository.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_MESH_DIR = Path.cwd() / ".mesh"
DEFAULT_MESH_DB = DEFAULT_MESH_DIR / "tool_mesh.db"


def get_db_path() -> Path:
    """Resolve database path from environment or default local project directory with security checks."""
    env_path = os.getenv("TOOL_CHAIN_DB")
    if env_path:
        if "\0" in env_path:
            raise ValueError("Security violation: null byte detected in TOOL_CHAIN_DB path")
        p = Path(env_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            p.parent.chmod(0o700)
        except OSError:
            pass
        return p
    DEFAULT_MESH_DIR.mkdir(parents=True, exist_ok=True)
    try:
        DEFAULT_MESH_DIR.chmod(0o700)
    except OSError:
        pass
    return DEFAULT_MESH_DB.resolve()


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS tools (
    id TEXT PRIMARY KEY,
    server_name TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    input_schema TEXT,
    output_schema TEXT,
    read_only INTEGER DEFAULT 1,
    sandbox_safe INTEGER DEFAULT 1,
    capability_weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS tools_fts USING fts5(
    id,
    server_name,
    tool_name,
    category,
    description,
    content='tools',
    content_rowid='rowid'
);

CREATE TABLE IF NOT EXISTS tool_relationships (
    source_tool_id TEXT NOT NULL,
    target_tool_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    rationale TEXT,
    PRIMARY KEY (source_tool_id, target_tool_id, relationship_type),
    FOREIGN KEY (source_tool_id) REFERENCES tools(id) ON DELETE CASCADE,
    FOREIGN KEY (target_tool_id) REFERENCES tools(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS golden_sequences (
    intent TEXT PRIMARY KEY,
    fsm_sequence TEXT NOT NULL,
    tool_pipeline TEXT NOT NULL,
    estimated_token_saving REAL,
    benchmark_score REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

SEEDED_TOOLS = [
    (
        "context-mode/ctx_execute",
        "context-mode",
        "ctx_execute",
        "compute",
        "Execute safe shell commands and sandbox scripts returning concise derived output",
        1,
        1,
        1.8,
    ),
    (
        "context-mode/ctx_execute_file",
        "context-mode",
        "ctx_execute_file",
        "compute",
        "Execute JavaScript/Python scripts against file contents in sandbox",
        1,
        1,
        1.7,
    ),
    (
        "context-mode/ctx_search",
        "context-mode",
        "ctx_search",
        "search",
        "Search indexed documentation chunks via BM25/RRF scoring",
        1,
        1,
        1.5,
    ),
    (
        "context-mode/ctx_fetch_and_index",
        "context-mode",
        "ctx_fetch_and_index",
        "ingest",
        "Ingest external web URLs or documents into sandbox SQLite FTS5",
        1,
        1,
        1.6,
    ),
    (
        "context7/resolve-library-id",
        "context7",
        "resolve-library-id",
        "docs",
        "Resolve canonical library ID for official documentation lookups",
        1,
        1,
        1.4,
    ),
    (
        "context7/query-docs",
        "context7",
        "query-docs",
        "docs",
        "Fetch verified documentation snippets and API signatures",
        1,
        1,
        1.6,
    ),
    (
        "sequential/sequentialthinking",
        "sequential",
        "sequentialthinking",
        "reasoning",
        "Multi-step dynamic chain-of-thought hypothesis evaluation",
        1,
        1,
        1.9,
    ),
    (
        "security/osvScanner",
        "security",
        "scan_vulnerable_dependencies",
        "security",
        "Audit open-source dependencies against OSV database",
        1,
        1,
        1.8,
    ),
    (
        "security/code_auditor",
        "security",
        "audit_code_safety",
        "security",
        "Scan codebase changes for common vulnerability patterns",
        1,
        1,
        1.7,
    ),
    (
        "clean_code/refactor_gate",
        "clean_code",
        "verify_pragmatic_refactor",
        "critique",
        "Verify smallest viable change and eliminate premature abstraction",
        1,
        1,
        1.5,
    ),
    (
        "mempalace/checkpoint",
        "mempalace",
        "checkpoint",
        "memory",
        "Persist key architectural decisions and session checkpoints to disk",
        0,
        1,
        1.3,
    ),
]

SEEDED_RELATIONSHIPS = [
    (
        "context7/resolve-library-id",
        "context7/query-docs",
        "PRECEDES",
        2.0,
        "Resolves ID before doc queries",
    ),
    (
        "context7/query-docs",
        "context-mode/ctx_execute",
        "COMPLEMENTS",
        1.8,
        "Provides exact API signatures to sandbox execution",
    ),
    (
        "context-mode/ctx_fetch_and_index",
        "context-mode/ctx_search",
        "PRECEDES",
        2.0,
        "Ingestion must precede indexing search",
    ),
    (
        "context-mode/ctx_execute",
        "security/osvScanner",
        "OPPOSES",
        1.9,
        "Security audit acts as adversarial gate for executed code",
    ),
    (
        "context-mode/ctx_execute",
        "clean_code/refactor_gate",
        "OPPOSES",
        1.8,
        "Clean code review blocks premature abstractions",
    ),
    (
        "sequential/sequentialthinking",
        "context-mode/ctx_execute",
        "COMPLEMENTS",
        1.7,
        "Hypothesis generation drives sandbox verification",
    ),
    (
        "clean_code/refactor_gate",
        "mempalace/checkpoint",
        "COMPLEMENTS",
        1.5,
        "Approved refactorings are checkpointed to memory",
    ),
]

SEEDED_SEQUENCES = [
    (
        "investigation",
        "STATE_REASONING,STATE_DOC_RESOLUTION,STATE_SANDBOX_COMPUTE,STATE_CRITIQUE_GATE,STATE_SYNTHESIS",
        "sequential/sequentialthinking -> context7/query-docs -> context-mode/ctx_execute -> security/osvScanner -> context-mode/ctx_search",
        0.88,
        96.0,
    ),
    (
        "docs_lookup",
        "STATE_DOC_RESOLUTION,STATE_SANDBOX_COMPUTE,STATE_SYNTHESIS",
        "context7/resolve-library-id -> context7/query-docs -> context-mode/ctx_search",
        0.92,
        98.0,
    ),
    (
        "refactoring",
        "STATE_REASONING,STATE_SANDBOX_COMPUTE,STATE_CRITIQUE_GATE,STATE_MUTATION_PREPARE,STATE_SYNTHESIS",
        "sequential/sequentialthinking -> context-mode/ctx_execute -> clean_code/refactor_gate -> clean_code/refactor_gate -> context-mode/ctx_execute",
        0.85,
        94.0,
    ),
]


def init_db(db_path: Path | None = None) -> Path:
    """Initialize database schema, enforce PRAGMAs, and seed default nodes and edges securely."""
    p = db_path or get_db_path()
    conn = sqlite3.connect(p, timeout=15.0)
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute("PRAGMA journal_mode = WAL;")
        cur.execute("PRAGMA synchronous = NORMAL;")
        cur.execute("PRAGMA busy_timeout = 5000;")
        cur.executescript(SCHEMA_SQL)

        for item in SEEDED_TOOLS:
            cur.execute(
                """
                INSERT OR IGNORE INTO tools (id, server_name, tool_name, category, description, read_only, sandbox_safe, capability_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                item,
            )

        for rel in SEEDED_RELATIONSHIPS:
            cur.execute(
                """
                INSERT OR IGNORE INTO tool_relationships (source_tool_id, target_tool_id, relationship_type, weight, rationale)
                VALUES (?, ?, ?, ?, ?)
                """,
                rel,
            )

        for seq in SEEDED_SEQUENCES:
            cur.execute(
                """
                INSERT OR REPLACE INTO golden_sequences (intent, fsm_sequence, tool_pipeline, estimated_token_saving, benchmark_score)
                VALUES (?, ?, ?, ?, ?)
                """,
                seq,
            )

        conn.commit()
    finally:
        conn.close()

    try:
        p.chmod(0o600)
    except OSError:
        pass

    return p


if __name__ == "__main__":
    path = init_db()
    print(f"Tool Chaining Mesh DB initialized successfully at: {path}")
