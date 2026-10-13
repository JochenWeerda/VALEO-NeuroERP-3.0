"""Lesender Belegweg: jeder Beleg in der Form des Belegvertrags (BELEG-011).

Die Belegmaske, ein MCP-Werkzeug und jede andere Stelle lesen Belege hier — nicht aus dem Speicher der Domaene.
Heute liefert DocFlow; weitere belegfuehrende Domaenen haengen einen eigenen Adapter ein.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.core.belegvertrag import BELEGARTEN, Beleg
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.docflow_belegadapter import lies_beleg
from app.services.docflow_service import DocflowService

router = APIRouter()


@router.get("/{belegart}/{beleg_id}", response_model=Beleg, summary="Beleg in Vertragsform lesen")
def beleg_lesen(
    belegart: str,
    beleg_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _nutzer: Any = Depends(get_current_user),
) -> Beleg:
    """Kopf, Partner, Positionen, Summen, Buchungsstand, Belegkette, Historie und die im Zustand moeglichen Aktionen."""
    if belegart not in BELEGARTEN:
        raise HTTPException(status_code=404, detail="Belegart nicht bekannt")
    beleg = lies_beleg(DocflowService(db, tenant_id), beleg_id)
    # Ein Beleg anderer Art unter dieser Adresse ist nicht dieser Beleg.
    if beleg is None or beleg.belegart != belegart:
        raise HTTPException(status_code=404, detail="Beleg nicht gefunden")
    return beleg
