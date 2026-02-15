"""
NaWaRo CRUD endpoints for print notifications, contracts, and cultivation areas.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Literal
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.infrastructure.models import (
    NawaroPrintNotification,
    NawaroContractSheet,
    NawaroContractSheetRow,
    NawaroAreaSheet,
    NawaroAreaSheetRow,
)

router = APIRouter()

DeliveryOption = Literal[
    'vollstaendige_ablieferung',
    'hoflagerung',
    'berichtigung',
    'nachmeldung',
]


def _to_decimal(value: str | None) -> Decimal | None:
    if value is None:
        return None
    normalized = value.strip().replace(',', '.')
    if not normalized:
        return None
    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise HTTPException(status_code=422, detail=f'Invalid decimal value: {value}') from exc


class NawaroNotificationIn(BaseModel):
    document_name: str = Field(..., min_length=3, max_length=255)
    harvest_year: int = Field(..., ge=2000, le=2100)
    article_number: str | None = Field(default=None, max_length=80)
    debtor_from: str | None = Field(default=None, max_length=80)
    debtor_to: str | None = Field(default=None, max_length=80)
    delivery_option: DeliveryOption = 'vollstaendige_ablieferung'
    form_code: str = Field(default='W12151', min_length=2, max_length=40)
    copies: int = Field(default=1, ge=1, le=999)
    printer_name: str | None = Field(default=None, max_length=255)


class NawaroNotificationOut(NawaroNotificationIn):
    id: str
    created_at: str | None = None
    updated_at: str | None = None


class NawaroContractRowIn(BaseModel):
    contract_number: str | None = None
    customer_name: str | None = None
    name_1: str | None = None
    total_area: str | None = None
    standard_quantity: str | None = None
    delivery_count: int | None = Field(default=None, ge=0)
    delivery_resource: str | None = None
    quantity_b: str | None = None
    harvest_declaration: str | None = None


class NawaroContractRowOut(NawaroContractRowIn):
    id: str


class NawaroContractSheetIn(BaseModel):
    harvest_year: int = Field(..., ge=2000, le=2100)
    article_number: str | None = Field(default=None, max_length=80)
    is_summer: bool = True
    is_winter: bool = False
    rows: list[NawaroContractRowIn] = Field(default_factory=list)


class NawaroContractSheetOut(NawaroContractSheetIn):
    id: str
    rows: list[NawaroContractRowOut]
    created_at: str | None = None
    updated_at: str | None = None


class NawaroAreaRowIn(BaseModel):
    customer_name: str | None = None
    name_1: str | None = None
    name_2: str | None = None
    postal_code: str | None = None
    city: str | None = None
    phone: str | None = None
    fax: str | None = None
    area_2022: str | None = None
    area_2023: str | None = None
    area_2024: str | None = None
    area_2025: str | None = None
    area_2026: str | None = None


class NawaroAreaRowOut(NawaroAreaRowIn):
    id: str


class NawaroAreaSheetIn(BaseModel):
    harvest_year_from: int = Field(..., ge=2000, le=2100)
    harvest_year_to: int = Field(..., ge=2000, le=2100)
    article_number: str | None = Field(default=None, max_length=80)
    is_summer: bool = True
    is_winter: bool = False
    form_code: str = Field(default='W12071', min_length=2, max_length=40)
    rows: list[NawaroAreaRowIn] = Field(default_factory=list)


class NawaroAreaSheetOut(NawaroAreaSheetIn):
    id: str
    rows: list[NawaroAreaRowOut]
    created_at: str | None = None
    updated_at: str | None = None


def _notification_out(item: NawaroPrintNotification) -> NawaroNotificationOut:
    return NawaroNotificationOut(
        id=item.id,
        document_name=item.document_name,
        harvest_year=item.harvest_year,
        article_number=item.article_number,
        debtor_from=item.debtor_from,
        debtor_to=item.debtor_to,
        delivery_option=item.delivery_option,
        form_code=item.form_code,
        copies=item.copies,
        printer_name=item.printer_name,
        created_at=item.created_at.isoformat() if item.created_at else None,
        updated_at=item.updated_at.isoformat() if item.updated_at else None,
    )


def _contract_sheet_out(db: Session, item: NawaroContractSheet) -> NawaroContractSheetOut:
    rows = (
        db.query(NawaroContractSheetRow)
        .filter(
            NawaroContractSheetRow.sheet_id == item.id,
            NawaroContractSheetRow.tenant_id == item.tenant_id,
        )
        .order_by(NawaroContractSheetRow.row_order.asc())
        .all()
    )
    return NawaroContractSheetOut(
        id=item.id,
        harvest_year=item.harvest_year,
        article_number=item.article_number,
        is_summer=item.is_summer,
        is_winter=item.is_winter,
        rows=[
            NawaroContractRowOut(
                id=row.id,
                contract_number=row.contract_number,
                customer_name=row.customer_name,
                name_1=row.name_1,
                total_area=str(row.total_area) if row.total_area is not None else None,
                standard_quantity=str(row.standard_quantity) if row.standard_quantity is not None else None,
                delivery_count=row.delivery_count,
                delivery_resource=row.delivery_resource,
                quantity_b=str(row.quantity_b) if row.quantity_b is not None else None,
                harvest_declaration=row.harvest_declaration,
            )
            for row in rows
        ],
        created_at=item.created_at.isoformat() if item.created_at else None,
        updated_at=item.updated_at.isoformat() if item.updated_at else None,
    )


def _area_sheet_out(db: Session, item: NawaroAreaSheet) -> NawaroAreaSheetOut:
    rows = (
        db.query(NawaroAreaSheetRow)
        .filter(
            NawaroAreaSheetRow.sheet_id == item.id,
            NawaroAreaSheetRow.tenant_id == item.tenant_id,
        )
        .order_by(NawaroAreaSheetRow.row_order.asc())
        .all()
    )
    return NawaroAreaSheetOut(
        id=item.id,
        harvest_year_from=item.harvest_year_from,
        harvest_year_to=item.harvest_year_to,
        article_number=item.article_number,
        is_summer=item.is_summer,
        is_winter=item.is_winter,
        form_code=item.form_code,
        rows=[
            NawaroAreaRowOut(
                id=row.id,
                customer_name=row.customer_name,
                name_1=row.name_1,
                name_2=row.name_2,
                postal_code=row.postal_code,
                city=row.city,
                phone=row.phone,
                fax=row.fax,
                area_2022=str(row.area_2022) if row.area_2022 is not None else None,
                area_2023=str(row.area_2023) if row.area_2023 is not None else None,
                area_2024=str(row.area_2024) if row.area_2024 is not None else None,
                area_2025=str(row.area_2025) if row.area_2025 is not None else None,
                area_2026=str(row.area_2026) if row.area_2026 is not None else None,
            )
            for row in rows
        ],
        created_at=item.created_at.isoformat() if item.created_at else None,
        updated_at=item.updated_at.isoformat() if item.updated_at else None,
    )


@router.get('/print-notifications', response_model=list[NawaroNotificationOut])
async def list_print_notifications(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    items = (
        db.query(NawaroPrintNotification)
        .filter(NawaroPrintNotification.tenant_id == tenant_id)
        .order_by(NawaroPrintNotification.created_at.desc())
        .limit(200)
        .all()
    )
    return [_notification_out(item) for item in items]


@router.post('/print-notifications', response_model=NawaroNotificationOut, status_code=201)
async def create_print_notification(
    payload: NawaroNotificationIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = NawaroPrintNotification(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        document_name=payload.document_name,
        harvest_year=payload.harvest_year,
        article_number=payload.article_number,
        debtor_from=payload.debtor_from,
        debtor_to=payload.debtor_to,
        delivery_option=payload.delivery_option,
        form_code=payload.form_code,
        copies=payload.copies,
        printer_name=payload.printer_name,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _notification_out(item)


@router.get('/print-notifications/{item_id}', response_model=NawaroNotificationOut)
async def get_print_notification(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroPrintNotification)
        .filter(NawaroPrintNotification.id == item_id, NawaroPrintNotification.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Print notification not found')
    return _notification_out(item)


@router.put('/print-notifications/{item_id}', response_model=NawaroNotificationOut)
async def update_print_notification(
    item_id: str,
    payload: NawaroNotificationIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroPrintNotification)
        .filter(NawaroPrintNotification.id == item_id, NawaroPrintNotification.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Print notification not found')

    item.document_name = payload.document_name
    item.harvest_year = payload.harvest_year
    item.article_number = payload.article_number
    item.debtor_from = payload.debtor_from
    item.debtor_to = payload.debtor_to
    item.delivery_option = payload.delivery_option
    item.form_code = payload.form_code
    item.copies = payload.copies
    item.printer_name = payload.printer_name

    db.commit()
    db.refresh(item)
    return _notification_out(item)


@router.delete('/print-notifications/{item_id}', response_model=dict)
async def delete_print_notification(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroPrintNotification)
        .filter(NawaroPrintNotification.id == item_id, NawaroPrintNotification.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Print notification not found')
    db.delete(item)
    db.commit()
    return {'ok': True, 'id': item_id}


@router.get('/contract-sheets', response_model=list[NawaroContractSheetOut])
async def list_contract_sheets(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    items = (
        db.query(NawaroContractSheet)
        .filter(NawaroContractSheet.tenant_id == tenant_id)
        .order_by(NawaroContractSheet.created_at.desc())
        .limit(200)
        .all()
    )
    return [_contract_sheet_out(db, item) for item in items]


@router.post('/contract-sheets', response_model=NawaroContractSheetOut, status_code=201)
async def create_contract_sheet(
    payload: NawaroContractSheetIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = NawaroContractSheet(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        harvest_year=payload.harvest_year,
        article_number=payload.article_number,
        is_summer=payload.is_summer,
        is_winter=payload.is_winter,
    )
    db.add(item)
    db.flush()

    for index, row in enumerate(payload.rows):
        db.add(
            NawaroContractSheetRow(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                sheet_id=item.id,
                contract_number=row.contract_number,
                customer_name=row.customer_name,
                name_1=row.name_1,
                total_area=_to_decimal(row.total_area),
                standard_quantity=_to_decimal(row.standard_quantity),
                delivery_count=row.delivery_count,
                delivery_resource=row.delivery_resource,
                quantity_b=_to_decimal(row.quantity_b),
                harvest_declaration=row.harvest_declaration,
                row_order=index,
            )
        )

    db.commit()
    db.refresh(item)
    return _contract_sheet_out(db, item)


@router.get('/contract-sheets/{sheet_id}', response_model=NawaroContractSheetOut)
async def get_contract_sheet(
    sheet_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroContractSheet)
        .filter(NawaroContractSheet.id == sheet_id, NawaroContractSheet.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Contract sheet not found')
    return _contract_sheet_out(db, item)


@router.put('/contract-sheets/{sheet_id}', response_model=NawaroContractSheetOut)
async def update_contract_sheet(
    sheet_id: str,
    payload: NawaroContractSheetIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroContractSheet)
        .filter(NawaroContractSheet.id == sheet_id, NawaroContractSheet.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Contract sheet not found')

    item.harvest_year = payload.harvest_year
    item.article_number = payload.article_number
    item.is_summer = payload.is_summer
    item.is_winter = payload.is_winter

    db.query(NawaroContractSheetRow).filter(
        NawaroContractSheetRow.sheet_id == item.id,
        NawaroContractSheetRow.tenant_id == tenant_id,
    ).delete()

    for index, row in enumerate(payload.rows):
        db.add(
            NawaroContractSheetRow(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                sheet_id=item.id,
                contract_number=row.contract_number,
                customer_name=row.customer_name,
                name_1=row.name_1,
                total_area=_to_decimal(row.total_area),
                standard_quantity=_to_decimal(row.standard_quantity),
                delivery_count=row.delivery_count,
                delivery_resource=row.delivery_resource,
                quantity_b=_to_decimal(row.quantity_b),
                harvest_declaration=row.harvest_declaration,
                row_order=index,
            )
        )

    db.commit()
    db.refresh(item)
    return _contract_sheet_out(db, item)


@router.delete('/contract-sheets/{sheet_id}', response_model=dict)
async def delete_contract_sheet(
    sheet_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroContractSheet)
        .filter(NawaroContractSheet.id == sheet_id, NawaroContractSheet.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Contract sheet not found')

    db.query(NawaroContractSheetRow).filter(
        NawaroContractSheetRow.sheet_id == item.id,
        NawaroContractSheetRow.tenant_id == tenant_id,
    ).delete()
    db.delete(item)
    db.commit()
    return {'ok': True, 'id': sheet_id}


@router.get('/area-sheets', response_model=list[NawaroAreaSheetOut])
async def list_area_sheets(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    items = (
        db.query(NawaroAreaSheet)
        .filter(NawaroAreaSheet.tenant_id == tenant_id)
        .order_by(NawaroAreaSheet.created_at.desc())
        .limit(200)
        .all()
    )
    return [_area_sheet_out(db, item) for item in items]


@router.post('/area-sheets', response_model=NawaroAreaSheetOut, status_code=201)
async def create_area_sheet(
    payload: NawaroAreaSheetIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = NawaroAreaSheet(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        harvest_year_from=payload.harvest_year_from,
        harvest_year_to=payload.harvest_year_to,
        article_number=payload.article_number,
        is_summer=payload.is_summer,
        is_winter=payload.is_winter,
        form_code=payload.form_code,
    )
    db.add(item)
    db.flush()

    for index, row in enumerate(payload.rows):
        db.add(
            NawaroAreaSheetRow(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                sheet_id=item.id,
                customer_name=row.customer_name,
                name_1=row.name_1,
                name_2=row.name_2,
                postal_code=row.postal_code,
                city=row.city,
                phone=row.phone,
                fax=row.fax,
                area_2022=_to_decimal(row.area_2022),
                area_2023=_to_decimal(row.area_2023),
                area_2024=_to_decimal(row.area_2024),
                area_2025=_to_decimal(row.area_2025),
                area_2026=_to_decimal(row.area_2026),
                row_order=index,
            )
        )

    db.commit()
    db.refresh(item)
    return _area_sheet_out(db, item)


@router.get('/area-sheets/{sheet_id}', response_model=NawaroAreaSheetOut)
async def get_area_sheet(
    sheet_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroAreaSheet)
        .filter(NawaroAreaSheet.id == sheet_id, NawaroAreaSheet.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Area sheet not found')
    return _area_sheet_out(db, item)


@router.put('/area-sheets/{sheet_id}', response_model=NawaroAreaSheetOut)
async def update_area_sheet(
    sheet_id: str,
    payload: NawaroAreaSheetIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroAreaSheet)
        .filter(NawaroAreaSheet.id == sheet_id, NawaroAreaSheet.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Area sheet not found')

    item.harvest_year_from = payload.harvest_year_from
    item.harvest_year_to = payload.harvest_year_to
    item.article_number = payload.article_number
    item.is_summer = payload.is_summer
    item.is_winter = payload.is_winter
    item.form_code = payload.form_code

    db.query(NawaroAreaSheetRow).filter(
        NawaroAreaSheetRow.sheet_id == item.id,
        NawaroAreaSheetRow.tenant_id == tenant_id,
    ).delete()

    for index, row in enumerate(payload.rows):
        db.add(
            NawaroAreaSheetRow(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                sheet_id=item.id,
                customer_name=row.customer_name,
                name_1=row.name_1,
                name_2=row.name_2,
                postal_code=row.postal_code,
                city=row.city,
                phone=row.phone,
                fax=row.fax,
                area_2022=_to_decimal(row.area_2022),
                area_2023=_to_decimal(row.area_2023),
                area_2024=_to_decimal(row.area_2024),
                area_2025=_to_decimal(row.area_2025),
                area_2026=_to_decimal(row.area_2026),
                row_order=index,
            )
        )

    db.commit()
    db.refresh(item)
    return _area_sheet_out(db, item)


@router.delete('/area-sheets/{sheet_id}', response_model=dict)
async def delete_area_sheet(
    sheet_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    item = (
        db.query(NawaroAreaSheet)
        .filter(NawaroAreaSheet.id == sheet_id, NawaroAreaSheet.tenant_id == tenant_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail='Area sheet not found')

    db.query(NawaroAreaSheetRow).filter(
        NawaroAreaSheetRow.sheet_id == item.id,
        NawaroAreaSheetRow.tenant_id == tenant_id,
    ).delete()
    db.delete(item)
    db.commit()
    return {'ok': True, 'id': sheet_id}
