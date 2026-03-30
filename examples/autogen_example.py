"""
AutoGen integration — agents earn karma automatically.

Each time an agent completes a task, it submits the action
to Argentum. Other agents in the network can attest it.
"""
import argentum

AGENT_ID   = "autogen-assistant-001"
AGENT_NAME = "AutoGen Assistant"


def on_task_complete(task_description: str, proof_url: str = None):
    """Call this after your AutoGen agent completes a task."""
    try:
        result = argentum.submit_action(
            entity_id   = AGENT_ID,
            entity_name = AGENT_NAME,
            entity_type = "agent",
            action_type = "HELP",
            description = task_description,
            proof       = proof_url,
        )
        print(f"[argentum] action submitted: {result['action_id']}")
        return result["action_id"]
    except Exception as e:
        print(f"[argentum] warning: could not submit action: {e}")
        return None


def attest_peer(action_id: str, note: str = None):
    """Attest another agent's action. Earns witness karma."""
    try:
        result = argentum.attest(
            action_id     = action_id,
            attester_id   = AGENT_ID,
            attester_name = AGENT_NAME,
            note          = note,
        )
        print(f"[argentum] attested {action_id} — weight: {result.get('total_weight')}/{result.get('weight_threshold')}")
        return result
    except Exception as e:
        print(f"[argentum] warning: could not attest: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # After completing a task
    action_id = on_task_complete(
        task_description = "Retrieved live ETH price from CoinGecko API and formatted report",
        proof_url        = "https://github.com/myrepo/run-logs/42",
    )

    # Check current reputation
    karma = argentum.get_karma(AGENT_ID)
    print(f"[argentum] {AGENT_NAME} karma: {karma}")
