# Study plan aur official online resources

## 7-day plan

### Day 1 — Python fundamentals

Revise functions, dictionaries, classes, exceptions, context managers, command-line arguments, and modules. Target: har source file read karke control flow identify kar pao.

### Day 2 — Socket programming

TCP client/server, bind/listen/accept, connect, send/receive, timeouts, ports, localhost, and byte encoding. `common.py`, `origin_server.py`, and `client.py` trace karo.

### Day 3 — Distributed-system basics

Partial failure, transparency, concurrency, replication, availability, scalability, and consistency. Project ke har feature ko ek property se map karo.

### Day 4 — Cache and algorithms

TTL, hit/miss, stale data, round robin, health checks, retry and failover. Whiteboard par pseudocode likho.

### Day 5 — Code walkthrough

Breakpoint ya print-based tracing ke through request flow follow karo. One edge stop karke manual behavior observe karo.

### Day 6 — Reports and slides

All four documents skim nahi, actively explain karo. Har slide ke liye 3–4 spoken sentences prepare karo.

### Day 7 — Viva rehearsal

Demo twice run karo. Viva questions bina notes answer karo. Failover, cache consistency, TCP framing aur limitations par focus karo.

## Official/reliable resources

### Cloudflare Workers

- [Cloudflare Workers learning path](https://developers.cloudflare.com/learning-paths/workers/concepts/workers-concepts/) — Workers ka execution model aur core concepts.
- [Cloudflare introduction](https://developers.cloudflare.com/learning-paths/workers/concepts/cloudflare-intro/) — global network aur developer platform context.
- [Build your first Worker](https://developers.cloudflare.com/learning-paths/workers/get-started/first-application/) — actual Cloudflare Worker banana seekhne ke liye.
- [Cloudflare Workers tutorials](https://developers.cloudflare.com/workers/tutorials/) — beginner se advanced practical examples.

### Python networking

- [Python Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html) — TCP sockets aur message behavior.
- [Python `socket` library](https://docs.python.org/3/library/socket.html) — exact API reference.
- [Python `socketserver` library](https://docs.python.org/3/library/socketserver.html) — reusable TCP server classes and threaded server behavior.
- [Python `unittest`](https://docs.python.org/3/library/unittest.html) — automated test structure and assertions.

### HTTP and caching

- [MDN HTTP caching guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching) — cache freshness, shared caches, validation and trade-offs.
- [MDN Cache-Control reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control) — production HTTP cache directives.

## Online content ko project se kaise connect karein

Socket tutorial dekhte waqt project ka newline framing note karo. Cache guide padhte waqt TTL implementation compare karo. Cloudflare learning path padhte waqt “real platform feature” aur “our simplified representation” ki two-column notes banao. Blind copying ke badle har topic ke niche ek sentence likho: “Ye mere project mein kahan hai?”

## Optional extension learning

Core assignment samajhne ke baad:

- consistent hashing for scalable node changes;
- least-connections/latency-aware load balancing;
- cache invalidation and ETag;
- circuit breaker and exponential backoff;
- async I/O with `asyncio`;
- TLS and authentication;
- metrics: hit ratio, latency percentiles, error rate;
- containers and deployment.

