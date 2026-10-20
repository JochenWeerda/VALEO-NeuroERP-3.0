"""Zeilenaktionen der Finance-Stammdatenlisten als Fachaktion fuer Maske, CLI und MCP (MASK-STUDIO-ROLLOUT, Welle 1).

Die handgebaute Debitorenliste sperrte ueber ``PATCH /finance/debtors/{id}`` ohne Begruendung und ohne Audit;
"Zahlungserinnerung" meldete Erfolg, ohne eine Anfrage zu senden. Hier sperren und entsperren mit Begruendung,
Audit, Trockenlauf und Wiederholungsschutz von ``statusaktion``, mit derselben Rolle wie der Fachweg.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.finance_roles import finance_admin, finance_write
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult
from app.services.mask_commands import bearbeiten, statusaktion, zeile_per_sql

router = APIRouter(tags=["mask-actions"])

_DEBITOR_STATUS = ("SELECT CASE WHEN coalesce(is_active, true) THEN 'AKTIV' ELSE 'GESPERRT' END AS status "
                   "FROM domain_crm.customers WHERE id::text = :id AND tenant_id = :tid AND deleted_at IS NULL")


async def _debitor_setzen(entity_id: str, body: dict[str, Any], db: Session, tenant_id: str, *,
                          aktiv: bool) -> MaskActionResult:
    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        session.execute(text("UPDATE domain_crm.customers SET is_active = :aktiv, updated_at = now() "
                             "WHERE id::text = :id AND tenant_id = :tid"),
                        {"aktiv": aktiv, "id": entity_id, "tid": tenant_id})
        return "Debitor entsperrt." if aktiv else "Debitor gesperrt."

    return await statusaktion(
        db, action_key="entsperren" if aktiv else "sperren", entity_type="debitor", entity_id=entity_id,
        tenant_id=tenant_id, body=body, status_sql=_DEBITOR_STATUS, erlaubt={"GESPERRT" if aktiv else "AKTIV"},
        ausfuehren=ausfuehren, event_type="finance.debitor.entsperrt" if aktiv else "finance.debitor.gesperrt",
        begruendung_pflicht=True)


@router.post("/finance/debitoren/{entity_id}/actions/sperren", response_model=MaskActionResult,
             summary="Debitor mit Begruendung sperren", dependencies=[Depends(finance_write)])
async def debitor_sperren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                          db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _debitor_setzen(entity_id, body, db, tenant_id, aktiv=False)


@router.post("/finance/debitoren/{entity_id}/actions/entsperren", response_model=MaskActionResult,
             summary="Debitor mit Begruendung entsperren", dependencies=[Depends(finance_write)])
async def debitor_entsperren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                             db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _debitor_setzen(entity_id, body, db, tenant_id, aktiv=True)


# --------------------------------------------------------------------------- Wechselkurse

_KURS_STATUS = ("SELECT CASE WHEN active THEN 'AKTIV' ELSE 'INAKTIV' END AS status "
                "FROM domain_erp.exchange_rates WHERE id::text = :id AND tenant_id = :tid")


async def _kurs_setzen(entity_id: str, body: dict[str, Any], db: Session, tenant_id: str, *,
                       aktiv: bool) -> MaskActionResult:
    """Deaktivieren statt Loeschen: gebuchte Fremdwaehrungsbelege behalten ihren Kurs. Die handgebaute Seite rief
    ``DELETE /finance/exchange-rates/{id}`` — einen Weg, den es nie gab (jedes Loeschen scheiterte, 20.10.2026)."""
    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        session.execute(text("UPDATE domain_erp.exchange_rates SET active = :aktiv, updated_at = now() "
                             "WHERE id::text = :id AND tenant_id = :tid"),
                        {"aktiv": aktiv, "id": entity_id, "tid": tenant_id})
        return "Wechselkurs aktiviert." if aktiv else "Wechselkurs deaktiviert."

    return await statusaktion(
        db, action_key="aktivieren" if aktiv else "deaktivieren", entity_type="wechselkurs", entity_id=entity_id,
        tenant_id=tenant_id, body=body, status_sql=_KURS_STATUS, erlaubt={"INAKTIV" if aktiv else "AKTIV"},
        ausfuehren=ausfuehren,
        event_type="finance.wechselkurs.aktiviert" if aktiv else "finance.wechselkurs.deaktiviert",
        begruendung_pflicht=True)


@router.post("/finance/exchange-rates/{entity_id}/actions/deaktivieren", response_model=MaskActionResult,
             summary="Wechselkurs mit Begruendung deaktivieren", dependencies=[Depends(finance_write)])
async def kurs_deaktivieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                            db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _kurs_setzen(entity_id, body, db, tenant_id, aktiv=False)


@router.post("/finance/exchange-rates/{entity_id}/actions/aktivieren", response_model=MaskActionResult,
             summary="Wechselkurs mit Begruendung aktivieren", dependencies=[Depends(finance_write)])
async def kurs_aktivieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                          db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _kurs_setzen(entity_id, body, db, tenant_id, aktiv=True)


# --------------------------------------------------------------------------- Zahlungsbedingungen

_ZABD_STATUS = ("SELECT CASE WHEN aktiv THEN 'AKTIV' ELSE 'INAKTIV' END AS status "
                "FROM domain_shared.zahlungsbedingungen WHERE id::text = :id AND tenant_id = :tid")
_ZABD_FELDER = ("bezeichnung", "zahlungsziel_tage", "skonto1_tage", "skonto1_prozent", "skonto2_tage",
                "skonto2_prozent", "netto_tage", "manuelles_datum", "zahlungsart")


@router.post("/fibu/zahlungsbedingungen/{entity_id}/actions/bearbeiten", response_model=MaskActionResult,
             summary="Zahlungsbedingung bearbeiten", dependencies=[Depends(finance_write)])
async def zahlungsbedingung_bearbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                       db: Session = Depends(get_db),
                                       tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    from app.api.v1.endpoints.zahlungsbedingungen import ZahlungsbedingungCreate, update_zahlungsbedingung

    def ergaenzen(session: Session, eingabe: dict, eid: str, tid: str) -> dict[str, Any]:
        # Vollersatz-Modell: Nummer und nicht gesendete Felder aus dem Ist-Stand, damit nichts geleert wird.
        zeile = session.execute(text(f"SELECT zabd_nr, {', '.join(_ZABD_FELDER)} FROM domain_shared.zahlungsbedingungen "  # nosec B608
                                     "WHERE id::text = :id AND tenant_id = :tid"), {"id": eid, "tid": tid}).mappings().first()
        return dict(zeile) if zeile else {}

    def aendern(session: Session, werte: Any, eid: str, tid: str) -> None:
        update_zahlungsbedingung(werte.zabd_nr, werte, db=session, tenant_id=tid)

    return await bearbeiten(
        db, entity_type="zahlungsbedingung", entity_id=entity_id, tenant_id=tenant_id, body=body,
        felder={f: f for f in _ZABD_FELDER}, modell=ZahlungsbedingungCreate, erlaubt={"AKTIV"}, ergaenzen=ergaenzen,
        lesen=zeile_per_sql(_ZABD_STATUS), aendern=aendern, event_type="finance.zahlungsbedingung.updated")


@router.post("/fibu/zahlungsbedingungen/{entity_id}/actions/deaktivieren", response_model=MaskActionResult,
             summary="Zahlungsbedingung deaktivieren", dependencies=[Depends(finance_admin)])
async def zahlungsbedingung_deaktivieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                         db: Session = Depends(get_db),
                                         tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        session.execute(text("UPDATE domain_shared.zahlungsbedingungen SET aktiv = false "
                             "WHERE id::text = :id AND tenant_id = :tid"), {"id": entity_id, "tid": tenant_id})
        return "Zahlungsbedingung deaktiviert."

    return await statusaktion(
        db, action_key="deaktivieren", entity_type="zahlungsbedingung", entity_id=entity_id, tenant_id=tenant_id,
        body=body, status_sql=_ZABD_STATUS, erlaubt={"AKTIV"}, ausfuehren=ausfuehren,
        event_type="finance.zahlungsbedingung.deaktiviert", begruendung_pflicht=True)
