"""
nadi-summarize — Summarize text or describe a topic via Nadiru.

Usage:
    python summarize.py "Paste your long text here"
    python summarize.py --file article.txt
    python summarize.py --file article.txt --length short
    python summarize.py --file article.txt --length detailed
"""

import sys
import httpx

ENGINE = "http://localhost:8765"


def connect():
    resp = httpx.post(f"{ENGINE}/connect", json={
        "name": "nadi-summarize",
        "description": "Text summarization",
        "default_priority": "balanced",
    }, timeout=10.0)
    resp.raise_for_status()
    return resp.json()["nadi_id"]


def summarize(nadi_id, text, length="concise"):
    length_instruction = {
        "short": "Summarize in 1-2 sentences.",
        "concise": "Summarize in a short paragraph (3-5 sentences).",
        "detailed": "Provide a detailed summary covering all key points.",
    }.get(length, "Summarize in a short paragraph.")

    prompt = (
        f"{length_instruction}\n\n"
        f"Text to summarize:\n\n"
        f"{text}"
    )
    resp = httpx.post(f"{ENGINE}/generate", json={
        "nadi_id": nadi_id,
        "prompt": prompt,
        "priority": "cost",
    }, timeout=120.0)
    resp.raise_for_status()
    return resp.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: python summarize.py <text or --file path> [--length short|concise|detailed]")
        sys.exit(1)

    # Parse arguments
    length = "concise"
    if "--length" in sys.argv:
        idx = sys.argv.index("--length")
        length = sys.argv[idx + 1]
        sys.argv = sys.argv[:idx] + sys.argv[idx + 2:]

    if sys.argv[1] == "--file":
        filepath = sys.argv[2]
        with open(filepath, encoding="utf-8") as f:
            text = f.read()
        print(f"Summarizing {filepath} ({len(text)} chars)...\n")
    else:
        text = " ".join(sys.argv[1:])

    try:
        nadi_id = connect()
    except httpx.ConnectError:
        print("Cannot connect to Nadiru engine on localhost:8765")
        sys.exit(1)

    result = summarize(nadi_id, text, length)

    print(result["content"])
    cost = result["cost_estimate"]
    cost_str = "free" if cost == 0 else f"${cost:.6f}"
    print(
        f"\n[{result['provider']}/{result['model']}] "
        f"{cost_str} · {result['latency_ms']}ms"
    )


if __name__ == "__main__":
    main()
