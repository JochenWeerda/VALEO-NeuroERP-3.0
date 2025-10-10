"""
Print Router
API-Endpoints für PDF-Generierung und Archivierung
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Dict, Any
import logging

from app.services.pdf_service import generator
from app.services.archive_service import archive
from app.services.workflow_service import workflow
from app.routers.workflow_router import _STATE
from app.integrations.dms_client import upload_document, is_configured as is_dms_configured

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["print"])

# Mock DB (TODO: durch echte DB ersetzen)
_DB: Dict[str, dict] = {}


@router.get("/{domain}/{doc_id}/print")
async def print_document(domain: str, doc_id: str) -> FileResponse:
    """
    Generiert PDF für Beleg

    Args:
        domain: Belegtyp (z.B. "sales_order")
        doc_id: Beleg-ID

    Returns:
        PDF-Datei als FileResponse
    """
    try:
        # Beleg aus DB holen
        doc = _DB.get(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Workflow-Status holen
        workflow_status = _STATE.get((domain, doc_id), "draft")

        # PDF generieren
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = temp_dir / f"{doc_id}.pdf"

        generator.render_document(domain, doc, str(pdf_path), workflow_status)

        # Archivieren
        archive.archive(domain, doc_id, str(pdf_path), user="system")

        # Optional: Upload to Mayan-DMS (falls konfiguriert)
        if is_dms_configured():
            try:
                metadata = {
                    "number": doc_id,
                    "domain": domain,
                    "status": workflow_status,
                    "date": doc.get("date", ""),
                    "customerId": doc.get("customer_id", ""),
                }
                dms_result = upload_document(domain, doc_id, str(pdf_path), metadata)
                if dms_result.get("ok"):
                    logger.info(f"Uploaded to DMS: {doc_id} → {dms_result.get('document_id')}")
            except Exception as e:
                logger.warning(f"DMS upload failed (non-critical): {e}")

        logger.info(f"Generated and archived PDF for {doc_id}")

        return FileResponse(
            pdf_path, media_type="application/pdf", filename=f"{doc_id}.pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{domain}/{doc_id}/history")
async def get_document_history(domain: str, doc_id: str) -> Dict[str, Any]:
    """
    Holt Archiv-Historie für Beleg

    Args:
        domain: Belegtyp
        doc_id: Beleg-ID

    Returns:
        Liste von Archiv-Einträgen
    """
    try:
        history = archive.get_history(doc_id)
        return {"ok": True, "items": history}
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{domain}/{doc_id}/verify/{archive_path:path}")
async def verify_archive(
    domain: str, doc_id: str, archive_path: str
) -> Dict[str, Any]:
    """
    Verifiziert Integrität einer archivierten Datei

    Args:
        domain: Belegtyp
        doc_id: Beleg-ID
        archive_path: Pfad zur archivierten Datei

    Returns:
        Verifikations-Status
    """
    try:
        is_valid = archive.verify_integrity(doc_id, archive_path)
        return {"ok": True, "valid": is_valid}
    except Exception as e:
        logger.error(f"Failed to verify archive: {e}")
        raise HTTPException(status_code=500, detail=str(e))

