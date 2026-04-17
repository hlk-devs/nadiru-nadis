import argparse
import platform
import subprocess
import sys

import httpx

ENGINE = "http://localhost:8765"


def build_prompt(query: str, shell_name: str) -> str:
    return (
        f"Translate the request into one {shell_name} command. "
        "Return ONLY the shell command. No explanation, no markdown, no code fences. Just the raw command.\n\n"
        f"Request: {query}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate natural language to shell commands")
    parser.add_argument("query", help="Natural language request")
    args = parser.parse_args()

    shell_name = "PowerShell" if platform.system() == "Windows" else "bash"

    try:
        with httpx.Client(timeout=60.0) as client:
            connect = client.post(f"{ENGINE}/connect", json={"name": "nadi-shell"})
            connect.raise_for_status()
            nadi_id = connect.json()["nadi_id"]

            response = client.post(
                f"{ENGINE}/generate",
                json={
                    "nadi_id": nadi_id,
                    "prompt": build_prompt(args.query, shell_name),
                    "priority": "cost",
                },
            )
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPError:
        print("Could not reach Nadiru engine. Is it running on http://localhost:8765?")
        return 1

    command = result.get("content", "").strip().strip("`")
    if not command:
        print("Engine returned an empty command")
        return 1

    print(f"Suggested {shell_name} command:\n")
    print(command)
    print("-" * 72)
    cost = result["cost_estimate"]
    cost_str = "free" if cost == 0 else f"${cost:.6f}"
    print(f"Routing: {result['provider']}/{result['model']} | cost {cost_str} | latency {result['latency_ms']}ms")

    if input("Run this command? (y/n): ").strip().lower() != "y":
        print("Aborted")
        return 0

    proc = subprocess.run(command, shell=True, text=True, capture_output=True, check=False)
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip())
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
