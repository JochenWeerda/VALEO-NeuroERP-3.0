"""Finance-Stamm fuer Debitoren und Kreditoren — Maskengenerator und Listen."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema, TypedObjectOut
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundError
from app.core.tenant import get_tenant_id
from app.infrastructure.models import Customer
from app.services.procurement_service import ProcurementService

router = APIRouter(tags=["finance", "stammdaten"])


class DebitorPatch(BaseSchema):
    is_active: Optional[bool] = None
    credit_limit: Optional[float] = None


class CreditorWrite(BaseSchema):
    creditor_number: Optional[str] = Field(None, min_length=1, max_length=50)
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    vat_id: Optional[str] = None
    tax_number: Optional[str] = None
    payment_terms_days: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    tenant_id: Optional[str] = None


def _op_by_name(db: Session, tenant_id: str, konto_typ: str) -> dict[str, dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                "SELECT COALESCE(kunde_name, lieferant_name, '') AS name, "
                "SUM(COALESCE(betrag, 0)) AS gesamt, "
                "SUM(COALESCE(offen, open_amount, betrag, 0)) AS offen, "
                "MIN(COALESCE(faelligkeit, due_date)) AS faellig, "
                "MAX(COALESCE(dunning_level, 0)) AS mahnstufe "
                "FROM domain_erp.offene_posten "
                "WHERE tenant_id = :t AND konto_typ = :k "
                "AND COALESCE(op_status,'') <> 'storniert' "
                "GROUP BY COALESCE(kunde_name, lieferant_name, '')"
            ),
            {"t": tenant_id, "k": konto_typ},
        ).mappings().all()
    except (ProgrammingError, OperationalError):
        # OP-Tabelle darf die Stammliste nicht blockieren — Debitor bleibt sichtbar.
        db.rollback()
        return {}
    return {
        str(row["name"] or ""): {
            "gesamtForderung": float(row["gesamt"] or 0),
            "offenerBetrag": float(row["offen"] or 0),
            "faelligkeit": row["faellig"].isoformat()[:10] if row["faellig"] else None,
            "mahnstufe": int(row["mahnstufe"] or 0),
        }
        for row in rows
    }


def _debitor_dict(customer: Customer, op: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    op = op or {}
    aktiv = bool(customer.is_active)
    payment = customer.payment_terms
    return {
        "id": customer.id,
        "kunde": customer.company_name,
        "kundennummer": customer.customer_number,
        "debitoren_nr": customer.customer_number,
        "name": customer.company_name,
        "kreditlimit": float(customer.credit_limit or 0),
        "zahlungsbedingungen": f"{payment} Tage" if payment is not None else None,
        "steuernummer": customer.tax_id,
        "ust_id": customer.tax_id,
        "status": "aktiv" if aktiv else "gesperrt",
        "is_active": aktiv,
        "credit_limit": float(customer.credit_limit or 0),
        "customer_number": customer.customer_number,
        "company_name": customer.company_name,
        "gesamtForderung": op.get("gesamtForderung", 0.0),
        "offenerBetrag": op.get("offenerBetrag", 0.0),
        "faelligkeit": op.get("faelligkeit"),
        "mahnstufe": op.get("mahnstufe", 0),
    }


def _creditor_from_lieferant(lf: dict[str, Any], op: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    op = op or {}
    aktiv = bool(lf.get("aktiv", True))
    name = lf.get("firmenname") or ""
    return {
        "id": str(lf.get("id")),
        "kreditoren_nr": lf.get("lieferantennummer"),
        "name": name,
        "zahlungsbedingungen": lf.get("zahlungsbedingungen"),
        "steuernummer": lf.get("steuernummer"),
        "ust_id": lf.get("ust_id"),
        "status": "aktiv" if aktiv else "gesperrt",
        "creditor_number": lf.get("lieferantennummer"),
        "company_name": name,
        "contact_person": lf.get("ansprechpartner"),
        "street": lf.get("strasse"),
        "postal_code": lf.get("plz"),
        "city": lf.get("ort"),
        "country": lf.get("land") or "DE",
        "phone": lf.get("telefon"),
        "email": lf.get("email"),
        "vat_id": lf.get("ust_id"),
        "tax_number": lf.get("steuernummer"),
        "payment_terms_days": lf.get("zahlungsziel_tage") or 30,
        "is_active": aktiv,
        "notes": lf.get("notiz"),
        "gesamtForderung": op.get("gesamtForderung", 0.0),
        "offenerBetrag": op.get("offenerBetrag", 0.0),
        "faelligkeit": op.get("faelligkeit"),
        "mahnstufe": op.get("mahnstufe", 0),
    }


@router.get("/finance/debitoren", response_model=list[TypedObjectOut], summary="Debitoren auflisten")
async def list_debitoren(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    op_map = _op_by_name(db, tenant_id, "debitoren")
    rows = (
        db.query(Customer)
        .filter(Customer.tenant_id == tenant_id, Customer.deleted_at.is_(None))
        .order_by(Customer.company_name)
        .all()
    )
    return [_debitor_dict(row, op_map.get(row.company_name or "")) for row in rows]


@router.get("/finance/debitoren/{debitor_id}", response_model=TypedObjectOut, summary="Debitor abrufen")
async def get_debitor(
    debitor_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    row = (
        db.query(Customer)
        .filter(
            Customer.tenant_id == tenant_id,
            Customer.deleted_at.is_(None),
            Customer.id == debitor_id,
        )
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Debitor nicht gefunden")
    op_map = _op_by_name(db, tenant_id, "debitoren")
    return _debitor_dict(row, op_map.get(row.company_name or ""))


@router.patch("/finance/debitoren/{debitor_id}", response_model=TypedObjectOut, summary="Debitor aktualisieren")
@router.patch("/finance/debtors/{debitor_id}", response_model=TypedObjectOut, summary="Debitor aktualisieren")
async def patch_debitor(
    debitor_id: str,
    payload: DebitorPatch,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    row = (
        db.query(Customer)
        .filter(Customer.tenant_id == tenant_id, Customer.id == debitor_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Debitor nicht gefunden")
    if payload.is_active is not None:
        row.is_active = payload.is_active
    if payload.credit_limit is not None:
        row.credit_limit = payload.credit_limit
    db.commit()
    db.refresh(row)
    return _debitor_dict(row)


@router.get("/finance/kreditoren", response_model=list[TypedObjectOut], summary="Kreditoren auflisten")
@router.get("/finance/creditors", response_model=list[TypedObjectOut], summary="Kreditoren auflisten")
async def list_kreditoren(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    op_map = _op_by_name(db, tenant_id, "kreditoren")
    items = ProcurementService(db, tenant_id).list_lieferanten()
    return [_creditor_from_lieferant(item, op_map.get(item.get("firmenname") or "")) for item in items]


@router.post("/finance/creditors", response_model=TypedObjectOut, status_code=201, summary="Kreditor anlegen")
async def create_kreditor(
    payload: CreditorWrite,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    if not payload.creditor_number or not payload.company_name:
        raise HTTPException(status_code=422, detail="creditor_number und company_name sind Pflicht")
    created = ProcurementService(db, tenant_id).create_lieferant(
        {
            "lieferantennummer": payload.creditor_number,
            "firmenname": payload.company_name,
            "ansprechpartner": payload.contact_person,
            "strasse": payload.street,
            "plz": payload.postal_code,
            "ort": payload.city,
            "land": payload.country or "Deutschland",
            "telefon": payload.phone,
            "email": payload.email,
            "ust_id": payload.vat_id,
            "steuernummer": payload.tax_number,
            "zahlungsziel_tage": payload.payment_terms_days,
            "notiz": payload.notes,
            "aktiv": True if payload.is_active is None else payload.is_active,
        }
    )
    return _creditor_from_lieferant(
        ProcurementService(db, tenant_id).get_lieferant(str(created["id"]))
    )


@router.get("/finance/kreditoren/{kreditor_id}", response_model=TypedObjectOut, summary="Kreditor abrufen")
@router.get("/finance/creditors/{kreditor_id}", response_model=TypedObjectOut, summary="Kreditor abrufen")
async def get_kreditor(
    kreditor_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        lf = ProcurementService(db, tenant_id).get_lieferant(kreditor_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Kreditor nicht gefunden") from exc
    op_map = _op_by_name(db, tenant_id, "kreditoren")
    return _creditor_from_lieferant(lf, op_map.get(lf.get("firmenname") or ""))


@router.put("/finance/creditors/{kreditor_id}", response_model=TypedObjectOut, summary="Kreditor aktualisieren")
@router.patch("/finance/creditors/{kreditor_id}", response_model=TypedObjectOut, summary="Kreditor aktualisieren")
async def update_kreditor(
    kreditor_id: str,
    payload: CreditorWrite,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    mapping = {
        "lieferantennummer": payload.creditor_number,
        "firmenname": payload.company_name,
        "ansprechpartner": payload.contact_person,
        "strasse": payload.street,
        "plz": payload.postal_code,
        "ort": payload.city,
        "land": payload.country,
        "telefon": payload.phone,
        "email": payload.email,
        "ust_id": payload.vat_id,
        "steuernummer": payload.tax_number,
        "zahlungsziel_tage": payload.payment_terms_days,
        "notiz": payload.notes,
        "aktiv": payload.is_active,
    }
    data = {key: value for key, value in mapping.items() if value is not None}
    try:
        ProcurementService(db, tenant_id).update_lieferant(kreditor_id, data)
        lf = ProcurementService(db, tenant_id).get_lieferant(kreditor_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Kreditor nicht gefunden") from exc
    return _creditor_from_lieferant(lf)


@router.delete("/finance/creditors/{kreditor_id}", status_code=204, summary="Kreditor loeschen")
async def delete_kreditor(
    kreditor_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> None:
    try:
        ProcurementService(db, tenant_id).update_lieferant(kreditor_id, {"aktiv": False})
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Kreditor nicht gefunden") from exc
