"""
Numbering Router
API-Endpoints für Nummernkreis-Verwaltung
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from app.services.numbering_service_pg import NumberingServicePG, get_numbering_pg
from app.auth.guards import require_scopes, require_all_scopes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/numbering", tags=["numbering"])


class NextNumberRequest(BaseModel):
    """Request für next_number"""
    domain: str
    tenant_id: str = "default"
    year: Optional[int] = None


class NumberResponse(BaseModel):
    """Response mit generierter Nummer"""
    ok: bool
    number: str


class StatusResponse(BaseModel):
    """Response mit Nummernkreis-Status"""
    ok: bool
    domain: str
    tenant_id: str
    year: Optional[int]
    prefix: str
    counter: int
    next_number: str


@router.post("/next", response_model=NumberResponse)
async def get_next_number(
    req: NextNumberRequest,
    numbering: NumberingServicePG = Depends(get_numbering_pg),
    user: dict = Depends(require_scopes("docs:write", "sales:write", "purchase:write")),
):
    """
    Generiert nächste Belegnummer
    
    Args:
        req: Request mit domain, tenant_id, year
    
    Returns:
        Formatierte Belegnummer
    
    Requires:
        Scope: docs:write, sales:write, oder purchase:write
    """
    try:
        # Auto-Jahr wenn yearly_reset aktiv
        year = req.year
        if year is None:
            import os
            yearly_reset = os.environ.get("NUMBERING_YEARLY_RESET", "false").lower() == "true"
            if yearly_reset:
                year = datetime.now().year
        
        number = await numbering.next_number(req.domain, req.tenant_id, year)
        
        return NumberResponse(ok=True, number=number)
    
    except Exception as e:
        logger.error(f"Failed to generate number: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=StatusResponse)
async def get_numbering_status(
    domain: str,
    tenant_id: str = "default",
    year: Optional[int] = None,
    numbering: NumberingServicePG = Depends(get_numbering_pg),
    user: dict = Depends(require_scopes("docs:read", "sales:read", "purchase:read")),
):
    """
    Gibt aktuellen Status eines Nummernkreises zurück
    
    Args:
        domain: Belegtyp
        tenant_id: Mandanten-ID
        year: Jahr (optional)
    
    Returns:
        Nummernkreis-Status mit nächster Nummer
    
    Requires:
        Scope: docs:read, sales:read, oder purchase:read
    """
    try:
        # Auto-Jahr wenn yearly_reset aktiv
        if year is None:
            import os
            yearly_reset = os.environ.get("NUMBERING_YEARLY_RESET", "false").lower() == "true"
            if yearly_reset:
                year = datetime.now().year
        
        next_num = await numbering.peek(domain, tenant_id, year)
        prefix = numbering._get_prefix(domain, tenant_id, year)
        
        # Extract counter from next_num
        counter_str = next_num.replace(prefix, "")
        counter = int(counter_str) - 1 if counter_str.isdigit() else 0
        
        return StatusResponse(
            ok=True,
            domain=domain,
            tenant_id=tenant_id,
            year=year,
            prefix=prefix,
            counter=counter,
            next_number=next_num,
        )
    
    except Exception as e:
        logger.error(f"Failed to get numbering status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_numbering(
    req: NextNumberRequest,
    numbering: NumberingServicePG = Depends(get_numbering_pg),
    user: dict = Depends(require_all_scopes("admin:all")),
):
    """
    Setzt Nummernkreis zurück (Admin-only)
    
    ⚠️ ACHTUNG: Nur für Testing/Notfälle verwenden!
    
    Args:
        req: Request mit domain, tenant_id, year
    
    Returns:
        Success-Message
    
    Requires:
        Scope: admin:all
    """
    try:
        await numbering.reset(req.domain, req.tenant_id, req.year)
        
        return {
            "ok": True,
            "message": f"Number series reset for {req.domain}/{req.tenant_id}/{req.year}"
        }
    
    except Exception as e:
        logger.error(f"Failed to reset numbering: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/init-year")
async def init_year(
    year: int,
    numbering: NumberingServicePG = Depends(get_numbering_pg),
    user: dict = Depends(require_scopes("admin:all")),
):
    """
    Initialisiert alle Nummernkreise für ein neues Jahr.
    """
    try:
        domains = ["sales_order", "delivery", "invoice", "purchase_order", "goods_receipt", "supplier_invoice"]
        initialized = 0
        
        for domain in domains:
            await numbering.peek(domain, "default", year)
            initialized += 1
        
        return {
            "ok": True,
            "year": year,
            "initialized": initialized,
            "domains": domains
        }
    
    except Exception as e:
        logger.error(f"Failed to init year: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class NumberSeriesConfig(BaseModel):
    """Konfiguration eines Nummernkreises"""
    domain: str
    tenant_id: str = "default"
    year: Optional[int] = None
    prefix: str
    width: int = 5
    counter: int = 0


class NumberSeriesListItem(BaseModel):
    """Item in der Nummernkreis-Liste"""
    domain: str
    tenant_id: str
    year: Optional[int]
    prefix: str
    width: int
    counter: int
    next_number: str


@router.get("/series", response_model=list[NumberSeriesListItem])
async def list_number_series(
    tenant_id: str = "default",
    numbering: NumberingServicePG = Depends(get_numbering_pg),
    user: dict = Depends(require_scopes("admin:all")),
):
    """Listet alle Nummernkreise eines Mandanten auf."""
    try:
        from sqlalchemy import text
        result = await numbering.db.execute(
            text("""
                SELECT domain, tenant_id, year, prefix, width, counter
                FROM number_series
                WHERE tenant_id = :tenant_id
                ORDER BY domain, year
            """),
            {"tenant_id": tenant_id}
        )
        rows = result.fetchall()
        items = []
        for r in rows:
            domain, tid, year, prefix, width, counter = r
            next_num = f"{prefix}{counter + 1:0{width}d}"
            items.append(NumberSeriesListItem(
                domain=domain, tenant_id=tid, year=year,
                prefix=prefix, width=width, counter=counter,
                next_number=next_num,
            ))
        return items
    except Exception as e:
        logger.error(f"Failed to list number series: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/series", response_model=NumberSeriesListItem)
async def create_or_update_number_series(
    config: NumberSeriesConfig,
    numbering: NumberingServicePG = Depends(get_numbering_pg),
    user: dict = Depends(require_all_scopes("admin:all")),
):
    """Erstellt oder aktualisiert einen Nummernkreis."""
    try:
        from sqlalchemy import text
        existing = await numbering.db.execute(
            text("""
                SELECT counter FROM number_series
                WHERE domain = :domain AND tenant_id = :tenant_id
                  AND (year = :year OR (:year IS NULL AND year IS NULL))
            """),
            {"domain": config.domain, "tenant_id": config.tenant_id, "year": config.year}
        )
        row = existing.fetchone()

        if row is None:
            await numbering.db.execute(
                text("""
                    INSERT INTO number_series (domain, tenant_id, year, prefix, counter, width)
                    VALUES (:domain, :tenant_id, :year, :prefix, :counter, :width)
                """),
                {
                    "domain": config.domain, "tenant_id": config.tenant_id,
                    "year": config.year, "prefix": config.prefix,
                    "counter": config.counter, "width": config.width,
                }
            )
        else:
            await numbering.db.execute(
                text("""
                    UPDATE number_series
                    SET prefix = :prefix, width = :width
                    WHERE domain = :domain AND tenant_id = :tenant_id
                      AND (year = :year OR (:year IS NULL AND year IS NULL))
                """),
                {
                    "domain": config.domain, "tenant_id": config.tenant_id,
                    "year": config.year, "prefix": config.prefix, "width": config.width,
                }
            )

        await numbering.db.commit()
        counter = config.counter if row is None else row[0]
        next_num = f"{config.prefix}{counter + 1:0{config.width}d}"
        return NumberSeriesListItem(
            domain=config.domain, tenant_id=config.tenant_id,
            year=config.year, prefix=config.prefix,
            width=config.width, counter=counter, next_number=next_num,
        )
    except Exception as e:
        logger.error(f"Failed to create/update number series: {e}")
        raise HTTPException(status_code=500, detail=str(e))

