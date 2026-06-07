"""KIM — „Kunde im Mittelpunkt": 360°-CRM-Cockpit-Backend.

Liefert die Datenströme für das führende CRM-Cockpit (`/crm`): Kundenliste,
Stammdaten, Ansprechpartner, Kontakthistorie/Wiedervorlage, offene Posten und
Belege. Mapping auf das Frontend-Datenmodell (Customer/ContactPerson/ContactLog/
OpenItem/BusinessDocument).

Quellen werden wiederverwendet: `public.kunden` (+ Satellit `kunden_crm360` für die
L3-Vertriebsfelder), `kunden_kontakte` (Historie, via CrmKontaktService),
`kunden_ansprechpartner` (Kontaktpersonen), Beleg-/OP-Tabellen (tolerant — fehlende
Tabellen/Daten liefern leere Listen statt 500).
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_kontakt_service import CrmKontaktService

router = APIRouter(prefix="/crm/kim", tags=["crm", "kim", "360"])


# ── Schemas (Frontend-Datenmodell) ────────────────────────────────────────────
class Customer(BaseModel):
    id: str
    name: str
    debtorNo: str
    custGroup: Optional[str] = None
    mainCust: Optional[str] = None
    coAffiliation: Optional[str] = None
    street: str = ""
    zipCode: str = ""
    city: str = ""
    postBox: Optional[str] = None
    phone1: str = ""
    phone2: Optional[str] = None
    fax: Optional[str] = None
    email: str = ""
    homepage: Optional[str] = None
    salesRepresentative: str = ""
    dispatcher: str = ""
    creditLimit: float = 0
    revenueStatus: str = "B"
    abcStatus: str = "B"
    alertMessages: list[str] = Field(default_factory=list)
    chefAnweisung: str = ""
    profileSummary: Optional[str] = None


class ContactPerson(BaseModel):
    id: str
    customerId: str
    salutation: str = ""
    name: str = ""
    firstName: str = ""
    position: str = ""
    birthdate: Optional[str] = None
    priority: int = 3
    phone1: str = ""
    phone2: Optional[str] = None
    fax: Optional[str] = None
    weeklySchedule: list[bool] = Field(default_factory=list)


class ContactLog(BaseModel):
    id: str
    customerId: str
    direction: str = "OUTGOING"
    date: str = ""
    completed: bool = False
    artKurzinfo: str = ""
    operator: str = ""
    reSubmissionDate: Optional[str] = None
    dispatcher: Optional[str] = None
    hasScan: bool = False
    emailSent: bool = False
    referenceType: str = "NONE"
    referenceNo: Optional[str] = None


class OpenItem(BaseModel):
    id: str
    customerId: str
    invoiceNo: str = ""
    date: str = ""
    dueDate: str = ""
    amount: float = 0
    dunningLevel: int = 0
    status: str = "PENDING"
    artKurzinfo: str = ""
    operator: str = ""
    isDropShipment: bool = False


class BusinessDocument(BaseModel):
    id: str
    customerId: str
    type: str = "ORDER"
    docNo: str = ""
    date: str = ""
    operator: str = ""
    representative: str = ""
    plannedDeliveryDate: Optional[str] = None
    netAmount: float = 0
    taxAmount: float = 0
    grossAmount: float = 0
    completed: bool = False


class StatusOut(BaseModel):
    status: str = "success"


class CustomerUpdateIn(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    creditLimit: Optional[float] = None
    salesRepresentative: Optional[str] = None
    dispatcher: Optional[str] = None
    chefAnweisung: Optional[str] = None
    alertMessages: Optional[list[str]] = None


# ── Helpers ───────────────────────────────────────────────────────────────────
def _safe(db: Session, sql: str, params: dict, many: bool = True) -> Any:
    try:
        res = db.execute(text(sql), params)
        return res.mappings().all() if many else res.mappings().first()
    except Exception:
        db.rollback()
        return [] if many else None


def _direction(richtung: Optional[str]) -> str:
    return "INCOMING" if (richtung or "").lower().startswith("ein") else "OUTGOING"


def _customer_from_row(r: dict) -> Customer:
    alerts = r.get("alert_messages") or []
    if isinstance(alerts, str):
        import json
        try:
            alerts = json.loads(alerts)
        except Exception:
            alerts = [alerts] if alerts else []
    return Customer(
        id=r["kunden_nr"],
        name=r.get("name1") or r["kunden_nr"],
        debtorNo=r["kunden_nr"],
        custGroup=r.get("cust_group"),
        coAffiliation=r.get("co_affiliation"),
        street=r.get("strasse") or "",
        zipCode=r.get("plz") or "",
        city=(f"{r.get('plz') or ''} {r.get('ort') or ''}".strip()) or (r.get("ort") or ""),
        phone1=r.get("tel") or "",
        fax=r.get("fax"),
        email=r.get("email") or "",
        homepage=r.get("homepage"),
        salesRepresentative=r.get("sales_rep_vb") or "",
        dispatcher=r.get("dispatcher_disp") or "",
        creditLimit=float(r.get("kv_limit") or 0),
        revenueStatus=r.get("revenue_status") or "B",
        abcStatus=r.get("abc_status") or "B",
        alertMessages=list(alerts),
        chefAnweisung=r.get("chef_anweisung") or "",
        profileSummary=r.get("profile_summary"),
    )


_CUST_SELECT = """
    SELECT k.kunden_nr, k.name1, k.strasse, k.plz, k.ort, k.tel, k.fax, k.email, k.homepage,
           c.kv_limit, c.sales_rep_vb, c.dispatcher_disp, c.abc_status, c.revenue_status,
           c.chef_anweisung, c.alert_messages, c.profile_summary, c.cust_group, c.co_affiliation
    FROM public.kunden k
    LEFT JOIN public.kunden_crm360 c ON c.kunden_nr = k.kunden_nr
    WHERE coalesce(k.geloescht, FALSE) = FALSE
"""


# ── Kundenliste / Stammdaten ──────────────────────────────────────────────────
@router.get("/customers", response_model=list[Customer], summary="Kundenliste (KIM)")
def list_customers(
    limit: int = 500,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[Customer]:
    rows = _safe(db, _CUST_SELECT + " ORDER BY k.name1 LIMIT :lim", {"lim": limit})
    return [_customer_from_row(dict(r)) for r in rows]


@router.get("/customers/{kunden_nr}", response_model=Optional[Customer], summary="Kundenstamm (KIM)")
def get_customer(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Optional[Customer]:
    r = _safe(db, _CUST_SELECT + " AND k.kunden_nr = :k", {"k": kunden_nr}, many=False)
    return _customer_from_row(dict(r)) if r else None


@router.put("/customers/{kunden_nr}", response_model=StatusOut, summary="Kundenstamm bearbeiten (KIM)")
def update_customer(
    kunden_nr: str,
    body: CustomerUpdateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StatusOut:
    import json

    # Adressfelder am kunden-Stamm, Vertriebsfelder am Satellit kunden_crm360.
    if body.street is not None:
        db.execute(text("UPDATE public.kunden SET strasse = :s, geaendert_am = now() WHERE kunden_nr = :k"),
                   {"s": body.street, "k": kunden_nr})
    if body.city is not None:
        db.execute(text("UPDATE public.kunden SET ort = :o, geaendert_am = now() WHERE kunden_nr = :k"),
                   {"o": body.city, "k": kunden_nr})
    # kunden_crm360 ist ein 1:1-Satellit OHNE tenant_id (Konvention: Mandant über
    # business_partner_id am Stamm, nicht am Satelliten).
    db.execute(
        text(
            """
            INSERT INTO public.kunden_crm360
                (kunden_nr, kv_limit, sales_rep_vb, dispatcher_disp, chef_anweisung, alert_messages)
            VALUES (:k, :lim, :vb, :disp, :chef, CAST(:alerts AS jsonb))
            ON CONFLICT (kunden_nr) DO UPDATE SET
                kv_limit = COALESCE(:lim, public.kunden_crm360.kv_limit),
                sales_rep_vb = COALESCE(:vb, public.kunden_crm360.sales_rep_vb),
                dispatcher_disp = COALESCE(:disp, public.kunden_crm360.dispatcher_disp),
                chef_anweisung = COALESCE(:chef, public.kunden_crm360.chef_anweisung),
                alert_messages = COALESCE(CAST(:alerts AS jsonb), public.kunden_crm360.alert_messages),
                updated_at = now()
            """
        ),
        {
            "k": kunden_nr, "lim": body.creditLimit, "vb": body.salesRepresentative,
            "disp": body.dispatcher, "chef": body.chefAnweisung,
            "alerts": json.dumps(body.alertMessages) if body.alertMessages is not None else None,
        },
    )
    db.commit()
    return StatusOut()


# ── Ansprechpartner ───────────────────────────────────────────────────────────
@router.get("/customers/{kunden_nr}/contacts", response_model=list[ContactPerson], summary="Ansprechpartner")
def list_contacts(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[ContactPerson]:
    # Nutzt die vorhandene L3-Tabelle (vorname/nachname/telefon1/anrede/…, kein tenant_id).
    rows = _safe(
        db,
        "SELECT id, anrede, nachname, vorname, position, prioritaet, telefon1, telefon2, mobil, "
        "geburtsdatum FROM public.kunden_ansprechpartner "
        "WHERE kunden_nr = :k ORDER BY prioritaet NULLS LAST, nachname",
        {"k": kunden_nr},
    )
    out = []
    for r in rows:
        d = dict(r)
        out.append(ContactPerson(
            id=str(d["id"]), customerId=kunden_nr,
            salutation=d.get("anrede") or "", name=d.get("nachname") or "",
            firstName=d.get("vorname") or "", position=d.get("position") or "",
            birthdate=str(d["geburtsdatum"]) if d.get("geburtsdatum") else None,
            priority=int(d.get("prioritaet") or 3),
            phone1=d.get("telefon1") or "", phone2=d.get("telefon2"), fax=d.get("mobil"),
            weeklySchedule=[],
        ))
    return out


@router.post("/customers/{kunden_nr}/contacts", response_model=StatusOut, summary="Ansprechpartner anlegen")
def create_contact(
    kunden_nr: str,
    body: ContactPerson,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StatusOut:
    # Vorhandene L3-Tabelle: id ist serial (auto), kein tenant_id/wochenplan.
    db.execute(
        text(
            """
            INSERT INTO public.kunden_ansprechpartner
                (kunden_nr, anrede, nachname, vorname, position, prioritaet, telefon1, telefon2, mobil)
            VALUES (:k, :anrede, :name, :vorname, :pos, :prio, :t1, :t2, :fax)
            """
        ),
        {
            "k": kunden_nr, "anrede": body.salutation, "name": body.name,
            "vorname": body.firstName, "pos": body.position, "prio": body.priority,
            "t1": body.phone1, "t2": body.phone2, "fax": body.fax,
        },
    )
    db.commit()
    return StatusOut()


# ── Kontakthistorie / Wiedervorlage (kunden_kontakte) ─────────────────────────
def _log_from_row(r: dict, kunden_nr: str) -> ContactLog:
    art = r.get("art") or ""
    kurz = r.get("kurzinfo") or ""
    return ContactLog(
        id=str(r["id"]), customerId=kunden_nr,
        direction=_direction(r.get("richtung")),
        date=str(r.get("created_at") or ""),
        completed=bool(r.get("erledigt")),
        artKurzinfo=(f"{art}: {kurz}".strip(": ") if art or kurz else ""),
        operator=r.get("bediener") or "",
        reSubmissionDate=str(r["wiedervorlage"]) if r.get("wiedervorlage") else None,
        dispatcher=r.get("weiterleitung_an"),
        referenceType="NONE", referenceNo=r.get("verweis"),
    )


@router.get("/customers/{kunden_nr}/logs", response_model=list[ContactLog], summary="Kontakthistorie")
def list_logs(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[ContactLog]:
    svc = CrmKontaktService(db, tenant_id)
    return [_log_from_row(r, kunden_nr) for r in svc.list_by_kunde(kunden_nr)]


class LogCreateIn(BaseModel):
    direction: Optional[str] = "OUTGOING"
    artKurzinfo: Optional[str] = None
    operator: Optional[str] = None
    completed: Optional[bool] = None
    reSubmissionDate: Optional[str] = None
    referenceType: Optional[str] = "NONE"


@router.post("/customers/{kunden_nr}/logs", response_model=StatusOut, summary="Kontakt protokollieren")
def create_log(
    kunden_nr: str,
    body: LogCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StatusOut:
    svc = CrmKontaktService(db, tenant_id)
    svc.create({
        "kunden_nr": kunden_nr,
        "richtung": "ein" if (body.direction or "").upper() == "INCOMING" else "aus",
        "art": "telefon",
        "kurzinfo": body.artKurzinfo,
        "bediener": body.operator,
        "wiedervorlage": body.reSubmissionDate or None,
    })
    return StatusOut()


@router.put("/contact-logs/{log_id}/completed", response_model=StatusOut, summary="Wiedervorlage erledigen")
def complete_log(
    log_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StatusOut:
    CrmKontaktService(db, tenant_id).set_erledigt(log_id, True)
    return StatusOut()


# ── Offene Posten (tolerant) ──────────────────────────────────────────────────
@router.get("/customers/{kunden_nr}/financials", response_model=list[OpenItem], summary="Offene Posten")
def list_financials(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[OpenItem]:
    # business_partner_id für die UUID-basierten Finanztabellen auflösen.
    bp = _safe(db, "SELECT business_partner_id FROM public.kunden WHERE kunden_nr = :k", {"k": kunden_nr}, many=False)
    cid = str(bp["business_partner_id"]) if bp and bp.get("business_partner_id") else kunden_nr
    rows = _safe(
        db,
        """
        SELECT id, invoice_number, created_at, due_date, amount, status, dunning_level
        FROM open_items
        WHERE customer_id = :cid AND status NOT IN ('PAID','CANCELLED')
        ORDER BY due_date LIMIT 50
        """,
        {"cid": cid},
    )
    out = []
    for r in rows:
        d = dict(r)
        out.append(OpenItem(
            id=str(d.get("id")), customerId=kunden_nr,
            invoiceNo=d.get("invoice_number") or "",
            date=str(d.get("created_at") or ""), dueDate=str(d.get("due_date") or ""),
            amount=float(d.get("amount") or 0), dunningLevel=int(d.get("dunning_level") or 0),
            status=d.get("status") or "PENDING",
        ))
    return out


# ── Belege (tolerant: sales_orders + portal customer_orders) ──────────────────
@router.get("/customers/{kunden_nr}/documents", response_model=list[BusinessDocument], summary="Belege")
def list_documents(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[BusinessDocument]:
    bp = _safe(db, "SELECT business_partner_id FROM public.kunden WHERE kunden_nr = :k", {"k": kunden_nr}, many=False)
    cid = str(bp["business_partner_id"]) if bp and bp.get("business_partner_id") else kunden_nr
    rows = _safe(
        db,
        """
        SELECT id, order_number, status, total_amount, created_at
        FROM domain_crm.sales_orders
        WHERE customer_id = :cid AND deleted_at IS NULL
        ORDER BY created_at DESC LIMIT 50
        """,
        {"cid": cid},
    )
    out = []
    for r in rows:
        d = dict(r)
        gross = float(d.get("total_amount") or 0)
        out.append(BusinessDocument(
            id=str(d.get("id")), customerId=kunden_nr, type="ORDER",
            docNo=d.get("order_number") or "", date=str(d.get("created_at") or ""),
            netAmount=round(gross / 1.19, 2), taxAmount=round(gross - gross / 1.19, 2),
            grossAmount=gross,
            completed=str(d.get("status") or "").lower() in ("abgeschlossen", "completed", "geliefert"),
        ))
    return out
