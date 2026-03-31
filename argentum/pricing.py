"""
argentum.pricing — karma-tiered pricing for Mycelium MCP servers.

For services running alongside a local Mycelium stack.
Queries Giskard Marks (identity) + Argentum (karma) to apply discounts.

Chain: Marks (identity) → Argentum (karma) → service price

Usage:
    from argentum.pricing import karma_discount

    price, karma = karma_discount("my-agent-001", base_price=21)
    # Returns (discounted_sats, karma_value)
    # Falls back to (base_price, 0) on any failure — no service disruption

KNOWN GAP: agent_id is self-declared. No cryptographic proof yet.
"""
import re
import httpx

ARGENTUM_URL = "http://localhost:8017"
MARKS_URL    = "http://localhost:8015"

# Tiers: (min_karma, fraction_of_base_price)
TIERS = [
    (50, 0.25),   # 75% off
    (21, 0.50),   # 50% off
    (1,  0.70),   # 30% off
    (0,  1.00),   # base price
]


def sanitize_agent_id(agent_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\-_]", "", agent_id)[:64]


def _verify_mark(agent_id: str) -> bool:
    try:
        r = httpx.get(f"{MARKS_URL}/verify/{agent_id}", timeout=2.0)
        if r.status_code == 200:
            return r.json().get("found", False)
    except Exception:
        pass
    return False


def _get_karma(agent_id: str) -> int:
    try:
        r = httpx.get(f"{ARGENTUM_URL}/entity/{agent_id}/trace", timeout=2.0)
        if r.status_code == 200:
            return r.json().get("wisdom", {}).get("total_karma", 0)
    except Exception:
        pass
    return 0


def karma_discount(agent_id: str, base_price: int) -> tuple:
    """
    Returns (price, karma) for the given agent_id.

    price  — sats to charge (>= 1, always at least 1 sat)
    karma  — karma score of the agent (0 if unknown or no mark)

    Requires a valid Giskard Mark. Falls back to (base_price, 0) on any failure.
    """
    if not agent_id:
        return base_price, 0
    agent_id = sanitize_agent_id(agent_id)
    if not _verify_mark(agent_id):
        return base_price, 0
    karma = _get_karma(agent_id)
    for threshold, fraction in TIERS:
        if karma >= threshold:
            price = max(1, int(base_price * fraction))
            return price, karma
    return base_price, 0
