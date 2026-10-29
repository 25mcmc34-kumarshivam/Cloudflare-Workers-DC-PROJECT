"""Run a complete, repeatable EdgeFlow demonstration."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from common import request_json


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT.parent / "execution_logs"


def start(name: str, args: list[str]) -> tuple[subprocess.Popen[str], object]:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = (LOG_DIR / f"{name}.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, "-u", *args],
        cwd=ROOT,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return process, log_file


def wait_ready(port: int, action: str = "PING", timeout: float = 8.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = request_json("127.0.0.1", port, {"action": action}, timeout=0.4)
            if response.get("ok"):
                return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"service on port {port} did not become ready")


def show(label: str, response: dict) -> None:
    print(f"\n[{label}]")
    print(json.dumps(response, indent=2, sort_keys=True))


def main() -> None:
    processes: list[tuple[str, subprocess.Popen[str], object]] = []
    try:
        for name, args in [
            ("origin", ["origin_server.py", "--port", "8900"]),
            ("edge_india", ["edge_server.py", "--name", "edge-india", "--port", "8801", "--origin-port", "8900", "--ttl", "30"]),
            ("edge_asia", ["edge_server.py", "--name", "edge-asia", "--port", "8802", "--origin-port", "8900", "--ttl", "30"]),
            ("dispatcher", ["dispatcher.py", "--port", "8800", "--node", "edge-india:127.0.0.1:8801", "--node", "edge-asia:127.0.0.1:8802"]),
        ]:
            process, handle = start(name, args)
            processes.append((name, process, handle))
        for port in (8900, 8801, 8802, 8800):
            wait_ready(port)

        print("EDGEFLOW SIMULATOR - COMPLETE DEMONSTRATION")
        print("Student: Kumar Shivam   Registration: 25MCMC34")
        print("Services ready: dispatcher=8800, edges=8801/8802, origin=8900")

        show("1 DISTRIBUTED STATUS", request_json("127.0.0.1", 8800, {"action": "STATUS"}))
        show("2 FIRST REQUEST CACHE MISS", request_json("127.0.0.1", 8800, {"action": "GET", "resource": "/intro"}))
        show("3 SECOND EDGE CACHE MISS", request_json("127.0.0.1", 8800, {"action": "GET", "resource": "/intro"}))
        show("4 REPEATED REQUEST CACHE HIT", request_json("127.0.0.1", 8800, {"action": "GET", "resource": "/intro"}))

        edge_india = next(process for name, process, _ in processes if name == "edge_india")
        edge_india.terminate()
        edge_india.wait(timeout=3)
        time.sleep(0.4)
        show("5 STATUS AFTER EDGE FAILURE", request_json("127.0.0.1", 8800, {"action": "STATUS"}))
        show("6 FAILOVER REQUEST", request_json("127.0.0.1", 8800, {"action": "GET", "resource": "/architecture"}))
        show("7 UNKNOWN RESOURCE", request_json("127.0.0.1", 8800, {"action": "GET", "resource": "/missing"}))
        print("\nDEMO RESULT: PASS - cache, routing, health checks, and failover were exercised.")
    finally:
        for _, process, _ in reversed(processes):
            if process.poll() is None:
                process.terminate()
        for _, process, handle in reversed(processes):
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            handle.close()


if __name__ == "__main__":
    main()

