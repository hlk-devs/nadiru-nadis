# nadi-deepreview

Three-stage independent code review pipeline. Two AI reviewers from different providers analyze your code independently, then a third AI from yet another provider integrates both reviews and implements the approved changes.

## How it works

1. **Reviewer A** (Provider 1): Reviews your code as a senior dev executive. Documents every issue with severity, category, and recommendations. Makes no changes.
2. **Reviewer B** (Provider 2): Reviews the same code independently. Different provider, different training, different blind spots. Makes no changes.
3. **Integration Architect** (Provider 3): Reads both reviews, identifies agreements and disagreements, decides which recommendations to implement, and produces the final corrected code with full documentation of every decision.

All three stages use different AI providers for genuinely independent perspectives.

## Usage

```bash
# Review a single file
python deepreview.py path/to/file.py

# Review an entire project directory
python deepreview.py path/to/project/

# Paste code directly
python deepreview.py --paste

# Save the full report to a markdown file
python deepreview.py path/to/file.py --save
```

## What you get

Full documentation of all three stages:

- **Stage 1 and 2**: Severity ratings (CRITICAL/HIGH/MEDIUM/LOW/INFO), categorized issues (BUG/SECURITY/PERFORMANCE/ARCHITECTURE/STYLE), specific line references, recommendations, overall quality rating, strengths, and areas for improvement
- **Stage 3**: Points of agreement between reviewers, points of disagreement with rulings, unique findings, accept/reject decisions for every recommendation with rationale, list of every change made, and the complete corrected code
- **Cost summary**: Individual cost per stage and total pipeline cost

## Requirements

- Nadiru engine running on `localhost:8765`
- At least 2 paid providers configured (3 recommended for full independence)
- `pip install httpx`

## Supported file types

Python, JavaScript, TypeScript, JSX, TSX, HTML, CSS, JSON, YAML, TOML, SQL, Shell, Go, Rust, Java, C/C++, Ruby, PHP. When given a directory, it walks the tree and skips common non-code directories (__pycache__, node_modules, .git, etc).
