"""Zeilenaktionen der Agrar- und Futtermittel-Stammdatenlisten als Fachaktion fuer Maske, CLI und MCP.

MASK-STUDIO-ROLLOUT, Welle 1.

Deaktivieren ist im Fachweg ``DELETE /agrar/duenger/{id}`` ein weiches Loeschen (``ist_aktiv = false``). Hier mit
Begruendung, Audit, Trockenlauf und Wiederholungsschutz von ``statusaktion``; ein schon inaktiver Duenger wird
abgewiesen statt still erneut "geloescht".
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult
from app.services.mask_commands import statusaktion

router = APIRouter(tags=["mask-actions"])

_DUENGER_STATUS = ("SELECT CASE WHEN coalesce(ist_aktiv, true) THEN 'AKTIV' ELSE 'INAKTIV' END AS status "
                   "FROM domain_agrar.agrar_duenger WHERE id = :id AND tenant_id = :tid")


@router.post("/agrar/duenger/{entity_id}/actions/deaktivieren", response_model=MaskActionResult,
             summary="Duenger mit Begruendung deaktivieren", dependencies=SCHREIBEN["AGRAR"])
async def duenger_deaktivieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                               db: Session = Depends(get_db),
                               tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        session.execute(text("UPDATE domain_agrar.agrar_duenger SET ist_aktiv = false, updated_at = now() "
                             "WHERE id = :id AND tenant_id = :tid"), {"id": entity_id, "tid": tenant_id})
        return "Duenger deaktiviert."

    return await statusaktion(
        db, action_key="deaktivieren", entity_type="duenger", entity_id=entity_id, tenant_id=tenant_id, body=body,
        status_sql=_DUENGER_STATUS, erlaubt={"AKTIV"}, ausfuehren=ausfuehren, event_type="agrar.duenger.deaktiviert",
        begruendung_pflicht=True)


_EINZEL_STATUS = ("SELECT CASE WHEN coalesce(aktiv, true) THEN 'AKTIV' ELSE 'INAKTIV' END AS status "
                  "FROM domain_shared.futtermittel_einzelfutter WHERE id::text = :id AND tenant_id = :tid")
_MISCH_STATUS = ("SELECT CASE WHEN coalesce(aktiv, true) THEN 'AKTIV' ELSE 'INAKTIV' END AS status "
                 "FROM domain_shared.futtermittel_mischfutter WHERE id::text = :id AND tenant_id = :tid")


@router.post("/futter/einzelfuttermittel/{entity_id}/actions/stilllegen", response_model=MaskActionResult,
             summary="Einzelfuttermittel im Futterkatalog stilllegen", dependencies=SCHREIBEN["FUTTERMITTEL"])
async def einzelfutter_stilllegen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                  db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                                  nutzer: dict = Depends(get_current_user)) -> MaskActionResult:
    from app.services.feeding_feed_catalog_service import FeedingFeedCatalogService
    from app.services.mask_commands import begruendung

    grund = begruendung(body)

    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        katalog = FeedingFeedCatalogService(session, tenant_id, str(nutzer.get("sub") or "unknown"))
        aktuell = katalog.get_feed(entity_id)
        katalog.update_feed(entity_id, {"expected_revision": aktuell["revision"], "reason": grund,
                                        "aktiv": False, "approval_status": "retired"})
        return "Einzelfuttermittel stillgelegt."

    # Wie DELETE /futter/einzelfuttermittel/{id}: neue Revision im Katalog, kein Loeschen.
    return await statusaktion(
        db, action_key="stilllegen", entity_type="einzelfuttermittel", entity_id=entity_id, tenant_id=tenant_id,
        body=body, status_sql=_EINZEL_STATUS, erlaubt={"AKTIV"}, ausfuehren=ausfuehren,
        event_type="futtermittel.einzelfutter.stillgelegt", begruendung_pflicht=True)


@router.post("/futter/mischfuttermittel/{entity_id}/actions/deaktivieren", response_model=MaskActionResult,
             summary="Mischfuttermittel mit Begruendung deaktivieren", dependencies=SCHREIBEN["FUTTERMITTEL"])
async def mischfutter_deaktivieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                   db: Session = Depends(get_db),
                                   tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        session.execute(text("UPDATE domain_shared.futtermittel_mischfutter SET aktiv = false "
                             "WHERE id::text = :id AND tenant_id = :tid"), {"id": entity_id, "tid": tenant_id})
        return "Mischfuttermittel deaktiviert."

    return await statusaktion(
        db, action_key="deaktivieren", entity_type="mischfuttermittel", entity_id=entity_id, tenant_id=tenant_id,
        body=body, status_sql=_MISCH_STATUS, erlaubt={"AKTIV"}, ausfuehren=ausfuehren,
        event_type="futtermittel.mischfutter.deaktiviert", begruendung_pflicht=True)
