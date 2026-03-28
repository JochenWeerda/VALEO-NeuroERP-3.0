"""
Direct debit endpoints used by finance UI masks.
"""

from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.tenant import get_tenant_id
from ....core.database import get_db

router = APIRouter(prefix="/direct-debits", tags=["finance", "direct-debits"])


@router.get("", response_model=list[dict])
async def list_direct_debits(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lastschriftlaeufe aus direct_debit_items aggregiert nach run_id."""
    try:
        rows = db.execute(text("""
            SELECT
                run_id,
                COUNT(*) AS anzahl,
                SUM(amount) AS gesamtbetrag,
                MIN(created_at) AS erstellt_am,
                MAX(CASE WHEN status = 'exported' THEN 'exported'
                         WHEN status = 'pending' THEN 'pending'
                         ELSE 'draft' END) AS status
            FROM domain_shared.direct_debit_items
            GROUP BY run_id
            ORDER BY MIN(created_at) DESC
            LIMIT 50
        """)).fetchall()
        return [
            {
                "id": r.run_id,
                "laufnummer": r.run_id,
                "anzahlLastschriften": r.anzahl,
                "gesamtbetrag": float(r.gesamtbetrag or 0),
                "status": r.status or "draft",
                "erstellt_am": str(r.erstellt_am) if r.erstellt_am else None,
            }
            for r in rows
        ]
    except Exception:
        return []


@router.get("/new", response_model=dict)
async def get_new_direct_debit_template(tenant_id: str = Depends(get_tenant_id)):
    """Return default values for direct debit create forms."""
    return {
        "id": None,
        "tenant_id": tenant_id,
        "laufnummer": "",
        "faelligkeitsdatum": date.today().isoformat(),
        "ausfuehrungsdatum": date.today().isoformat(),
        "sepaSchema": "CORE",
        "sequenzTyp": "RCUR",
        "glaeubigerId": "",
        "abbucherName": "",
        "anzahlLastschriften": 0,
        "gesamtbetrag": 0,
        "status": "draft",
        "lastschriften": [],
    }
