"""filament.py — Quipu-Inspired Branched Filament Thread & SYN-TEX Signal Telemetry for Tool Chaining.

Provides sliding-window execution thread inspection (backward_levels, current_node,
forward_levels) and branched cord knowledge (analogous to Incan Quipu cords: primary
cord, secondary pendants, auxiliary branches for similar/substitute tools and probabilistic
alternatives). Emits ultra-dense SYN-TEX quantum resonant telemetry signals derived
from the AI Factory SYN-TEX / SYN-CODE specification.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class NodeStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    EXECUTED = "EXECUTED"
    HALTED = "HALTED"
    FAILED = "FAILED"
    BRANCHED = "BRANCHED"


class BranchKind(StrEnum):
    """Categorization of branched cords stemming from a node (Quipu pendant types)."""

    SIMILAR = "SIMILAR"  # Complementary or substitute tools (e.g. ripgrep <-> grep)
    PROBABILISTIC = "PROBABLE"  # Highly probable contextual next candidates
    CRITIQUE = "CRITIQUE"  # Adversarial / verification gates (OPPOSES)


@dataclass
class FilamentBranch:
    """A secondary pendant cord hanging from a primary thread node (Quipu subsidiary)."""

    tool_id: str
    kind: BranchKind
    affinity: float = 1.0  # Weight or probability (0.0 to 1.0+)
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "kind": self.kind.value,
            "affinity": round(self.affinity, 2),
            "rationale": self.rationale,
        }


@dataclass
class FilamentNode:
    """Atomic node on the tool execution filament thread (primary cord knot)."""

    index: int
    tool_id: str
    state: str
    status: NodeStatus = NodeStatus.PENDING
    summary: str = ""
    duration_ms: float = 0.0
    capability_weight: float = 1.0
    branches: list[FilamentBranch] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "tool_id": self.tool_id,
            "state": self.state,
            "status": self.status.value,
            "summary": self.summary,
            "duration_ms": round(self.duration_ms, 2),
            "capability_weight": self.capability_weight,
            "branches": [b.to_dict() for b in self.branches],
        }


@dataclass
class FilamentSlidingWindow:
    """Sliding-window context around the active node on the execution thread, including Quipu branches."""

    past: list[FilamentNode]
    current: FilamentNode
    future: list[FilamentNode]

    @property
    def active_branches(self) -> list[FilamentBranch]:
        return self.current.branches

    def to_dict(self) -> dict[str, Any]:
        return {
            "past": [n.to_dict() for n in self.past],
            "current": self.current.to_dict(),
            "future": [n.to_dict() for n in self.future],
            "active_branches": [b.to_dict() for b in self.current.branches],
        }


class SynTexFormatter:
    """SYN-TEX Quantum Resonant Telemetry Generator for Quipu Filaments.

    Uses formal operators from the AI Factory SYN-TEX standard:
    - ⟲ : Backward history nodes (primary cord retrospect)
    - ● ◈ : Active current execution node (primary knot)
    - ⤑ : Dynamic forward transition / flow
    - ◎ : Horizon target nodes (primary cord preview)
    - ⑂ : Branched pendant cord (Quipu secondary strand: similar/probable tools)
    - ∷ : Invariant checkpoint gate
    - ∅ : Via Negativa context savings
    """

    @staticmethod
    def format_signal(
        window: FilamentSlidingWindow,
        token_saving_ratio: float = 0.0,
        gate_status: str = "OK",
        include_branches: bool = True,
    ) -> str:
        parts: list[str] = ["[SYN-TEX::FILAMENT]"]

        # 1. Backward Nodes (Past knots on the main cord)
        if window.past:
            past_strs = []
            for offset, n in enumerate(reversed(window.past), 1):
                past_strs.append(f"⟲[-{offset}:{n.tool_id}]")
            parts.append(" ".join(reversed(past_strs)))
            parts.append("⤑")

        # 2. Current Node (Active sovereign knot)
        parts.append(f"●[0:{window.current.tool_id}]◈")

        # 2b. Quipu Branches / Pendants (Auxiliary cords)
        if include_branches and window.current.branches:
            branch_tokens = []
            for b in window.current.branches[:3]:  # Top 3 salient branches
                branch_tokens.append(f"⑂{b.kind.value[:3]}~{b.tool_id}({b.affinity:.1f})")
            parts.append(f"[{' '.join(branch_tokens)}]")

        # 3. Forward Nodes (Future knots on the main cord)
        if window.future:
            parts.append("⤑")
            future_strs = []
            for offset, n in enumerate(window.future, 1):
                future_strs.append(f"◎[+{offset}:{n.tool_id}]")
            parts.append(" > ".join(future_strs))

        # 4. Invariant Gate & Token Compression
        savings_pct = int(token_saving_ratio * 100) if token_saving_ratio > 0 else 0
        parts.append(f"∷ {gate_status} ∅[-{savings_pct}% ctx]")

        return " ".join(parts)


class ToolFilamentThread:
    """Manages the Quipu-inspired execution thread of tool nodes with branched cords."""

    def __init__(
        self,
        tools_pipeline: list[str],
        states: list[str],
        backward_levels: int = 1,
        forward_levels: int = 2,
        token_saving_ratio: float = 0.0,
        signal_callback: Callable[[str], None] | None = None,
        graph: Any | None = None,
    ):
        self.backward_levels = max(0, backward_levels)
        self.forward_levels = max(0, forward_levels)
        self.token_saving_ratio = token_saving_ratio
        self.signal_callback = signal_callback
        self.graph = graph
        self.telemetry_history: list[str] = []

        self.nodes: list[FilamentNode] = []
        for idx, (tool_id, state) in enumerate(zip(tools_pipeline, states)):
            branches = self._resolve_branches(tool_id)
            self.nodes.append(
                FilamentNode(index=idx, tool_id=tool_id, state=state, branches=branches)
            )

    def _resolve_branches(self, tool_id: str) -> list[FilamentBranch]:
        """Discover secondary pendant cords (similar, alternative, or probable tools)."""
        branches: list[FilamentBranch] = []
        if not self.graph:
            return branches

        # 1. Discover similar / complementary tools (Quipu pendant cords)
        friends = self.graph.get_friends(tool_id) if hasattr(self.graph, "get_friends") else []
        for f in friends:
            target = f.get("target_tool") or f.get("tool_id", "")
            if target and target != tool_id:
                branches.append(
                    FilamentBranch(
                        tool_id=target,
                        kind=BranchKind.SIMILAR,
                        affinity=float(f.get("weight") or 1.0),
                        rationale=f.get("rationale") or "Complementary partner tool",
                    )
                )

        # 2. Discover critique / gate opponents
        opponents = (
            self.graph.get_opponents(tool_id) if hasattr(self.graph, "get_opponents") else []
        )
        for o in opponents:
            target = o.get("target_tool") or o.get("tool_id", "")
            if target and target != tool_id:
                branches.append(
                    FilamentBranch(
                        tool_id=target,
                        kind=BranchKind.CRITIQUE,
                        affinity=float(o.get("weight") or 1.0),
                        rationale=o.get("rationale") or "Adversarial critique gate",
                    )
                )

        # 3. Contextual heuristic fallback (if graph has no edges yet)
        if not branches:
            if "search" in tool_id or "docs" in tool_id:
                branches.append(
                    FilamentBranch(
                        tool_id="context-mode/ctx_search",
                        kind=BranchKind.PROBABILISTIC,
                        affinity=0.85,
                        rationale="High contextual probability for information retrieval",
                    )
                )
            elif "execute" in tool_id:
                branches.append(
                    FilamentBranch(
                        tool_id="clean_code/refactor_gate",
                        kind=BranchKind.PROBABILISTIC,
                        affinity=0.80,
                        rationale="Recommended post-execution safety gate",
                    )
                )

        # Sort by affinity descending
        branches.sort(key=lambda b: b.affinity, reverse=True)
        return branches

    def step(self, current_index: int) -> tuple[FilamentSlidingWindow, str]:
        """Activate the node at current_index and emit a SYN-TEX telemetry signal with Quipu branches."""
        if not (0 <= current_index < len(self.nodes)):
            err_msg = f"Filament node index out of bounds: {current_index}"
            raise IndexError(err_msg)

        current_node = self.nodes[current_index]
        current_node.status = NodeStatus.ACTIVE

        # Extract backward nodes
        start_idx = max(0, current_index - self.backward_levels)
        past_nodes = self.nodes[start_idx:current_index]

        # Extract forward nodes
        end_idx = min(len(self.nodes), current_index + 1 + self.forward_levels)
        future_nodes = self.nodes[current_index + 1 : end_idx]

        window = FilamentSlidingWindow(past=past_nodes, current=current_node, future=future_nodes)
        signal = SynTexFormatter.format_signal(
            window=window,
            token_saving_ratio=self.token_saving_ratio,
            gate_status="OK",
            include_branches=True,
        )

        self.telemetry_history.append(signal)
        if self.signal_callback:
            self.signal_callback(signal)

        return window, signal

    def complete_step(
        self,
        current_index: int,
        status: NodeStatus = NodeStatus.EXECUTED,
        summary: str = "",
        duration_ms: float = 0.0,
    ) -> None:
        """Mark the node at current_index as completed with telemetry metadata."""
        if 0 <= current_index < len(self.nodes):
            node = self.nodes[current_index]
            node.status = status
            node.summary = summary
            node.duration_ms = duration_ms

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "backward_levels": self.backward_levels,
            "forward_levels": self.forward_levels,
            "telemetry_signals": self.telemetry_history,
            "nodes": [n.to_dict() for n in self.nodes],
        }
