# Cloudflare Workers DC Project — EdgeFlow Simulator

**Student:** Kumar Shivam  
**Roll number:** 25MCMC34  
**Course:** Distributed Computing — Minor III Mini Project  
**Selected application:** Cloudflare Workers  
**Implemented simplified system:** EdgeFlow Simulator

EdgeFlow Simulator is a working Python socket-programming project that demonstrates four important ideas behind a distributed edge platform: request routing, replicated edge nodes, TTL caching, and automatic failover. It is an educational simulation—not Cloudflare's proprietary production code.

## What the project proves

1. A client sends a resource request to one stable dispatcher endpoint.
2. The dispatcher checks edge-node health and selects a healthy node using round robin.
3. Each edge node keeps an independent time-limited cache.
4. A cache miss is fetched from the origin; a fresh cache hit avoids origin access.
5. If one edge node stops, the dispatcher retries another healthy node.
6. Five automated integration tests verify status, caching, routing, failover, and error handling.

## Repository structure

```text
.
├── source_code/                  # Complete runnable Python implementation
├── documents/                    # Four final DOCX reports/manuals
├── presentation/                 # Final presentation deck
├── execution_screenshots/        # Evidence of cache, health, failover and tests
├── execution_logs/               # Plain-text output from verified runs
├── learning/                     # Detailed Hinglish study and viva material
├── 25MCMC34_..._Submission.zip   # Clean Classroom-ready package
├── README.md                     # Project overview and quick start
└── .gitignore                    # Excludes generated/temp files
```

## Quick start

Requirement: Python 3.10 or newer. No third-party Python package is required.

```powershell
cd source_code
python demo.py
```

Run the automated tests:

```powershell
python -m unittest -v test_system.py
```

Windows users can also double-click `source_code/run_demo.bat`.

## Expected demo behavior

- Both edge nodes initially report healthy.
- First request to an edge is a cache `MISS`.
- Repeated request to the same edge becomes a cache `HIT`.
- The demo deliberately stops `edge-india`.
- The dispatcher detects the failure and serves through `edge-asia`.
- A missing resource returns a structured `not_found` error instead of crashing.

## Submission files

- `documents/Architecture_25MCMC34.docx`
- `documents/ParadigmsandAlgorithms_25MCMC34.docx`
- `documents/RequirementSpecificationSimpleApp_25MCMC34.docx`
- `documents/Tutorial_Installation_and_Usage_25MCMC34.docx`
- `presentation/Cloudflare_Workers_EdgeFlow_25MCMC34.pptx`
- `source_code/`
- `execution_screenshots/`

## Start learning here

Open [`learning/00_START_HERE_HINGLISH.md`](learning/00_START_HERE_HINGLISH.md). It tells you exactly what to study, in which order, what every file means, how to explain the project in viva, and which official online resources to use.

## Academic honesty and scope

The repository includes complete learning material so the student can understand and defend every design choice. Cloudflare Workers is used as the inspiration. The implementation deliberately simplifies real global edge infrastructure into four local socket services that can be observed and tested on one computer.

