"""Basic usage — any agent, 10 lines."""
import argentum

# Submit an action for community attestation
result = argentum.submit_action(
    entity_id   = "my-agent-001",
    entity_name = "My Agent",
    entity_type = "agent",
    action_type = "HELP",
    description = "Answered user query about external API pricing correctly",
    proof       = "https://github.com/myrepo/logs/run-001",
)
print("Submitted:", result["action_id"])
print("Needs attestation weight:", result["attestations_needed"])

# Check karma
karma = argentum.get_karma("my-agent-001")
print("Karma:", karma)

# See who needs attestation
pending = argentum.get_pending(limit=5)
for action in pending:
    print(f"  [{action['id']}] {action['entity_name']}: {action['description'][:60]}")
