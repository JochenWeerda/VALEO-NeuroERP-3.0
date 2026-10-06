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

from pydantic import BaseModel, Field

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.customers_schemas import CustomersOut


router = APIRouter()

logger = logging.getLogger(__name__)


# ── Interessenten (Register: public.crm_leads) ──────────────────────────────
# Die Schemata stehen oben, weil der Listenweg weiter unten auf sie zeigt.

class InteressentCreate(BaseModel):
    """Ein Interessent, wie die Maske ihn erfasst.

    Die Felder heissen deutsch, das Register (`public.crm_leads`) englisch. Die
    Abbildung steht **einmal** in `interessent_service.als_dict` beziehungsweise
    `HERKUNFT_ZU_QUELLE` — damit nicht beide Benennungen durch den Code wandern.
    """

    name: str = Field(min_length=1)
    ansprechpartner: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    adresse: Optional[str] = None
    branche: Optional[str] = None
    herkunft: str = "SONSTIGES"  # WEBSITE/MESSE/EMPFEHLUNG/KALTAKQUISE/SONSTIGES
    notizen: Optional[str] = None


class InteressentOut(BaseModel):
    """Der Interessent, wie der Weg ihn nennt.

    Vorher hing an diesen Wegen `CustomersOut` mit `extra="allow"` — ein Modell,
    das alles erlaubt und deshalb nichts beschreibt.
    """

    id: str
    tenant_id: Optional[str] = None
    #: Nur gesetzt, wenn eine Nummer vermerkt ist. Uebernommene Leads aus der
    #: Akquise haben keine, und erfunden wird keine.
    interessenten_nr: Optional[str] = None
    name: Optional[str] = None
    ansprechpartner: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    herkunft: Optional[str] = None
    branche: Optional[str] = None
    prioritaet: Optional[str] = None
    status: Optional[str] = None
    betreut_von: Optional[str] = None
    notizen: Optional[str] = None
    erstellt_am: Optional[str] = None



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
    response_model=list[CustomersOut]
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
    response_model=list[CustomersOut]
)
def recent_customers(
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Zuletzt aktualisierte Kunden des Mandanten — MVP-Prefetch fuer die Combobox."""
    return _svc(db, tenant_id or DEFAULT_TENANT).recent(limit=limit)


class KundenLookupItem(BaseSchema):
    """Schlanker Datensatz aus der kunden_lookup-View (Phase 2D, schnelle Auswahl)."""

    business_partner_id: Optional[str] = None
    kunden_nr: str
    name: Optional[str] = None
    matchcode: Optional[str] = None
    aktiv: bool = True
    plz: Optional[str] = None
    ort: Optional[str] = None
    strasse: Optional[str] = None
    ust_id_nr: Optional[str] = None
    kundengruppe: Optional[str] = None
    betreuer: Optional[str] = None
    sperrgrund: Optional[str] = None


@router.get("/lookup", response_model=list[KundenLookupItem], summary="Schnelle Kundenauswahl (kunden_lookup)")
def customer_lookup(
    q: str = Query("", description="Suchbegriff (Matchcode/Name/Kundennr./PLZ)"),
    limit: int = Query(20, ge=1, le=2000),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Schmale Such-/Listen-Auswahl aus der kunden_lookup-View; Detaildaten on-demand."""
    from ....services.business_partner_service import BusinessPartnerService

    return BusinessPartnerService(db, tenant_id or DEFAULT_TENANT).search_lookup(q, limit)


class KundenDetail(BaseSchema):
    """On-demand-Detail eines Kunden aus den Domänensatelliten (Phase 2D)."""

    kunden_nr: str
    adresse: dict[str, Any] = Field(default_factory=dict)
    zahlung: dict[str, Any] = Field(default_factory=dict)
    external_refs: dict[str, str] = Field(default_factory=dict)


@router.get(
    "/lookup/{kunden_nr}/detail",
    response_model=KundenDetail,
    summary="Kunden-Detail aus Domänensatelliten (on-demand)",
)
def customer_lookup_detail(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Lädt Adresse/Zahlung/External-Refs aus den ``kunden_*``-Satelliten.

    Gegenstück zu ``/lookup`` (Listenfelder): das UI ruft dies erst beim Öffnen
    eines Kunden. Liest über die kanonische Zugriffsschicht (Satellit bevorzugt,
    Fallback public.kunden während des Übergangs).
    """
    from ....services.business_partner_service import BusinessPartnerService

    return BusinessPartnerService(db, tenant_id or DEFAULT_TENANT).get_customer_detail(kunden_nr)


class KundenIdentitaet(BaseSchema):
    """Vereinheitlichte Kunden-Identität (Identitätsbrücke, Phase 2D Schritt 5)."""

    kunden_nr: Optional[str] = None
    business_partner_id: Optional[str] = None
    partner_number: Optional[str] = None
    crm_customer_id: Optional[str] = None


@router.get(
    "/lookup/resolve",
    response_model=KundenIdentitaet,
    summary="Identitätsbrücke: business_partner_id ↔ kunden_nr ↔ crm_customer_id",
)
def customer_identity_resolve(
    kunden_nr: Optional[str] = Query(None),
    business_partner_id: Optional[str] = Query(None),
    crm_customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Löst genau einen übergebenen Schlüssel zu den übrigen Identitäten auf.

    Brücke ist ``public.kunden.business_partner_id`` (per kunden_merge gefüllt) +
    ``domain_crm.customers``. Nicht auflösbare Felder bleiben ``null``.
    """
    if not any([kunden_nr, business_partner_id, crm_customer_id]):
        raise HTTPException(status_code=400, detail="Mindestens ein Schlüssel erforderlich.")
    from ....services.business_partner_service import BusinessPartnerService

    return BusinessPartnerService(db, tenant_id or DEFAULT_TENANT).resolve_customer_identity(
        kunden_nr=kunden_nr,
        business_partner_id=business_partner_id,
        crm_customer_id=crm_customer_id,
    )


@router.get(
    "/by-partner/{business_partner_id}/detail",
    response_model=KundenDetail,
    summary="Kunden-Detail über business_partner_id (Identitätsbrücke)",
)
def customer_detail_by_partner(
    business_partner_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Brücken-Endpoint für die BP-keyed Masken (Kundenstamm): löst
    business_partner_id → kunden_nr auf und liefert das Satelliten-Detail.

    404, wenn die business_partner_id (noch) nicht mit einer kunden_nr verbrückt
    ist (Brücke unvollständig → erst kunden_merge --apply).
    """
    from ....services.business_partner_service import BusinessPartnerService

    svc = BusinessPartnerService(db, tenant_id or DEFAULT_TENANT)
    kunden_nr = svc.kunden_nr_for_partner(business_partner_id)
    if not kunden_nr:
        raise HTTPException(
            status_code=404,
            detail=f"Keine kunden_nr für business_partner_id {business_partner_id} verbrückt.",
        )
    return svc.get_customer_detail(kunden_nr)


@router.get("/interessenten", summary="Interessenten auflisten",
    response_model=list[InteressentOut]
)
def list_interessenten(
    status: Optional[str] = Query(None, description="NEW | CONTACTED | … | CONVERTED"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    """Die Interessenten des Mandanten aus dem Register `public.crm_leads`.

    Bis zum 06.10.2026 las dieser Weg `domain_crm.interessenten` — eine Tabelle,
    die keine Datenbank hat — und antwortete bei jedem Lesefehler `[]`. Ein Haus,
    das keine Interessenten sieht, akquiriert nicht und merkt nicht, dass die
    Liste nur nicht lesbar war.
    """
    try:
        return interessent.auflisten(db, tenant_id, status, limit, offset)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise interessent.nicht_lesbar(db, fehler, "Interessenten", tenant_id) from fehler


@router.get("/{customer_id}/sales-eligibility", summary="Customer sales eligibility abrufen",
    response_model=CustomersOut
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

from app.core.uuid7 import uuid7
from app.services import interessent_service as interessent
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
    response_model=CustomersOut
)
def umkreissuche(
    payload: UmkreissucheInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Geo-Umkreissuche: Kunden im Umkreis von radius_km um den angegebenen Punkt."""
    from ....services.business_partner_service import BusinessPartnerService

    try:
        rows = BusinessPartnerService(db, tenant_id).list_customers_with_coordinates()
    except Exception:
        rows = []
    if not rows:
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


class KonvertierungResult(_BaseModel):
    kunden_nr: str
    name: str
    konvertiert_am: str
    status: str  # KUNDE / INTERESSENT


@router.post("/interessenten", status_code=201, summary="Interessent anlegen",
    response_model=InteressentOut
)
def create_interessent(
    payload: InteressentCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Legt einen Interessenten im Register an.

    Vorher schrieb dieser Weg `domain_crm.interessenten`, fing den Fehlschlag mit
    `except Exception: db.rollback()` und antwortete trotzdem `201` mit einer
    Interessentennummer — eine Quittung ohne Vorgang. Jetzt gibt es die Zeile
    oder einen Fehler.
    """
    try:
        nummer = interessent.naechste_nummer(db, tenant_id)
        ergebnis = interessent.anlegen(db, tenant_id, str(uuid7()), nummer, payload)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Interessent nicht anlegbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=409,
            detail={"error": "Interessent nicht angelegt", "grund": str(fehler),
                    "migration_hint": interessent.MIGRATIONS_HINWEIS["X-Migration-Hint"]},
            headers=interessent.MIGRATIONS_HINWEIS,
        ) from fehler
    return ergebnis


@router.post("/interessenten/{interessent_id}/konvertieren", response_model=KonvertierungResult, summary="Konvertieren")
def konvertieren(
    interessent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Macht aus dem Interessenten einen Kunden — in **einer** Transaktion.

    Vorher legte dieser Weg den Kundensatz an und setzte danach den
    Interessentenstand in einem eigenen `try/except: db.rollback()`. Scheiterte
    das UPDATE, nahm das `rollback` den Kundensatz mit — dieselbe Transaktion —
    und die Antwort meldete trotzdem `status: "KUNDE"` samt Kundennummer. Ein Haus
    haette eine Kundennummer gehabt, zu der es keinen Kunden gibt.
    """
    from ....services.business_partner_service import BusinessPartnerService

    try:
        zeile = interessent.holen(db, tenant_id, interessent_id, sperren=True)
        interessent.schon_konvertiert(zeile)

        neue_kunden_id = str(uuid7())
        kunden_nr = f"KD-{_date.today().year}-{neue_kunden_id[-6:].upper()}"
        BusinessPartnerService(db, tenant_id).create_customer_record(
            customer_id=neue_kunden_id,
            customer_number=kunden_nr,
            name=zeile.get("company") or "",
            email=zeile.get("email"),
            phone=zeile.get("phone"),
        )
        interessent.stand_setzen(db, tenant_id, interessent_id, interessent.KONVERTIERT)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Konvertierung fehlgeschlagen (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=409,
            detail={
                "error": "Konvertierung nicht durchgefuehrt — es entsteht kein Kunde",
                "grund": str(fehler),
            },
        ) from fehler
    return {
        "kunden_nr": kunden_nr,
        "name": zeile.get("company") or "",
        "konvertiert_am": _date.today().isoformat(),
        "status": "KUNDE",
    }
