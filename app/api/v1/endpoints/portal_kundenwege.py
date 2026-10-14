"""Portalwege des Kundenportals: Uebersicht, Anfragen, Bestellungen, Rechnungen, Unterlagen, Feldbuchliste,
Lieferscheine, Nachhaltigkeitsexport (TENANT-DOC-001, PORTAL-CONTEXT-001).

Bis 14.10.2026 standen diese Wege in ``compat.py``; dort wurden sie ausgelagert, damit die Kundengrenze an einer
Stelle lesbar ist. Pfade, Funktionsnamen und Antwortschemas sind unveraendert.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1.endpoints.compat import PortalOut
from app.api.v1.schemas.base import CompatBridgeOut
from app.auth.portal_kunde import (
    AUSWERTUNGEN, FELDBUCH_LESEN, FINANZEN, KONTRAKTE, UEBERSICHT, VERKAUF, PortalKunde, portal_recht,
)
from app.core.database import get_db
from app.services.portal_compat_service import PortalCompatService

router = APIRouter(tags=["compat"])


# Mandant und Kundenkonto kommen aus ``portal_kunde`` (Anmeldung + gepruefte Zuordnung, TENANT-DOC-001). Bis
# 14.10.2026 sah jede angemeldete Person hier die Belege aller Kunden des Mandanten; ``/portal/feldbuch`` nahm den
# Kunden aus dem Parameter ``customer_id``. Welche Wege eine Portalrolle sieht, bestimmt ``PORTAL_RECHTE``
# (PORTAL-CONTEXT-001).


def _portal(db: Session, kunde: PortalKunde) -> PortalCompatService:
    return PortalCompatService(db, kunde.tenant_id, kunde.customer_id)


@router.get("/portal/dashboard", response_model=PortalOut, summary="Dashboard portal")
async def portal_dashboard(
    kunde: PortalKunde = Depends(portal_recht(UEBERSICHT)), db: Session = Depends(get_db)
) -> dict:
    return _portal(db, kunde).get_portal_dashboard_full(kunde.rechte)


@router.get("/portal/anfragen", response_model=list[CompatBridgeOut], summary="Anfragen portal")
async def portal_anfragen(
    kunde: PortalKunde = Depends(portal_recht(VERKAUF)), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return _portal(db, kunde).list_portal_anfragen()


@router.get("/portal/bestellungen", response_model=list[CompatBridgeOut], summary="Bestellungen portal")
async def portal_bestellungen(
    kunde: PortalKunde = Depends(portal_recht(VERKAUF)), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return _portal(db, kunde).list_portal_bestellungen()


@router.get("/portal/dokumente", response_model=list[CompatBridgeOut], summary="Dokumente portal")
async def portal_dokumente(
    kunde: PortalKunde = Depends(portal_recht(FINANZEN)), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return _portal(db, kunde).list_portal_dokumente()


@router.get("/portal/feldbuch", response_model=list[CompatBridgeOut], summary="Feldbuch portal")
async def portal_feldbuch(
    kunde: PortalKunde = Depends(portal_recht(FELDBUCH_LESEN)), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return _portal(db, kunde).list_portal_feldbuch(kunde.schlag_ids)


@router.get("/portal/naehrstoffbilanzen", response_model=list[CompatBridgeOut], summary="Naehrstoffbilanzen portal")
async def portal_naehrstoffbilanzen(
    kunde: PortalKunde = Depends(portal_recht(AUSWERTUNGEN)), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return _portal(db, kunde).list_portal_naehrstoffbilanzen()


@router.get("/portal/rechnungen", response_model=list[CompatBridgeOut], summary="Rechnungen portal")
async def portal_rechnungen(
    kunde: PortalKunde = Depends(portal_recht(FINANZEN)), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return _portal(db, kunde).list_portal_rechnungen()


@router.get("/portal/shop", response_model=list[CompatBridgeOut], summary="Shop portal")
async def portal_shop(
    kunde: PortalKunde = Depends(portal_recht(VERKAUF)), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return _portal(db, kunde).list_portal_shop()


@router.get("/portal/vertraege", response_model=list[CompatBridgeOut], summary="Vertraege portal")
async def portal_vertraege(
    kunde: PortalKunde = Depends(portal_recht(KONTRAKTE)), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return _portal(db, kunde).list_portal_vertraege()


@router.get("/portal/zertifikate", response_model=list[CompatBridgeOut], summary="Zertifikate portal")
async def portal_zertifikate(
    kunde: PortalKunde = Depends(portal_recht(AUSWERTUNGEN)), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return _portal(db, kunde).list_portal_zertifikate()


@router.get("/portal/lieferscheine", response_model=CompatBridgeOut, summary="Lieferscheine des Kundenkontos")
async def portal_lieferscheine(
    kunde: PortalKunde = Depends(portal_recht(VERKAUF, FINANZEN)), db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Bis 14.10.2026 las das Portal die Lieferscheine ueber den internen Belegrouter — alle Kunden des Mandanten."""
    return {"ok": True, "data": _portal(db, kunde)._kundenbelege("sales_delivery", 1000)}


@router.get("/portal/nachhaltigkeit/export.csv", response_class=StreamingResponse,
            summary="Naehrstoff- und CO2e-Auswertung des Kundenkontos als CSV")
async def portal_nachhaltigkeit_csv(
    year: int = Query(..., ge=2000, le=2100),
    kunde: PortalKunde = Depends(portal_recht(AUSWERTUNGEN)),
    db: Session = Depends(get_db),
):
    from app.documents.router import export_sales_delivery_sustainability_csv

    return await export_sales_delivery_sustainability_csv(
        year=year, customer_id=kunde.customer_id, db=db, tenant_id=kunde.tenant_id)


@router.get("/portal/nachhaltigkeit/export.pdf", response_class=StreamingResponse,
            summary="Naehrstoff- und CO2e-Auswertung des Kundenkontos als PDF")
async def portal_nachhaltigkeit_pdf(
    year: int = Query(..., ge=2000, le=2100),
    kunde: PortalKunde = Depends(portal_recht(AUSWERTUNGEN)),
    db: Session = Depends(get_db),
):
    from app.documents.router import export_sales_delivery_sustainability_pdf

    return await export_sales_delivery_sustainability_pdf(
        year=year, customer_id=kunde.customer_id, db=db, tenant_id=kunde.tenant_id)
