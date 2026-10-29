"""Health-aware request dispatcher for EdgeFlow Simulator."""

from __future__ import annotations

import argparse
import logging
import socketserver
import threading
from dataclasses import dataclass
from typing import Any

from common import error_response, receive_json, request_json, send_json


@dataclass(frozen=True)
class EdgeNode:
    name: str
    host: str
    port: int


class DispatcherState:
    def __init__(self, nodes: list[EdgeNode]) -> None:
        self.nodes = nodes
        self.counter = 0
        self.lock = threading.Lock()

    def ordered_nodes(self) -> list[EdgeNode]:
        with self.lock:
            start = self.counter % len(self.nodes)
            self.counter += 1
        return self.nodes[start:] + self.nodes[:start]

    @staticmethod
    def is_healthy(node: EdgeNode) -> bool:
        try:
            response = request_json(node.host, node.port, {"action": "PING"}, timeout=0.45)
            return bool(response.get("ok"))
        except Exception:
            return False

    def route(self, request: dict[str, Any]) -> dict[str, Any]:
        attempts: list[dict[str, Any]] = []
        for node in self.ordered_nodes():
            if not self.is_healthy(node):
                attempts.append({"node": node.name, "result": "health_check_failed"})
                logging.warning("health check failed for %s", node.name)
                continue
            try:
                response = request_json(node.host, node.port, request, timeout=3.0)
                attempts.append({"node": node.name, "result": "served"})
                response["dispatcher"] = "edge-dispatcher"
                response["routing_attempts"] = attempts
                return response
            except Exception as exc:
                attempts.append({"node": node.name, "result": "request_failed", "detail": type(exc).__name__})
                logging.warning("request to %s failed: %s", node.name, exc)
        return {"ok": False, "error": "no_edge_available", "message": "all edge nodes failed", "routing_attempts": attempts}

    def status(self) -> dict[str, Any]:
        return {
            "ok": True,
            "nodes": [
                {"name": node.name, "host": node.host, "port": node.port, "healthy": self.is_healthy(node)}
                for node in self.nodes
            ],
        }


class DispatcherHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        state: DispatcherState = self.server.state  # type: ignore[attr-defined]
        try:
            request = receive_json(self.request)
            action = request.get("action")
            if action == "PING":
                send_json(self.request, {"ok": True, "role": "dispatcher"})
                return
            if action == "STATUS":
                send_json(self.request, state.status())
                return
            if action == "GET":
                response = state.route(request)
                logging.info("GET %s served_by=%s cache=%s", request.get("resource"), response.get("served_by"), response.get("cache"))
                send_json(self.request, response)
                return
            send_json(self.request, error_response("supported actions are PING, STATUS, and GET"))
        except Exception as exc:
            logging.exception("dispatcher request failed")
            try:
                send_json(self.request, error_response(str(exc), "dispatcher_error"))
            except Exception:
                pass


class DispatcherServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address: tuple[str, int], state: DispatcherState) -> None:
        super().__init__(address, DispatcherHandler)
        self.state = state


def parse_node(value: str) -> EdgeNode:
    try:
        name, host, port_text = value.split(":", 2)
        return EdgeNode(name, host, int(port_text))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("node must be NAME:HOST:PORT") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the EdgeFlow edge dispatcher")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--node", action="append", type=parse_node, required=True, help="NAME:HOST:PORT")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s DISPATCHER %(message)s", datefmt="%H:%M:%S")
    state = DispatcherState(args.node)
    with DispatcherServer((args.host, args.port), state) as server:
        logging.info("listening on %s:%s nodes=%s", args.host, args.port, ",".join(node.name for node in args.node))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("shutdown requested")


if __name__ == "__main__":
    main()

