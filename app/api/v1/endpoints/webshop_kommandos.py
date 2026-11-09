"""Webshop-Anbindung als Fachaktion fuer Maske, CLI und MCP (Studio-Listen, 09.11.2026).

Ersetzt die handgebaute Seite ``admin/webshop-legacy``. Deren Knopf "Bestellungen importieren" rief einen
Platzhalterweg, der immer 0 meldete; einen Abruf aus dem Shop gibt es nicht. Ehrlich bleibt:

* ``konfigurationen/actions/anlegen`` / ``konfigurationen/{id}/actions/entfernen``: Shop-Anbindung pflegen
  (der API-Schluessel wird nur maskiert gespeichert und nie zurueckgegeben).
* ``bestellungen/{id}/actions/verarbeiten``: importierte Bestellung als DocFlow-Auftragsentwurf anlegen
  (``WebshopIntegrationService.process_order``; Blocker wie fehlender Kunde oder Steuerschluessel melden).
* ``GET bestellungen/liste``: typisierte Zeilen mit Stand, Blockern und Auftragsbezug.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import get_current_user
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.eingabefelder_stamm import SHOPSYSTEME
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(prefix="/webshop", tags=["webshop", "integration", "mask-actions"])


class WebshopBestellZeileOut(BaseSchema):
    id: str
    externe_bestellnr: str
    shop_system: Optional[str] = None
    kunde_name: Optional[str] = None
    gesamtbetrag_brutto: float = 0
    bestelldatum: Optional[str] = None
    status: str
    blocker: Optional[str] = None
    erp_order_number: Optional[str] = None
    imported_at: Optional[str] = None


def _blockiert(meldung: str, feld: str = "_entity") -> list[dict]:
    return [{"field": feld, "message": meldung, "severity": "blocking"}]


def _dienst(session: Session, tid: str):
    from app.services.webshop_integration_service import WebshopIntegrationService

    return WebshopIntegrationService(session, tid)


@router.get("/bestellungen/liste", response_model=list[WebshopBestellZeileOut],
            summary="Importierte Webshop-Bestellungen mit Stand und Blockern")
def bestellungen_liste(db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id)) -> list[WebshopBestellZeileOut]:
    return [WebshopBestellZeileOut(**{k: b.get(k) for k in WebshopBestellZeileOut.model_fields if k != "blocker"},
                                   blocker=", ".join(b.get("blockers") or []) or None)
            for b in _dienst(db, tenant_id).list_orders()]


@router.post("/konfigurationen/actions/anlegen", response_model=MaskActionResult, summary="Shop-Anbindung anlegen",
             dependencies=SCHREIBEN["VERKAUF"])
async def anbindung_anlegen(body: dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db),
                            tenant_id: str = Depends(get_tenant_id),
                            nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        url = str(payload.get("shop_url") or "").strip()
        if not url.startswith(("https://", "http://")):
            return _blockiert("Shop-Adresse muss mit https:// beginnen.", "shop_url")
        if payload.get("shop_system") not in dict(SHOPSYSTEME):
            return _blockiert("Unbekanntes Shopsystem.", "shop_system")
        if not str(payload.get("api_key") or "").strip():
            return _blockiert("API-Schluessel fehlt.", "api_key")
        intervall = str(payload.get("sync_interval_minutes") or "15").strip()
        if not intervall.isdigit() or not 1 <= int(intervall) <= 1440:
            return _blockiert("Abrufintervall muss zwischen 1 und 1440 Minuten liegen.", "sync_interval_minutes")
        if session.execute(text("SELECT 1 FROM domain_shared.webshop_configs WHERE tenant_id = :t AND shop_url = :u"),
                           {"t": tid, "u": url}).scalar():
            return _blockiert("Diesen Shop gibt es schon.", "shop_url")
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        url = str(payload["shop_url"]).strip()
        _dienst(session, tid).create_configuration({
            "shop_url": url, "shop_system": payload["shop_system"], "api_key": str(payload["api_key"]).strip(),
            "sync_interval_minutes": int(str(payload.get("sync_interval_minutes") or "15").strip()), "is_active": True})
        return f"Shop-Anbindung {url} angelegt."

    return await run_delegated_mask_action(
        db, action_key="anlegen", entity_type="webshop_config", entity_id="neu", tenant_id=tenant_id, body=body,
        check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="webshop.config.created")


@router.post("/konfigurationen/{entity_id}/actions/entfernen", response_model=MaskActionResult,
             summary="Shop-Anbindung entfernen", dependencies=SCHREIBEN["VERKAUF"])
async def anbindung_entfernen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                              db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                              nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        da = session.execute(text("SELECT 1 FROM domain_shared.webshop_configs WHERE tenant_id = :t AND id::text = :i"),
                             {"t": tid, "i": eid}).scalar()
        return [] if da else _blockiert("Shop-Anbindung nicht gefunden.")

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        _dienst(session, tid).delete_configuration(eid)
        return "Shop-Anbindung entfernt."

    return await run_delegated_mask_action(
        db, action_key="entfernen", entity_type="webshop_config", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="webshop.config.deleted",
        require_audit_reason=True)


def _bestellnummer(session: Session, tid: str, kennung: str) -> str | None:
    return session.execute(text(
        "SELECT externe_bestellnr FROM domain_shared.webshop_bestellungen WHERE tenant_id = :t "
        "AND (id::text = :k OR externe_bestellnr = :k) LIMIT 1"), {"t": tid, "k": kennung}).scalar()


@router.post("/bestellungen/{entity_id}/actions/verarbeiten", response_model=MaskActionResult,
             summary="Webshop-Bestellung als DocFlow-Auftragsentwurf anlegen", dependencies=SCHREIBEN["VERKAUF"])
async def bestellung_verarbeiten(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                 db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                                 nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    gepruefter_akteur(nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        nummer = _bestellnummer(session, tid, eid)
        if nummer is None:
            return _blockiert("Webshop-Bestellung nicht gefunden.")
        bestellung = _dienst(session, tid).get_order(nummer) or {}
        if bestellung.get("erp_order_number"):
            return _blockiert(f"Bestellung ist bereits Auftrag {bestellung['erp_order_number']}.")
        if bestellung.get("blockers"):
            return _blockiert("Bestellung hat Blocker: " + ", ".join(bestellung["blockers"]))
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        ergebnis = _dienst(session, tid).process_order(_bestellnummer(session, tid, eid))
        if not ergebnis.get("verarbeitet"):
            # Blocker, die erst die Verarbeitung findet (Kunde zur E-Mail, Steuerschluessel): ablehnen, nichts buchen.
            raise ValueError("Nicht verarbeitet: " + ", ".join(ergebnis.get("blockers") or [ergebnis.get("hinweis")]))
        return f"Auftragsentwurf {ergebnis['auftrag_nr']} in DocFlow angelegt."

    return await run_delegated_mask_action(
        db, action_key="verarbeiten", entity_type="webshop_bestellung", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="webshop.bestellung.verarbeitet")
