"""
Mycelium Trails — utilidades para linkeo cross-surface de records.

compute_action_ref() produce el identificador canónico de un trail:
SHA-256 de "agent_id:action_type:scope:timestamp".

Uso:
    from argentum.trails import compute_action_ref
    ref = compute_action_ref("aps-agent-1", "permit", "giskard-oasis", 1746518400)

Cualquier caller que conozca los 4 valores puede pre-generar el mismo hash
antes de que Mycelium escriba el trail. Eso crea dependencia estructural:
el record externo apunta al trail antes de que exista.
"""
import hashlib
from datetime import datetime, timezone


def compute_action_ref(
    agent_id: str,
    action_type: str,
    scope: str,
    timestamp: int,
) -> str:
    """
    Retorna el SHA-256 canónico que identifica un trail de forma única.

    Args:
        agent_id:    Identificador del agente (ej. "aps-agent-1")
        action_type: Operación realizada (ej. "enter_oasis", "permit")
        scope:       Servicio donde ocurrió (ej. "giskard-oasis")
        timestamp:   Unix epoch en segundos (int)

    Returns:
        hex string de 64 caracteres, determinístico para los mismos inputs.
    """
    payload = f"{agent_id}:{action_type}:{scope}:{int(timestamp)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_trail(
    agent_id: str,
    action_ref: str,
    base_url: str = "https://argentum.rgiskard.xyz",
    timeout: int = 10,
) -> dict:
    """
    Consulta el endpoint público de verificación de trails.

    Returns:
        {verified: bool, block: int|None, tx_hash: str|None, timestamp: str|None}
    """
    import requests  # lazy import — no dep en import-time

    r = requests.get(
        f"{base_url}/trails/verify",
        params={"agent_id": agent_id, "action_ref": action_ref},
        timeout=timeout,
    )
    if r.status_code == 404:
        return {"verified": False, "block": None, "tx_hash": None, "timestamp": None}
    r.raise_for_status()
    return r.json()


def timestamp_now() -> int:
    """Unix timestamp actual. Helper para callers que construyen action_ref."""
    return int(datetime.now(timezone.utc).timestamp())
