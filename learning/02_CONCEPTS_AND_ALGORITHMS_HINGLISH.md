# Concepts aur algorithms — detailed Hinglish explanation

## 1. Distributed computing

Distributed system mein components network messages se coordinate karte hain. Har process ki apni memory aur failure possibility hoti hai. Is project mein origin, dispatcher, do edge nodes, aur client separate processes hain. Ek process ka Python object doosre process ko directly visible nahi; information socket messages se travel karti hai.

Main consequences:

- Network fail ya slow ho sakta hai.
- Partial failure possible hai: Edge India down, Edge Asia alive.
- Har edge ke paas different cache state ho sakti hai.
- Timeout aur structured error handling essential hai.

## 2. Client-server and multi-tier architecture

Client request initiate karta hai; server listen aur respond karta hai. Yahan multi-tier flow hai:

`Client -> Dispatcher -> Edge -> Origin`

Benefits: responsibilities separate, components independently replace/test ho sakte, client simple rehta hai. Cost: extra network hops aur failure points.

## 3. Edge computing

Edge computing ka idea processing/data ko end user ke closer lana hai. Real Cloudflare global network user ke near data centers mein code execute kar sakta hai. Local simulator physical geography reproduce nahi karta; two edge processes logical regions represent karte hain.

## 4. Caching and TTL

Cache repeated work bachata hai. Entry ko conceptually `(value, expiry_time)` store kiya gaya hai.

```text
fresh if current_time < expiry_time
expiry_time = stored_time + TTL
```

- HIT: fresh entry mil gayi; origin call nahi.
- MISS: entry absent ya stale; origin fetch required.
- Small TTL: data fresher, origin load higher.
- Large TTL: fast and low load, but stale-data window larger.

Cache consistency intentionally eventual/staleness-bounded hai. Two edges instant synchronized cache maintain nahi karte.

## 5. Round-robin selection

Healthy nodes list `[A, B]` ho to preferred order requests ke saath rotate hota hai:

```text
Request 1: A then B
Request 2: B then A
Request 3: A then B
```

Complexity small list ke liye effectively O(n), kyunki worst case health/failure checks all nodes tak ja sakte hain. Advantage fairness and simplicity; limitation node capacity/latency aware nahi.

## 6. Health check and failover

Dispatcher `PING` bhejta hai. Valid `PONG`-style response within timeout means healthy. Connection refused, timeout, invalid response, ya request error failure signal hai.

Failover algorithm:

```text
for each candidate in rotated edge list:
    health check
    if unhealthy: record attempt and continue
    send actual request
    if success: return response
    otherwise continue
return service_unavailable
```

Health check perfect knowledge nahi deta. Check ke baad node fail ho sakta hai—isse time-of-check/time-of-use race bol sakte hain. Isliye actual request failure par bhi retry necessary hai.

## 7. Concurrency

Servers `ThreadingTCPServer` pattern use karte hain. Har connection ko separate handler thread mil sakta hai, isliye ek slow client sab clients ko block nahi karta.

Trade-off: unlimited threads production scale ke liye risky ho sakte hain. Production systems thread pools, event loops, backpressure, and rate limits use karte hain. Classroom scope mein thread-per-connection simple and observable hai.

## 8. TCP and message framing

TCP reliable ordered byte stream deta hai, message packets nahi. Isliye JSON ke end mein newline delimiter lagta hai. Receiver newline tak read karke exactly one logical message decode karta hai.

Timeout prevents indefinite wait. Max-size validation oversized message reject karti hai. JSON human-readable and language-independent hai, but binary protocols ke comparison mein verbose hai.

## 9. Availability, scalability, fault tolerance, consistency

- **Availability:** one edge failure ke baad second edge response deta hai.
- **Scalability:** more edge entries add karke request distribution extend ho sakti hai; concurrent server multiple clients handle karta hai.
- **Fault tolerance:** timeout, health check, retry, alternate node, structured errors.
- **Consistency:** origin authoritative; edge data TTL tak stale ho sakta hai.

CAP theorem ko overclaim mat karna. Ye simulator network partition ka rigorous CAP experiment nahi. Ye availability and cache-staleness trade-off demonstrate karta hai.

## 10. Real system vs simulator

Real Cloudflare Workers uses global routing, secure production isolation, observability, deployment control, and many managed services. Simulator local ports, in-memory caches, simple health checks, and fixed resource data use karta hai. Mapping conceptual hai: dispatcher global routing ka simplified representation, edge processes edge locations ka representation, origin customer backend ka representation.

