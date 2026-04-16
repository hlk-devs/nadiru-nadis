# nadi-costs

Terminal cost reporting for the Nadiru engine.

## Usage

```bash
python costs.py              # Today's costs
python costs.py --all        # All time
python costs.py --days 7     # Last 7 days
```

## What it shows

- Total interactions, cost, free vs paid breakdown
- Spending by provider and by model
- Most expensive single request

## Requirements

- Nadiru engine running on `localhost:8765`
- `pip install httpx`
