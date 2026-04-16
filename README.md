# Nadiru Nadis

Tools and applications built on the [Nadiru engine](https://github.com/hlk-devs/nadiru-engine).

Each Nadi is a standalone tool that talks to a running Nadiru engine via its REST API. No engine code is imported — everything goes through `/connect`, `/generate`, and `/query`.

## Nadis

| Nadi | What it does | How to run |
|------|-------------|------------|
| [nadi-chat](nadi-chat/) | CLI chat interface with routing display | `python chat.py` |
| [nadi-dashboard](nadi-dashboard/) | Web UI with chat, routing, and cost tracking | Open `index.html` in browser |
| [nadi-costs](nadi-costs/) | Terminal cost report by provider and model | `python costs.py` |
| [nadi-health](nadi-health/) | Test all providers, report status and latency | `python health.py` |
| [nadi-translate](nadi-translate/) | Translate text between languages | `python translate.py "text" spanish` |
| [nadi-summarize](nadi-summarize/) | Summarize text or files | `python summarize.py --file doc.txt` |

## Building Your Own Nadi

A Nadi is any application that connects to Nadiru. The pattern is simple:

```python
import httpx

ENGINE = "http://localhost:8765"

# 1. Connect
resp = httpx.post(f"{ENGINE}/connect", json={"name": "my-nadi"})
nadi_id = resp.json()["nadi_id"]

# 2. Generate
resp = httpx.post(f"{ENGINE}/generate", json={
    "nadi_id": nadi_id,
    "prompt": "Your prompt here",
    "priority": "balanced",  # cost, balanced, or quality
})
print(resp.json()["content"])

# 3. Query history (optional)
resp = httpx.get(f"{ENGINE}/query", params={"nadi_id": nadi_id})
```

Three endpoints. That's the entire API. Build a Discord bot, a CLI tool, a web app, a batch processor — anything that can make HTTP requests can be a Nadi.

## Setup

1. Make sure the Nadiru engine is running: `python -m nadiru_engine`
2. `cd` into any Nadi directory
3. Run it

All Nadis require `httpx` (`pip install httpx`).

## License

MIT
