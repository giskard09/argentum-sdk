"""
Argentum + Google ADK — Trust layer example.

Google ADK 1.0.0 launched March 30, 2026.
This is the first trust plugin for it.

What this does:
  - Before each tool call: checks service karma on Arbitrum
  - After each tool call: submits verified action to build agent reputation
  - Flywheel: every tool call through ADK builds karma automatically

Install:
    pip install google-adk requests

Run:
    python google_adk_example.py
"""

import asyncio
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from argentum.adk_plugin import make_trust_callback
import argentum


# ── 1. Define your agent's identity in Argentum ───────────────────────────────

AGENT_ID   = "adk-research-agent-001"
AGENT_NAME = "ADK Research Agent"

# This callback runs before EVERY tool call this agent makes.
# It checks service karma and auto-submits actions to build reputation.
trust_callback = make_trust_callback(
    agent_id    = AGENT_ID,
    agent_name  = AGENT_NAME,
    entity_type = "agent",
    auto_submit = True,   # builds karma automatically
    min_karma   = 0,      # blocks services with karma < 0 (explicitly blacklisted)
)


# ── 2. Define tools (your normal ADK tools) ───────────────────────────────────

def fetch_eth_price() -> dict:
    """Fetch current ETH price from public API."""
    import requests
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
        timeout=5
    )
    return r.json()


def search_github(query: str) -> dict:
    """Search GitHub repositories."""
    import requests
    r = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": query, "sort": "stars", "per_page": 3},
        timeout=5
    )
    results = r.json().get("items", [])
    return {"results": [{"name": i["full_name"], "stars": i["stargazers_count"]} for i in results]}


# ── 3. Wrap tools with Argentum trust callback ────────────────────────────────

eth_tool    = FunctionTool(fetch_eth_price, before_tool_callback=trust_callback)
github_tool = FunctionTool(search_github,   before_tool_callback=trust_callback)


# ── 4. Create your ADK agent (no changes from normal ADK usage) ───────────────

agent = Agent(
    model       = "gemini-2.5-flash",
    name        = AGENT_NAME,
    description = "Research agent with on-chain reputation via Argentum",
    instruction = "You are a research agent. Help with crypto and code research.",
    tools       = [eth_tool, github_tool],
)


# ── 5. Run and watch karma build ──────────────────────────────────────────────

async def main():
    runner = Runner(
        agent           = agent,
        session_service = InMemorySessionService(),
    )

    print(f"\n[Argentum] Agent: {AGENT_NAME}")
    print(f"[Argentum] Starting karma: {argentum.get_karma(AGENT_ID)}\n")

    # Run the agent — each tool call automatically submits to Argentum
    response = await runner.run("What's the current ETH price?")
    print(f"\nAgent response: {response}\n")

    print(f"[Argentum] Karma after run: {argentum.get_karma(AGENT_ID)}")
    print(f"[Argentum] Actions pending attestation:")
    for action in argentum.get_pending(limit=3):
        if action["entity_id"] == AGENT_ID:
            print(f"  [{action['id']}] {action['description'][:60]}")
    print(f"\n[Argentum] Full trace: https://giskard09.github.io/argentum-web/")


if __name__ == "__main__":
    asyncio.run(main())
