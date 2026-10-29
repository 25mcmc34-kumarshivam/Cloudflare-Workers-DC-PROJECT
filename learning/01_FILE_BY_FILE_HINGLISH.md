# Har file kya karti hai — detailed Hinglish guide

## `source_code/common.py`

Ye shared networking utility file hai. Client aur servers ko same message framing follow karni chahiye, isliye common logic ek jagah rakha gaya hai.

- `send_json(...)` Python dictionary ko JSON string mein convert karta hai, newline add karta hai, aur socket par bytes bhejta hai.
- `receive_json(...)` newline tak bytes read karta hai, size limit enforce karta hai, phir JSON ko dictionary banata hai.
- Message size limit memory abuse aur accidentally endless input se protection deti hai.
- Newline delimiter zaroori hai kyunki TCP message boundaries preserve nahi karta; TCP ek byte stream hai.

Viva line: “TCP mein ek `send` ka matlab ek `recv` guaranteed nahi hota. Isliye maine newline-delimited JSON framing use ki.”

## `source_code/origin_server.py`

Origin authoritative data source hai. Is project mein predefined resources dictionary mein stored hain. Edge node ko requested path apne cache mein nahi milta to woh origin ko `GET` request bhejta hai.

Main responsibilities:

- TCP port par listen karna.
- `PING` ka health response dena.
- valid path par original content return karna.
- unknown path par structured `not_found` error dena.
- har connection ko safely handle karna.

Real-world analogy: website/application ka primary backend ya storage. Real Cloudflare architecture mein origin Cloudflare network ke bahar customer ka web server ho sakta hai.

## `source_code/edge_server.py`

Ye project ka caching layer hai. Do separate processes same code ko different name/port ke saath run karte hain: `edge-india` aur `edge-asia`.

Request handling logic:

1. Request validate karo.
2. Current time check karo.
3. Path cache mein hai aur expiry future mein hai to `HIT`.
4. Entry absent/expired ho to origin se fetch; ye `MISS` hai.
5. Successful origin response ko `current_time + TTL` expiry ke saath store karo.
6. Response mein serving node aur cache status add karo.

Har edge ka cache independent hai. Isliye same resource pe Edge India ka HIT aur Edge Asia ka MISS possible hai. Ye distributed state ka simple example hai.

## `source_code/dispatcher.py`

Dispatcher client aur edge pool ke beech gateway hai. Client ko individual edge addresses ya failure state jaanne ki zaroorat nahi.

Main responsibilities:

- `STATUS` request par configured edges ki health report dena.
- `GET` request se pehle candidate ordering banana.
- round-robin counter se first preference rotate karna.
- `PING` se node health check karna.
- unhealthy/unreachable node skip karna.
- selected node request fail kare to next candidate try karna.
- routing attempts response mein dena, jisse behavior observable rahe.

Round robin perfect load balancing nahi hai—request cost aur node capacity ko equal assume karta hai—but classroom simulator ke liye deterministic aur explainable hai.

## `source_code/client.py`

Client user-facing command-line program hai. Ye dispatcher ko structured request bhejta hai aur formatted response print karta hai.

- User resource path de sakta hai.
- Dispatcher host/port configurable hai.
- JSON output debugging aur evidence ke liye readable hai.

Client intentionally edge nodes ko direct call nahi karta. Isse **location transparency** milti hai: client ko service location change hone ki concern nahi.

## `source_code/demo.py`

Demo complete system orchestration karta hai:

1. Origin start.
2. Two edge processes start.
3. Dispatcher start.
4. Services ready hone ka wait.
5. Status, cache MISS/HIT, and routing demonstrate.
6. Edge India process terminate karke failure inject.
7. Failover request execute.
8. Missing resource error demonstrate.
9. `finally` cleanup mein child processes stop.

Failure injection important hai: sirf code mein failover likhna sufficient proof nahi; demo actual process stop karke behavior observe karta hai.

## `source_code/test_system.py`

Five integration tests real sockets aur subprocesses ke through components ko together verify karte hain.

- Initial health/status test.
- Cache MISS then HIT test.
- Dispatcher routing test.
- Edge failure ke baad failover test.
- Missing resource structured error test.

Unit test ek isolated function check karta; integration test components ke interaction ko check karta hai. Is project mein assignment ka main behavior interaction-based hai, isliye integration testing zyada valuable hai.

## `source_code/generate_evidence.py`

Tests aur demo ko run karke reproducible text logs aur screenshot-friendly evidence pages generate karta hai. Isse report ka evidence manually type nahi hota; actual program output use hota hai.

## `source_code/run_demo.bat`

Windows convenience launcher hai. Double click se Python demo start hota hai. Logic ka source `demo.py` hi hai.

## `source_code/requirements.txt`

Project Python standard library use karta hai, isliye external package dependency nahi. File mein ye explicitly documented hai taaki evaluator ko installation expectation clear rahe.

## Documents folder

- `Architecture_25MCMC34.docx`: chosen app ki architecture study, simulator mapping, components, flows, failure/state discussion.
- `ParadigmsandAlgorithms_25MCMC34.docx`: distributed paradigms, round robin, health checks, TTL caching, threading, framing, consistency trade-offs.
- `RequirementSpecificationSimpleApp_25MCMC34.docx`: scope, functional/non-functional requirements, interfaces, use cases, acceptance criteria, constraints, risks.
- `Tutorial_Installation_and_Usage_25MCMC34.docx`: install, quick demo, manual execution, screenshots, testing, troubleshooting and viva preparation.

## Presentation and evidence

- PPTX is presentation-ready summary; sirf slide read mat karo—architecture flow apne words mein explain karo.
- Screenshots actual verified execution ke evidence hain.
- Logs complete plain-text output provide karte hain, jahan screenshot mein limited lines visible hain.

