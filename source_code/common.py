"""Shared JSON-over-TCP helpers for the EdgeFlow Simulator."""

from __future__ import annotations

import json
import socket
from typing import Any


MAX_MESSAGE_BYTES = 64 * 1024


def send_json(sock: socket.socket, payload: dict[str, Any]) -> None:
    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8") + b"\n"
    if len(data) > MAX_MESSAGE_BYTES:
        raise ValueError("message is too large")
    sock.sendall(data)


def receive_json(sock: socket.socket) -> dict[str, Any]:
    chunks: list[bytes] = []
    size = 0
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        chunks.append(chunk)
        size += len(chunk)
        if size > MAX_MESSAGE_BYTES:
            raise ValueError("message exceeds size limit")
        if b"\n" in chunk:
            break
    if not chunks:
        raise ConnectionError("peer closed the connection before sending data")
    raw = b"".join(chunks).split(b"\n", 1)[0]
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("message must be a JSON object")
    return value


def request_json(host: str, port: int, payload: dict[str, Any], timeout: float = 2.0) -> dict[str, Any]:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        send_json(sock, payload)
        return receive_json(sock)


def error_response(message: str, code: str = "bad_request") -> dict[str, Any]:
    return {"ok": False, "error": code, "message": message}

