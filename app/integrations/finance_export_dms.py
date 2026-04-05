"""
Optionales Hochladen von Finance-Follow-up-Exporten nach Mayan-DMS.

Erfordert DMS_TOKEN und typischerweise DMS_DOCUMENT_TYPE_ID (Mayan document_type PK).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def try_upload_finance_csv_to_dms(
    file_path: str,
    *,
    label: str,
) -> dict[str, Any]:
    """
    Laedt eine CSV-Datei als Dokument hoch, falls Konfiguration vorhanden.

    Returns:
        {"ok": bool, "document_id": int | None, "url": str | None, "error": str | None}
    """
    doc_type_id = os.environ.get("DMS_DOCUMENT_TYPE_ID")
    if not doc_type_id:
        return {"ok": False, "document_id": None, "url": None, "error": "DMS_DOCUMENT_TYPE_ID not set"}

    try:
        from app.integrations.dms_client import DMS_BASE, get_client
    except Exception as exc:
        return {"ok": False, "document_id": None, "url": None, "error": str(exc)}

    path = Path(file_path)
    if not path.is_file():
        return {"ok": False, "document_id": None, "url": None, "error": "file not found"}

    try:
        with get_client() as client:
            with open(path, "rb") as f:
                response = client.post(
                    "/api/documents/documents/",
                    files={"file": (label, f, "text/csv")},
                    data={"document_type_id": doc_type_id, "label": label},
                )
            response.raise_for_status()
            body = response.json()
            doc_id = int(body.get("id") or body.get("pk") or 0)
            url = f"{DMS_BASE.rstrip('/')}/documents/{doc_id}/"
            return {"ok": True, "document_id": doc_id, "url": url, "error": None}
    except Exception as exc:
        logger.warning("Finance export DMS upload failed: %s", exc)
        return {"ok": False, "document_id": None, "url": None, "error": str(exc)}
