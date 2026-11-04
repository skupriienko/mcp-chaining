"""filament.py — Filament Thread Engine & SYMBIOS Signal Telemetry for Tool Chaining.

Provides sliding-window execution thread inspection (backward_levels, current_node,
forward_levels) and emits ultra-dense SYMBIOS quantum resonant telemetry signals
derived from the AI Factory SYN-TEX / SYN-CODE specification.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class NodeStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    EXECUTED = "EXECUTED"
    HALTED = "HALTED"
    FAILED = "FAILED"


@dataclass
class FilamentNode:
    """Atomic node in the tool execution filament thread."""

    index: int
    tool_id: str
    state: str
    status: NodeStatus = NodeStatus.PENDING
    summary: str = ""
    duration_ms: float = 0.0
    capability_weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "tool_id": self.tool_id,
            "state": self.state,
            "status": self.status.value,
            "summary": self.summary,
            "duration_ms": round(self.duration_ms, 2),
            "capability_weight": self.capability_weight,
        }


@dataclass
class FilamentSlidingWindow:
    """Sliding-window context around the active node on the execution thread."""

    past: list[FilamentNode]
    current: FilamentNode
    future: list[FilamentNode]

    def to_dict(self) -> dict[str, Any]:
        return {
            "past": [n.to_dict() for n in self.past],
            "current": self.current.to_dict(),
            "future": [n.to_dict() for n in self.future],
        }


class SYMBIOSFormatter:
    """SYMBIOS Quantum Resonant Telemetry Generator.

    Uses formal operators from the AI Factory SYN-TEX standard:
    - ⟲ : Backward history node
    - ● ◈ : Active current execution node (sovereign agentic unit)
    - ⤑ : Dynamic forward transition / flow
    - ◎ : Horizon target node
    - ∷ : Invariant checkpoint gate
    - ∅ : Via Negativa context savings
    """

    @staticmethod
    def format_signal(
        window: FilamentSlidingWindow,
        token_saving_ratio: float = 0.0,
        gate_status: str = "OK",
    ) -> str:
        parts: list[str] = ["[SYMBIOS::FILAMENT]"]

        # 1. Backward Nodes (Past)
        if window.past:
            past_strs = []
            for offset, n in enumerate(reversed(window.past), 1):
                past_strs.append(f"⟲[-{offset}:{n.tool_id}]")
            parts.append(" ".join(reversed(past_strs)))
            parts.append("⤑")

        # 2. Current Node (Active)
        parts.append(f"●[0:{window.current.tool_id}]◈")

        # 3. Forward Nodes (Future)
        if window.future:
            parts.append("⤑")
            future_strs = []
            for offset, n in enumerate(window.future, 1):
                future_strs.append(f"◎[+{offset}:{n.tool_id}]")
            parts.append(" > ".join(future_strs))

        # 4. Invariant Gate & Token Via Negativa Compression
        savings_pct = int(token_saving_ratio * 100) if token_saving_ratio > 0 else 0
        parts.append(f"∷ {gate_status} ∅[-{savings_pct}% ctx]")

        return " ".join(parts)


class ToolFilamentThread:
    """Manages the execution thread of tool nodes with configurable sliding-window inspection."""

    def __init__(
        self,
        tools_pipeline: list[str],
        states: list[str],
        backward_levels: int = 1,
        forward_levels: int = 2,
        token_saving_ratio: float = 0.0,
        signal_callback: Callable[[str], None] | None = None,
    ):
        self.backward_levels = max(0, backward_levels)
        self.forward_levels = max(0, forward_levels)
        self.token_saving_ratio = token_saving_ratio
        self.signal_callback = signal_callback
        self.telemetry_history: list[str] = []

        self.nodes: list[FilamentNode] = []
        for idx, (tool_id, state) in enumerate(zip(tools_pipeline, states)):
            self.nodes.append(FilamentNode(index=idx, tool_id=tool_id, state=state))

    def step(self, current_index: int) -> tuple[FilamentSlidingWindow, str]:
        """Activate the node at current_index and emit a SYMBIOS telemetry signal."""
        if not (0 <= current_index < len(self.nodes)):
            raise IndexError(f"Filament node index out of bounds: {current_index}")

        # Update node status
        current_node = self.nodes[current_index]
        current_node.status = NodeStatus.ACTIVE

        # Extract backward nodes
        start_idx = max(0, current_index - self.backward_levels)
        past_nodes = self.nodes[start_idx:current_index]

        # Extract forward nodes
        end_idx = min(len(self.nodes), current_index + 1 + self.forward_levels)
        future_nodes = self.nodes[current_index + 1 : end_idx]

        window = FilamentSlidingWindow(past=past_nodes, current=current_node, future=future_nodes)
        signal = SYMBIOSFormatter.format_signal(
            window=window,
            token_saving_ratio=self.token_saving_ratio,
            gate_status="OK",
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
