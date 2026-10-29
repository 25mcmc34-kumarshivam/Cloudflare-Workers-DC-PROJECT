"""Automated integration tests for EdgeFlow Simulator."""

from __future__ import annotations

import subprocess
import sys
import time
import unittest
from pathlib import Path

from common import request_json


ROOT = Path(__file__).resolve().parent


class EdgeFlowIntegrationTests(unittest.TestCase):
    processes: list[subprocess.Popen[str]] = []

    @classmethod
    def setUpClass(cls) -> None:
        commands = [
            ["origin_server.py", "--port", "9100"],
            ["edge_server.py", "--name", "test-edge-1", "--port", "8101", "--origin-port", "9100", "--ttl", "20"],
            ["edge_server.py", "--name", "test-edge-2", "--port", "8102", "--origin-port", "9100", "--ttl", "20"],
            ["dispatcher.py", "--port", "8100", "--node", "test-edge-1:127.0.0.1:8101", "--node", "test-edge-2:127.0.0.1:8102"],
        ]
        for command in commands:
            cls.processes.append(
                subprocess.Popen([sys.executable, "-u", *command], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
            )
        deadline = time.time() + 8
        while time.time() < deadline:
            try:
                if request_json("127.0.0.1", 8100, {"action": "PING"}, timeout=0.3).get("ok"):
                    return
            except Exception:
                time.sleep(0.1)
        raise RuntimeError("test services did not start")

    @classmethod
    def tearDownClass(cls) -> None:
        for process in reversed(cls.processes):
            if process.poll() is None:
                process.terminate()
        for process in reversed(cls.processes):
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()

    def test_01_status_lists_two_healthy_nodes(self) -> None:
        response = request_json("127.0.0.1", 8100, {"action": "STATUS"})
        self.assertTrue(response["ok"])
        self.assertEqual(2, len(response["nodes"]))
        self.assertTrue(all(node["healthy"] for node in response["nodes"]))

    def test_02_cache_changes_from_miss_to_hit(self) -> None:
        first = request_json("127.0.0.1", 8101, {"action": "GET", "resource": "/intro"})
        second = request_json("127.0.0.1", 8101, {"action": "GET", "resource": "/intro"})
        self.assertEqual("MISS", first["cache"])
        self.assertEqual("HIT", second["cache"])
        self.assertEqual(first["content"], second["content"])

    def test_03_dispatcher_routes_to_an_edge(self) -> None:
        response = request_json("127.0.0.1", 8100, {"action": "GET", "resource": "/concepts"})
        self.assertTrue(response["ok"])
        self.assertIn(response["served_by"], {"test-edge-1", "test-edge-2"})

    def test_04_failover_after_edge_shutdown(self) -> None:
        first_edge = self.processes[1]
        if first_edge.poll() is None:
            first_edge.terminate()
            first_edge.wait(timeout=2)
        time.sleep(0.3)
        response = request_json("127.0.0.1", 8100, {"action": "GET", "resource": "/architecture"})
        self.assertTrue(response["ok"])
        self.assertEqual("test-edge-2", response["served_by"])

    def test_05_missing_resource_returns_error(self) -> None:
        response = request_json("127.0.0.1", 8100, {"action": "GET", "resource": "/does-not-exist"})
        self.assertFalse(response["ok"])
        self.assertEqual("not_found", response["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

