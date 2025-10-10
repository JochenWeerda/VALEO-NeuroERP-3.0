"""
Admin DMS Router
Mayan-DMS-Integration für Admin-Benutzer
"""

from __future__ import annotations
from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import BaseModel, AnyHttpUrl, Field
import httpx
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

from app.auth.guards import require_all_scopes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/dms", tags=["admin:dms"])

CONFIG_PATH = Path("data/config/dms.json")
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


class DmsConn(BaseModel):
    """DMS-Verbindungs-Konfiguration"""
    base: AnyHttpUrl
    token: str = Field(min_length=8)


def _cli(base: str, token: str) -> httpx.Client:
    """Erstellt httpx-Client für Mayan-API"""
    return httpx.Client(
        base_url=base,
        headers={"Authorization": f"Token {token}"},
        timeout=15.0
    )


# VALEO-Preset: Document Types
DOCUMENT_TYPES = [
    "sales_order",
    "delivery",
    "invoice",
    "purchase_order",
    "goods_receipt",
    "supplier_invoice",
    "contract"
]

# VALEO-Preset: Metadata Fields
METADATA = [
    {"name": "number", "label": "Number", "type": "text", "required": True},
    {"name": "domain", "label": "Domain", "type": "choice", "choices": ["sales", "purchase", "logistics", "contract"]},
    {"name": "customerId", "label": "Customer", "type": "text"},
    {"name": "supplierId", "label": "Supplier", "type": "text"},
    {"name": "status", "label": "Status", "type": "choice", "choices": ["draft", "pending", "approved", "posted", "rejected"]},
    {"name": "hash", "label": "Hash", "type": "text"},
    {"name": "date", "label": "Date", "type": "date"},
]

# VALEO-Preset: Metadata-Bindings
BINDINGS = {
    "invoice": ["number", "domain", "customerId", "status", "hash", "date"],
    "delivery": ["number", "domain", "customerId", "status", "hash", "date"],
    "sales_order": ["number", "domain", "customerId", "status", "hash", "date"],
    "purchase_order": ["number", "domain", "supplierId", "status", "hash", "date"],
    "goods_receipt": ["number", "domain", "supplierId", "status", "hash", "date"],
    "supplier_invoice": ["number", "domain", "supplierId", "status", "hash", "date"],
    "contract": ["number", "domain", "status", "date", "hash"],
}


def _ensure_doc_types(c: httpx.Client) -> Dict[str, int]:
    """
    Stellt sicher, dass alle Document Types existieren
    
    Returns:
        Mapping: doc_type_name → doc_type_id
    """
    ids: Dict[str, int] = {}
    
    # Hole existierende Document Types
    response = c.get("/api/document_types/document_types/?page_size=1000")
    response.raise_for_status()
    cur = response.json().get("results", [])
    by_label = {x["label"]: x["id"] for x in cur}
    
    # Erstelle fehlende Document Types
    for name in DOCUMENT_TYPES:
        if name not in by_label:
            logger.info(f"Creating document type: {name}")
            r = c.post("/api/document_types/document_types/", json={"label": name})
            r.raise_for_status()
            by_label[name] = r.json()["id"]
        ids[name] = by_label[name]
    
    return ids


def _ensure_metadata(c: httpx.Client) -> Dict[str, int]:
    """
    Stellt sicher, dass alle Metadata Types existieren
    
    Returns:
        Mapping: metadata_name → metadata_id
    """
    ids: Dict[str, int] = {}
    
    # Hole existierende Metadata Types
    response = c.get("/api/metadata/metadata_types/?page_size=1000")
    response.raise_for_status()
    cur = response.json().get("results", [])
    by_name = {x["name"]: x["id"] for x in cur}
    
    # Erstelle fehlende Metadata Types
    for m in METADATA:
        if m["name"] not in by_name:
            logger.info(f"Creating metadata type: {m['name']}")
            body = {k: v for k, v in m.items() if k in ("name", "label", "type")}
            body.update({
                "required": m.get("required", False),
                "choices": m.get("choices", [])
            })
            r = c.post("/api/metadata/metadata_types/", json=body)
            r.raise_for_status()
            by_name[m["name"]] = r.json()["id"]
        ids[m["name"]] = by_name[m["name"]]
    
    return ids


def _ensure_bindings(c: httpx.Client, doc_ids: Dict[str, int], meta_ids: Dict[str, int]) -> int:
    """
    Stellt sicher, dass alle Metadata-Bindings existieren
    
    Returns:
        Anzahl erstellter Bindings
    """
    # Hole existierende Bindings
    response = c.get("/api/metadata/document_type_metadata_types/?page_size=1000")
    response.raise_for_status()
    cur = response.json().get("results", [])
    existing = {(x["document_type"], x["metadata_type"]) for x in cur}
    
    created = 0
    for dt, metas in BINDINGS.items():
        for m in metas:
            tup = (doc_ids[dt], meta_ids[m])
            if tup not in existing:
                logger.info(f"Creating binding: {dt} → {m}")
                r = c.post(
                    "/api/metadata/document_type_metadata_types/",
                    json={"document_type": tup[0], "metadata_type": tup[1]}
                )
                r.raise_for_status()
                created += 1
    
    return created


@router.post("/test")
async def test_connection(
    conn: DmsConn,
    user: dict = Depends(require_all_scopes("admin:all"))
):
    """
    Testet Verbindung zu Mayan-DMS
    
    Args:
        conn: DMS-Verbindungs-Konfiguration (base-URL + token)
    
    Returns:
        Erfolgs-Status
    
    Requires:
        Scope: admin:all
    """
    try:
        with _cli(str(conn.base), conn.token) as c:
            r = c.get("/api/")
            r.raise_for_status()
            
            # Verify we can access document_types endpoint
            r2 = c.get("/api/document_types/document_types/?page_size=1")
            r2.raise_for_status()
        
        logger.info(f"DMS connection test successful: {conn.base}")
        return {"ok": True, "message": "Connection successful"}
    
    except httpx.HTTPStatusError as e:
        logger.error(f"DMS connection test failed (HTTP {e.response.status_code}): {e}")
        return {"ok": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        logger.error(f"DMS connection test failed: {e}")
        return {"ok": False, "error": str(e)}


@router.post("/bootstrap")
async def bootstrap_dms(
    conn: DmsConn,
    user: dict = Depends(require_all_scopes("admin:all"))
):
    """
    Bootstrap Mayan-DMS mit VALEO-NeuroERP-Preset
    
    Erstellt idempotent:
    - Document Types (sales_order, delivery, invoice, etc.)
    - Metadata Types (number, domain, status, etc.)
    - Metadata-Bindings (welche Felder zu welchem DocType)
    
    Args:
        conn: DMS-Verbindungs-Konfiguration
    
    Returns:
        Erfolgs-Status mit Anzahl erstellter Objekte
    
    Requires:
        Scope: admin:all
    """
    try:
        with _cli(str(conn.base), conn.token) as c:
            # 1. Ensure Document Types
            doc_ids = _ensure_doc_types(c)
            logger.info(f"Document types ensured: {len(doc_ids)}")
            
            # 2. Ensure Metadata Types
            meta_ids = _ensure_metadata(c)
            logger.info(f"Metadata types ensured: {len(meta_ids)}")
            
            # 3. Ensure Bindings
            created_bindings = _ensure_bindings(c, doc_ids, meta_ids)
            logger.info(f"Metadata bindings created: {created_bindings}")
        
        # Persist config for ERP adapters
        config_data = {
            "base": str(conn.base),
            "token_set": True,  # Don't store actual token in config
            "document_types": doc_ids,
            "metadata_types": meta_ids,
        }
        CONFIG_PATH.write_text(json.dumps(config_data, indent=2))
        
        logger.info(f"DMS bootstrap completed: {conn.base}")
        
        return {
            "ok": True,
            "created": created_bindings,
            "updated": 0,
            "message": "Mayan bereit für VALEO NeuroERP",
            "document_types": len(doc_ids),
            "metadata_types": len(meta_ids),
        }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"DMS bootstrap failed (HTTP {e.response.status_code}): {e}")
        raise HTTPException(
            status_code=502,
            detail=f"DMS API error: {e.response.status_code} - {e.response.text}"
        )
    except Exception as e:
        logger.error(f"DMS bootstrap failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_dms_status(
    user: dict = Depends(require_all_scopes("admin:all"))
):
    """
    Holt DMS-Status und Konfiguration
    
    Returns:
        DMS-Config und Verbindungs-Status
    
    Requires:
        Scope: admin:all
    """
    if not CONFIG_PATH.exists():
        return {
            "ok": True,
            "configured": False,
            "message": "DMS not configured yet"
        }
    
    try:
        config = json.loads(CONFIG_PATH.read_text())
        return {
            "ok": True,
            "configured": True,
            "base": config.get("base"),
            "document_types": len(config.get("document_types", {})),
            "metadata_types": len(config.get("metadata_types", {})),
        }
    except Exception as e:
        logger.error(f"Failed to read DMS config: {e}")
        return {
            "ok": False,
            "configured": False,
            "error": str(e)
        }

