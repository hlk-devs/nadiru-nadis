# nadi-health

Test all configured providers and report their status.

## Usage

```bash
python health.py
```

## What it shows

- Engine status and Conductor model
- Each provider tested with a tiny prompt
- Response time per provider
- Which model handled the test
- Whether requests routed to the intended provider or got rerouted

## Requirements

- Nadiru engine running on `localhost:8765`
- `pip install httpx`
