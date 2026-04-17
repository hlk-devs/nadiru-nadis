# nadi-commit

Generate commit messages from staged git changes via Nadiru.

## Requirements

- Python 3.11+
- `httpx` (`pip install httpx`)
- Git repository with staged changes
- Running Nadiru engine at `http://localhost:8765`

## Usage

```bash
python commit.py
python commit.py --style conventional
```

## Behavior

1. Reads staged changes with `git diff --cached`.
2. Sends diff to Nadiru (`priority: "cost"`).
3. Shows suggested message.
4. Prompts `y/n/edit` to commit immediately or abort.

Routing details are shown at the bottom of each run.
