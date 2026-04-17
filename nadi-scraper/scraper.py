import argparse
import sys
from pathlib import Path

import httpx

ENGINE = "http://localhost:8765"


def build_prompt(task: str, output_mode: str) -> str:
    extra = ""
    if output_mode == "json":
        extra = "The script should output structured JSON records to stdout."
    elif output_mode == "script":
        extra = "Return only the Python script with no explanation."
    return (
        "Generate a complete, runnable Python script using requests and BeautifulSoup4. "
        "Include error handling, user-agent headers, and respectful rate limiting. "
        "The script should be ready to run with no modifications. "
        f"{extra}\n\nTask: {task}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate scraping scripts with Nadiru")
    parser.add_argument("task", help="Scraping task description")
    parser.add_argument("--output", choices=["json", "script"], default="json", help="Output mode")
    args = parser.parse_args()

    try:
        with httpx.Client(timeout=90.0) as client:
            connect = client.post(f"{ENGINE}/connect", json={"name": "nadi-scraper"})
            connect.raise_for_status()
            nadi_id = connect.json()["nadi_id"]

            response = client.post(
                f"{ENGINE}/generate",
                json={
                    "nadi_id": nadi_id,
                    "prompt": build_prompt(args.task, args.output),
                    "priority": "quality",
                },
            )
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPError:
        print("Could not reach Nadiru engine. Is it running on http://localhost:8765?")
        return 1

    script = result.get("content", "").strip()
    if not script:
        print("Engine returned empty script content")
        return 1

    if args.output == "script":
        out_path = Path("generated_scraper.py")
        out_path.write_text(script + "\n", encoding="utf-8")
        print(f"Saved script to {out_path.resolve()}")

    print("Generated script:\n")
    print(script)
    print("-" * 72)
    cost = result["cost_estimate"]
    cost_str = "free" if cost == 0 else f"${cost:.6f}"
    print(f"Routing: {result['provider']}/{result['model']} | cost {cost_str} | latency {result['latency_ms']}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
