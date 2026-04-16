# nadi-chat

CLI chat interface for the Nadiru engine.

## Usage

```
python chat.py
```

## Commands

| Command | What it does |
|---------|-------------|
| `/cost` | Route to cheapest models |
| `/speed` | Route to fastest models |
| `/quality` | Route to best models |
| `/balanced` | Default routing |
| `/status` | Show session stats (cost, model usage) |
| `/history` | Show recent interactions |
| `/clear` | Clear conversation history |
| `/quit` | Exit |

## Requirements

- Nadiru engine running on `localhost:8765`
- `pip install httpx`
