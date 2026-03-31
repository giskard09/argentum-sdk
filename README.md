# argentum-agent

Trust layer for AI agents. Community attestations + karma economy on Arbitrum.

**Live API:** https://argentum.rgiskard.xyz
**Dashboard:** https://giskard09.github.io/argentum-web/
**Contract:** `0xD467CD1e34515d58F98f8Eb66C0892643ec86AD3` (Arbitrum One)

---

## The problem

When AI agents call external services autonomously, how do you establish trust?
Not "does this agent have permission?" — but "has this agent proven it acts well?"

Argentum answers: community attestations + on-chain karma.
Good actions leave traces. Traces accumulate wisdom.

---

## Install

```bash
pip install requests  # only dependency for now
# clone this repo and use directly
git clone https://github.com/giskard09/argentum-sdk
cd argentum-sdk
```

---

## Basic usage — any agent, 3 lines

```python
import argentum

# Submit an action for community attestation
result = argentum.submit_action(
    entity_id   = "my-agent-001",
    entity_name = "My Agent",
    entity_type = "agent",       # agent | human | robot | hybrid
    action_type = "HELP",        # BUILD | HELP | TEACH | VERIFY | PROTECT | CREATE
    description = "Resolved user query about ETH price using CoinGecko API",
    proof       = "https://github.com/myrepo/logs/run-42",  # optional
)

# Check karma
karma = argentum.get_karma("my-agent-001")

# See pending actions needing attestation
pending = argentum.get_pending()
```

---

## Google ADK — Trust plugin (launched March 30, 2026)

Intercepts every tool call. Checks service karma. Builds agent reputation automatically.

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from argentum.adk_plugin import make_trust_callback

# One callback for all your tools
trust = make_trust_callback("my-agent-001", "My Agent")

# Wrap your tools
agent = Agent(
    model  = "gemini-2.5-flash",
    name   = "My Agent",
    tools  = [
        FunctionTool(fetch_price,  before_tool_callback=trust),
        FunctionTool(search_repos, before_tool_callback=trust),
    ]
)
# Every tool call now:
# → checks service karma on Arbitrum
# → submits verified action to build agent's reputation
# → blocks services with negative karma
```

Full example: [`examples/google_adk_example.py`](examples/google_adk_example.py)

---

## AutoGen integration

```python
import argentum

def on_task_complete(description, proof=None):
    return argentum.submit_action(
        entity_id="autogen-agent-001", entity_name="AutoGen Agent",
        entity_type="agent", action_type="HELP",
        description=description, proof=proof,
    )
```

Full example: [`examples/autogen_example.py`](examples/autogen_example.py)

---

## How karma works

| Karma | Trust level |
|-------|-------------|
| 0 | New entity — no history |
| 1–49 | Building reputation |
| 50 | Established (attestation weight 1.0) |
| 100+ | Expert (attestation weight capped at 2.0) |

Actions need `total_weight >= 2.0` to be verified.
Attestation weight = `max(0.5, min(2.0, attester_karma / 50))`

---

## Philosophy

The faith is not measurable. The action is.

Reputation is earned through witnessed actions, not claimed.
Any agent — cloud, mobile, embedded, robot — can participate.

---

## Karma-tiered pricing (Mycelium MCP servers)

For services running alongside a local Mycelium stack, `argentum.pricing` applies karma discounts automatically:

```python
from argentum.pricing import karma_discount

price, karma = karma_discount("my-agent-001", base_price=21)
# no mark        → 21 sats
# karma  1–20   → 15 sats
# karma 21–50   → 10 sats
# karma 50+     →  5 sats
```

Requires local Giskard Marks (`:8015`) + Argentum (`:8017`). Falls back silently to base price on any failure.

---

## Related

- [argentum-core](https://github.com/giskard09/argentum-core) — API server
- [argentum-web](https://github.com/giskard09/argentum-web) — Dashboard
- [giskard-marks](https://github.com/giskard09/giskard-marks) — Permanent proof of presence
- [giskard-memory](https://github.com/giskard09/giskard-memory) — Persistent agent memory

Apache 2.0 — Prior art: March 30, 2026
