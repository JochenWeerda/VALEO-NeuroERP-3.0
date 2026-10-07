"""Benannte Register der Kundenakte, vor der generischen Tab-Route."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.endpoints.crm_360_reads import (
    _fetch_customer_tab_items,
    _paginate_items,
)
from app.api.v1.endpoints.crm_360_sql import _kunde_finden
from app.api.v1.schemas.base import TypedObjectOut
from app.api.v1.schemas.crm_customer_tab import (
    CustomerActivitiesTabOut,
    CustomerAddressesTabOut,
    CustomerContactsTabOut,
    CustomerContractsTabOut,
    CustomerCpdTabOut,
    CustomerDiscountsTabOut,
    CustomerDocumentsTabOut,
    CustomerHistoryTabOut,
    CustomerInstructionsTabOut,
    CustomerOffersTabOut,
    CustomerOrdersTabOut,
    CustomerPricesTabOut,
    CustomerGiftsTabOut,
    CustomerTasksTabOut,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter()


# Vier benannte Register vor der generischen Route
# -----------------------------------------------
#
# Die generische Route `/{customer_id}/tabs/{tab_key}` antwortet mit
# ``TypedObjectOut`` — einer Huelle, die jede Form durchlaesst. Damit kann das
# Feldvertrags-Gate nicht pruefen, ob die Spalten der Maske (ScreenDefinition
# `crm/customer-360`) den Schluesseln der Antwort entsprechen; eine Spalte, die
# ins Leere zeigt, bliebe eine leere Zelle und faellt niemandem auf.
#
# Deshalb dieselbe Aufteilung wie bei Auftrag und Rechnung: je Register eine
# eigene Route mit deklarierter Zeilenform. Sie muessen **vor** der generischen
# Route stehen, sonst verschluckt `{tab_key}` sie.

@router.get(
    "/{customer_id}/tabs/contacts",
    response_model=CustomerContactsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Ansprechpartner",
)
async def get_customer_tab_contacts(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Die Ansprechpartner des Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="contacts", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/auftraege",
    response_model=CustomerOrdersTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Auftraege",
)
async def get_customer_tab_auftraege(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Die letzten Auftraege des Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="auftraege", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/aktivitaeten",
    response_model=CustomerActivitiesTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Aktivitaeten",
)
async def get_customer_tab_aktivitaeten(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Die letzten CRM-Aktivitaeten zum Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="aktivitaeten", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/dokumente",
    response_model=CustomerDocumentsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Dokumente",
)
async def get_customer_tab_dokumente(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Die offenen Posten des Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="dokumente", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/aufgaben",
    response_model=CustomerTasksTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Aufgaben",
)
async def get_customer_tab_aufgaben(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Offene Aufgaben und Wiedervorlagen zum Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="aufgaben", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/kontrakte",
    response_model=CustomerContractsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Kontrakte",
)
async def get_customer_tab_kontrakte(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Kontrakte der Partei."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="kontrakte", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/angebote",
    response_model=CustomerOffersTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Angebote",
)
async def get_customer_tab_angebote(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Verkaufschancen der Partei aus der lokalen Pipeline."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="angebote", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/historie",
    response_model=CustomerHistoryTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Historie",
)
async def get_customer_tab_historie(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Aktivitaeten des Kunden in zeitlicher Reihenfolge."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="historie", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/chefanweisungen",
    response_model=CustomerInstructionsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Chef-Anweisungen",
)
async def get_customer_tab_chefanweisungen(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Normalisierte Chef-Anweisungen des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="chefanweisungen", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/anschriften",
    response_model=CustomerAddressesTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Anschriften",
)
async def get_customer_tab_anschriften(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Normalisierte Anschriften des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="anschriften", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/cpd",
    response_model=CustomerCpdTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: CPD-Konten",
)
async def get_customer_tab_cpd(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """CPD-Konten des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="cpd", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/rabatte",
    response_model=CustomerDiscountsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Rabatte",
)
async def get_customer_tab_rabatte(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Artikelrabatte des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="rabatte", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/preise",
    response_model=CustomerPricesTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Preise",
)
async def get_customer_tab_preise(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Preisvereinbarungen des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="preise", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/praesente",
    response_model=CustomerGiftsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Praesente",
)
async def get_customer_tab_praesente(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None),
    filter_plan_legacy: Optional[str] = Query(None, alias="filterPlan", include_in_schema=False),
    db: Session = Depends(get_db),
):
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="praesente", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=filter_plan_legacy, db=db,
    )


@router.get(
    "/{customer_id}/tabs/{tab_key}",
    response_model=TypedObjectOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Customer tab list data abrufen",
)
async def get_customer_tab_data(
    customer_id: str,
    tab_key: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    filter_plan_legacy: Optional[str] = Query(
        None,
        alias="filterPlan",
        include_in_schema=False,
        description="Deprecated camelCase alias for filter_plan.",
    ),
    db: Session = Depends(get_db),
):
    """Limitierte Tab-Listen fuer den Universal Mask Generator (read-only)."""
    import json

    customer = _kunde_finden(db, customer_id, tenant_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Kunde {customer_id} nicht gefunden")

    parsed_filter_plan: dict | None = None
    raw_filter_plan = filter_plan or filter_plan_legacy
    if raw_filter_plan:
        try:
            parsed_filter_plan = json.loads(raw_filter_plan)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="filter_plan must be valid JSON")

    table_key, items = _fetch_customer_tab_items(
        db,
        customer_id=str(customer.get("id") or customer_id),
        tenant_id=tenant_id,
        tab_key=tab_key,
        kunden_nr=customer.get("kunden_nr"),
        kunden_name=customer.get("name"),
        partner_id=customer.get("business_partner_id"),
    )
    paged_items, total = _paginate_items(
        items, page=page, limit=limit, q=q,
        sort=sort, sort_dir=sort_dir,
        screen_id="crm/customer-360", tab_key=tab_key,
        filter_plan=parsed_filter_plan,
    )
    return {
        "tab_key": tab_key,
        "table_key": table_key,
        "items": paged_items,
        "page": page,
        "limit": limit,
        "total": total,
    }
