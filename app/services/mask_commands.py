"""Statusaktionen einer Maske als Kommando-Weg (MASK-COMMANDS-ROLLOUT-20261019).

Die meisten Zeilenaktionen der Cockpit-Masken sind Zustandswechsel eines Objekts: pruefen, freigeben,
ausfuehren, wiederholen. Ihr Fachweg existiert schon als Service-Methode. ``statusaktion`` legt um ihn
den Rahmen, den Maske, CLI und MCP gemeinsam brauchen — ueber ``run_delegated_mask_action``:

* Pruefung in jedem Modus gegen die Datenbank: Begruendung (falls Pflicht), Objekt im Mandanten, Zustand
  aus der erlaubten Menge. Ein Trockenlauf meldet so, was abgelehnt wuerde, und schreibt nichts.
* Bei ``execute`` laeuft der Fachweg in einem Savepoint; Audit, Ereignis und Mutation werden gemeinsam
  committet, eine Ablehnung des Fachwegs rollt alles zurueck und kommt als ``success=false`` zurueck.
* Eine Wiederholung mit demselben Schluessel wirkt einmal.
"""
from __future__ import annotations

from collections.abc import Callable, Collection
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action


def begruendung(body: dict[str, Any]) -> str:
    return str(body.get("_auditReason") or "").strip()


async def statusaktion(
    db: Session,
    *,
    action_key: str,
    entity_type: str,
    entity_id: str,
    tenant_id: str,
    body: dict[str, Any],
    status_sql: str,
    erlaubt: Collection[str] | None,
    ausfuehren: Callable[[Session, dict[str, Any]], str | None],
    event_type: str,
    begruendung_pflicht: bool = True,
    zusatzpruefung: Callable[[dict[str, Any]], str | None] | None = None,
) -> MaskActionResult:
    """``status_sql`` liest eine Zeile mit ``status`` fuer ``:id`` und ``:tid`` (mandantengenau)."""
    reason = begruendung(body)

    async def pruefen(db_: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        if begruendung_pflicht and not 5 <= len(reason) <= 500:
            return [{"field": "_auditReason", "message": "Begruendung mit 5 bis 500 Zeichen erforderlich.",
                     "severity": "blocking"}]
        row = db_.execute(text(status_sql), {"id": eid, "tid": tid}).mappings().first()
        if row is None:
            return [{"field": "_entity", "message": "Objekt nicht gefunden.", "severity": "blocking"}]
        if erlaubt is not None and row["status"] not in erlaubt:
            return [{"field": "_entity", "message": f"Aktion im Status {row['status']} nicht moeglich.",
                     "severity": "blocking"}]
        if zusatzpruefung is not None:
            grund = zusatzpruefung(dict(row))
            if grund:
                return [{"field": "_entity", "message": grund, "severity": "blocking"}]
        return []

    async def delegieren(db_: Session, payload: dict, eid: str, tid: str) -> str:
        return ausfuehren(db_, payload) or f"{action_key} ausgefuehrt."

    return await run_delegated_mask_action(
        db, action_key=action_key, entity_type=entity_type, entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=delegieren, outbox_event_type=event_type,
        require_audit_reason=begruendung_pflicht,
    )
