---
name: mcp-chaining
type: Skill
description: Autonomous tool chaining and sub-loop pipelining using Fuzz State Machine (FSM) sequences and NetworkX dependency graphs. Organizes disparate tools (MCPs, CLIs, scripts) into an orchestrated mesh with automatic friend/opponent discovery and capability-to-consumption verification. Eliminates context pollution, saves up to 90% of tokens, and returns clean synthesized answers. Works standalone in any repository.
version: 1.0.0
status: stable
tags:
  - mcp-chaining
  - fsm
  - networkx
  - mcp-mesh
  - token-saving
  - sub-loop
  - autonomous-agents
disable-slash-command: false
---

# Skill: MCP Chaining (Autonomous FSM Sub-Loop & Tool Mesh)

Unifies fragmented MCP servers, CLI binaries, and scripts into a self-organizing, token-efficient dependency graph. Instead of returning intermediate tool outputs to the agent context across multiple chat turns, this skill executes multi-step tool pipelines inside a sandboxed sub-loop and returns only a clean, synthesized answer.

---

## 1. Core Capabilities

1. **Sub-Loop Chaining (Zero Context Pollution):** Chained execution runs in an isolated sub-loop. Raw bytes stay in the sandbox; only the final derived result enters the conversation context.
2. **Topological Tool Mesh (NetworkX):**
   * **`COMPLEMENTS`:** Tools that feed or enrich each other (e.g., doc resolution $\to$ sandbox execution).
   * **`OPPOSES`:** Mandatory adversarial critique gates (e.g., code generation $\to$ security scan $\to$ clean code review).
   * **`PIPES_TO`:** Streaming data directly without intermediate serialization.
3. **Capability Invariant ($L_c \le L_d$):** Evaluates capability added ($L_d$) against resource consumption ($L_c$). Rejects bloat where consumption exceeds added value.
4. **Two-Tier Execution Policy:** Read-only analysis runs autonomously in one pass; code mutation strictly gates on human confirmation.
5. **Universal Portability:** Works standalone in any user project (`./.mesh/tool_mesh.db`).

---

## 2. CLI Usage

```bash
# 1. Initialize mesh database
mcp-chain init

# 2. View topological summary
mcp-chain summary

# 3. Discover complementary tools
mcp-chain friends context7/query-docs

# 4. Discover critique gates
mcp-chain opponents context-mode/ctx_execute

# 5. Execute an autonomous sub-loop
mcp-chain run "Investigate security blast radius for auth service" --intent investigation

# 6. Run 100-point benchmark evaluation
mcp-chain benchmark
```
