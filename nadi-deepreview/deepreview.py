"""
nadi-deepreview: Three-stage independent code review pipeline.

Stage 1: Reviewer A (Provider 1) reviews code as a senior dev exec
Stage 2: Reviewer B (Provider 2) reviews same code independently
Stage 3: Integrator (Provider 3) reviews both reviews, decides what
         to implement, and produces the final corrected code

All three stages use DIFFERENT providers for independent perspectives.
Full documentation of every stage's findings, recommendations, and actions.

Usage:
    python deepreview.py path/to/file.py
    python deepreview.py path/to/project/        (reviews all .py files)
    python deepreview.py --paste                  (paste code directly)
    python deepreview.py path/to/file.py --save   (save report to file)
"""

import sys
import os
import json
import argparse
import httpx
from datetime import datetime

ENGINE = "http://localhost:8765"
CLIENT = httpx.Client(timeout=180.0)

# Providers to cycle through for independent reviews
PROVIDER_ROTATION = ["anthropic", "openai", "google", "deepseek", "groq"]


def connect():
    try:
        resp = CLIENT.post(f"{ENGINE}/connect", json={
            "name": "nadi-deepreview",
            "description": "Three-stage independent code review pipeline",
            "default_priority": "quality",
        })
        resp.raise_for_status()
        return resp.json()["nadi_id"]
    except httpx.ConnectError:
        print("Cannot connect to Nadiru engine on localhost:8765")
        sys.exit(1)


def generate(nadi_id, prompt, prefer_provider=None):
    payload = {
        "nadi_id": nadi_id,
        "prompt": prompt,
        "priority": "quality",
    }
    if prefer_provider:
        payload["prefer_provider"] = prefer_provider
    resp = CLIENT.post(f"{ENGINE}/generate", json=payload)
    resp.raise_for_status()
    return resp.json()


def pick_three_providers():
    """Pick three different providers for the three stages."""
    try:
        resp = CLIENT.get(f"{ENGINE}/providers")
        resp.raise_for_status()
        available = [p["name"] for p in resp.json()["providers"]
                     if p["available"] and p["name"] != "ollama"]
    except Exception:
        available = PROVIDER_ROTATION

    # Pick first three available from rotation order
    selected = []
    for p in PROVIDER_ROTATION:
        if p in available and p not in selected:
            selected.append(p)
        if len(selected) == 3:
            break

    # If we don't have 3, fill with whatever is available
    for p in available:
        if p not in selected:
            selected.append(p)
        if len(selected) == 3:
            break

    if len(selected) < 2:
        print("Need at least 2 paid providers for independent review.")
        print(f"Available: {available}")
        sys.exit(1)

    # If only 2 available, use the first one twice for integration
    while len(selected) < 3:
        selected.append(selected[0])

    return selected


def read_code(path):
    """Read code from a file or directory."""
    if os.path.isfile(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        return {os.path.basename(path): content}

    if os.path.isdir(path):
        files = {}
        for root, dirs, filenames in os.walk(path):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in (
                "__pycache__", "node_modules", ".git", ".venv",
                "venv", "env", ".env", "dist", "build"
            )]
            for f in filenames:
                if f.endswith((".py", ".js", ".ts", ".jsx", ".tsx",
                               ".html", ".css", ".json", ".yaml",
                               ".yml", ".toml", ".sql", ".sh",
                               ".go", ".rs", ".java", ".cpp", ".c",
                               ".h", ".rb", ".php")):
                    filepath = os.path.join(root, f)
                    relpath = os.path.relpath(filepath, path)
                    try:
                        with open(filepath, encoding="utf-8",
                                  errors="replace") as fh:
                            files[relpath] = fh.read()
                    except Exception:
                        pass
        return files

    print(f"Path not found: {path}")
    sys.exit(1)


def format_code_for_review(files):
    """Format multiple files into a single review document."""
    if len(files) == 1:
        name, content = next(iter(files.items()))
        return f"File: {name}\n{'='*60}\n{content}"

    parts = []
    total_lines = 0
    for name, content in files.items():
        lines = len(content.splitlines())
        total_lines += lines
        parts.append(f"{'='*60}\nFile: {name} ({lines} lines)\n{'='*60}\n{content}")

    header = f"Project with {len(files)} files, {total_lines} total lines\n\n"
    return header + "\n\n".join(parts)


def build_reviewer_prompt(code_text, reviewer_label):
    return f"""You are {reviewer_label}, a senior development executive 
conducting a thorough code review. You have 20+ years of experience 
across systems architecture, security, performance, and team leadership.

Review the following code. DO NOT make any changes to the code. 
Your job is to analyze and document only.

For each issue or observation, provide:
- Severity: CRITICAL / HIGH / MEDIUM / LOW / INFO
- Category: BUG / SECURITY / PERFORMANCE / ARCHITECTURE / STYLE / DOCUMENTATION
- Location: file and line number or function name
- Description: what the issue is
- Recommendation: what should be done

Also provide:
- Overall quality rating: 1-10
- Top 3 strengths of the code
- Top 3 areas needing improvement
- Architecture assessment (if applicable)

CODE TO REVIEW:

{code_text}

Provide your complete review. Be thorough and specific."""


def build_integrator_prompt(code_text, review_a_text, review_b_text,
                            provider_a, provider_b):
    return f"""You are the Integration Architect. You have received two 
independent code reviews from different senior reviewers. Your job is to:

1. Analyze both reviews for agreement, disagreement, and unique findings
2. Determine which recommendations should be implemented
3. Implement the approved changes to produce the final corrected code
4. Document every decision and action taken

IMPORTANT: You must produce the COMPLETE corrected code, not just 
snippets or diffs. If no changes are needed, return the original code.

ORIGINAL CODE:

{code_text}

REVIEW A (from {provider_a}):

{review_a_text}

REVIEW B (from {provider_b}):

{review_b_text}

Provide your response in this exact structure:

## REVIEW ANALYSIS

### Points of Agreement
(Issues both reviewers identified)

### Points of Disagreement
(Where reviewers differed and your ruling)

### Unique Findings
(Issues only one reviewer caught)

## IMPLEMENTATION DECISIONS

For each recommendation from both reviews, state:
- The recommendation
- ACCEPT or REJECT
- Rationale for your decision

## CHANGES MADE

List every change you implemented with:
- What was changed
- Why
- Before/after if applicable

## FINAL CODE

(The complete corrected code)

## SUMMARY

- Total issues found across both reviews
- Issues addressed
- Issues deferred (with rationale)
- Final quality assessment"""


def print_header(text, char="="):
    width = 70
    print(f"\n{char*width}")
    print(f"  {text}")
    print(f"{char*width}\n")


def print_stage(stage_num, title, provider, model, cost, latency):
    cost_str = "free" if cost == 0 else f"${cost:.6f}"
    print(f"  [{provider}/{model}] {cost_str}, {latency}ms")


def main():
    parser = argparse.ArgumentParser(
        description="Three-stage independent code review pipeline"
    )
    parser.add_argument("path", nargs="?", help="File or directory to review")
    parser.add_argument("--paste", action="store_true",
                        help="Paste code directly (reads until EOF)")
    parser.add_argument("--save", action="store_true",
                        help="Save full report to a file")
    args = parser.parse_args()

    # Read code
    if args.paste:
        print("Paste your code below. Press Ctrl+Z (Windows) or Ctrl+D (Unix) when done:\n")
        code_input = sys.stdin.read()
        files = {"pasted_code": code_input}
    elif args.path:
        files = read_code(args.path)
    else:
        parser.print_help()
        sys.exit(1)

    if not files:
        print("No code files found.")
        sys.exit(1)

    code_text = format_code_for_review(files)
    file_count = len(files)
    line_count = sum(len(c.splitlines()) for c in files.values())

    print_header("NADI DEEP REVIEW: Three-Stage Independent Code Review")
    print(f"  Files: {file_count}")
    print(f"  Lines: {line_count}")
    print(f"  Time:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Connect and pick providers
    nadi_id = connect()
    providers = pick_three_providers()

    print(f"\n  Pipeline:")
    print(f"    Stage 1 (Reviewer A): prefer {providers[0]}")
    print(f"    Stage 2 (Reviewer B): prefer {providers[1]}")
    print(f"    Stage 3 (Integrator): prefer {providers[2]}")

    total_cost = 0.0
    report_parts = []

    # Stage 1: Reviewer A
    print_header("STAGE 1: REVIEWER A", "-")
    print("  Sending code for independent review...")
    prompt_a = build_reviewer_prompt(code_text, "Reviewer A")
    result_a = generate(nadi_id, prompt_a, prefer_provider=providers[0])
    total_cost += result_a["cost_estimate"]
    print_stage(1, "Reviewer A", result_a["provider"], result_a["model"],
                result_a["cost_estimate"], result_a["latency_ms"])
    print(f"\n{result_a['content']}")
    report_parts.append(("STAGE 1: REVIEWER A", result_a))

    # Stage 2: Reviewer B
    print_header("STAGE 2: REVIEWER B", "-")
    print("  Sending code for independent review...")
    prompt_b = build_reviewer_prompt(code_text, "Reviewer B")
    result_b = generate(nadi_id, prompt_b, prefer_provider=providers[1])
    total_cost += result_b["cost_estimate"]
    print_stage(2, "Reviewer B", result_b["provider"], result_b["model"],
                result_b["cost_estimate"], result_b["latency_ms"])
    print(f"\n{result_b['content']}")
    report_parts.append(("STAGE 2: REVIEWER B", result_b))

    # Stage 3: Integration
    print_header("STAGE 3: INTEGRATION ARCHITECT", "-")
    print("  Analyzing both reviews and implementing changes...")
    prompt_int = build_integrator_prompt(
        code_text, result_a["content"], result_b["content"],
        f"{result_a['provider']}/{result_a['model']}",
        f"{result_b['provider']}/{result_b['model']}",
    )
    result_int = generate(nadi_id, prompt_int, prefer_provider=providers[2])
    total_cost += result_int["cost_estimate"]
    print_stage(3, "Integrator", result_int["provider"], result_int["model"],
                result_int["cost_estimate"], result_int["latency_ms"])
    print(f"\n{result_int['content']}")
    report_parts.append(("STAGE 3: INTEGRATION", result_int))

    # Summary
    print_header("PIPELINE COMPLETE")
    print(f"  Stage 1 (Reviewer A): {result_a['provider']}/{result_a['model']}")
    cost_a = result_a['cost_estimate']
    print(f"    Cost: {'free' if cost_a == 0 else f'${cost_a:.6f}'}")

    print(f"  Stage 2 (Reviewer B): {result_b['provider']}/{result_b['model']}")
    cost_b = result_b['cost_estimate']
    print(f"    Cost: {'free' if cost_b == 0 else f'${cost_b:.6f}'}")

    print(f"  Stage 3 (Integrator): {result_int['provider']}/{result_int['model']}")
    cost_c = result_int['cost_estimate']
    print(f"    Cost: {'free' if cost_c == 0 else f'${cost_c:.6f}'}")

    total_str = "free" if total_cost == 0 else f"${total_cost:.6f}"
    print(f"\n  Total pipeline cost: {total_str}")

    # Save report
    if args.save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.path:
            base = os.path.basename(args.path.rstrip("/\\"))
        else:
            base = "pasted"
        report_file = f"deepreview_{base}_{timestamp}.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"# Deep Review Report\n\n")
            f.write(f"- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **Files**: {file_count}\n")
            f.write(f"- **Lines**: {line_count}\n")
            f.write(f"- **Total Cost**: {total_str}\n\n")

            for title, result in report_parts:
                cost = result['cost_estimate']
                c = "free" if cost == 0 else f"${cost:.6f}"
                f.write(f"## {title}\n\n")
                f.write(f"**Provider**: {result['provider']}/{result['model']}\n")
                f.write(f"**Cost**: {c}\n")
                f.write(f"**Latency**: {result['latency_ms']}ms\n\n")
                f.write(result["content"])
                f.write("\n\n---\n\n")

        print(f"\n  Report saved to: {report_file}")


if __name__ == "__main__":
    main()
