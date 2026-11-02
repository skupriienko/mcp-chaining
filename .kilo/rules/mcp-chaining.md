# MCP Sub-Loop Chaining Rule (Kilo Code)

When handling multi-step tasks (investigation, doc resolution, sandbox execution, security verification):
1. Execute multi-tool pipelines through `mcp-chain run "<query>" --intent <investigation|docs_lookup|refactoring>`.
2. All intermediate bytes stay in the sandbox; only clean derived synthesis (<8,000 chars) enters conversational context.
3. Obey Capability Invariant ($L_c <= L_d$): Tools consuming more resources than capability added are rejected.
4. Mutation states halt for explicit user confirmation.
