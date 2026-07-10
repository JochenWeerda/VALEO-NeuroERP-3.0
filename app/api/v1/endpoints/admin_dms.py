"""
Admin DMS Endpoints
Konfigurationsstatus, Verbindungstest und Bootstrap für die Mayan-DMS-Integration.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import AnyHttpUrl, BaseModel

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema, StatusResponse


router = APIRouter(prefix="/admin/dms")

def _workspace_path(relative_path: str) -> Path:
    path = (Path.cwd() / relative_path).resolve()
    cwd = Path.cwd().resolve()
    if path != cwd and cwd not in path.parents:
        raise RuntimeError(f"Runtime path must stay inside the working directory: {relative_path}")
    return path


# Pfad zur DMS-Konfigurationsdatei (identisch mit dms_client.py)
_CONFIG_PATH = _workspace_path("data/config/dms.json")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class DmsStatusResponse(BaseModel):
    ok: bool
    configured: bool
    base: Optional[str] = None
    document_types: Optional[List[str]] = None
    metadata_types: Optional[List[str]] = None
    message: Optional[str] = None


class DmsConnectionRequest(BaseModel):
    base: AnyHttpUrl
    token: str


class DmsTestResponse(BaseModel):
    ok: bool
    error: Optional[str] = None


class DmsBootstrapResponse(BaseModel):
    ok: bool
    created: Optional[int] = None
    updated: Optional[int] = None
    message: Optional[str] = None
    document_types: Optional[List[str]] = None
    metadata_types: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_config() -> Dict[str, Any]:
    if _CONFIG_PATH.exists():
        try:
            return json.loads(_CONFIG_PATH.read_text())
        except Exception as exc:
            logger.warning("Failed to read DMS config: %s", exc)
    return {}


def _is_configured() -> bool:
    token = os.environ.get("DMS_TOKEN") or ""
    cfg = _load_config()
    base = os.environ.get("DMS_BASE") or cfg.get("base") or ""
    return bool(token and base)


def _make_client(base: AnyHttpUrl | str, token: str) -> httpx.Client:
    normalized_base = str(base).rstrip("/")
    return httpx.Client(
        base_url=normalized_base,  # NOSONAR - validated as AnyHttpUrl before constructing the client.
        headers={"Authorization": f"Token {token}"},
        timeout=15.0,
    )


# ---------------------------------------------------------------------------
# Mayan document-type and metadata bootstrap definitions
# ---------------------------------------------------------------------------

_DOCUMENT_TYPES = [
    "Eingangsrechnung",
    "Ausgangsrechnung",
    "Lieferschein",
    "Kontrakt",
    "Qualitätsprotokoll",
    "Angebot",
    "Bestellung",
    "Gutschrift",
    "Sonstiges",
]

_METADATA_TYPES = [
    "invoice_number",
    "supplier",
    "date",
    "total",
    "customer_id",
    "supplier_id",
    "domain",
]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/status", response_model=DmsStatusResponse, tags=["admin", "dms"], summary="Dms status abrufen")
async def get_dms_status():
    """Gibt den aktuellen DMS-Konfigurationsstatus zurück."""
    cfg = _load_config()
    token = os.environ.get("DMS_TOKEN") or ""
    base = os.environ.get("DMS_BASE") or cfg.get("base") or ""
    configured = bool(token and base)

    doc_types = list(cfg.get("document_types", {}).keys()) or None
    meta_types = list(cfg.get("metadata_types", {}).keys()) or None

    return DmsStatusResponse(
        ok=True,
        configured=configured,
        base=base if configured else None,
        document_types=doc_types,
        metadata_types=meta_types,
        message=None if configured else "DMS nicht konfiguriert — DMS_TOKEN und DMS_BASE setzen oder Bootstrap ausführen.",
    )


@router.post("/test", response_model=DmsTestResponse, tags=["admin", "dms"], summary="Dms connection testen")
async def test_dms_connection(body: DmsConnectionRequest):
    """Testet die Verbindung zu Mayan-DMS mit den angegebenen Credentials."""
    try:
        with _make_client(body.base, body.token) as client:
            response = client.get("/api/documents/document_types/")
            response.raise_for_status()
        return DmsTestResponse(ok=True)
    except httpx.HTTPStatusError as exc:
        logger.warning("DMS connection test failed (HTTP %s): %s", exc.response.status_code, exc)
        return DmsTestResponse(ok=False, error=f"HTTP {exc.response.status_code}: {exc.response.text[:200]}")
    except httpx.RequestError as exc:
        logger.warning("DMS connection test request error: %s", exc)
        return DmsTestResponse(ok=False, error=f"Verbindungsfehler: {exc}")
    except Exception as exc:
        logger.error("DMS connection test unexpected error: %s", exc)
        return DmsTestResponse(ok=False, error=str(exc))


@router.post("/bootstrap", response_model=DmsBootstrapResponse, tags=["admin", "dms"], summary="Dms bootstrap")
async def bootstrap_dms(body: DmsConnectionRequest):
    """
    Erstellt oder aktualisiert Dokumenttypen und Metadatenfelder in Mayan-DMS
    und speichert die IDs in der lokalen Konfiguration.
    """
    created = 0
    updated = 0
    doc_type_ids: Dict[str, int] = {}
    meta_type_ids: Dict[str, int] = {}

    try:
        with _make_client(body.base, body.token) as client:
            # --- Dokumenttypen ---
            existing_types_resp = client.get("/api/documents/document_types/")
            existing_types_resp.raise_for_status()
            existing_types = {
                dt["label"]: dt["id"]
                for dt in existing_types_resp.json().get("results", [])
            }

            for label in _DOCUMENT_TYPES:
                if label in existing_types:
                    doc_type_ids[label] = existing_types[label]
                    updated += 1
                else:
                    resp = client.post(
                        "/api/documents/document_types/",
                        json={"label": label},
                    )
                    resp.raise_for_status()
                    doc_type_ids[label] = resp.json()["id"]
                    created += 1

            # --- Metadatenfelder ---
            existing_meta_resp = client.get("/api/metadata/metadata_types/")
            existing_meta_resp.raise_for_status()
            existing_meta = {
                mt["name"]: mt["id"]
                for mt in existing_meta_resp.json().get("results", [])
            }

            for name in _METADATA_TYPES:
                if name in existing_meta:
                    meta_type_ids[name] = existing_meta[name]
                    updated += 1
                else:
                    resp = client.post(
                        "/api/metadata/metadata_types/",
                        json={"name": name, "label": name},
                    )
                    resp.raise_for_status()
                    meta_type_ids[name] = resp.json()["id"]
                    created += 1

    except httpx.HTTPStatusError as exc:
        logger.error("DMS bootstrap HTTP error %s: %s", exc.response.status_code, exc)
        raise HTTPException(
            status_code=502,
            detail=f"Mayan-DMS antwortete mit HTTP {exc.response.status_code}: {exc.response.text[:300]}",
        )
    except httpx.RequestError as exc:
        logger.error("DMS bootstrap request error: %s", exc)
        raise HTTPException(status_code=502, detail=f"Verbindungsfehler zu Mayan-DMS: {exc}")
    except Exception as exc:
        logger.error("DMS bootstrap unexpected error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    # Konfiguration lokal speichern
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = _load_config()
    config["base"] = str(body.base)
    config["document_types"] = doc_type_ids
    config["metadata_types"] = meta_type_ids
    try:
        _CONFIG_PATH.write_text(  # NOSONAR - _CONFIG_PATH is anchored under the working directory.
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.error("Failed to write DMS config: %s", exc)
        raise HTTPException(status_code=500, detail=f"Konfiguration konnte nicht gespeichert werden: {exc}")

    logger.info(
        "DMS bootstrap complete: %d created, %d updated, %d doc_types, %d meta_types",
        created, updated, len(doc_type_ids), len(meta_type_ids),
    )

    return DmsBootstrapResponse(
        ok=True,
        created=created,
        updated=updated,
        message=f"Bootstrap abgeschlossen: {created} erstellt, {updated} aktualisiert.",
        document_types=list(doc_type_ids.keys()),
        metadata_types=list(meta_type_ids.keys()),
    )
