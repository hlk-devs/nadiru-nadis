# Nadiru Nadis

## What is a Nadi?

A Nadi is any application that connects to the
[Nadiru engine](https://github.com/hlk-devs/nadiru-engine).
The engine handles intelligent routing between AI providers â€”
your Nadi just sends prompts and gets responses. Build a chatbot,
a translation tool, a code assistant, a data pipeline, a full
SaaS product â€” anything that needs AI goes through Nadiru.

**The engine is the brain. Your Nadi is the body.**

The engine discovers 130+ models across 15+ providers, routes
intelligently based on task type and priority, streams responses,
detects content refusals and retries automatically, and learns
from every interaction. Your Nadi gets all of this for free
through three HTTP endpoints.

## Nadis

| Nadi | What it does | How to run |
|------|-------------|------------|
| [nadi-chat](nadi-chat/) | CLI chat interface with routing display | `python chat.py` |
| [nadi-dashboard](nadi-dashboard/) | Web UI with chat, routing, and cost tracking | Open `index.html` in browser |
| [nadi-costs](nadi-costs/) | Terminal cost report by provider and model | `python costs.py` |
| [nadi-health](nadi-health/) | Test all providers, report status and latency | `python health.py` |
| [nadi-translate](nadi-translate/) | Translate text between languages | `python translate.py "text" spanish` |
| [nadi-summarize](nadi-summarize/) | Summarize text or files | `python summarize.py --file doc.txt` |
| [nadi-codereview](nadi-codereview/) | Code review from file path | `python review.py file.py` |
| [nadi-commit](nadi-commit/) | Git commit message generator | `python commit.py` |
| [nadi-shell](nadi-shell/) | Natural language to shell command | `python shell.py "query"` |
| [nadi-scraper](nadi-scraper/) | Web scraper generator | `python scraper.py "task"` |
| [nadi-builder](nadi-builder/) | Build Nadis with AI + independent code review | Open `index.html` |
| [nadi-deepreview](nadi-deepreview/) | Three-stage independent code review pipeline | `python deepreview.py file.py` |

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

Three endpoints. That's the entire API. Build a Discord bot, a CLI tool, a web app, a batch processor â€” anything that can make HTTP requests can be a Nadi.

## Setup

1. Make sure the Nadiru engine is running: `python -m nadiru_engine`
2. `cd` into any Nadi directory
3. Run it

All Nadis require `httpx` (`pip install httpx`).

## License

MIT
