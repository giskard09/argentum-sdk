"""
Argentum trust plugin — standalone demo (no Gemini API key needed).

Shows exactly what happens before each ADK tool call:
  1. Karma check for the service being called
  2. Action submitted to Argentum for community attestation

Install:
    pip install git+https://github.com/giskard09/argentum-sdk requests

Run:
    python adk_trust_demo.py
"""

import argentum
from argentum.adk_plugin import make_trust_callback


# ── Minimal ADK stubs so the demo runs without google-adk installed ───────────

class FakeTool:
    def __init__(self, name): self.name = name

class FakeContext:
    state = {}


# ── Demo ──────────────────────────────────────────────────────────────────────

AGENT_ID   = "demo-agent-001"
AGENT_NAME = "Demo Agent"

print(f"\n=== Argentum ADK Trust Plugin — Demo ===\n")
print(f"Agent: {AGENT_NAME}")
print(f"Karma before: {argentum.get_karma(AGENT_ID)}\n")

# Build the trust callback — same one you'd pass to FunctionTool(before_tool_callback=...)
trust = make_trust_callback(
    agent_id    = AGENT_ID,
    agent_name  = AGENT_NAME,
    entity_type = "agent",
    auto_submit = True,
    min_karma   = 0,
)

# Simulate two tool calls
tools = [
    FakeTool("fetch_eth_price"),
    FakeTool("search_github"),
]

for tool in tools:
    print(f"→ Tool call: {tool.name}")
    result = trust(tool, {"query": "test"}, FakeContext())
    if result and result.get("argentum_blocked"):
        print(f"  BLOCKED — karma too low: {result['service_karma']}")
    else:
        print(f"  Allowed — action submitted to Argentum")

print(f"\nKarma after: {argentum.get_karma(AGENT_ID)}")
print(f"Pending attestations:")
for a in argentum.get_pending(limit=5):
    if a["entity_id"] == AGENT_ID:
        print(f"  [{a['id']}] {a['description'][:70]}")

print(f"\nDashboard: https://giskard09.github.io/argentum-web/\n")
