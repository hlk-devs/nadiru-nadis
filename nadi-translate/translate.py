"""
nadi-translate — Translate text between languages via Nadiru.

A simple single-purpose Nadi demonstrating the pattern.

Usage:
    python translate.py "Hello, how are you?" spanish
    python translate.py "Bonjour le monde" english
    python translate.py --file input.txt japanese
"""

import sys
import httpx

ENGINE = "http://localhost:8765"


def connect():
    resp = httpx.post(f"{ENGINE}/connect", json={
        "name": "nadi-translate",
        "description": "Language translation",
        "default_priority": "balanced",
    }, timeout=10.0)
    resp.raise_for_status()
    return resp.json()["nadi_id"]


def translate(nadi_id, text, target_language):
    prompt = (
        f"Translate the following text to {target_language}. "
        f"Return ONLY the translation, no explanation, no original text.\n\n"
        f"{text}"
    )
    resp = httpx.post(f"{ENGINE}/generate", json={
        "nadi_id": nadi_id,
        "prompt": prompt,
        "priority": "balanced",
    }, timeout=60.0)
    resp.raise_for_status()
    return resp.json()


def main():
    if len(sys.argv) < 3:
        print("Usage: python translate.py <text or --file path> <target_language>")
        print('Example: python translate.py "Hello world" spanish')
        sys.exit(1)

    target = sys.argv[-1]

    if sys.argv[1] == "--file":
        filepath = sys.argv[2]
        with open(filepath, encoding="utf-8") as f:
            text = f.read()
    else:
        text = " ".join(sys.argv[1:-1])

    try:
        nadi_id = connect()
    except httpx.ConnectError:
        print("Cannot connect to Nadiru engine on localhost:8765")
        sys.exit(1)

    result = translate(nadi_id, text, target)

    print(result["content"])
    print(
        f"\n[{result['provider']}/{result['model']}] "
        f"{'free' if result['cost_estimate'] == 0 else f'${result[\"cost_estimate\"]:.6f}'} · "
        f"{result['latency_ms']}ms"
    )


if __name__ == "__main__":
    main()
