"""List all models available to Nadiru across configured providers."""

from __future__ import annotations

import argparse
import sys

import httpx

ENGINE = "http://localhost:8765"


def fetch_providers() -> list[dict]:
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(f"{ENGINE}/providers")
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPError as e:
        print(
            f"Could not reach Nadiru engine at {ENGINE}: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
    return sorted(data.get("providers") or [], key=lambda p: p.get("name", ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="List models available to Nadiru")
    parser.add_argument(
        "--count",
        action="store_true",
        help="Show model counts per provider only",
    )
    parser.add_argument("--provider", help="Show models for a single provider")
    args = parser.parse_args()

    providers = fetch_providers()
    if args.provider:
        want = args.provider.strip().lower()
        providers = [p for p in providers if p.get("name", "").lower() == want]
        if not providers:
            print(f"Unknown provider: {args.provider}", file=sys.stderr)
            return 1

    total_models = sum(len(p.get("models") or []) for p in providers)

    if args.count:
        counts = [(p["name"], len(p.get("models") or [])) for p in providers]
        num_w = max((len(str(c)) for _, c in counts), default=1)
        name_w = max((len(n) for n, _ in counts), default=0)
        for name, cnt in counts:
            print(f"  {name.ljust(name_w)}: {str(cnt).rjust(num_w)} models")
        print()
        print(f"  Total: {total_models} models across {len(providers)} providers")
        return 0

    print()
    print("  nadi-models: Available Models")
    print()
    for p in providers:
        models = p.get("models") or []
        n = len(models)
        avail = p.get("available", False)
        tag = "available" if avail else "unavailable"
        print(f"  {p['name']} ({n} models, {tag})")
        for m in sorted(models):
            print(f"    {m}")
        print()

    print(f"  Total: {total_models} models across {len(providers)} providers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
