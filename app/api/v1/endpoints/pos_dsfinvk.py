"""Compatibility endpoints for provider-backed DSFinV-K exports.

The former implementation emitted fixed demonstration rows. It is deliberately
replaced by the canonical fiscalization provider service.
"""
from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.fiscalization.contracts import ExportCommand
from app.services.fiscalization.providers import FiscalProviderError
from app.services.fiscalization.service import FiscalizationService


router = APIRouter()


@router.get("/dsfinvk/export", summary="Providergestuetzten DSFinV-K-Export anfordern")
async def dsfinvk_export(
    period_from: date | None = Query(default=None),
    period_to: date | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    service = FiscalizationService(db, tenant_id)
    config = service.get_config()
    if not config.get("cash_register_id"):
        raise HTTPException(status_code=409, detail="Fiskalisierungsprovider ist nicht konfiguriert")
    target_to = period_to or date.today()
    target_from = period_from or target_to
    try:
        result = service.request_export(
            ExportCommand(
                export_id=str(uuid4()),
                cash_register_id=config["cash_register_id"],
                period_from=target_from,
                period_to=target_to,
                export_type="dsfinvk",
            )
        )
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if result.download_url:
        return RedirectResponse(result.download_url, status_code=303)
    return result


@router.get("/dsfinvk/status", response_model=dict, summary="Providergestuetzten DSFinV-K-Status abrufen")
async def dsfinvk_status(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    service = FiscalizationService(db, tenant_id)
    readiness = service.readiness()
    latest = db.execute(
        text(
            """
            SELECT export_id, status, period_from, period_to, download_url, simulated, created_at
            FROM domain_docflow.pos_fiscal_exports
            WHERE tenant_id = :tenant_id AND export_type = 'dsfinvk'
            ORDER BY created_at DESC
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id},
    ).mappings().first()
    return {
        "status": "bereit" if readiness["dsfinvk"]["ready"] else "blockiert",
        "taxonomie_version": "provider-managed",
        "letzter_export": latest["created_at"].date().isoformat() if latest else None,
        "letzter_export_dateiname": latest["export_id"] if latest else None,
        "kasse_id": service.get_config().get("cash_register_id") or "",
        "hinweis": (
            "DSFinV-K wird ueber den konfigurierten Provider erzeugt. "
            "TSE-Export und DSFinV-K-Export sind getrennte Artefakte."
        ),
        "readiness": readiness["dsfinvk"],
        "latest": dict(latest) if latest else None,
    }
