import argparse
import subprocess
import sys

import httpx

ENGINE = "http://localhost:8765"


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def build_prompt(diff: str, conventional: bool) -> str:
    if conventional:
        style = "Use Conventional Commits format (feat:, fix:, docs:, chore:, refactor:, test:, perf:)."
    else:
        style = "Use a clear, concise commit message."
    return (
        "Generate one high-quality git commit message from this staged diff. "
        "Return plain text only with the final message and no explanation. "
        f"{style}\n\nStaged diff:\n{diff}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate git commit messages with Nadiru")
    parser.add_argument("--style", choices=["conventional"], help="Commit style preference")
    args = parser.parse_args()

    diff = run_git(["diff", "--cached"])
    if diff.returncode != 0:
        print(diff.stderr.strip() or "Failed to read staged changes")
        return 1
    if not diff.stdout.strip():
        print("No staged changes")
        return 0

    try:
        with httpx.Client(timeout=60.0) as client:
            connect = client.post(f"{ENGINE}/connect", json={"name": "nadi-commit"})
            connect.raise_for_status()
            nadi_id = connect.json()["nadi_id"]

            response = client.post(
                f"{ENGINE}/generate",
                json={
                    "nadi_id": nadi_id,
                    "prompt": build_prompt(diff.stdout, args.style == "conventional"),
                    "priority": "cost",
                },
            )
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPError:
        print("Could not reach Nadiru engine. Is it running on http://localhost:8765?")
        return 1

    message = result.get("content", "").strip()
    if not message:
        print("Engine returned an empty commit message")
        return 1

    print("Suggested commit message:\n")
    print(message)
    print("-" * 72)
    cost = result["cost_estimate"]
    cost_str = "free" if cost == 0 else f"${cost:.6f}"
    print(f"Routing: {result['provider']}/{result['model']} | cost {cost_str} | latency {result['latency_ms']}ms")

    choice = input("Use this message? (y/n/edit): ").strip().lower()
    if choice == "n":
        print("Aborted")
        return 0
    if choice == "edit":
        edited = input("Enter commit message: ").strip()
        if edited:
            message = edited
        else:
            print("Empty message. Aborted")
            return 1
    elif choice != "y":
        print("Invalid choice. Aborted")
        return 1

    commit = run_git(["commit", "-m", message])
    if commit.stdout.strip():
        print(commit.stdout.strip())
    if commit.returncode != 0 and commit.stderr.strip():
        print(commit.stderr.strip())
    return commit.returncode


if __name__ == "__main__":
    sys.exit(main())

