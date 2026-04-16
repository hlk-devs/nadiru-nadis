"""
nadi-chat — CLI interface for the Nadiru engine.

Talk to your AI through Nadiru. See routing decisions in real time.

Usage:
    python chat.py

Commands:
    /cost       Switch to cost priority (cheapest model)
    /speed      Switch to speed priority (fastest model)
    /quality    Switch to quality priority (best model)
    /balanced   Switch to balanced priority (default)
    /status     Show current session stats
    /history    Show recent interactions
    /quit       Exit

Requires: Nadiru engine running on localhost:8765
"""

import sys
import time
import httpx

ENGINE = "http://localhost:8765"
CLIENT = httpx.Client(timeout=120.0)


def connect():
    """Register with the engine."""
    try:
        resp = CLIENT.post(f"{ENGINE}/connect", json={
            "name": "nadi-chat",
            "description": "CLI chat interface",
            "default_priority": "balanced",
        })
        resp.raise_for_status()
        return resp.json()
    except httpx.ConnectError:
        print("Cannot connect to Nadiru engine.")
        print("Start it with: cd C:\\_PROJECTS\\nadiru-engine && python -m nadiru_engine")
        sys.exit(1)


def generate(nadi_id: str, prompt: str, priority: str, messages: list) -> dict:
    """Send a prompt to the engine."""
    payload = {
        "nadi_id": nadi_id,
        "prompt": prompt,
        "priority": priority,
    }
    if messages:
        payload["messages"] = messages

    start = time.time()
    resp = CLIENT.post(f"{ENGINE}/generate", json=payload)
    wall_time = time.time() - start
    resp.raise_for_status()

    result = resp.json()
    result["wall_time"] = wall_time
    return result


def get_status(nadi_id: str) -> dict:
    """Get session stats."""
    resp = CLIENT.get(f"{ENGINE}/query", params={
        "nadi_id": nadi_id,
        "limit": 1000,
    })
    resp.raise_for_status()
    data = resp.json()

    total_cost = sum(i["cost_estimate"] for i in data["interactions"])
    local_count = sum(1 for i in data["interactions"] if i["provider"] == "ollama")
    delegated_count = data["total"] - local_count

    providers_used = {}
    for i in data["interactions"]:
        key = f"{i['provider']}/{i['model']}"
        if key not in providers_used:
            providers_used[key] = 0
        providers_used[key] += 1

    return {
        "total": data["total"],
        "local": local_count,
        "delegated": delegated_count,
        "total_cost": total_cost,
        "providers_used": providers_used,
    }


def get_history(nadi_id: str, limit: int = 10) -> list:
    """Get recent interactions."""
    resp = CLIENT.get(f"{ENGINE}/query", params={
        "nadi_id": nadi_id,
        "limit": limit,
    })
    resp.raise_for_status()
    return resp.json()["interactions"]


def format_routing_bar(result: dict) -> str:
    """Format the one-line status bar under each response."""
    provider = result["provider"]
    model = result["model"]
    cost = result["cost_estimate"]
    latency = result["latency_ms"]
    wall = result.get("wall_time", 0)
    reason = result["routing_reason"]

    if provider == "ollama":
        cost_str = "free"
    else:
        cost_str = f"${cost:.6f}"

    return (
        f"\033[90m"  # dim gray
        f"[{provider}/{model}] "
        f"{cost_str} · {latency}ms · "
        f"{reason}"
        f"\033[0m"  # reset
    )


def main():
    print("nadi-chat")
    print("Connecting to Nadiru engine...")
    print()

    nadi = connect()
    nadi_id = nadi["nadi_id"]
    priority = "balanced"
    messages = []

    print(f"Connected. Priority: {priority}")
    print("Type a message, or /help for commands.")
    print()

    while True:
        try:
            user_input = input("\033[1myou:\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            cmd = user_input.lower()

            if cmd == "/quit" or cmd == "/exit" or cmd == "/q":
                print("Bye.")
                break

            elif cmd == "/help":
                print()
                print("  /cost      Cheapest routing")
                print("  /speed     Fastest routing")
                print("  /quality   Best model routing")
                print("  /balanced  Default routing")
                print("  /status    Session stats")
                print("  /history   Recent interactions")
                print("  /clear     Clear conversation history")
                print("  /quit      Exit")
                print()
                continue

            elif cmd in ("/cost", "/speed", "/quality", "/balanced"):
                priority = cmd[1:]
                print(f"  Priority set to: {priority}")
                print()
                continue

            elif cmd == "/status":
                stats = get_status(nadi_id)
                print()
                print(f"  Interactions: {stats['total']}")
                print(f"  Local: {stats['local']} · Delegated: {stats['delegated']}")
                print(f"  Total cost: ${stats['total_cost']:.6f}")
                if stats["providers_used"]:
                    print(f"  Models used:")
                    for model, count in stats["providers_used"].items():
                        print(f"    {model}: {count}")
                print()
                continue

            elif cmd == "/history":
                history = get_history(nadi_id)
                print()
                if not history:
                    print("  No interactions yet.")
                else:
                    for ix in reversed(history):
                        prompt_preview = ix["prompt"][:60]
                        cost = ix["cost_estimate"]
                        provider = ix["provider"]
                        model = ix["model"]
                        print(f"  [{provider}/{model}] ${cost:.6f} — {prompt_preview}...")
                print()
                continue

            elif cmd == "/clear":
                messages = []
                print("  Conversation history cleared.")
                print()
                continue

            else:
                print(f"  Unknown command: {cmd}")
                print("  Type /help for commands.")
                print()
                continue

        # Send message
        result = generate(nadi_id, user_input, priority, messages)

        # Update conversation history
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": result["content"]})

        # Keep history manageable (last 20 turns)
        if len(messages) > 40:
            messages = messages[-40:]

        # Display response
        print()
        print(result["content"])
        print()
        print(format_routing_bar(result))
        print()


if __name__ == "__main__":
    main()
