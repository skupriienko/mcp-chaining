#!/usr/bin/env bash
# ==============================================================================
# MCP Chaining — One-Line Universal Installer & AI Tool Integrator
# ==============================================================================
# Installs MCP Chaining and immediately integrates with all major AI tools:
# - Claude Code (CLAUDE.md)
# - Gemini CLI & Antigravity (GEMINI.md, AGENTS.md)
# - Cursor (.cursorrules, .cursor/rules/mcp-chaining.mdc)
# - Windsurf (.windsurfrules)
# - Kilo / KiloCode (.kilo/kilo.jsonc, .kilo/rules/mcp-chaining.md, .kilocoderules)
# - GitHub Copilot (.github/copilot-instructions.md)
# - Aider / OpenCode (CONVENTIONS.md, .aider.conf.yml)
#
# Zero friction: Run anywhere in one command.
# ==============================================================================

set -euo pipefail

# ANSI Colors
BOLD="\033[1m"
GREEN="\033[32m"
BLUE="\033[34m"
YELLOW="\033[33m"
CYAN="\033[36m"
RED="\033[31m"
RESET="\033[0m"

log_info() { echo -e "${CYAN}ℹ [INFO]${RESET} $*"; }
log_ok()   { echo -e "${GREEN}✔ [OK]${RESET} $*"; }
log_warn() { echo -e "${YELLOW}⚠ [WARN]${RESET} $*"; }
log_err()  { echo -e "${RED}✖ [ERR]${RESET} $*" >&2; }

echo -e "${BOLD}${BLUE}"
echo "================================================================================"
echo "          MCP CHAINING — AUTONOMOUS FSM SUB-LOOP INSTALLER                       "
echo "================================================================================"
echo -e "${RESET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-${PWD}}"

log_info "Target project directory: ${TARGET_DIR}"

# 1. Install CLI binary
mkdir -p "${TARGET_DIR}/bin"
cp "${SCRIPT_DIR}/bin/mcp-chain" "${TARGET_DIR}/bin/mcp-chain"
chmod +x "${TARGET_DIR}/bin/mcp-chain"
log_ok "CLI installed -> ${TARGET_DIR}/bin/mcp-chain"

# 2. Initialize default mesh database
log_info "Initializing SQLite FTS5 tool mesh..."
PYTHON_BIN="$(command -v python3 || command -v python || echo "python3")"

cd "${TARGET_DIR}"
PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH:-}" "${PYTHON_BIN}" -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}/src')
from mcp_chaining.mesh_db import init_db
p = init_db()
print(f'Database initialized at {p}')
" 2>/dev/null || log_warn "Database will be initialized on first run."

# 3. Install Agent Skill & Module integration
SKILLS_DIR="${TARGET_DIR}/.agents/skills/mcp-chaining"
mkdir -p "${SKILLS_DIR}/src"
cp "${SCRIPT_DIR}/SKILL.md" "${SKILLS_DIR}/SKILL.md"
cp -r "${SCRIPT_DIR}/src/mcp_chaining" "${SKILLS_DIR}/src/"
log_ok "Agent Skill & library installed -> ${SKILLS_DIR}"

# 4. Inject MCP Chaining Rule into ALL AI Tools
INSTRUCTION_SNIPPET=$(cat <<'EOF'

<!-- MCP CHAINING RULE -->
### ⚡ Mandatory MCP Sub-Loop Chaining Invariant
To prevent context rot and save ~90% of tokens, never invoke disparate tools in multiple serial turns.
When handling multi-step tasks (investigation, docs resolution, sandboxed execution, security critique):
1. Execute multi-tool pipelines through `mcp-chain run "<query>" --intent <investigation|docs_lookup|refactoring>`.
2. All intermediate bytes stay in the sandbox; only clean derived synthesis (<8,000 chars) enters context.
3. Obey Capability Invariant ($L_c \le L_d$): Tools consuming more resources than capability added are rejected.
4. Mutation states halt for explicit user confirmation.
<!-- END MCP CHAINING RULE -->
EOF
)

# Append or create AI tool instruction files
append_rule() {
    local file="$1"
    local tool_name="$2"
    mkdir -p "$(dirname "${file}")"
    if [[ ! -f "${file}" ]]; then
        echo "# Project AI Instructions" > "${file}"
    fi
    if ! grep -q "MCP CHAINING RULE" "${file}"; then
        echo "${INSTRUCTION_SNIPPET}" >> "${file}"
        log_ok "[${tool_name}] Injected chaining rule -> ${file}"
    else
        log_ok "[${tool_name}] Chaining rule already present -> ${file}"
    fi
}

append_rule "${TARGET_DIR}/CLAUDE.md" "Claude Code"
append_rule "${TARGET_DIR}/GEMINI.md" "Gemini CLI / Antigravity"
append_rule "${TARGET_DIR}/AGENTS.md" "Universal Agents"
append_rule "${TARGET_DIR}/.cursorrules" "Cursor Legacy"
append_rule "${TARGET_DIR}/.windsurfrules" "Windsurf Cascade"
append_rule "${TARGET_DIR}/.github/copilot-instructions.md" "GitHub Copilot"
append_rule "${TARGET_DIR}/CONVENTIONS.md" "Aider / OpenCode"

# Cursor MDC modern rule
CURSOR_MDC="${TARGET_DIR}/.cursor/rules/mcp-chaining.mdc"
mkdir -p "$(dirname "${CURSOR_MDC}")"
cat <<'EOF' > "${CURSOR_MDC}"
---
description: MCP Chaining Autonomous Sub-Loop and Token Conservation
globs: "**/*"
alwaysApply: true
---
When executing multi-tool workflows, always use `mcp-chain run "<query>"` to avoid context saturation.
Enforce the capability invariant ($L_c \le L_d$) and two-tier mutation security.
EOF
log_ok "[Cursor MDC] Rule created -> ${CURSOR_MDC}"

# Kilo / KiloCode integration (.kilo/kilo.jsonc and .kilo/rules/mcp-chaining.md)
KILO_DIR="${TARGET_DIR}/.kilo"
mkdir -p "${KILO_DIR}/rules"
KILO_CONFIG="${KILO_DIR}/kilo.jsonc"
if [[ ! -f "${KILO_CONFIG}" ]]; then
    cat <<'EOF' > "${KILO_CONFIG}"
{
  "$schema": "https://app.kilo.ai/config.json",
  "instructions": [
    ".kilo/rules/*.md"
  ]
}
EOF
fi

cat <<'EOF' > "${KILO_DIR}/rules/mcp-chaining.md"
# MCP Sub-Loop Chaining Rule

When executing multi-tool workflows, always use `mcp-chain run "<query>"` to avoid context saturation.
- Intermediate tool outputs stay in sandbox sub-loops.
- Enforce capability invariant ($L_c <= L_d$).
- Two-tier security: write mutations halt for user confirmation.
EOF
log_ok "[Kilo / KiloCode] Rule created -> ${KILO_DIR}/rules/mcp-chaining.md"

# KiloCode legacy compatibility (.kilocoderules)
append_rule "${TARGET_DIR}/.kilocoderules" "KiloCode Legacy"

# 5. Output receipt
cat <<RECEIPT

================================================================================
                    INSTALLATION COMPLETED SUCCESSFULLY                         
================================================================================

[RECEIPT]
- Status: INSTALLED & INTEGRATED
- Target Directory: ${TARGET_DIR}
- CLI Executable: ${TARGET_DIR}/bin/mcp-chain
- Agent Skill: ${SKILLS_DIR}/SKILL.md
- Configured AI Endpoints:
    • Claude Code      : ${TARGET_DIR}/CLAUDE.md
    • Gemini / AGY     : ${TARGET_DIR}/GEMINI.md & AGENTS.md
    • Cursor           : ${TARGET_DIR}/.cursorrules & ${CURSOR_MDC}
    • Windsurf         : ${TARGET_DIR}/.windsurfrules
    • Kilo / KiloCode  : ${KILO_DIR}/kilo.jsonc & ${KILO_DIR}/rules/mcp-chaining.md
    • GitHub Copilot   : ${TARGET_DIR}/.github/copilot-instructions.md
    • Aider / OpenCode : ${TARGET_DIR}/CONVENTIONS.md
- Database: ${TARGET_DIR}/.mesh/tool_mesh.db

Every AI tool in this repository will now immediately utilize MCP sub-loop chaining!
RECEIPT
