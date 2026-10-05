"""Ambient-Agent-Framework (UIX-092) — beobachtende, deterministische Agenten.

Agenten ueberwachen Read Models und erzeugen ERKLAERTE Worklist-Vorschlaege —
sie mutieren NIE (keine Buchungen). v1-Regeln sind deterministisch (confidence
1.0). Jeder Vorschlag traegt eine Begruendung (reason) und einen Beleg-Verweis
(source_ref). Dedupe per dedupe_key; entfallene Sachverhalte werden auto-resolved.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class WorklistProposal:
    agent_id: str
    tenant_id: str
    dedupe_key: str            # idempotent je Sachverhalt
    title: str
    reason: str                # Pflicht: warum meldet der Agent das?
    source_ref: str            # object_type:object_id
    confidence: float          # 1.0 bei deterministischen Regeln
    severity: str              # info|warning|critical
    target_screen_id: str
    target_route: str
    payload: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class AmbientAgent(Protocol):
    agent_id: str
    schedule: str              # 'nightly' | 'hourly'

    def evaluate(self, rows: list[dict[str, Any]], tenant_id: str) -> list[WorklistProposal]:
        """Reine Regel-Auswertung ueber vorgeladene Read-Model-Zeilen."""
        ...


@dataclass
class ReconcileResult:
    """Ergebnis eines Laufs: was upserten, was auto-aufloesen."""
    upserts: list[WorklistProposal]
    auto_resolve_keys: list[str]


def reconcile(
    proposals: list[WorklistProposal],
    existing_open_keys: set[str],
) -> ReconcileResult:
    """Lauf-Semantik: upsert je Proposal; `open`-Items ausserhalb der aktuellen
    Proposal-Menge werden auto-resolved (done). `dismissed` bleibt (nicht in
    existing_open_keys — der Aufrufer liefert nur offene Keys)."""
    current_keys = {p.dedupe_key for p in proposals}
    auto_resolve = sorted(existing_open_keys - current_keys)
    return ReconcileResult(upserts=list(proposals), auto_resolve_keys=auto_resolve)
