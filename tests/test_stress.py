#!/usr/bin/env python3
"""test_stress.py — Comprehensive Stress & Security Test Suite for MCP Chaining.

Tests massive graph scalability (hundreds of tools and relationships),
sub-loop boundary execution, capability invariant enforcement ($L_c <= L_d$),
adversarial input handling (SQL injection, buffer limits), and mutation security gates.
"""

import sys
import tempfile
import time
import unittest
from pathlib import Path

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mcp_chaining.fsm_runner import MAX_HOOK_OUTPUT_CHARS, FSMSequenceRunner
from mcp_chaining.graph_engine import PortableToolGraph
from mcp_chaining.mesh_db import init_db


class TestMCPChainingStress(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_mesh.db"
        init_db(self.db_path)
        self.graph = PortableToolGraph(self.db_path)
        self.runner = FSMSequenceRunner(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_graph_scalability_stress(self):
        """Stress: Onboard 200 dynamic tools and 400 relationships; test query latency."""
        t0 = time.time()
        for i in range(200):
            cat = "compute" if i % 3 == 0 else ("docs" if i % 3 == 1 else "security")
            self.graph.onboard_tool(
                tool_id=f"tool_provider_{i}/action_{i}",
                server_name=f"provider_{i}",
                tool_name=f"action_{i}",
                category=cat,
                description=f"Automated benchmark test tool {i}",
                read_only=True,
                capability_weight=1.5,
            )
        elapsed_onboard = time.time() - t0
        print(
            f"\n[STRESS] Onboarded 200 tools in {elapsed_onboard:.3f}s ({200 / elapsed_onboard:.1f} tools/sec)"
        )

        summary = self.graph.summary()
        self.assertGreaterEqual(summary["total_nodes"], 211)
        self.assertGreaterEqual(summary["total_edges"], 200)

        # Query friends and opponents across 200 tools
        t1 = time.time()
        for i in range(200):
            friends = self.graph.get_friends(f"tool_provider_{i}/action_{i}")
            opponents = self.graph.get_opponents(f"tool_provider_{i}/action_{i}")
            self.assertIsInstance(friends, list)
            self.assertIsInstance(opponents, list)
        elapsed_queries = time.time() - t1
        print(
            f"[STRESS] 400 semantic relationship queries completed in {elapsed_queries:.3f}s ({400 / elapsed_queries:.1f} queries/sec)"
        )
        self.assertLess(elapsed_queries, 0.5, "Graph queries should complete in under 500ms")

    def test_02_subloop_execution_volume(self):
        """Stress: Execute 300 autonomous sub-loop chains; verify latency and invariants."""
        t0 = time.time()
        for i in range(300):
            intent = "docs_lookup" if i % 2 == 0 else "investigation"
            seq_info = self.runner.generate_fuzz_sequence(intent=intent, is_mutation=False)
            res = self.runner.execute_chain(
                f"Benchmark task iteration {i}", seq_info, allow_mutation=False
            )
            self.assertEqual(res["status"], "SUCCESS")
            self.assertIn("synthesis", res)
            self.assertLessEqual(len(res["synthesis"]), MAX_HOOK_OUTPUT_CHARS)
        elapsed = time.time() - t0
        print(
            f"[STRESS] 300 sub-loop chains executed in {elapsed:.3f}s ({300 / elapsed:.1f} chains/sec)"
        )
        self.assertLess(elapsed, 1.0, "300 chains should execute in under 1 second")

    def test_03_two_tier_mutation_security_gate(self):
        """Security: Verify MUTATION_PREPARE halts for confirmation without allow_mutation=True."""
        seq_info = self.runner.generate_fuzz_sequence(intent="refactoring", is_mutation=True)

        # Attempt 1: Without explicit authorization -> must halt
        res_blocked = self.runner.execute_chain(
            "Modify database records", seq_info, allow_mutation=False
        )
        steps = res_blocked["execution_steps"]
        halted_step = [s for s in steps if s.get("action") == "HALT_FOR_USER_APPROVAL"]
        self.assertEqual(len(halted_step), 1)
        self.assertIn("Two-Tier Policy", halted_step[0]["reason"])

        # Attempt 2: With explicit authorization -> proceeds
        res_allowed = self.runner.execute_chain(
            "Modify database records", seq_info, allow_mutation=True
        )
        self.assertEqual(res_allowed["status"], "SUCCESS")
        self.assertEqual(len(res_allowed["execution_steps"]), 5)

    def test_04_adversarial_sql_injection_defense(self):
        """Security CWE-89: Verify parameterized queries resist SQL injection payloads."""
        malicious_ids = [
            "'; DROP TABLE tools; --",
            "' OR '1'='1",
            "admin'--",
            'tool"; DELETE FROM tools; --',
        ]
        for bad_id in malicious_ids:
            # Onboard with malicious string as ID
            res = self.graph.onboard_tool(
                tool_id=bad_id,
                server_name="exploit_srv",
                tool_name="exploit_fn",
                category="compute",
                description="SQLi test payload",
            )
            self.assertEqual(res["status"], "ONBOARDED")

            # Verify table still exists and data is intact
            summary = self.graph.summary()
            self.assertGreaterEqual(summary["total_nodes"], 11)

            # Query with malicious ID
            friends = self.graph.get_friends(bad_id)
            self.assertIsInstance(friends, list)

    def test_05_anti_context_pollution_ceiling(self):
        """Anti-Pollution: Synthesis strictly adheres to 8,000 char maximum hook limit."""
        huge_query = "X" * 15000
        seq_info = self.runner.generate_fuzz_sequence(intent="investigation", is_mutation=False)
        res = self.runner.execute_chain(huge_query, seq_info)
        synthesis = res["synthesis"]
        self.assertLessEqual(len(synthesis), MAX_HOOK_OUTPUT_CHARS)
        self.assertTrue(synthesis.endswith("... [TRUNCATED_AT_8000]"))

    def test_06_capability_invariant_enforcement(self):
        """Capability Invariant: Rejects sequences where consumption exceeds capability."""
        failing_seq = {
            "intent": "failing_task",
            "states": ["STATE_REASONING"],
            "tools_pipeline": ["context-mode/ctx_execute"],
            "token_saving_ratio": 0.5,
            "capability_l_d": 0.5,
            "consumption_l_c": 10.0,
            "progress_check_passed": False,
            "progress_margin": -95.0,
            "mutation_required": False,
        }
        res = self.runner.execute_chain("Heavy un-scalable task", failing_seq)
        self.assertEqual(res["status"], "REJECTED")
        self.assertIn("Capability Invariant violated", res["reason"])


if __name__ == "__main__":
    unittest.main()
