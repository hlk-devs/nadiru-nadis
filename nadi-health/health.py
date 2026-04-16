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

    providers = health.get("providers", [])
    if not providers:
        print("\n  No paid providers configured.")
        return

    print(f"\n  Testing {len(providers)} providers...\n")

    results = []
    for provider in providers:
        start = time.time()
        try:
            resp = httpx.post(
                f"{ENGINE}/test-provider",
                params={"provider_name": provider},
                timeout=60.0,
            )
            elapsed = time.time() - start
            if resp.status_code != 200:
                try:
                    detail = resp.json().get("detail", resp.text)
                except Exception:
                    detail = resp.text
                results.append({
                    "provider": provider,
                    "status": f"HTTP {resp.status_code}",
                    "latency": elapsed,
                    "model": "?",
                    "cost": 0,
                })
                print(f"  {provider:20s}  HTTP {resp.status_code}: {str(detail)[:40]}")
                continue

            data = resp.json()
            model = data.get("model", "?")
            cost = data.get("cost_estimate", 0)
            api_status = data.get("status", "error")
            err = data.get("error")
            lat_ms = data.get("latency_ms")

            if api_status == "ok" and not err:
                status = "OK"
            else:
                status = f"ERROR: {err or 'unknown'}"

            lat_disp = (lat_ms / 1000.0) if lat_ms is not None else elapsed
            results.append({
                "provider": provider,
                "status": status,
                "latency": lat_disp,
                "model": model,
                "cost": cost,
            })
            print(f"  {provider:20s}  {status:20s}  {lat_disp:.1f}s  {model}")

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
