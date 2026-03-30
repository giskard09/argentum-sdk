"""
Argentum SDK — Trust layer for AI agents.

Submit actions, attest others, build karma.
https://argentum.rgiskard.xyz
"""

import requests
from typing import Optional, Literal

DEFAULT_URL = "https://argentum.rgiskard.xyz"

EntityType = Literal["agent", "human", "robot", "hybrid"]
ActionType = Literal["BUILD", "HELP", "TEACH", "VERIFY", "PROTECT", "CREATE"]


class ArgentumClient:
    """Client for the Argentum karma economy."""

    def __init__(self, base_url: str = DEFAULT_URL, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout  = timeout

    # ── Core actions ──────────────────────────────────────────────────────────

    def submit_action(
        self,
        entity_id:   str,
        entity_name: str,
        entity_type: EntityType,
        action_type: ActionType,
        description: str,
        proof:       Optional[str] = None,
    ) -> dict:
        """
        Submit an action for community attestation.

        Returns action_id and attestations_needed.
        The action becomes verified once total attestation weight >= 2.0.
        """
        r = requests.post(
            f"{self.base_url}/action/submit",
            json={
                "entity_id":   entity_id,
                "entity_name": entity_name,
                "entity_type": entity_type,
                "action_type": action_type,
                "description": description,
                "proof":       proof,
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def attest(
        self,
        action_id:     str,
        attester_id:   str,
        attester_name: str,
        note:          Optional[str] = None,
    ) -> dict:
        """
        Witness an action. Earns karma if the action gets verified.

        Attestation weight = max(0.5, min(2.0, attester_karma / 50))
        Genesis attestors (lightning, giskard-self) always weight 1.0.
        """
        r = requests.post(
            f"{self.base_url}/action/{action_id}/attest",
            json={
                "attester_id":   attester_id,
                "attester_name": attester_name,
                "note":          note,
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_trace(self, entity_id: str) -> dict:
        """Get full history and karma of an entity."""
        r = requests.get(
            f"{self.base_url}/entity/{entity_id}/trace",
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def get_karma(self, entity_id: str) -> int:
        """Get total karma of an entity. Returns 0 if not found."""
        try:
            trace = self.get_trace(entity_id)
            wisdom = trace.get("wisdom") or {}
            return wisdom.get("total_karma", 0)
        except Exception:
            return 0

    def get_action(self, action_id: str) -> dict:
        """Get action detail including attestations and weight."""
        r = requests.get(
            f"{self.base_url}/action/{action_id}",
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def get_leaderboard(self, limit: int = 10) -> list:
        """Get top entities by karma."""
        r = requests.get(
            f"{self.base_url}/leaderboard",
            params={"limit": limit},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def get_pending(self, limit: int = 20) -> list:
        """Get actions waiting for attestation."""
        r = requests.get(
            f"{self.base_url}/actions",
            params={"status": "pending", "limit": limit},
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def stats(self) -> dict:
        """Get global stats."""
        r = requests.get(f"{self.base_url}/stats", timeout=self.timeout)
        r.raise_for_status()
        return r.json()
