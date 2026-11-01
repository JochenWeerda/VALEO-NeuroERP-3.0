"""Finance-Stamm fuer Debitoren und Kreditoren — Maskengenerator und Listen."""

from __future__ import annotations

from app.auth.finance_roles import finance_admin, finance_write
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import EmailStr, Field
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema, TypedObjectOut
from app.api.v1.schemas.mask_entity_contracts import FinanceDebitorOut, FinanceKreditorOut
from app.core.database import get_db
from app.api.v1.endpoints.creditors import _validate_iban
from app.api.v1.endpoints.debtors import _validate_vat_id_format
from app.api.v1.schemas.crm import CustomerCreate
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.tenant import get_tenant_id
from app.infrastructure.models import Customer
from app.services.customer_service import CustomerService
from app.services.procurement_service import ProcurementService

router = APIRouter(tags=["finance", "stammdaten"])


class DebitorPatch(BaseSchema):
    is_active: Optional[bool] = None
    credit_limit: Optional[float] = None


class DebitorCreate(BaseSchema):
    """Debitor-Anlage; Felder ausser den Altfeldern unten haelt der fuehrende Kundenstamm."""

    debtor_number: str = Field(..., min_length=1, max_length=50)
    company_name: str = Field(..., min_length=1, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=100)
    street: Optional[str] = Field(None, max_length=200)
    postal_code: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    vat_id: Optional[str] = Field(None, max_length=50)
    payment_terms_days: Optional[int] = Field(None, ge=0)
    credit_limit: Optional[float] = Field(None, ge=0)
    is_active: bool = True
    tenant_id: Optional[str] = None
    # Rollenfelder (Stufe 3): Bank, Skonto und Steuernummer fuehrt der Geschaeftspartner.
    tax_number: Optional[str] = Field(None, max_length=50)
    iban: Optional[str] = Field(None, max_length=34)
    bic: Optional[str] = Field(None, max_length=11)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_holder: Optional[str] = Field(None, max_length=255)
    discount_days: Optional[int] = Field(None, ge=0)
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    # Altfeld aus domain_erp.debitors ohne Ziel: gefuellt wird es abgelehnt statt still verworfen.
    notes: Optional[str] = None


_NICHT_GEHALTENE_DEBITORFELDER = ("notes",)


def _partner_rollenfelder(payload: Any) -> dict[str, Any]:
    """Bank, Skonto und Steuernummer einer Debitor- oder Kreditoranlage fuer den Geschaeftspartner."""
    _validate_iban(payload.iban)
    return {"iban": payload.iban, "bic": payload.bic, "bank_name": payload.bank_name,
            "account_holder": payload.account_holder, "cash_discount_days": payload.discount_days,
            "cash_discount_percent": payload.discount_percent, "tax_number": payload.tax_number}


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
    # Rollenfelder (Stufe 3) am Geschaeftspartner; nur bei der Anlage.
    iban: Optional[str] = Field(None, max_length=34)
    bic: Optional[str] = Field(None, max_length=11)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_holder: Optional[str] = Field(None, max_length=255)
    discount_days: Optional[int] = Field(None, ge=0)
    discount_percent: Optional[float] = Field(None, ge=0, le=100)


#: Kennungen, mit denen offene Posten ihren Debitor bzw. Kreditor nennen (je nach Schreiber verschieden).
_OP_ID_SPALTEN = ("debtor_id", "kunde_id", "creditor_id", "lieferant_id", "partner_id")
_OP_SPALTEN_JE_DB: dict[str, tuple[str, ...]] = {}


def _op_id_spalten(db: Session) -> tuple[str, ...]:
    # Die gewachsene Entwicklungsdatenbank hat partner_id an offene_posten nicht; frisch migriert ist sie da.
    bind = db.get_bind()
    key = str(getattr(bind, "engine", bind).url)
    if key not in _OP_SPALTEN_JE_DB:
        vorhanden = set(db.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = 'domain_erp' "
            "AND table_name = 'offene_posten'")).scalars().all())
        _OP_SPALTEN_JE_DB[key] = tuple(c for c in _OP_ID_SPALTEN if c in vorhanden)
    return _OP_SPALTEN_JE_DB[key]


def _op_zuordner(spalten: tuple[str, ...], saetze: list[tuple]) -> Any:
    """Liefert zu einer OP-Zeile die ID des Satzes, dem sie eindeutig gehoert, sonst None (Regel: _op_zuordnung)."""
    kennung: dict[str, set[str]] = {}
    namen: dict[str, set[str]] = {}
    for satz_id, nummer, partner_id, name in saetze:
        for wert in (satz_id, nummer, partner_id):
            if wert:
                kennung.setdefault(str(wert), set()).add(str(satz_id))
        namen.setdefault((name or "").strip().lower(), set()).add(str(satz_id))

    def ziel_von(row: Any) -> Optional[str]:
        ziele: set[str] = set()
        for spalte in spalten:
            if row[spalte]:
                ziele |= kennung.get(str(row[spalte]), set())
        if not ziele and row["name"]:
            ziele = namen.get(str(row["name"]).strip().lower(), set())
        return next(iter(ziele)) if len(ziele) == 1 else None

    return ziel_von


def offene_posten_registerseite(db: Session, tenant_id: str, konto_typ: str, satz_id: str, *,
                                page: int, page_size: int) -> dict[str, Any]:
    """Register "Offene Posten" der Debitor- bzw. Kreditor-Maske nach derselben Zuordnung wie die Liste.

    Bis 01.11.2026 war das Register ein leerer Stub."""
    saetze = (_debitor_saetze(db, tenant_id) if konto_typ == "debitoren"
              else _kreditor_saetze(ProcurementService(db, tenant_id).list_lieferanten()))
    spalten = _op_id_spalten(db)
    auswahl = "".join(f"{c}, " for c in spalten)  # Spaltennamen aus _OP_ID_SPALTEN
    try:
        rows = db.execute(
            text(f"SELECT id, {auswahl}COALESCE(kunde_name, lieferant_name, '') AS name, "  # nosec B608
                 "rechnungsnr, COALESCE(rechnungsdatum, datum) AS datum, COALESCE(faelligkeit, due_date) AS faellig, "
                 "COALESCE(offen, open_amount, betrag, 0) AS betrag, op_status FROM domain_erp.offene_posten "
                 "WHERE tenant_id = :t AND konto_typ = :k AND COALESCE(op_status,'') <> 'storniert' "
                 "ORDER BY COALESCE(faelligkeit, due_date) NULLS LAST, id"),  # reviewed-safe: feste Spalten
            {"t": tenant_id, "k": konto_typ},
        ).mappings().fetchmany(100_000)
    except (ProgrammingError, OperationalError):
        db.rollback()
        rows = []
    ziel_von = _op_zuordner(spalten, saetze)
    eigene = [r for r in rows if ziel_von(r) == str(satz_id)]
    start = max(page - 1, 0) * page_size
    return {
        "tab_key": "offene_posten", "table_key": "offene_posten", "page": page, "limit": page_size,
        "total": len(eigene),
        "items": [{"id": str(r["id"]), "beleg_nr": r["rechnungsnr"], "datum": r["datum"], "faellig": r["faellig"],
                   "betrag": float(r["betrag"] or 0), "status": r["op_status"]}
                  for r in eigene[start:start + page_size]],
    }


def _op_zuordnung(db: Session, tenant_id: str, konto_typ: str,
                  saetze: list[tuple[str, Optional[str], Optional[str], Optional[str]]]) -> dict[str, dict[str, Any]]:
    """Offene Posten je Debitor/Kreditor (Stufe 4 Geschaeftspartnerstamm).

    ``saetze``: (ID, Nummer, Partner-ID, Name) aller Debitoren bzw. Kreditoren des Mandanten. Ein Posten gehoert
    dem Satz, auf den seine Kennungen (ID, Nummer oder Partner-ID) eindeutig zeigen. Nur wenn keine Kennung auf
    einen Satz zeigt, entscheidet der Name, und auch das nur, wenn genau ein Satz so heisst. Bis 01.11.2026
    summierte die Liste nach Namen: zwei gleichnamige Kunden teilten sich ihre Forderungen.
    """
    spalten = _op_id_spalten(db)
    auswahl = "".join(f"{c}, " for c in spalten)  # Spaltennamen aus _OP_ID_SPALTEN
    try:
        rows = db.execute(
            text(
                f"SELECT {auswahl}COALESCE(kunde_name, lieferant_name, '') AS name, "  # nosec B608
                "SUM(COALESCE(betrag, 0)) AS gesamt, "
                "SUM(COALESCE(offen, open_amount, betrag, 0)) AS offen, "
                "MIN(COALESCE(faelligkeit, due_date)) AS faellig, "
                "MAX(COALESCE(dunning_level, 0)) AS mahnstufe "
                "FROM domain_erp.offene_posten "
                "WHERE tenant_id = :t AND konto_typ = :k "
                "AND COALESCE(op_status,'') <> 'storniert' "
                f"GROUP BY {auswahl}COALESCE(kunde_name, lieferant_name, '')"  # reviewed-safe: feste Spalten
            ),
            {"t": tenant_id, "k": konto_typ},
        ).mappings().fetchmany(100_000)
    except (ProgrammingError, OperationalError):
        # OP-Tabelle darf die Stammliste nicht blockieren — Debitor bleibt sichtbar.
        db.rollback()
        return {}
    ziel_von = _op_zuordner(spalten, saetze)
    summe: dict[str, dict[str, Any]] = {}
    for row in rows:
        satz = ziel_von(row)
        if satz is None:
            continue  # mehrdeutig oder unbekannt: lieber keine als eine falsche Zuordnung
        ziel = summe.setdefault(satz, {"gesamtForderung": 0.0, "offenerBetrag": 0.0,
                                                    "faelligkeit": None, "mahnstufe": 0})
        ziel["gesamtForderung"] += float(row["gesamt"] or 0)
        ziel["offenerBetrag"] += float(row["offen"] or 0)
        faellig = row["faellig"].isoformat()[:10] if row["faellig"] else None
        if faellig and (ziel["faelligkeit"] is None or faellig < ziel["faelligkeit"]):
            ziel["faelligkeit"] = faellig
        ziel["mahnstufe"] = max(ziel["mahnstufe"], int(row["mahnstufe"] or 0))
    return summe


def _debitor_saetze(db: Session, tenant_id: str) -> list[tuple]:
    return [tuple(r) for r in db.execute(
        text("SELECT id, customer_number, business_partner_id, company_name FROM domain_crm.customers "
             "WHERE tenant_id = :t AND deleted_at IS NULL"), {"t": tenant_id}).fetchmany(100_000)]


def _partnernummern(db: Session, tenant_id: str) -> dict[str, str]:
    return {str(r[0]): r[1] for r in db.execute(
        text("SELECT partner_id, partner_number FROM domain_crm.business_partners WHERE tenant_id = :t"),
        {"t": tenant_id}).fetchmany(100_000)}


def _kreditor_saetze(items: list[dict[str, Any]]) -> list[tuple]:
    return [(str(i.get("id")), i.get("lieferantennummer"), i.get("partner_id"), i.get("firmenname")) for i in items]


def _partner_felder(db: Session, tenant_id: str, partner_id: Optional[str]) -> dict[str, Any]:
    """Bank, Skonto und Partnernummer vom Geschaeftspartner (Stufe 3); leer ohne Partner."""
    if not partner_id:
        return {}
    row = db.execute(
        text("SELECT partner_number, iban, bic, bank_name, account_holder, cash_discount_days, "
             "cash_discount_percent FROM domain_crm.business_partners WHERE partner_id = :p AND tenant_id = :t"),
        {"p": str(partner_id), "t": tenant_id},
    ).mappings().first()
    if row is None:
        return {}
    return {"geschaeftspartner_nr": row["partner_number"], "iban": row["iban"], "bic": row["bic"],
            "bank": row["bank_name"], "kontoinhaber": row["account_holder"],
            "skonto_tage": row["cash_discount_days"],
            "skonto_prozent": float(row["cash_discount_percent"]) if row["cash_discount_percent"] is not None else None}


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
    op_map = _op_zuordnung(db, tenant_id, "debitoren", _debitor_saetze(db, tenant_id))
    rows = (
        db.query(Customer)
        .filter(Customer.tenant_id == tenant_id, Customer.deleted_at.is_(None))
        .order_by(Customer.company_name)
        .all()
    )
    partner = _partnernummern(db, tenant_id)
    return [{**_debitor_dict(row, op_map.get(str(row.id))),
             "geschaeftspartner_nr": partner.get(str(row.business_partner_id or ""))} for row in rows]


@router.get("/finance/debitoren/{debitor_id}", response_model=FinanceDebitorOut, summary="Debitor abrufen")
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
    op_map = _op_zuordnung(db, tenant_id, "debitoren", _debitor_saetze(db, tenant_id))
    return {**_debitor_dict(row, op_map.get(str(row.id))),
            **_partner_felder(db, tenant_id, row.business_partner_id)}


@router.post("/finance/debitoren", response_model=TypedObjectOut, status_code=201, summary="Debitor anlegen", dependencies=[Depends(finance_write)])
@router.post("/finance/debtors/", response_model=TypedObjectOut, status_code=201, summary="Debitor anlegen", dependencies=[Depends(finance_write)])
async def create_debitor(
    payload: DebitorCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Legt den Debitor im fuehrenden Kundenstamm an - dieselbe Fachaktion wie die Kundenanlage im CRM.

    Bis 01.11.2026 schrieb die Anlage in domain_erp.debitors, Liste und Detail lasen domain_crm.customers:
    ein neuer Debitor erschien nie in der Liste, und die Detailmaske nach der Anlage meldete 404."""
    if payload.tenant_id is not None and payload.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant context mismatch")
    _validate_vat_id_format(payload.vat_id)
    gefuellt = [k for k in _NICHT_GEHALTENE_DEBITORFELDER if getattr(payload, k) not in (None, "", 0)]
    if gefuellt:
        raise HTTPException(
            status_code=422,
            detail=f"Diese Felder haben kein Ziel im Stamm: {', '.join(gefuellt)}.",
        )
    kunde = CustomerCreate(
        customer_number=payload.debtor_number.strip(),
        company_name=payload.company_name.strip(),
        contact_person=payload.contact_person,
        email=payload.email,
        phone=payload.phone,
        address=payload.street,
        city=payload.city,
        postal_code=payload.postal_code,
        country=payload.country,
        tax_id=payload.vat_id,
        payment_terms=payload.payment_terms_days,
        credit_limit=payload.credit_limit,
        is_active=payload.is_active,
    )
    try:
        created = await CustomerService(db, tenant_id).create_customer(kunde, _partner_rollenfelder(payload))
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Kundenstamm hat die Anlage abgelehnt") from exc
    row = (
        db.query(Customer)
        .filter(Customer.tenant_id == tenant_id, Customer.id == str(created["id"]))
        .first()
    )
    if row is None:
        raise HTTPException(status_code=500, detail="Debitor angelegt, aber im Kundenstamm nicht lesbar")
    return _debitor_dict(row)


@router.patch("/finance/debitoren/{debitor_id}", response_model=TypedObjectOut, summary="Debitor aktualisieren", dependencies=[Depends(finance_write)])
@router.patch("/finance/debtors/{debitor_id}", response_model=TypedObjectOut, summary="Debitor aktualisieren", dependencies=[Depends(finance_write)])
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
    items = ProcurementService(db, tenant_id).list_lieferanten()
    op_map = _op_zuordnung(db, tenant_id, "kreditoren", _kreditor_saetze(items))
    partner = _partnernummern(db, tenant_id)
    return [{**_creditor_from_lieferant(item, op_map.get(str(item.get("id")))),
             "geschaeftspartner_nr": partner.get(str(item.get("partner_id") or ""))} for item in items]


@router.post("/finance/creditors", response_model=TypedObjectOut, status_code=201, summary="Kreditor anlegen", dependencies=[Depends(finance_write)])
async def create_kreditor(
    payload: CreditorWrite,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    if not payload.creditor_number or not payload.company_name:
        raise HTTPException(status_code=422, detail="creditor_number und company_name sind Pflicht")
    try:
        created = _lieferant_anlegen(db, tenant_id, payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _creditor_from_lieferant(
        ProcurementService(db, tenant_id).get_lieferant(str(created["id"]))
    )


def _lieferant_anlegen(db: Session, tenant_id: str, payload: CreditorWrite) -> dict[str, Any]:
    return ProcurementService(db, tenant_id).create_lieferant(
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
        },
        _partner_rollenfelder(payload),
    )


@router.get("/finance/kreditoren/{kreditor_id}", response_model=FinanceKreditorOut, summary="Kreditor abrufen")
@router.get("/finance/creditors/{kreditor_id}", response_model=FinanceKreditorOut, summary="Kreditor abrufen")
async def get_kreditor(
    kreditor_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        lf = ProcurementService(db, tenant_id).get_lieferant(kreditor_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Kreditor nicht gefunden") from exc
    op_map = _op_zuordnung(db, tenant_id, "kreditoren",
                           _kreditor_saetze(ProcurementService(db, tenant_id).list_lieferanten()))
    return {**_creditor_from_lieferant(lf, op_map.get(str(lf.get("id")))),
            **_partner_felder(db, tenant_id, lf.get("partner_id"))}


@router.put("/finance/creditors/{kreditor_id}", response_model=TypedObjectOut, summary="Kreditor aktualisieren", dependencies=[Depends(finance_write)])
@router.patch("/finance/creditors/{kreditor_id}", response_model=TypedObjectOut, summary="Kreditor aktualisieren", dependencies=[Depends(finance_write)])
async def update_kreditor(
    kreditor_id: str,
    payload: CreditorWrite,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    am_partner = [k for k in ("iban", "bic", "bank_name", "account_holder", "discount_days", "discount_percent")
                  if getattr(payload, k) not in (None, "")]
    if am_partner:
        # Bank und Skonto liegen am Geschaeftspartner; hier geaendert wuerden sie still verworfen.
        raise HTTPException(status_code=422, detail=f"Diese Felder werden am Geschaeftspartner gepflegt: "
                                                    f"{', '.join(am_partner)}.")
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


@router.delete("/finance/creditors/{kreditor_id}", status_code=204, summary="Kreditor loeschen", dependencies=[Depends(finance_admin)])
async def delete_kreditor(
    kreditor_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> None:
    try:
        ProcurementService(db, tenant_id).update_lieferant(kreditor_id, {"aktiv": False})
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Kreditor nicht gefunden") from exc
