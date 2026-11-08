"""
DMS Webhook Router
Empfängt Webhooks von Mayan-DMS für eingehende Dokumente.
Inbox wird in DB persistiert (domain_shared.dms_inbox).

Mandant kommt nur aus dem serverseitig verifizierten Claim
(``get_tenant_id`` / BearerAuth), nie aus einem frei wählbaren Payload-Feld.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.auth.bereich_roles import SCHREIBEN
from app.auth.finance_roles import beleg_read
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.documents.dms_inbox_model import (
    DmsInboxEntry,
    booking_not_from_inbox,
    inbox_id_for_document,
    require_connector_tenant,
    verified_inbox_tenant,
)
from app.integrations.dms_client import get_client, is_configured
from app.integrations.dms_parser import parser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dms", tags=["dms"])


class WebhookPayload(BaseModel):
    event: str
    document_id: int = Field(gt=0)
    document_type: Optional[str] = None
    user: Optional[str] = None


@router.post("/webhook", dependencies=SCHREIBEN["BELEGE"])
async def handle_webhook(
    payload: WebhookPayload,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Webhook-Handler für Mayan-DMS-Events."""
    mandant = require_connector_tenant(tenant_id)
    if not is_configured():
        raise HTTPException(status_code=503, detail="DMS connector is not configured")

    try:
        logger.info(
            "Received DMS webhook: %s for document %s tenant=%s",
            payload.event,
            payload.document_id,
            mandant,
        )

        if payload.event in ("document.created", "document.ocr.finished"):
            await _process_incoming_document(payload.document_id, db, mandant)

        return {"ok": True, "message": "Webhook processed"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Webhook processing failed: %s", e)
        raise HTTPException(status_code=502, detail="DMS webhook processing failed") from e


async def _process_incoming_document(document_id: int, db: Session, tenant_id: str):
    require_connector_tenant(tenant_id)
    if not is_configured():
        raise HTTPException(status_code=503, detail="DMS connector is not configured")

    try:
        pdf_bytes = None
        version_id = None
        with get_client() as client:
            response = client.get(f"/api/documents/documents/{document_id}/versions/")
            response.raise_for_status()
            versions = response.json()["results"]

            if not versions:
                raise HTTPException(status_code=502, detail="DMS document has no version")

            version_id = versions[0]["id"]
            ocr_response = client.get(
                f"/api/documents/documents/{document_id}/versions/{version_id}/ocr_content/"
            )
            ocr_response.raise_for_status()
            ocr_text = ocr_response.text

            # Best-effort PDF fuer Claude-Vision (EINKAUF_OCR_ENGINE=claude).
            from app.documents.position_extraction import try_fetch_mayan_pdf

            pdf_bytes = try_fetch_mayan_pdf(
                client, document_id, version_id, download_url=versions[0].get("download_url")
            )

        parse_result = parser.parse(ocr_text)
        fields = dict(parse_result["fields"] or {})

        # Positionszeilen: Claude hinter bestehendem Flag; ohne Key graceful leer + Gaps.
        from app.documents.position_extraction import enrich_parsed_fields_with_positions

        fields, position_gaps = enrich_parsed_fields_with_positions(
            fields,
            ocr_text,
            pdf_bytes=pdf_bytes,
            item_id=inbox_id_for_document(tenant_id, document_id),
            db=db,
            tenant_id=tenant_id,
        )
        if position_gaps:
            logger.info(
                "DMS inbox position extraction gaps for %s: %s",
                document_id,
                ",".join(position_gaps),
            )

        entry_id = inbox_id_for_document(tenant_id, document_id)
        values = {
            "id": entry_id,
            "dms_document_id": document_id,
            "dms_url": f"http://localhost:8010/documents/{document_id}/",
            "ocr_text": ocr_text[:2000],
            "parsed_fields": fields,
            "confidence": parse_result["confidence"],
            "status": "pending",
            "tenant_id": tenant_id,
        }
        stmt = pg_insert(DmsInboxEntry).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[DmsInboxEntry.id],
            set_={key: values[key] for key in ("dms_url", "ocr_text", "parsed_fields", "confidence")},
            where=(DmsInboxEntry.tenant_id == tenant_id)
            & (DmsInboxEntry.dms_document_id == document_id),
        ).returning(DmsInboxEntry.status)
        status = db.execute(stmt).scalar_one_or_none()
        if status is None:
            raise HTTPException(status_code=409, detail="DMS inbox identity conflict")
        db.commit()

        logger.info(
            "Incoming document processed: %s tenant=%s confidence=%.2f positions=%s",
            entry_id,
            tenant_id,
            values["confidence"],
            len(fields.get("positionen") or []),
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to process incoming document: %s", e)
        raise


@router.get("/inbox", dependencies=[Depends(beleg_read)])
async def get_inbox(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    """Holt alle Inbox-Dokumente."""
    mandant = verified_inbox_tenant(tenant_id)
    items = db.query(DmsInboxEntry).filter(
        DmsInboxEntry.tenant_id == mandant, DmsInboxEntry.status == "pending"
    ).all()
    return {
        "ok": True,
        "items": [
            {
                "id": i.id,
                "dms_document_id": i.dms_document_id,
                "dms_url": i.dms_url,
                "ocr_text": i.ocr_text,
                "parsed_fields": i.parsed_fields,
                "confidence": i.confidence,
                "status": i.status,
            }
            for i in items
        ],
        "count": len(items),
    }


@router.get("/inbox/{inbox_id}", dependencies=[Depends(beleg_read)])
async def get_inbox_document(
    inbox_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
):
    """Holt einzelnes Inbox-Dokument."""
    mandant = verified_inbox_tenant(tenant_id)
    entry = db.query(DmsInboxEntry).filter(
        DmsInboxEntry.id == inbox_id, DmsInboxEntry.tenant_id == mandant
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Inbox document not found")
    return {"ok": True, "document": {
        "id": entry.id,
        "dms_document_id": entry.dms_document_id,
        "dms_url": entry.dms_url,
        "ocr_text": entry.ocr_text,
        "parsed_fields": entry.parsed_fields,
        "confidence": entry.confidence,
        "status": entry.status,
    }}


@router.post("/inbox/{inbox_id}/create", dependencies=SCHREIBEN["BELEGE"])
async def create_from_inbox(
    inbox_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Block fake booking; the purchase invoice mask owns the domain command."""
    mandant = verified_inbox_tenant(tenant_id)
    entry = db.query(DmsInboxEntry).filter(
        DmsInboxEntry.id == inbox_id, DmsInboxEntry.tenant_id == mandant
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Inbox document not found")
    raise booking_not_from_inbox(inbox_id)


@router.delete("/inbox/{inbox_id}", dependencies=SCHREIBEN["BELEGE"])
async def delete_inbox_document(
    inbox_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
):
    """Löscht Inbox-Dokument (ablehnen/verwerfen)."""
    mandant = verified_inbox_tenant(tenant_id)
    entry = db.query(DmsInboxEntry).filter(
        DmsInboxEntry.id == inbox_id, DmsInboxEntry.tenant_id == mandant
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Inbox document not found")
    db.delete(entry)
    db.commit()
    logger.info("Deleted inbox document: %s", inbox_id)
    return {"ok": True, "message": "Inbox document deleted"}
