# Viva questions with Hinglish answers

## 1. Aapne Cloudflare Workers kyun choose kiya?

Cloudflare Workers distributed edge/serverless platform ka clear example hai. Isme user-near execution, global distribution, low latency, availability aur caching jaise DC concepts naturally connect hote hain. Classroom implementation ke liye maine selected behaviors ka local simplified simulator banaya.

## 2. Aapka project exactly kya karta hai?

Client dispatcher ko resource request bhejta hai. Dispatcher healthy edge node select karta hai. Edge fresh cache ho to cached response deta hai, otherwise origin se fetch karke TTL cache mein store karta hai. Ek edge fail ho to dispatcher alternate edge par request retry karta hai.

## 3. Ye real Cloudflare Worker hai?

Nahi. Ye Cloudflare Workers architecture se inspired educational simulator hai. Real platform global infrastructure aur production isolation use karta hai; mera project local Python socket processes se core distributed behaviors demonstrate karta hai.

## 4. Socket programming kyun use ki?

Assignment mein Java/Python socket programming specified thi. Sockets components ko genuinely separate processes mein network messages ke through communicate karwate hain, isliye distributed interaction observable hota hai.

## 5. TCP kyun, UDP kyun nahi?

Resource request/response ko reliable, ordered delivery chahiye. TCP ye properties deta hai. UDP lower overhead hai but loss, ordering, retransmission application ko handle karna padta.

## 6. JSON ke saath newline kyun?

TCP byte stream hai, message boundary nahi deta. Newline one logical JSON message ka delimiter hai. Receiver newline tak read karke complete object parse karta hai.

## 7. Dispatcher ka role kya hai?

Single entry point, health-aware node selection, round-robin ordering, failed node skip, retry/failover, and routing visibility.

## 8. Round robin ka limitation?

It assumes nodes and requests roughly equal. It actual CPU load, connection count, latency, ya node capacity consider nahi karta. Extension mein weighted round robin ya least-connections use ho sakta hai.

## 9. Cache HIT aur MISS?

Fresh entry local cache mein available ho to HIT. Entry absent ya expired ho to MISS; edge origin se fetch karta hai. HIT origin load aur response latency reduce karta hai.

## 10. TTL ka trade-off?

Long TTL better hit rate and lower origin load deta hai but stale data longer possible. Short TTL fresher data deta hai but origin traffic increase hota hai.

## 11. Failover kaise hota hai?

Dispatcher candidate node ko health check karta hai. Node unreachable/invalid ho to attempt record karke next node try karta hai. Actual request failure par bhi next node retry hota hai.

## 12. Partial failure kya hai?

Distributed system ka ek component fail ho sakta hai while others work. Demo mein Edge India stop hota hai but dispatcher, origin, and Edge Asia alive rehte hain, so service continue karti hai.

## 13. Consistency model kya hai?

Origin authoritative source hai. Edge caches independently TTL tak old value serve kar sakte hain. Isliye strong instant consistency nahi; time-bounded staleness/eventual refresh behavior hai.

## 14. Threading kyun?

Threaded server multiple connections concurrently handle kar sakta hai. Ek slow connection entire listener ko block nahi karta. Production scale par bounded pool/event loop useful hoga.

## 15. Tests kya prove karte hain?

Initial health, MISS-to-HIT transition, dispatcher routing, real process shutdown ke baad failover, and unknown resource ka structured error. Five tests components ke integration ko verify karte hain.

## 16. System ki limitations?

Local-only topology, in-memory cache, fixed origin data, no TLS/authentication, simple health check, no persistent storage, no geographic latency, and small static edge list.

## 17. Production banane ke liye kya add karoge?

TLS, authentication, configuration service, service discovery, metrics/log aggregation, bounded concurrency, circuit breaker, persistent/distributed cache, cache invalidation, rate limiting, and secure deployment.

## 18. Agar origin fail ho jaye?

Fresh cached content still serve ho sakta hai until TTL expiry, depending on implementation policy. Current simulator cache miss par structured origin error return karega. Future enhancement stale-if-error policy ho sakti hai.

## 19. Health check successful hone ke immediately baad node fail ho sakta hai?

Haan. Health knowledge instant guarantee nahi. Isliye actual request timeout/failure par retry bhi implemented hai; only pre-check sufficient nahi.

## 20. Aapne kya personally learn kiya?

Distributed system mein normal success flow se zyada failure handling important hai. TCP framing explicitly define karna padta hai, caches consistency trade-off create karte hain, and automated integration tests design claims ko repeatable evidence mein convert karte hain.

## Rapid-fire one-line revision

- Origin = authoritative source.
- Edge = cache/processing layer closer to client.
- Dispatcher = health-aware router.
- TTL = freshness duration.
- HIT = origin call saved.
- MISS = origin fetch required.
- Failover = alternate node after failure.
- Timeout = infinite wait prevention.
- Round robin = turn-wise node preference.
- Structured error = crash ke badle predictable JSON response.

