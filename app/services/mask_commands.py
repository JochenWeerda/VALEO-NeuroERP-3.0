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

from collections.abc import Awaitable, Callable, Collection, Mapping
from typing import Any

from pydantic import BaseModel, ValidationError
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


def zeile_per_sql(sql: str) -> Callable[[Session, str, str], Awaitable[Mapping[str, Any] | None]]:
    """Lesefunktion fuer ``bearbeiten``: ``sql`` liest eine Zeile mit ``status`` fuer ``:id`` und ``:tid``."""
    async def lesen(db: Session, entity_id: str, tenant_id: str) -> Mapping[str, Any] | None:
        return db.execute(text(sql), {"id": entity_id, "tid": tenant_id}).mappings().first()
    return lesen


def _feldfehler(exc: ValidationError) -> list[dict]:
    return [{"field": ".".join(str(t) for t in fehler["loc"]) or "_entity", "message": fehler["msg"],
             "severity": "blocking"} for fehler in exc.errors()]


async def bearbeiten(
    db: Session,
    *,
    entity_type: str,
    entity_id: str,
    tenant_id: str,
    body: dict[str, Any],
    felder: Mapping[str, str],
    modell: type[BaseModel],
    lesen: Callable[[Session, str, str], Awaitable[Mapping[str, Any] | None]],
    aendern: Callable[[Session, BaseModel, str, str], Awaitable[Any]],
    event_type: str,
    erlaubt: Collection[str] | None = None,
    ergaenzen: Callable[[Session, dict[str, Any], str, str], dict[str, Any]] | None = None,
    begruendung_pflicht: bool = False,
) -> MaskActionResult:
    """Aenderung eines Objekts aus der Maske, der CLI oder MCP ueber den **bestehenden** Aenderungsweg
    (STAMMDATEN-BEARBEITEN-20261019).

    * ``felder`` bildet die deklarierten Eingabefelder der Maske auf die Felder des Aenderungsmodells ab. Nur sie
      zaehlen; die Maske schickt den ganzen Objektkontext mit, ``None`` gilt als nicht gesendet.
    * Pruefung in jedem Modus: Begruendung (falls Pflicht), mindestens ein Feld, Objekt im Mandanten (``lesen``
      liefert die Zeile mit ``status`` oder ``None``, meist ``zeile_per_sql``), Status aus ``erlaubt``, Modell.
    * ``ergaenzen`` liefert Pflichtfelder eines Vollersatz-Modells aus dem Ist-Stand, damit nichts geleert wird.
    * ``aendern(session, werte, entity_id, tenant_id)`` ruft den Fachweg im Savepoint auf.
    """
    reason = begruendung(body)
    eingabe = {ziel: body[quelle] for quelle, ziel in felder.items()
               if quelle in body and body[quelle] is not None}

    def werte_aus(db_: Session, eid: str, tid: str) -> BaseModel:
        daten = {**(ergaenzen(db_, eingabe, eid, tid) if ergaenzen else {}), **eingabe}
        return modell.model_validate(daten)

    async def pruefen(db_: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        if begruendung_pflicht and not 5 <= len(reason) <= 500:
            return [{"field": "_auditReason", "message": "Begruendung mit 5 bis 500 Zeichen erforderlich.",
                     "severity": "blocking"}]
        if not eingabe:
            return [{"field": "_entity", "message": "Keine Aenderung angegeben.", "severity": "blocking"}]
        row = await lesen(db_, eid, tid)
        if row is None:
            return [{"field": "_entity", "message": "Objekt nicht gefunden.", "severity": "blocking"}]
        if erlaubt is not None and row["status"] not in erlaubt:
            return [{"field": "_entity", "message": f"Im Status {row['status']} nicht aenderbar.",
                     "severity": "blocking"}]
        try:
            werte_aus(db_, eid, tid)
        except ValidationError as exc:
            return _feldfehler(exc)
        return []

    async def delegieren(db_: Session, payload: dict, eid: str, tid: str) -> str:
        await aendern(db_, werte_aus(db_, eid, tid), eid, tid)
        return f"Geaendert: {', '.join(sorted(eingabe))}."

    return await run_delegated_mask_action(
        db, action_key="bearbeiten", entity_type=entity_type, entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=delegieren, outbox_event_type=event_type,
        require_audit_reason=begruendung_pflicht,
    )
