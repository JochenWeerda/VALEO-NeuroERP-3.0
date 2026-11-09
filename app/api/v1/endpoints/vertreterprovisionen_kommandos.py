"""Vertreterprovisionen als Fachaktion fuer Maske, CLI und MCP (Studio-Listen, 09.11.2026).

Ersetzt die handgebaute Seite ``crm/vertreterprovisionen-legacy``:

* ``gruppen/actions/anlegen``: Provisionsgruppe anlegen (Nummer je Richtung eindeutig; fix braucht einen Satz).
* ``gruppen/{entity_id}/actions/deaktivieren``: Gruppe stilllegen (wie bisher ``aktiv = false``), mit Grund.
* ``gruppen/{entity_id}/actions/staffelzeile_anlegen``: eine Staffelzeile anlegen; die Staffel der Gruppe und
  Vertreterklasse entsteht dabei, falls es sie noch nicht gibt. Zeilennummer = naechste freie.
* ``GET staffelzeilen``: alle Staffelzeilen flach mit Gruppe und Klasse (Leseweg der Liste).
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.endpoints.vertreterprovisionen import GUELTIGE_PROVISIONSTYPEN, GUELTIGE_RICHTUNG
from app.api.v1.schemas.base import BaseSchema
from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import get_current_user
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(prefix="/crm/vertreter/provisionen", tags=["CRM - Vertreterprovisionen", "mask-actions"])

RICHTUNGEN = [("vk", "Verkauf"), ("ek", "Einkauf")]
PROVISIONSTYPEN = [("fix", "Fester Satz"), ("staffel_optpreis", "Staffel nach OPT-Preis"),
                   ("staffel_preis_zuab", "Staffel nach Preis + Zu-/Abschlägen")]

GRUPPE_FELDER: list[dict[str, Any]] = [
    {"key": "gruppe_nr", "label": "Gruppe", "type": "text", "required": True},
    {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
    {"key": "richtung", "label": "Richtung", "type": "select", "required": True,
     "options": [{"value": w, "label": t} for w, t in RICHTUNGEN]},
    {"key": "provisionstyp", "label": "Provisionstyp", "type": "select", "required": True,
     "options": [{"value": w, "label": t} for w, t in PROVISIONSTYPEN]},
    {"key": "provisionssatz", "label": "Provisionssatz %", "type": "number"},
]
STAFFEL_FELDER: list[dict[str, Any]] = [
    {"key": "vertreterklasse", "label": "Vertreterklasse", "type": "text"},
    {"key": "ab_wert", "label": "Ab Wert (EUR)", "type": "number", "required": True},
    {"key": "provisionssatz", "label": "Provisionssatz %", "type": "number", "required": True},
]


class StaffelzeileOut(BaseSchema):
    id: str
    gruppe_id: str
    gruppe_nr: str
    gruppe_bezeichnung: str
    vertreterklasse: Optional[str] = None
    zeile_nr: int
    ab_wert: Decimal
    provisionssatz: Decimal


def _blockiert(meldung: str, feld: str = "_entity") -> list[dict]:
    return [{"field": feld, "message": meldung, "severity": "blocking"}]


def _satz(wert: Any) -> Optional[Decimal]:
    if wert in (None, ""):
        return None
    try:
        return Decimal(str(wert).replace(",", "."))
    except InvalidOperation:
        return Decimal("-1")  # ungueltig; die Pruefung meldet es


@router.get("/staffelzeilen", response_model=list[StaffelzeileOut], summary="Staffelzeilen aller Provisionsgruppen")
def staffelzeilen(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[StaffelzeileOut]:
    zeilen = db.execute(text(
        "SELECT z.id::text AS id, g.id::text AS gruppe_id, g.gruppe_nr, g.bezeichnung AS gruppe_bezeichnung, "
        "s.vertreterklasse, z.zeile_nr, z.ab_wert, z.provisionssatz "
        "FROM domain_shared.vertreter_staffel_zeilen z "
        "JOIN domain_shared.vertreter_provisionsstaffeln s ON s.id = z.staffel_id "
        "JOIN domain_shared.vertreter_provisionsgruppen g ON g.id = s.gruppe_id "
        "WHERE g.tenant_id = :t AND g.aktiv = true ORDER BY g.gruppe_nr, s.vertreterklasse NULLS FIRST, z.zeile_nr"),
        {"t": tenant_id}).mappings().fetchmany(2000)
    return [StaffelzeileOut(**dict(z)) for z in zeilen]


@router.post("/gruppen/actions/anlegen", response_model=MaskActionResult, summary="Provisionsgruppe anlegen",
             dependencies=SCHREIBEN["CRM"])
async def gruppe_anlegen(body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                         tenant_id: str = Depends(get_tenant_id),
                         nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        nr, bez = str(payload.get("gruppe_nr") or "").strip(), str(payload.get("bezeichnung") or "").strip()
        richtung, typ = payload.get("richtung") or "vk", payload.get("provisionstyp") or "fix"
        satz = _satz(payload.get("provisionssatz"))
        if not nr or len(nr) > 20:
            return _blockiert("Gruppennummer fehlt oder ist laenger als 20 Zeichen.", "gruppe_nr")
        if not bez:
            return _blockiert("Bezeichnung fehlt.", "bezeichnung")
        if richtung not in GUELTIGE_RICHTUNG:
            return _blockiert("Richtung muss Verkauf oder Einkauf sein.", "richtung")
        if typ not in GUELTIGE_PROVISIONSTYPEN:
            return _blockiert("Unbekannter Provisionstyp.", "provisionstyp")
        if typ == "fix" and satz is None:
            return _blockiert("Ein fester Provisionstyp braucht einen Satz.", "provisionssatz")
        if satz is not None and not Decimal(0) <= satz <= Decimal(100):
            return _blockiert("Provisionssatz muss zwischen 0 und 100 % liegen.", "provisionssatz")
        if session.execute(text("SELECT 1 FROM domain_shared.vertreter_provisionsgruppen "
                                "WHERE tenant_id = :t AND gruppe_nr = :nr AND richtung = :r"),
                           {"t": tid, "nr": nr, "r": richtung}).scalar():
            return _blockiert(f"Provisionsgruppe {nr} gibt es fuer diese Richtung schon.", "gruppe_nr")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        nr = str(payload["gruppe_nr"]).strip()
        session.execute(text(
            "INSERT INTO domain_shared.vertreter_provisionsgruppen "
            "(id, tenant_id, gruppe_nr, bezeichnung, richtung, provisionstyp, provisionssatz) "
            "VALUES (:id, :t, :nr, :bez, :r, :pt, :ps)"),
            {"id": uuid7(), "t": tid, "nr": nr, "bez": str(payload["bezeichnung"]).strip(),
             "r": payload.get("richtung") or "vk", "pt": payload.get("provisionstyp") or "fix",
             "ps": _satz(payload.get("provisionssatz"))})
        return f"Provisionsgruppe {nr} angelegt."

    return await run_delegated_mask_action(
        db, action_key="anlegen", entity_type="vertreter_provisionsgruppe", entity_id="neu", tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="crm.vertreterprovision.gruppe_angelegt")


def _gruppe_aktiv(session: Session, tid: str, gruppe: str) -> bool:
    return bool(session.execute(text(
        "SELECT 1 FROM domain_shared.vertreter_provisionsgruppen WHERE tenant_id = :t AND id::text = :g AND aktiv"),
        {"t": tid, "g": gruppe}).scalar())


@router.post("/gruppen/{entity_id}/actions/deaktivieren", response_model=MaskActionResult,
             summary="Provisionsgruppe stilllegen", dependencies=SCHREIBEN["CRM"])
async def gruppe_deaktivieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                              db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                              nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        return [] if _gruppe_aktiv(session, tid, eid) else _blockiert("Provisionsgruppe nicht gefunden oder still.")

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        session.execute(text("UPDATE domain_shared.vertreter_provisionsgruppen SET aktiv = false "
                             "WHERE tenant_id = :t AND id::text = :g"), {"t": tid, "g": eid})
        return "Provisionsgruppe stillgelegt."

    return await run_delegated_mask_action(
        db, action_key="deaktivieren", entity_type="vertreter_provisionsgruppe", entity_id=entity_id,
        tenant_id=tenant_id, body=body, check_fn=pruefen, delegate_fn=ausfuehren,
        outbox_event_type="crm.vertreterprovision.gruppe_stillgelegt", require_audit_reason=True)


@router.post("/gruppen/{entity_id}/actions/staffelzeile_anlegen", response_model=MaskActionResult,
             summary="Staffelzeile einer Provisionsgruppe anlegen", dependencies=SCHREIBEN["CRM"])
async def staffelzeile_anlegen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                               db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                               nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        if not _gruppe_aktiv(session, tid, eid):
            return _blockiert("Provisionsgruppe nicht gefunden oder still.")
        ab, satz = _satz(payload.get("ab_wert")), _satz(payload.get("provisionssatz"))
        if ab is None or ab < 0:
            return _blockiert("Ab-Wert fehlt oder ist negativ.", "ab_wert")
        if satz is None or not Decimal(0) <= satz <= Decimal(100):
            return _blockiert("Provisionssatz muss zwischen 0 und 100 % liegen.", "provisionssatz")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        klasse = str(payload.get("vertreterklasse") or "").strip() or None
        staffel = session.execute(text(
            "SELECT id FROM domain_shared.vertreter_provisionsstaffeln WHERE gruppe_id::text = :g "
            "AND vertreterklasse IS NOT DISTINCT FROM :k ORDER BY created_at LIMIT 1"), {"g": eid, "k": klasse}).scalar()
        if staffel is None:
            staffel = uuid7()
            session.execute(text("INSERT INTO domain_shared.vertreter_provisionsstaffeln "
                                 "(id, tenant_id, gruppe_id, vertreterklasse) VALUES (:id, :t, :g, :k)"),
                            {"id": staffel, "t": tid, "g": eid, "k": klasse})
        nummer = session.execute(text("SELECT COALESCE(MAX(zeile_nr), 0) + 1 FROM domain_shared.vertreter_staffel_zeilen "
                                      "WHERE staffel_id = :s"), {"s": staffel}).scalar()
        session.execute(text("INSERT INTO domain_shared.vertreter_staffel_zeilen "
                             "(id, tenant_id, staffel_id, zeile_nr, ab_wert, provisionssatz) "
                             "VALUES (:id, :t, :s, :n, :ab, :ps)"),
                        {"id": uuid7(), "t": tid, "s": staffel, "n": nummer, "ab": _satz(payload["ab_wert"]),
                         "ps": _satz(payload["provisionssatz"])})
        return f"Staffelzeile {nummer} angelegt."

    return await run_delegated_mask_action(
        db, action_key="staffelzeile_anlegen", entity_type="vertreter_provisionsgruppe", entity_id=entity_id,
        tenant_id=tenant_id, body=body, check_fn=pruefen, delegate_fn=ausfuehren,
        outbox_event_type="crm.vertreterprovision.staffelzeile_angelegt")
