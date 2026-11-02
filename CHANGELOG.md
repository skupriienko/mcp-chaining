# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with secondary CalVer release tracking (`YYYY.MM.DD.N`).

## [1.0.0] - 2026-11-02 (CalVer: 2026.11.02.1)

### Added
- Initial public open-source release of `mcp-chaining` (Autonomous FSM Sub-Loop & NetworkX Tool Mesh).
- NetworkX topological dependency graph resolution for multi-tool calls.
- Isolated sandbox sub-loops eliminating context pollution (up to 90% token savings).
- Automatic friend/opponent tool discovery and Fuzz State Machine sequences.
- Official Kilo Code, Claude Code, and Cursor rules integration.
- Full PEP 517/621 packaging (`pyproject.toml`, `setup.py`, `MANIFEST.in`, `src/*/py.typed`).
- Native Kilo Code / Kilo integration (`.kilo/kilo.jsonc`, `.kilo/rules/`, `.kilocoderules`).
- Developer tooling: Ruff linter, Mypy strict typing, pre-commit hooks, GitHub Actions CI matrix (Python 3.10–3.13).
- Comprehensive stress benchmarks under extreme concurrency (`tests/test_stress.py`).
- One-line deployment script (`install.sh`).
- Permissive MIT License.
