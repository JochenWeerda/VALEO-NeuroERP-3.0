"""
Export Router
API-Endpoints für CSV/XLSX-Export
"""

from __future__ import annotations
from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Dict, List
import pandas as pd
import logging
import time

from app.auth.deps import require_roles, get_current_user, User
from app.auth.guards import require_scopes
from app.core.sse import sse_hub

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["export"])

# Mock DB (TODO: durch echte DB ersetzen)
_DB: Dict[str, dict] = {}


@router.get("/{domain}")
async def export_documents(
    domain: str,
    from_date: str = Query(""),
    to_date: str = Query(""),
    fmt: str = Query("csv"),
    user: dict = Depends(require_scopes("docs:export")),
) -> FileResponse:
    """
    Exportiert Belege als CSV/XLSX

    Args:
        domain: Belegtyp (z.B. "sales_order")
        from_date: Start-Datum (YYYY-MM-DD)
        to_date: End-Datum (YYYY-MM-DD)
        fmt: Format (csv oder xlsx)

    Returns:
        Export-Datei
    """
    try:
        # Filter documents (TODO: echte Filterung)
        docs = list(_DB.values())

        # Flatten für Export
        rows = []
        for doc in docs:
            lines = doc.get("lines", [])
            total = sum(l.get("qty", 0) * l.get("price", 0) for l in lines)

            row = {
                "Belegnummer": doc.get("number", ""),
                "Datum": doc.get("date", ""),
                "Kunde": doc.get("customerId", ""),
                "Positionen": len(lines),
                "Gesamt": round(total, 2),
            }
            rows.append(row)

        # Export
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        output_path = temp_dir / f"export_{domain}.{fmt}"

        df = pd.DataFrame(rows)

        if fmt == "xlsx":
            df.to_excel(output_path, index=False, engine="openpyxl")
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            df.to_csv(output_path, index=False)
            media_type = "text/csv"

        # Audit-Logging für Export
        logger.info(f"User {user.get('sub', 'unknown')} exported {len(rows)} {domain} documents as {fmt}")

        # SSE Broadcast für Export-Audit
        import asyncio
        asyncio.create_task(sse_hub.broadcast("audit", {
            "id": f"export-{domain}-{int(time.time())}",
            "ts": time.time(),
            "source": "mcp",
            "topic": "audit",
            "type": "export",
            "user": user.get('sub', 'unknown'),
            "domain": domain,
            "format": fmt,
            "count": len(rows),
            "filename": f"{domain}_export.{fmt}",
        }))

        return FileResponse(
            output_path, media_type=media_type, filename=f"{domain}_export.{fmt}"
        )
    except Exception as e:
        logger.error(f"Failed to export: {e}")
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=str(e))

