import argparse
import sys
from pathlib import Path

import httpx

ENGINE = "http://localhost:8765"


def build_prompt(source: str, focus: str | None) -> str:
    focus_line = ""
    if focus:
        focus_line = f"\nEmphasize this focus area: {focus}."
    return (
        "You are performing a practical code review. Analyze the file and provide plain text sections: "
        "Bugs/Logic, Security, Performance, Style/Readability, and a final Summary Rating (1-5). "
        "Keep findings actionable and concise."
        f"{focus_line}\n\n"
        "File content:\n"
        f"{source}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a source file using Nadiru")
    parser.add_argument("file_path", help="Path to the file to review")
    parser.add_argument("--focus", choices=["security", "performance"], help="Emphasize one review area")
    args = parser.parse_args()

    path = Path(args.file_path)
    if not path.is_file():
        print(f"File not found: {path}")
        return 1

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Could not read file: {exc}")
        return 1

    if not content.strip():
        print("File is empty. Nothing to review.")
        return 1

    try:
        with httpx.Client(timeout=60.0) as client:
            connect = client.post(f"{ENGINE}/connect", json={"name": "nadi-codereview"})
            connect.raise_for_status()
            nadi_id = connect.json()["nadi_id"]

            response = client.post(
                f"{ENGINE}/generate",
                json={
                    "nadi_id": nadi_id,
                    "prompt": build_prompt(content, args.focus),
                    "priority": "quality",
                },
            )
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPError:
        print("Could not reach Nadiru engine. Is it running on http://localhost:8765?")
        return 1

    print("=" * 72)
    print(f"Code Review: {path}")
    print("=" * 72)
    print(result.get("content", "(No review content returned)").strip())
    print("-" * 72)
    cost = result["cost_estimate"]
    cost_str = "free" if cost == 0 else f"${cost:.6f}"
    print(f"Routing: {result['provider']}/{result['model']} | cost {cost_str} | latency {result['latency_ms']}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
