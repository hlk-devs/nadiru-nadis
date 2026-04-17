# nadi-codereview

Code review tool that reads a local file and asks Nadiru for a structured review.

## Requirements

- Python 3.11+
- `httpx` (`pip install httpx`)
- Running Nadiru engine at `http://localhost:8765`

## Usage

```bash
python review.py path/to/file.py
python review.py path/to/file.py --focus security
python review.py path/to/file.py --focus performance
```

## Notes

- Uses Nadiru `/connect` and `/generate`.
- Requests `priority: "quality"` for stronger review quality.
- Prints routing details (provider/model, cost, latency) at the end.
