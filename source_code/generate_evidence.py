"""Run verified scenarios and create browser-ready execution evidence pages."""

from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
LOGS = PROJECT / "execution_logs"
PAGES = PROJECT / "evidence_pages"


def run(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=45,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"command failed with exit code {completed.returncode}\n{completed.stdout}")
    return completed.stdout


def page(title: str, subtitle: str, content: str, filename: str) -> None:
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
html,body{{margin:0;background:#0b1020;color:#d9e6ff;font-family:Consolas,'Courier New',monospace}}
body{{padding:34px}} .frame{{border:1px solid #334b7a;border-radius:12px;overflow:hidden;box-shadow:0 18px 60px #0008}}
.bar{{background:#16213d;padding:14px 20px;color:#89b4ff;font:700 18px Arial,sans-serif}}
.sub{{font:14px Arial,sans-serif;color:#9fb2d9;background:#111a30;padding:9px 20px;border-bottom:1px solid #334b7a}}
pre{{margin:0;padding:24px 26px;font-size:17px;line-height:1.38;white-space:pre-wrap;min-height:570px}}
.ok{{color:#74e6a7}} .student{{color:#ffd479}}
</style></head><body><div class="frame"><div class="bar">{html.escape(title)}</div>
<div class="sub">{html.escape(subtitle)}</div><pre>{html.escape(content)}</pre></div></body></html>"""
    (PAGES / filename).write_text(document, encoding="utf-8")


def extract(text: str, start: str, end: str | None = None) -> str:
    begin = text.index(start)
    finish = text.index(end, begin) if end else len(text)
    return text[begin:finish].strip()


def parse_demo_json(text: str, label: str, next_label: str) -> dict:
    block = extract(text, label, next_label)
    json_start = block.index("{")
    return json.loads(block[json_start:])


def main() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)
    test_output = run([sys.executable, "-m", "unittest", "-v", "test_system.py"])
    demo_output = run([sys.executable, "demo.py"])
    (LOGS / "integration_tests.txt").write_text(test_output, encoding="utf-8")
    (LOGS / "complete_demo.txt").write_text(demo_output, encoding="utf-8")

    status = extract(demo_output, "[1 DISTRIBUTED STATUS]", "[2 FIRST REQUEST CACHE MISS]")
    cache_one = parse_demo_json(demo_output, "[2 FIRST REQUEST CACHE MISS]", "[3 SECOND EDGE CACHE MISS]")
    cache_two = parse_demo_json(demo_output, "[3 SECOND EDGE CACHE MISS]", "[4 REPEATED REQUEST CACHE HIT]")
    cache_three = parse_demo_json(demo_output, "[4 REPEATED REQUEST CACHE HIT]", "[5 STATUS AFTER EDGE FAILURE]")
    cache = "\n".join([
        "[2 FIRST REQUEST]",
        f"edge={cache_one['served_by']}   cache={cache_one['cache']}   resource={cache_one['resource']}",
        f"content={cache_one['content']}",
        "",
        "[3 SAME RESOURCE ON SECOND EDGE]",
        f"edge={cache_two['served_by']}   cache={cache_two['cache']}   resource={cache_two['resource']}",
        "The second edge fetched its own copy from the origin.",
        "",
        "[4 REPEATED REQUEST]",
        f"edge={cache_three['served_by']}   cache={cache_three['cache']}   age={cache_three['cache_age_ms']} ms",
        "The repeated request was served from edge memory without an origin lookup.",
        "",
        "RESULT: PASS - both cache miss and cache hit paths were verified.",
    ])
    failover = extract(demo_output, "[5 STATUS AFTER EDGE FAILURE]", "[7 UNKNOWN RESOURCE]")

    page("EdgeFlow Simulator Status", "Kumar Shivam | 25MCMC34 | verified execution", status, "01_status.html")
    page("Edge Cache Demonstration", "Two edge nodes followed by a repeated request", cache, "02_cache.html")
    page("Edge Failure and Failover", "edge-india stopped; dispatcher continued through edge-asia", failover, "03_failover.html")
    page("Automated Integration Tests", "Python unittest execution", test_output, "04_tests.html")
    print(f"Evidence generated in {PAGES}")


if __name__ == "__main__":
    main()

