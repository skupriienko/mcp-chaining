# Examples & Operational Patterns for MCP Chaining

This document demonstrates concrete, real-world examples of using `mcp-chain` in autonomous AI agent workflows, CI/CD pipelines, and terminal pair-programming sessions.

---

## Example 1: Investigation & Research Pipeline

When an AI agent investigates a library or bug, running tools individually burns thousands of tokens. `mcp-chain` executes this in a single sub-loop:

```bash
mcp-chain run "Investigate security blast radius for auth dependency" --intent investigation
```

### JSON Output Received by the Agent:
```json
{
  "status": "SUCCESS",
  "query": "Investigate security blast radius for auth dependency",
  "chain_length": 5,
  "execution_steps": [
    {
      "state": "STATE_REASONING",
      "tool": "sequential/sequentialthinking",
      "output_status": "SUCCESS",
      "summary": "Step executed in sandbox"
    },
    {
      "state": "STATE_DOC_RESOLUTION",
      "tool": "context7/query-docs",
      "output_status": "SUCCESS",
      "summary": "Step executed in sandbox"
    },
    {
      "state": "STATE_SANDBOX_COMPUTE",
      "tool": "context-mode/ctx_execute",
      "output_status": "SUCCESS",
      "summary": "Step executed in sandbox"
    },
    {
      "state": "STATE_CRITIQUE_GATE",
      "tool": "security/osvScanner",
      "output_status": "SUCCESS",
      "summary": "Step executed in sandbox"
    },
    {
      "state": "STATE_SYNTHESIS",
      "tool": "context-mode/ctx_search",
      "output_status": "SUCCESS",
      "summary": "Step executed in sandbox"
    }
  ],
  "tokens_saved_ratio": 0.88,
  "progress_margin": 88.4,
  "latency_sec": 0.005,
  "synthesis": "[SUB-LOOP DERIVED SYNTHESIS]\nQuery: Investigate security blast radius for auth dependency\nPipeline: STATE_REASONING -> STATE_DOC_RESOLUTION -> STATE_SANDBOX_COMPUTE -> STATE_CRITIQUE_GATE -> STATE_SYNTHESIS\nResult: All 5 sub-loop steps executed safely inside sandbox.\nZero Context Pollution: Intermediate bytes suppressed from conversational tokens.\nQuality & Safety Gates: Clean"
}
```

---

## Example 2: Partner Tool Discovery (`friends`)

Find tools that naturally feed or complement a given tool:

```bash
mcp-chain friends context7/query-docs
```

```json
[
  {
    "target_tool": "context-mode/ctx_execute",
    "relationship": "COMPLEMENTS",
    "weight": 1.8,
    "rationale": "Provides exact API signatures to sandbox execution",
    "category": "compute"
  }
]
```

---

## Example 3: Adversarial Quality Gate Discovery (`opponents`)

Find critique tools that must challenge or audit code changes before execution:

```bash
mcp-chain opponents context-mode/ctx_execute
```

```json
[
  {
    "target_tool": "security/osvScanner",
    "relationship": "OPPOSES",
    "weight": 1.9,
    "rationale": "Security audit acts as adversarial gate for executed code",
    "category": "security"
  },
  {
    "target_tool": "clean_code/refactor_gate",
    "relationship": "OPPOSES",
    "weight": 1.8,
    "rationale": "Clean code review blocks premature abstractions",
    "category": "critique"
  }
]
```
