from .client import ArgentumClient

_default = ArgentumClient()

def submit_action(entity_id, entity_name, entity_type, action_type, description, proof=None):
    return _default.submit_action(entity_id, entity_name, entity_type, action_type, description, proof)

def attest(action_id, attester_id, attester_name, note=None):
    return _default.attest(action_id, attester_id, attester_name, note)

def get_trace(entity_id):
    return _default.get_trace(entity_id)

def get_karma(entity_id):
    return _default.get_karma(entity_id)

def get_leaderboard(limit=10):
    return _default.get_leaderboard(limit)

def get_pending(limit=20):
    return _default.get_pending(limit)

def stats():
    return _default.stats()

__all__ = [
    "ArgentumClient",
    "submit_action", "attest", "get_trace",
    "get_karma", "get_leaderboard", "get_pending", "stats",
]
