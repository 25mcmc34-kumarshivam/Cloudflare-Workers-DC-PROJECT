# EdgeFlow Simulator

Student: Kumar Shivam  
Registration number: 25MCMC34

EdgeFlow Simulator is a Python socket programming project that models a simplified distributed edge platform inspired by Cloudflare Workers. It includes a client, a health-aware dispatcher, two caching edge nodes, and one origin server.

## Quick start

1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Run `python demo.py`.
4. Run `python -m unittest -v test_system.py` to execute the integration tests.

The project uses only the Python standard library and does not need third-party packages.

## Manual execution

Open five terminals in this folder and run:

```text
python origin_server.py --port 9000
python edge_server.py --name edge-india --port 8001 --ttl 30
python edge_server.py --name edge-asia --port 8002 --ttl 30
python dispatcher.py --port 8000 --node edge-india:127.0.0.1:8001 --node edge-asia:127.0.0.1:8002
python client.py /intro --repeat 3
```

Stop `edge-india` and run the client again to observe dispatcher health checking and failover to `edge-asia`.

