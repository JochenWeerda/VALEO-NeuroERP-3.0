"""CRM Customer endpoints backed by the crm-core service."""

from __future__ import annotations

import logging
from math import ceil
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from ....services.customer_service import CustomerService
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Customer, CustomerCreate, CustomerUpdate

router = APIRouter()

logger = logging.getLogger(__name__)

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def _svc(db: Session, tenant_id: str) -> CustomerService:
    return CustomerService(db, tenant_id)



def _to_http_exception(error: httpx.HTTPStatusError) -> HTTPException:
    """Map downstream errors to FastAPI HTTPException."""
    detail = None
    try:
        payload = error.response.json()
        detail = payload.get("detail")
    except ValueError:
        detail = error.response.text or "crm-core request failed"
    return HTTPException(status_code=error.response.status_code, detail=detail or "crm-core request failed")




@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED, summary="Customer anlegen")
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
) -> Customer:
    """Create a new customer via crm-core, or in PostgreSQL if crm-core is unreachable."""
    try:
        d = await _svc(db, str(customer_data.tenant_id)).create_customer(customer_data)  # type: ignore[arg-type]
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Customer.model_validate(d)


@router.get("/", response_model=PaginatedResponse[Customer], summary="Customers auflisten")
async def list_customers(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, description="Search in display name"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[Customer]:
    effective_tenant = tenant_id or DEFAULT_TENANT
    items_raw, total = await _svc(db, effective_tenant).list_customers(skip=skip, limit=limit, search=search)
    items = [Customer.model_validate(d) for d in items_raw]
    pages = ceil(total / limit) if total else 1
    return PaginatedResponse[Customer](
        items=items,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/quick-search", summary="Search customers quick",
    response_model=dict
)
def quick_search_customers(
    q: str = Query("", description="Suchterm (Name oder Kundennummer)"),
    limit: int = Query(8, ge=1, le=25),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Schlanker Typeahead-Endpoint — nur die Felder, die die Combobox braucht.

    Sortierung: Exakt-/Prefix-Matches auf Kundennummer zuerst, dann Prefix auf Name,
    danach Trigram-Ähnlichkeit. Nutzt pg_trgm GIN-Indizes
    (siehe Migration crm_customers_search_index_20260414).
    """
    return _svc(db, tenant_id or DEFAULT_TENANT).quick_search(q or "", limit=limit)


@router.get("/recent", summary="Customers recent",
    response_model=dict
)
def recent_customers(
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Zuletzt aktualisierte Kunden des Mandanten — MVP-Prefetch fuer die Combobox."""
    return _svc(db, tenant_id or DEFAULT_TENANT).recent(limit=limit)


@router.get("/{customer_id}/sales-eligibility", summary="Customer sales eligibility abrufen",
    response_model=dict
)
async def get_customer_sales_eligibility(
    customer_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, object]:
    """Verkaufs-/Lieferfreigabe aus Stammdaten (Business-Partner), für Belegmasken."""
    from ....services.customer_sales_eligibility import describe_sales_eligibility

    return describe_sales_eligibility(db, tenant_id, customer_id)


@router.get("/{customer_id}", response_model=Customer, summary="Customer abrufen")
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Customer:
    try:
        d = await _svc(db, tenant_id).get_customer(customer_id)
    except EntityNotFoundError as exc:
        raise HTTPException(404, exc.detail)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Customer.model_validate(d)


@router.put("/{customer_id}", response_model=Customer, summary="Customer aktualisieren")
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Customer:
    try:
        d = await _svc(db, tenant_id).update_customer(customer_id, customer_data)
    except EntityNotFoundError:
        raise HTTPException(404, "Customer not found")
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Customer.model_validate(d)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Customer löschen",
)
async def delete_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    try:
        await _svc(db, tenant_id).delete_customer(customer_id)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Interessenten (Prospects)
# ---------------------------------------------------------------------------

import math as _math
import uuid as _uuid
from datetime import date as _date

from sqlalchemy import text as _text
from pydantic import BaseModel as _BaseModel


# ---------------------------------------------------------------------------
# Geo helpers
# ---------------------------------------------------------------------------

def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = _math.radians(lat2 - lat1)
    dlon = _math.radians(lon2 - lon1)
    a = _math.sin(dlat / 2) ** 2 + _math.cos(_math.radians(lat1)) * _math.cos(_math.radians(lat2)) * _math.sin(dlon / 2) ** 2
    return R * 2 * _math.asin(_math.sqrt(a))


class UmkreissucheInput(_BaseModel):
    breitengrad: float
    laengengrad: float
    radius_km: float = 50.0
    max_ergebnisse: int = 20


class UmkreissucheErgebnis(_BaseModel):
    kunden_nr: str
    name: str
    adresse: Optional[str] = None
    breitengrad: float
    laengengrad: float
    entfernung_km: float


@router.post("/umkreissuche", summary="Umkreissuche",
    response_model=None
)
def umkreissuche(
    payload: UmkreissucheInput,
    db: Session = Depends(get_db),
) -> dict:
    """Geo-Umkreissuche: Kunden im Umkreis von radius_km um den angegebenen Punkt."""
    try:
        rows = db.execute(
            _text(
                "SELECT kunden_nr, name, adresse, breitengrad, laengengrad "
                "FROM domain_crm.customers "
                "WHERE breitengrad IS NOT NULL AND laengengrad IS NOT NULL"
            )
        ).mappings().all()
    except Exception:
        return {
            "ergebnisse": [],
            "hinweis": "Geo-Koordinaten noch nicht eingepflegt",
            "migration_hint": "Spalten breitengrad/laengengrad in domain_crm.customers anlegen",
        }

    ergebnisse = []
    for r in rows:
        dist = _haversine(payload.breitengrad, payload.laengengrad, float(r["breitengrad"]), float(r["laengengrad"]))
        if dist <= payload.radius_km:
            ergebnisse.append({
                "kunden_nr": r["kunden_nr"],
                "name": r["name"],
                "adresse": r.get("adresse"),
                "breitengrad": float(r["breitengrad"]),
                "laengengrad": float(r["laengengrad"]),
                "entfernung_km": round(dist, 3),
            })

    ergebnisse.sort(key=lambda x: x["entfernung_km"])
    ergebnisse = ergebnisse[: payload.max_ergebnisse]
    return {"ergebnisse": ergebnisse}


class InteressentCreate(_BaseModel):
    name: str
    email: Optional[str] = None
    telefon: Optional[str] = None
    adresse: Optional[str] = None
    branche: Optional[str] = None
    herkunft: str = "SONSTIGES"  # WEBSITE/MESSE/EMPFEHLUNG/KALTAKQUISE/SONSTIGES
    notizen: Optional[str] = None


class KonvertierungResult(_BaseModel):
    kunden_nr: str
    name: str
    konvertiert_am: str
    status: str  # KUNDE / INTERESSENT


@router.post("/interessenten", status_code=status.HTTP_201_CREATED, summary="Interessent anlegen",
    response_model=dict
)
def create_interessent(
    payload: InteressentCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    new_id = str(_uuid.uuid4())
    year = _date.today().year

    # Determine next sequence number (best-effort)
    seq = 1
    try:
        row = db.execute(
            _text(
                "SELECT COUNT(*) AS cnt FROM domain_crm.interessenten "
                "WHERE tenant_id=:tenant_id AND EXTRACT(year FROM erstellt_am)=:year"
            ),
            {"tenant_id": tenant_id, "year": year},
        ).first()
        if row:
            seq = (row[0] or 0) + 1
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass

    interessenten_nr = f"INT-{year}-{seq:05d}"

    try:
        db.execute(
            _text(
                "INSERT INTO domain_crm.interessenten "
                "(id, tenant_id, interessenten_nr, name, email, telefon, adresse, "
                "branche, herkunft, notizen, status, erstellt_am) "
                "VALUES (:id, :tenant_id, :nr, :name, :email, :telefon, :adresse, "
                ":branche, :herkunft, :notizen, 'INTERESSENT', NOW())"
            ),
            {
                "id": new_id,
                "tenant_id": tenant_id,
                "nr": interessenten_nr,
                **payload.model_dump(),
            },
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "id": new_id,
        "interessenten_nr": interessenten_nr,
        "status": "INTERESSENT",
        **payload.model_dump(),
    }


@router.get("/interessenten", summary="Interessenten auflisten",
    response_model=list
)
def list_interessenten(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        rows = db.execute(
            _text(
                "SELECT id, interessenten_nr, name, email, telefon, adresse, branche, "
                "herkunft, notizen, status, erstellt_am "
                "FROM domain_crm.interessenten WHERE tenant_id=:tenant_id ORDER BY erstellt_am DESC"
            ),
            {"tenant_id": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


@router.post("/interessenten/{interessent_id}/konvertieren", response_model=KonvertierungResult, summary="Konvertieren")
def konvertieren(
    interessent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    # Load Interessent
    interessent: dict = {}
    try:
        row = db.execute(
            _text(
                "SELECT * FROM domain_crm.interessenten WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": interessent_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row:
            interessent = dict(row)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": "DB unavailable", "migration_hint": "domain_crm.interessenten missing"},
        )

    if not interessent:
        raise HTTPException(status_code=404, detail="Interessent nicht gefunden")

    new_customer_id = str(_uuid.uuid4())
    kunden_nr = f"KD-{_date.today().year}-{new_customer_id[:6].upper()}"
    konvertiert_am = _date.today().isoformat()

    # Try domain_crm.customers first, fallback domain_shared.customers
    for schema in ("domain_crm", "domain_shared"):
        try:
            db.execute(
                _text(
                    f"INSERT INTO {schema}.customers "  # noqa: S608
                    "(id, tenant_id, kunden_nr, name, email, telefon, erstellt_am) "
                    "VALUES (:id, :tenant_id, :kunden_nr, :name, :email, :telefon, NOW())"
                ),
                {
                    "id": new_customer_id,
                    "tenant_id": tenant_id,
                    "kunden_nr": kunden_nr,
                    "name": interessent.get("name", ""),
                    "email": interessent.get("email"),
                    "telefon": interessent.get("telefon"),
                },
            )
            db.commit()
            break
        except Exception:
            db.rollback()

    # Update Interessent status
    try:
        db.execute(
            _text(
                "UPDATE domain_crm.interessenten SET status='KONVERTIERT' WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": interessent_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "kunden_nr": kunden_nr,
        "name": interessent.get("name", ""),
        "konvertiert_am": konvertiert_am,
        "status": "KUNDE",
    }
