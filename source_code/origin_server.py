"""Central origin server for the EdgeFlow Simulator."""

from __future__ import annotations

import argparse
import logging
import socketserver
import threading
import time
from typing import Any

from common import error_response, receive_json, send_json


CONTENT: dict[str, dict[str, Any]] = {
    "/intro": {
        "content": "Cloudflare Workers runs application code on distributed edge locations.",
        "version": 1,
    },
    "/architecture": {
        "content": "Client requests pass through routing, edge compute, cache, and an origin service.",
        "version": 1,
    },
    "/concepts": {
        "content": "The project demonstrates caching, load distribution, health checks, and failover.",
        "version": 1,
    },
}
CONTENT_LOCK = threading.Lock()


class OriginHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        try:
            request = receive_json(self.request)
            action = request.get("action")
            if action == "PING":
                send_json(self.request, {"ok": True, "role": "origin"})
                return
            if action == "GET":
                resource = str(request.get("resource", ""))
                with CONTENT_LOCK:
                    item = CONTENT.get(resource)
                if item is None:
                    send_json(self.request, error_response(f"resource {resource!r} was not found", "not_found"))
                    return
                time.sleep(0.08)
                response = {
                    "ok": True,
                    "resource": resource,
                    "content": item["content"],
                    "version": item["version"],
                    "served_by": "origin",
                    "generated_at": round(time.time(), 3),
                }
                logging.info("GET %s version=%s", resource, item["version"])
                send_json(self.request, response)
                return
            if action == "PUT":
                resource = str(request.get("resource", ""))
                content = str(request.get("content", "")).strip()
                if not resource.startswith("/") or not content:
                    send_json(self.request, error_response("PUT requires a /resource and non-empty content"))
                    return
                with CONTENT_LOCK:
                    previous = CONTENT.get(resource, {"version": 0})
                    version = int(previous["version"]) + 1
                    CONTENT[resource] = {"content": content, "version": version}
                logging.info("PUT %s version=%s", resource, version)
                send_json(self.request, {"ok": True, "resource": resource, "version": version})
                return
            send_json(self.request, error_response("supported actions are PING, GET, and PUT"))
        except Exception as exc:
            logging.exception("origin request failed")
            try:
                send_json(self.request, error_response(str(exc), "server_error"))
            except Exception:
                pass


class ThreadingServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the EdgeFlow origin server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s ORIGIN %(message)s", datefmt="%H:%M:%S")
    with ThreadingServer((args.host, args.port), OriginHandler) as server:
        logging.info("listening on %s:%s", args.host, args.port)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("shutdown requested")


if __name__ == "__main__":
    main()

