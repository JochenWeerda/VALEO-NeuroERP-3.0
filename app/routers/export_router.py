"""
Export Router
API-Endpoints für CSV/XLSX-Export
"""

from __future__ import annotations
from fastapi import APIRouter, Query, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import pandas as pd
import logging
import re
import time

from app.auth.guards import require_scopes
from app.core.sse import sse_hub
from app.repositories.document_repository import DocumentRepository
from app.core.dependency_container import container

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["export"])

_SAFE_SLUG_RE = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")


def _safe_slug(value: str, *, field_name: str) -> str:
    if not _SAFE_SLUG_RE.fullmatch(value):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")
    return value


@router.get("/{domain}")
async def export_documents(
    domain: str,
    from_date: str = Query(""),
    to_date: str = Query(""),
    fmt: str = Query("csv"),
    tenant_id: str = Query("system", description="Tenant ID"),
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
        # Get DocumentRepository from container
        doc_repo = container.resolve(DocumentRepository)

        from datetime import datetime
        docs = []

        list_kwargs: dict = {"limit": 5000}
        if hasattr(doc_repo, "list_by_type_and_date") and from_date and to_date:
            all_docs = doc_repo.list_by_type_and_date(domain, from_date=from_date, to_date=to_date, **list_kwargs)
        else:
            all_docs = doc_repo.list_by_type(domain, **list_kwargs)

        # Filter by date if provided
        for doc_header in all_docs:
            doc_dict = doc_repo.to_dict(doc_header)

            # Date filtering
            if from_date or to_date:
                doc_date = doc_dict.get("date")
                if doc_date:
                    try:
                        doc_date_obj = datetime.fromisoformat(doc_date).date()
                        if from_date:
                            from_date_obj = datetime.fromisoformat(from_date).date()
                            if doc_date_obj < from_date_obj:
                                continue
                        if to_date:
                            to_date_obj = datetime.fromisoformat(to_date).date()
                            if doc_date_obj > to_date_obj:
                                continue
                    except (ValueError, TypeError):
                        pass  # Skip date filtering if date parsing fails

            docs.append(doc_dict)

        # Flatten für Export
        rows = []
        for doc in docs:
            lines = doc.get("lines", [])
            total = sum(line_item.get("qty", 0) * line_item.get("price", 0) for line_item in lines)

            row = {
                "Belegnummer": doc.get("number", ""),
                "Datum": doc.get("date", ""),
                "Kunde": doc.get("customerId", ""),
                "Positionen": len(lines),
                "Gesamt": round(total, 2),
            }
            rows.append(row)

        domain_slug = _safe_slug(domain, field_name="domain")
        fmt_slug = _safe_slug(fmt.lower(), field_name="format")
        if fmt_slug not in {"csv", "xlsx"}:
            from fastapi import HTTPException

            raise HTTPException(status_code=400, detail="Invalid format")

        # Export
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        output_path = temp_dir / f"export_{domain_slug}.{fmt_slug}"

        df = pd.DataFrame(rows)

        if fmt_slug == "xlsx":
            df.to_excel(output_path, index=False, engine="openpyxl")
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            df.to_csv(output_path, index=False)
            media_type = "text/csv"

        # Audit-Logging für Export
        logger.info(f"User {user.get('sub', 'unknown')} exported {len(rows)} {domain_slug} documents as {fmt_slug}")

        # SSE Broadcast für Export-Audit
        import asyncio
        asyncio.create_task(sse_hub.broadcast("audit", {
            "id": f"export-{domain}-{int(time.time())}",
            "ts": time.time(),
            "source": "mcp",
            "topic": "audit",
            "type": "export",
            "user": user.get('sub', 'unknown'),
            "domain": domain_slug,
            "format": fmt_slug,
            "count": len(rows),
            "filename": f"{domain_slug}_export.{fmt_slug}",
        }))

        return FileResponse(  # NOSONAR - output_path is built from a fixed temp dir and validated slugs.
            output_path, media_type=media_type, filename=f"{domain_slug}_export.{fmt_slug}"
        )
    except Exception as e:
        logger.error(f"Failed to export: {e}")
        from fastapi import HTTPException  # noqa: F811

        raise HTTPException(status_code=500, detail=str(e))

