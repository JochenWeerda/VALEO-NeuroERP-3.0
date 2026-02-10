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
    Initialisiert alle Nummernkreise für ein neues Jahr
    
    Nützlich für Jahreswechsel-Vorbereitung
    
    Args:
        year: Neues Jahr
    
    Returns:
        Anzahl initialisierter Nummernkreise
    
    Requires:
        Scope: admin:all
    """
    try:
        domains = ["sales_order", "delivery", "invoice", "purchase_order", "goods_receipt", "supplier_invoice"]
        initialized = 0
        
        for domain in domains:
            # Peek initialisiert automatisch wenn nicht vorhanden
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

