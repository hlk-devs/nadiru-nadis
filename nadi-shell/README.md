# nadi-shell

Translate natural language requests into shell commands using Nadiru.

## Requirements

- Python 3.11+
- `httpx` (`pip install httpx`)
- Running Nadiru engine at `http://localhost:8765`

## Usage

```bash
python shell.py "find all python files larger than 1MB"
python shell.py "compress this directory into a tar.gz"
python shell.py "show disk usage sorted by size"
```

## Notes

- Detects host shell target (`PowerShell` on Windows, `bash` otherwise).
- Prompts before execution.
- Uses `priority: "cost"`.
- Prints routing details (provider/model, cost, latency).
