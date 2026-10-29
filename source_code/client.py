"""Command-line client for the EdgeFlow Simulator."""

from __future__ import annotations

import argparse
import json
import time

from common import request_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a request to the EdgeFlow dispatcher")
    parser.add_argument("resource", nargs="?", default="/intro")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()
    for number in range(1, args.repeat + 1):
        started = time.perf_counter()
        response = request_json(args.host, args.port, {"action": "GET", "resource": args.resource}, timeout=4.0)
        elapsed_ms = (time.perf_counter() - started) * 1000
        print(f"Request {number}: resource={args.resource} elapsed={elapsed_ms:.1f} ms")
        print(json.dumps(response, indent=2, sort_keys=True))
        if number < args.repeat:
            time.sleep(args.delay)


if __name__ == "__main__":
    main()

