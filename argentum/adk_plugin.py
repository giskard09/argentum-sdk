"""
Argentum ADK Plugin — Trust layer for Google Agent Development Kit agents.

Intercepts tool calls to:
  1. Check karma of the service being called (blocks if karma < 0)
  2. Auto-submit actions to build the calling agent's reputation

This creates the flywheel: every tool call through ADK
automatically contributes to the agent's on-chain karma.

Usage:
    from argentum.adk_plugin import make_trust_callback
    from google.adk.tools import FunctionTool

    callback = make_trust_callback("my-agent-001", "My Agent")
    tool = FunctionTool(my_function, before_tool_callback=callback)

Requires: pip install google-adk argentum-agent
"""

from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING
from . import submit_action, get_karma

if TYPE_CHECKING:
    from google.adk.tools.base_tool import BaseTool
    from google.adk.tools.tool_context import ToolContext


def make_trust_callback(
    agent_id:    str,
    agent_name:  str,
    entity_type: str = "agent",
    auto_submit: bool = True,
    min_karma:   int  = 0,
) -> callable:
    """
    Factory that returns a before_tool_callback for Google ADK agents.

    Args:
        agent_id:    Unique ID for this agent in Argentum (e.g. "my-agent-001")
        agent_name:  Human-readable name (e.g. "Customer Support Agent")
        entity_type: "agent", "human", "robot", or "hybrid"
        auto_submit: If True, submits an action to Argentum after each tool call
                     This builds the agent's karma automatically.
        min_karma:   Minimum karma required for a service to be trusted.
                     Services with karma below this threshold are blocked.
                     Default 0 — only blocks explicitly malicious services (karma < 0).

    Returns:
        A before_tool_callback function compatible with google.adk.tools.FunctionTool
    """

    def before_tool_callback(
        tool: "BaseTool",
        args: Dict[str, Any],
        tool_context: "ToolContext",
    ) -> Optional[Dict[str, Any]]:
        """
        Runs before each tool call.
        - Checks service karma (blocks if below min_karma)
        - Submits action to build calling agent's reputation
        """

        service_id = tool.name

        # ── 1. Check service karma ────────────────────────────────────────────
        try:
            service_karma = get_karma(service_id)
            if service_karma < min_karma:
                return {
                    "error": (
                        f"[Argentum] Service '{service_id}' has insufficient karma "
                        f"({service_karma} < {min_karma}). Action blocked."
                    ),
                    "argentum_blocked": True,
                    "service_karma": service_karma,
                }
        except Exception:
            pass  # non-blocking — if Argentum is unreachable, allow the call

        # ── 2. Auto-submit action (flywheel) ──────────────────────────────────
        if auto_submit:
            try:
                args_preview = str(args)[:200] if args else ""
                result = submit_action(
                    entity_id   = agent_id,
                    entity_name = agent_name,
                    entity_type = entity_type,
                    action_type = "HELP",
                    description = f"Called external tool '{service_id}'" + (
                        f" — args: {args_preview}" if args_preview else ""
                    ),
                )
                # Store action_id in session state for potential attestation later
                if hasattr(tool_context, "state") and result.get("action_id"):
                    tool_context.state["last_argentum_action_id"] = result["action_id"]
            except Exception:
                pass  # non-blocking — karma submission should never break the agent

        return None  # Allow tool execution to proceed

    return before_tool_callback


def wrap_tools(tools: list, agent_id: str, agent_name: str, **kwargs) -> list:
    """
    Convenience function to add Argentum trust callbacks to all tools at once.

    Usage:
        from google.adk.tools import FunctionTool
        from argentum.adk_plugin import wrap_tools

        raw_tools = [FunctionTool(search), FunctionTool(fetch_price)]
        trusted_tools = wrap_tools(raw_tools, "my-agent", "My Agent")
    """
    try:
        from google.adk.tools import FunctionTool
    except ImportError:
        raise ImportError("google-adk is required: pip install google-adk")

    callback = make_trust_callback(agent_id, agent_name, **kwargs)
    wrapped  = []
    for tool in tools:
        if isinstance(tool, FunctionTool):
            tool.before_tool_callback = callback
        wrapped.append(tool)
    return wrapped
