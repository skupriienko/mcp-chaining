"""MCP Chaining — Autonomous FSM Sub-Loop & Tool Mesh for AI Agents.

Orchestrates disparate MCP servers, CLI binaries, and scripts into a self-organizing,
token-efficient dependency graph with sub-loop sandboxed execution.
"""

__version__ = "1.0.0"
__all__ = ["FSMSequenceRunner", "PortableToolGraph", "init_db", "get_db_path"]

from .mesh_db import get_db_path, init_db
from .graph_engine import PortableToolGraph
from .fsm_runner import FSMSequenceRunner
