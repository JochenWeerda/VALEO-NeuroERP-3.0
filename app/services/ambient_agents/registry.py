"""Ambient-Agent-Registry + Kill-Switch (UIX-092).

Registriert die v1-Agenten und filtert deaktivierte je Tenant (Kill-Switch nach
TENANT_MODULE_FLAGS-Muster). Die Registry wird von der Nightly-/Interval-
Infrastruktur aufgerufen; sie prueft VOR jedem Lauf den Kill-Switch.
"""
from __future__ import annotations

from .agents import (
    KontraktUntererfuellungAgent,
    OpEskalationAgent,
    PreisabweichungEinkaufAgent,
    QsFristenAgent,
)
from .base import AmbientAgent

# Registrierte v1-Agenten (deterministisch, nightly).
ALL_AGENTS: list[AmbientAgent] = [
    KontraktUntererfuellungAgent(),
    PreisabweichungEinkaufAgent(),
    OpEskalationAgent(),
    QsFristenAgent(),
]


def active_agents(
    tenant_id: str,
    disabled: dict[str, list[str]] | None = None,
) -> list[AmbientAgent]:
    """Agenten, die fuer diesen Tenant NICHT per Kill-Switch deaktiviert sind.

    `disabled`: {tenant_id: [agent_id, ...]}; '*' als Wildcard-Tenant erlaubt.
    """
    disabled = disabled or {}
    blocked = set(disabled.get(tenant_id, [])) | set(disabled.get("*", []))
    return [a for a in ALL_AGENTS if a.agent_id not in blocked]


def get_agent(agent_id: str) -> AmbientAgent | None:
    return next((a for a in ALL_AGENTS if a.agent_id == agent_id), None)
