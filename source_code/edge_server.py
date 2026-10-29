"""Caching edge node for the EdgeFlow Simulator."""

from __future__ import annotations

import argparse
import logging
import socketserver
import threading
import time
from dataclasses import dataclass
from typing import Any

from common import error_response, receive_json, request_json, send_json


@dataclass
class CacheEntry:
    response: dict[str, Any]
    expires_at: float


class EdgeState:
    def __init__(self, name: str, origin_host: str, origin_port: int, ttl: float) -> None:
        self.name = name
        self.origin_host = origin_host
        self.origin_port = origin_port
        self.ttl = ttl
        self.cache: dict[str, CacheEntry] = {}
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, resource: str) -> dict[str, Any]:
        now = time.time()
        with self.lock:
            entry = self.cache.get(resource)
            if entry and entry.expires_at > now:
                self.hits += 1
                result = dict(entry.response)
                result.update({"served_by": self.name, "cache": "HIT", "cache_age_ms": int((now - result["cached_at"]) * 1000)})
                return result
            if entry:
                self.cache.pop(resource, None)
            self.misses += 1
        origin_response = request_json(
            self.origin_host,
            self.origin_port,
            {"action": "GET", "resource": resource},
            timeout=2.5,
        )
        if not origin_response.get("ok"):
            return origin_response
        cached = dict(origin_response)
        cached["cached_at"] = now
        with self.lock:
            self.cache[resource] = CacheEntry(cached, now + self.ttl)
        result = dict(cached)
        result.update({"served_by": self.name, "cache": "MISS", "cache_age_ms": 0})
        return result

    def stats(self) -> dict[str, Any]:
        with self.lock:
            return {"hits": self.hits, "misses": self.misses, "cached_resources": sorted(self.cache)}


class EdgeHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        state: EdgeState = self.server.state  # type: ignore[attr-defined]
        try:
            request = receive_json(self.request)
            action = request.get("action")
            if action == "PING":
                send_json(self.request, {"ok": True, "role": "edge", "node": state.name, **state.stats()})
                return
            if action == "GET":
                resource = str(request.get("resource", ""))
                if not resource.startswith("/"):
                    send_json(self.request, error_response("resource must start with /"))
                    return
                result = state.get(resource)
                logging.info("GET %s cache=%s", resource, result.get("cache", "N/A"))
                send_json(self.request, result)
                return
            if action == "STATS":
                send_json(self.request, {"ok": True, "node": state.name, **state.stats()})
                return
            send_json(self.request, error_response("supported actions are PING, GET, and STATS"))
        except Exception as exc:
            logging.exception("edge request failed")
            try:
                send_json(self.request, error_response(str(exc), "edge_error"))
            except Exception:
                pass


class EdgeServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address: tuple[str, int], state: EdgeState) -> None:
        super().__init__(address, EdgeHandler)
        self.state = state


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one EdgeFlow caching edge node")
    parser.add_argument("--name", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--origin-host", default="127.0.0.1")
    parser.add_argument("--origin-port", type=int, default=9000)
    parser.add_argument("--ttl", type=float, default=15.0)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format=f"%(asctime)s {args.name} %(message)s", datefmt="%H:%M:%S")
    state = EdgeState(args.name, args.origin_host, args.origin_port, args.ttl)
    with EdgeServer((args.host, args.port), state) as server:
        logging.info("listening on %s:%s origin=%s:%s ttl=%ss", args.host, args.port, args.origin_host, args.origin_port, args.ttl)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("shutdown requested")


if __name__ == "__main__":
    main()

