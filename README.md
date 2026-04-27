# Nadiru Nadis

**Reference Nadis for the [Nadiru engine](https://github.com/hlk-devs/nadiru-engine). Run them, read the code, build your own.**

A Nadi is any application that talks to Nadiru. The engine handles routing, cost optimization, streaming, and provider failover. Your Nadi just sends prompts and gets responses through three HTTP endpoints. This repo is a collection of working Nadis you can run today, both as demos of what Nadiru enables and as starting points for your own tools.

## Start here if you've never used Nadiru

Run these three in order, in a fresh terminal each:

1. **[nadi-dashboard](nadi-dashboard/)** — open `index.html` in a browser. Send a few prompts. Watch the routing change in real time. This is the fastest way to feel what Nadiru does.
2. **[nadi-chat](nadi-chat/)** — `python chat.py`. Same idea but in your terminal. Use `/cost` and `/quality` mid-conversation to see how routing shifts.
3. **[nadi-deepreview](nadi-deepreview/)** — `python deepreview.py somefile.py`. Three AI providers independently review your code. This is the one that makes the case for orchestrated multi-provider workflows.

If those three don't get you interested, the rest probably won't either. If they do, dig into the table below.

## All Nadis

| Nadi | What it does | How to run |
|------|--------------|------------|
| [nadi-builder](nadi-builder/) | Build new Nadis with AI plus independent code review | Open `index.html` |
| [nadi-chat](nadi-chat/) | CLI chat interface with routing display | `python chat.py` |
| [nadi-codereview](nadi-codereview/) | Quick structured code review for any file | `python review.py file.py` |
| [nadi-commit](nadi-commit/) | Generate commit messages from staged git changes | `python commit.py` |
| [nadi-costs](nadi-costs/) | Terminal cost report by provider and model | `python costs.py` |
| [nadi-dashboard](nadi-dashboard/) | Web UI with chat, routing, and cost tracking | Open `index.html` |
| [nadi-deepreview](nadi-deepreview/) | Three-stage independent code review pipeline | `python deepreview.py file.py` |
| [nadi-health](nadi-health/) | Test all providers, report status and latency | `python health.py` |
| [nadi-models](nadi-models/) | List all discovered models by provider | `python models.py` |
| [nadi-scraper](nadi-scraper/) | Generate runnable web scraper from a description | `python scraper.py "task"` |
| [nadi-shell](nadi-shell/) | Natural language to shell command | `python shell.py "query"` |
| [nadi-summarize](nadi-summarize/) | Summarize text or files | `python summarize.py --file doc.txt` |
| [nadi-translate](nadi-translate/) | Translate between languages | `python translate.py "text" spanish` |

Each Nadi has its own README explaining what it does, what you'll see when you run it, and how it uses Nadiru. The READMEs all follow the same shape so you can scan quickly across the collection.

## Building your own Nadi

The pattern is three HTTP endpoints. That's the whole API.

```python
import httpx

ENGINE = "http://localhost:8765"

# 1. Register your Nadi (once)
resp = httpx.post(f"{ENGINE}/connect", json={"name": "my-nadi"})
nadi_id = resp.json()["nadi_id"]

# 2. Generate (any number of times)
resp = httpx.post(f"{ENGINE}/generate", json={
    "nadi_id": nadi_id,
    "prompt": "Your prompt here",
    "priority": "balanced",   # cost, balanced, or quality
})
result = resp.json()
print(result["content"])
print(f"Routed to {result['provider']}/{result['model']}, ${result['cost_estimate']:.6f}")

# 3. Query history (optional, for cost reports or session memory)
resp = httpx.get(f"{ENGINE}/query", params={"nadi_id": nadi_id})
```

That's enough to build a Discord bot, a CLI tool, a web app, a batch processor, or a full SaaS product. The Nadis in this repo are all variations on this pattern.

If you want a clean reference implementation to copy from, [nadi-translate](nadi-translate/) is the smallest single-purpose Nadi in the collection. [nadi-chat](nadi-chat/) is the most readable conversational one.

## Setup

1. Get the [Nadiru engine](https://github.com/hlk-devs/nadiru-engine) running on `localhost:8765`
2. `cd` into any Nadi directory
3. Run the command from the table above

All Python Nadis require `httpx`:

```bash
pip install httpx
```

The web Nadis (`nadi-builder`, `nadi-dashboard`) need no install at all. Open the HTML file in a browser.

## Contributing your own Nadi

If you build a Nadi you think others would find useful, open a PR. Put it in a new top-level directory (`nadi-yourname`), include a README following the same template the existing ones use, and make sure it works against a fresh Nadiru install.

The bar for inclusion is "does this teach someone something useful about what Nadiru can do." Single-purpose tools are welcome. Polished demos are welcome. Half-finished experiments belong in your own fork until they're ready.

## License

MIT, see [LICENSE](LICENSE).
