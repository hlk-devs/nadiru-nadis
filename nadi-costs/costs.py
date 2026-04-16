"""
nadi-costs — Session and historical cost reporting.

Shows spending by provider, model, and time period.

Usage:
    python costs.py              # Today's costs
    python costs.py --all        # All time
    python costs.py --days 7     # Last 7 days
"""

import sys
import httpx
from datetime import datetime, timedelta, timezone

ENGINE = "http://localhost:8765"


def query(params):
    resp = httpx.get(f"{ENGINE}/query", params=params, timeout=10.0)
    resp.raise_for_status()
    return resp.json()


def fmt_cost(c):
    if c == 0:
        return "free"
    if c < 0.01:
        return f"${c:.6f}"
    return f"${c:.4f}"


def report(interactions):
    if not interactions:
        print("  No interactions found.")
        return

    total_cost = sum(i["cost_estimate"] for i in interactions)
    local = [i for i in interactions if i["provider"] == "ollama"]
    delegated = [i for i in interactions if i["provider"] != "ollama"]
    free = [i for i in interactions if i["cost_estimate"] == 0]

    print(f"  Interactions: {len(interactions)}")
    print(f"  Total cost:   {fmt_cost(total_cost)}")
    print(f"  Free:         {len(free)}")
    print(f"  Local:        {len(local)}")
    print(f"  Delegated:    {len(delegated)}")

    # By provider
    providers = {}
    for i in interactions:
        p = i["provider"]
        if p not in providers:
            providers[p] = {"count": 0, "cost": 0.0}
        providers[p]["count"] += 1
        providers[p]["cost"] += i["cost_estimate"]

    print(f"\n  By Provider:")
    for p, data in sorted(providers.items(), key=lambda x: -x[1]["cost"]):
        print(f"    {p:20s}  {data['count']:4d} requests  {fmt_cost(data['cost'])}")

    # By model
    models = {}
    for i in interactions:
        m = f"{i['provider']}/{i['model']}"
        if m not in models:
            models[m] = {"count": 0, "cost": 0.0}
        models[m]["count"] += 1
        models[m]["cost"] += i["cost_estimate"]

    print(f"\n  By Model:")
    for m, data in sorted(models.items(), key=lambda x: -x[1]["cost"]):
        print(f"    {m:40s}  {data['count']:3d}×  {fmt_cost(data['cost'])}")

    # Most expensive single request
    most_expensive = max(interactions, key=lambda i: i["cost_estimate"])
    print(f"\n  Most expensive request:")
    print(f"    {most_expensive['provider']}/{most_expensive['model']}")
    print(f"    Cost: {fmt_cost(most_expensive['cost_estimate'])}")
    print(f"    Prompt: {most_expensive['prompt'][:80]}...")


def main():
    try:
        httpx.get(f"{ENGINE}/health", timeout=5.0)
    except httpx.ConnectError:
        print("Cannot connect to Nadiru engine on localhost:8765")
        sys.exit(1)

    params = {"limit": 1000}

    if "--all" in sys.argv:
        print("\nnadi-costs: All Time\n")
    elif "--days" in sys.argv:
        idx = sys.argv.index("--days")
        days = int(sys.argv[idx + 1])
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        params["since"] = since
        print(f"\nnadi-costs: Last {days} Days\n")
    else:
        since = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).isoformat()
        params["since"] = since
        print("\nnadi-costs: Today\n")

    data = query(params)
    report(data["interactions"])
    print()


if __name__ == "__main__":
    main()
