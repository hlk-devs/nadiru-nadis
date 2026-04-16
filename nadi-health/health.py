"""
nadi-health — Test all configured providers.

Sends a tiny prompt to each provider and reports status and latency.

Usage:
    python health.py
"""

import sys
import time
import httpx

ENGINE = "http://localhost:8765"
TEST_PROMPT = "Reply with the single word OK."


def main():
    print("\nnadi-health: Provider Status\n")

    # Check engine
    try:
        resp = httpx.get(f"{ENGINE}/health", timeout=5.0)
        health = resp.json()
        print(f"  Engine:     OK")
        print(f"  Conductor:  {health.get('conductor_model', '?')}")
        print(f"  Providers:  {', '.join(health.get('providers', []))}")
        print(f"  Database:   {health.get('interactions', 0)} interactions logged")
    except httpx.ConnectError:
        print("  Engine:     OFFLINE")
        print("  Start with: python -m nadiru_engine")
        sys.exit(1)

    # Connect a test nadi
    resp = httpx.post(f"{ENGINE}/connect", json={
        "name": "nadi-health",
        "description": "Provider health check",
        "default_priority": "cost",
    }, timeout=10.0)
    nadi_id = resp.json()["nadi_id"]

    providers = health.get("providers", [])
    if not providers:
        print("\n  No paid providers configured.")
        return

    print(f"\n  Testing {len(providers)} providers...\n")

    results = []
    for provider in providers:
        start = time.time()
        try:
            resp = httpx.post(f"{ENGINE}/generate", json={
                "nadi_id": nadi_id,
                "prompt": TEST_PROMPT,
                "prefer_provider": provider,
                "priority": "cost",
            }, timeout=60.0)
            elapsed = time.time() - start
            data = resp.json()

            actual_provider = data.get("provider", "?")
            model = data.get("model", "?")
            cost = data.get("cost_estimate", 0)
            content = data.get("content", "")[:50]
            routed_correctly = actual_provider == provider

            if routed_correctly:
                status = "OK"
            else:
                status = f"REROUTED → {actual_provider}"

            results.append({
                "provider": provider,
                "status": status,
                "latency": elapsed,
                "model": model,
                "cost": cost,
            })
            print(f"  {provider:20s}  {status:20s}  {elapsed:.1f}s  {model}")

        except Exception as e:
            elapsed = time.time() - start
            results.append({
                "provider": provider,
                "status": "ERROR",
                "latency": elapsed,
                "model": "?",
                "cost": 0,
            })
            print(f"  {provider:20s}  ERROR ({str(e)[:40]})")

    # Summary
    ok = sum(1 for r in results if r["status"] == "OK")
    print(f"\n  {ok}/{len(results)} providers responding directly")
    total_cost = sum(r["cost"] for r in results)
    print(f"  Health check cost: ${total_cost:.6f}")
    print()


if __name__ == "__main__":
    main()
