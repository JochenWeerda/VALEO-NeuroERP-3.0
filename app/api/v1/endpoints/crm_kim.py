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

import time
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_kontakt_service import CrmKontaktService
from app.services.crm_notification_service import CrmNotificationService
from app.services.llm_gateway import LLMGateway

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
    email: Optional[str] = None
    fax: Optional[str] = None
    weeklySchedule: list[bool] = Field(default_factory=list)


class ContactPersonCreate(BaseModel):
    salutation: str = ""
    name: str
    firstName: str = ""
    position: str = ""
    birthdate: Optional[str] = None
    priority: int = 3
    phone1: str = ""
    phone2: Optional[str] = None
    email: Optional[str] = None
    fax: Optional[str] = None
    weeklySchedule: list[bool] = Field(default_factory=list)


class ContactLog(BaseModel):
    id: str
    customerId: str
    direction: str = "OUTGOING"
    date: str = ""
    completed: bool = False
    artKurzinfo: str = ""
    art: Optional[str] = None          # Kontaktart: persoenlich/telefon/email/whatsapp
    betreff: Optional[str] = None      # Betreffzeile (== kurzinfo)
    kommentar: Optional[str] = None    # Freitext-Kommentar (== notiz)
    ccIntern: Optional[str] = None     # interne Weiterleitung (Mitarbeiter/Abteilung)
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


class NeuroSummary(BaseModel):
    healthScore: int = 0
    statusLabel: str = ""
    summary: str = ""
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    engine: str = "fallback"


class NeuroSummaryIn(BaseModel):
    customerId: str


class DraftEmailIn(BaseModel):
    customerId: str
    tone: str = "friendly"


class DraftEmailOut(BaseModel):
    subject: str = ""
    body: str = ""
    engine: str = "fallback"


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
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[Customer]:
    """Kundenliste mit serverseitiger Suche (`q` über Name/Nr/Ort) und Pagination
    (`limit`/`offset`). Default-Limit bewusst klein (kein Voll-Laden des Stammes);
    das Cockpit holt die Liste seitenweise und sucht serverseitig."""
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    sql = _CUST_SELECT
    params: dict[str, Any] = {"lim": limit, "off": offset}
    if q and q.strip():
        sql += " AND (k.name1 ILIKE :q OR k.kunden_nr ILIKE :q OR coalesce(k.ort,'') ILIKE :q)"
        params["q"] = f"%{q.strip()}%"
    sql += " ORDER BY k.name1 LIMIT :lim OFFSET :off"
    rows = _safe(db, sql, params)
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
        "SELECT id, anrede, nachname, vorname, position, prioritaet, telefon1, telefon2, mobil, email, "
        "geburtsdatum FROM public.kunden_ansprechpartner "
        "WHERE kunden_nr = :k ORDER BY prioritaet NULLS LAST, nachname",
        {"k": kunden_nr},
    )
    if not rows:
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
            phone1=d.get("telefon1") or "", phone2=d.get("telefon2"),
            email=d.get("email"), fax=d.get("mobil"),
            weeklySchedule=[],
        ))
    return out


@router.post("/customers/{kunden_nr}/contacts", response_model=StatusOut, summary="Ansprechpartner anlegen")
def create_contact(
    kunden_nr: str,
    body: ContactPersonCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StatusOut:
    # Vorhandene L3-Tabelle: id ist serial (auto), kein tenant_id/wochenplan.
    db.execute(
        text(
            """
            INSERT INTO public.kunden_ansprechpartner
                (kunden_nr, anrede, nachname, vorname, position, prioritaet, telefon1, telefon2, mobil, email)
            VALUES (:k, :anrede, :name, :vorname, :pos, :prio, :t1, :t2, :fax, :email)
            """
        ),
        {
            "k": kunden_nr, "anrede": body.salutation, "name": body.name,
            "vorname": body.firstName, "pos": body.position, "prio": body.priority,
            "t1": body.phone1, "t2": body.phone2, "fax": body.fax, "email": body.email,
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
        # Betreff/Kurzinfo bleibt die Haupt-Anzeige; die Kontaktart wird separat geführt.
        artKurzinfo=kurz or (art if art else ""),
        art=art or None,
        betreff=kurz or None,
        kommentar=r.get("notiz") or None,
        ccIntern=r.get("weiterleitung_an"),
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


_ALLOWED_ARTEN = {"persoenlich", "telefon", "email", "whatsapp", "brief", "fax"}


class LogCreateIn(BaseModel):
    direction: Optional[str] = "OUTGOING"
    art: Optional[str] = None          # persoenlich/telefon/email/whatsapp
    betreff: Optional[str] = None      # Betreffzeile
    kommentar: Optional[str] = None    # Freitext/Kommentar (blob)
    artKurzinfo: Optional[str] = None  # Rueckwaertskompatibel: Kurzinfo, falls kein Betreff
    ccIntern: Optional[str] = None     # interne Weiterleitung (Mitarbeiter/Abteilung)
    operator: Optional[str] = None
    completed: Optional[bool] = None
    reSubmissionDate: Optional[str] = None
    referenceType: Optional[str] = "NONE"
    referenceNo: Optional[str] = None


@router.post("/customers/{kunden_nr}/logs", response_model=StatusOut, summary="Kontakt protokollieren")
def create_log(
    kunden_nr: str,
    body: LogCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StatusOut:
    svc = CrmKontaktService(db, tenant_id)
    art = (body.art or "").strip().lower()
    if art not in _ALLOWED_ARTEN:
        art = "telefon"
    created = svc.create({
        "kunden_nr": kunden_nr,
        "richtung": "ein" if (body.direction or "").upper() == "INCOMING" else "aus",
        "art": art,
        "kurzinfo": body.betreff or body.artKurzinfo,
        "notiz": body.kommentar,
        "bediener": body.operator,
        "wiedervorlage": body.reSubmissionDate or None,
        "weiterleitung_an": body.ccIntern,
        "verweis": body.referenceNo,
    })
    # CC: interne Mitarbeiter/Abteilung (In-App-Postfach) bzw. externer Fachberater (Mail).
    if body.ccIntern:
        try:
            CrmNotificationService(db, tenant_id).dispatch_cc(
                cc=body.ccIntern,
                betreff=body.betreff or body.artKurzinfo,
                kommentar=body.kommentar,
                sender=body.operator,
                kunden_nr=kunden_nr,
                kontakt_id=created.get("id"),
            )
        except Exception:  # Benachrichtigung ist Folgeaktion; Kontakt bleibt gespeichert.
            db.rollback()
    return StatusOut()


@router.put("/contact-logs/{log_id}/completed", response_model=StatusOut, summary="Wiedervorlage erledigen")
def complete_log(
    log_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StatusOut:
    CrmKontaktService(db, tenant_id).set_erledigt(log_id, True)
    return StatusOut()


# ── Benachrichtigungen (internes Postfach + externe Fachberater-Mail) ──────────
class NotificationIn(BaseModel):
    recipient: str                       # interner Empfaenger (Code/Abteilung) oder E-Mail
    betreff: Optional[str] = None
    kommentar: Optional[str] = None
    sender: Optional[str] = None
    kunden_nr: Optional[str] = None
    kontaktId: Optional[str] = None
    channel: Optional[str] = None        # 'internal' | 'email'; None -> Auto (@ => email)


@router.post("/notifications", response_model=dict, summary="Benachrichtigung senden (intern/extern)")
def create_notification(
    body: NotificationIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    svc = CrmNotificationService(db, tenant_id)
    ch = (body.channel or "").strip().lower()
    if ch == "internal":
        return svc.notify_internal(
            recipient=body.recipient, betreff=body.betreff, kommentar=body.kommentar,
            sender=body.sender, kunden_nr=body.kunden_nr, kontakt_id=body.kontaktId,
        )
    if ch == "email":
        return svc.notify_external(
            email=body.recipient, betreff=body.betreff, kommentar=body.kommentar,
            sender=body.sender, kunden_nr=body.kunden_nr, kontakt_id=body.kontaktId,
        )
    return svc.dispatch_cc(
        cc=body.recipient, betreff=body.betreff, kommentar=body.kommentar,
        sender=body.sender, kunden_nr=body.kunden_nr, kontakt_id=body.kontaktId,
    )


@router.get("/notifications", response_model=list[dict], summary="Postfach (interne Benachrichtigungen)")
def list_notifications(
    recipient: str,
    unread: bool = False,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return CrmNotificationService(db, tenant_id).inbox(recipient, only_unread=unread)


@router.post("/notifications/{notification_id}/read", response_model=dict, summary="Benachrichtigung als gelesen markieren")
def read_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmNotificationService(db, tenant_id).mark_read(notification_id)


# ── Kontaktbezogene Belegtabs (Rechnungen/Mahnungen/Kontrakte/Strecken) ────────
class ContactDoc(BaseModel):
    id: str
    kind: str
    docNo: str = ""
    date: str = ""
    dueDate: Optional[str] = None
    amount: float = 0.0
    status: str = ""
    info: Optional[str] = None


_CONTACT_DOC_KINDS = {"invoices", "dunning", "contracts", "drop_shipments"}


def _resolve_partner_id(db: Session, kunden_nr: str) -> str:
    bp = _safe(db, "SELECT business_partner_id FROM public.kunden WHERE kunden_nr = :k", {"k": kunden_nr}, many=False)
    return str(bp["business_partner_id"]) if bp and bp.get("business_partner_id") else kunden_nr


@router.get("/customers/{kunden_nr}/contact-docs", response_model=list[ContactDoc],
            summary="Kontaktbezogene Belege (Rechnungen/Mahnungen/Kontrakte/Strecken)")
def list_contact_docs(
    kunden_nr: str,
    kind: str = "invoices",
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[ContactDoc]:
    kind = (kind or "").strip().lower()
    if kind not in _CONTACT_DOC_KINDS:
        kind = "invoices"

    # Rechnungen + Mahnungen aus der kanonischen Debitoren-OP-Quelle.
    if kind in {"invoices", "dunning"}:
        if db.execute(text("SELECT to_regclass('domain_shared.open_items')")).scalar() is None:
            return []
        pid = _resolve_partner_id(db, kunden_nr)
        overdue = " AND due_date < current_date" if kind == "dunning" else ""
        rows = _safe(
            db,
            f"""
            SELECT id, document_number, document_date, due_date, amount, status
            FROM domain_shared.open_items
            WHERE tenant_id = :t AND type = 'debitor'
              AND lower(coalesce(status,'')) <> 'paid'{overdue}
              AND partner_id = :pid
            ORDER BY due_date DESC LIMIT 100
            """,
            {"t": tenant_id, "pid": pid},
        )
        out: list[ContactDoc] = []
        for r in rows:
            d = dict(r)
            out.append(ContactDoc(
                id=str(d.get("id")), kind=kind,
                docNo=str(d.get("document_number") or ""),
                date=str(d.get("document_date") or ""),
                dueDate=str(d["due_date"]) if d.get("due_date") else None,
                amount=float(d.get("amount") or 0),
                status=str(d.get("status") or "").upper() or "OPEN",
            ))
        return out

    # Kontrakte / Strecken-Geschaefte: kanonische Quelle wird verdrahtet, sobald
    # eindeutig verfuegbar; bis dahin tolerant leer (kein Scheinerfolg).
    return []


# ── Offene Posten (tolerant) ──────────────────────────────────────────────────
@router.get("/customers/{kunden_nr}/financials", response_model=list[OpenItem], summary="Offene Posten")
def list_financials(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[OpenItem]:
    # Kanonische Debitoren-OP-Quelle: domain_shared.open_items (wie finance_followup).
    # partner_id ist die business_partner_id (UUID). Tolerant, falls Tabelle fehlt.
    if db.execute(text("SELECT to_regclass('domain_shared.open_items')")).scalar() is None:
        return []
    bp = _safe(db, "SELECT business_partner_id FROM public.kunden WHERE kunden_nr = :k", {"k": kunden_nr}, many=False)
    pid = str(bp["business_partner_id"]) if bp and bp.get("business_partner_id") else kunden_nr
    from datetime import date as _date
    rows = _safe(
        db,
        """
        SELECT id, document_number, document_date, due_date, amount, status
        FROM domain_shared.open_items
        WHERE tenant_id = :t AND type = 'debitor'
          AND lower(coalesce(status,'')) <> 'paid'
          AND partner_id = :pid
        ORDER BY due_date LIMIT 50
        """,
        {"t": tenant_id, "pid": pid},
    )
    today = _date.today()
    out = []
    for r in rows:
        d = dict(r)
        due = d.get("due_date")
        due_d = due.date() if hasattr(due, "date") else due
        if str(d.get("status") or "").lower() == "paid":
            status = "PAID"
        elif due_d is not None and due_d < today:
            status = "OVERDUE"
        else:
            status = "PENDING"
        out.append(OpenItem(
            id=str(d.get("id")), customerId=kunden_nr,
            invoiceNo=d.get("document_number") or "",
            date=str(d.get("document_date") or ""), dueDate=str(d.get("due_date") or ""),
            amount=float(d.get("amount") or 0), dunningLevel=0,
            status=status,
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


# ── 360°-Dashboard (gebündelt) ────────────────────────────────────────────────
class DashboardMeta(BaseModel):
    timings: dict[str, float]          # ms je Quelle + total
    sourceStatus: dict[str, str]       # ok | error:<Typ> je Quelle


class CustomerDashboard(BaseModel):
    customer: Optional[Customer]
    contacts: list[ContactPerson]
    logs: list[ContactLog]
    financials: list[OpenItem]
    documents: list[BusinessDocument]
    meta: DashboardMeta


@router.get("/customers/{kunden_nr}/dashboard", response_model=CustomerDashboard,
            summary="360°-Dashboard gebündelt (Stammdaten + Ansprechpartner + Historie + OP + Belege)")
def customer_dashboard(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> CustomerDashboard:
    """Bündelt die fünf Einzelströme in EINEN Request (statt vier Roundtrips beim
    Kundenwechsel). Reine Wiederverwendung der bestehenden Endpoint-Funktionen über
    dieselbe DB-Session; jede Quelle ist tolerant (ein Fehlschlag liefert leer +
    Status, kein 500 fürs ganze Dashboard) und liefert ihre Laufzeit in `meta`."""
    timings: dict[str, float] = {}
    status: dict[str, str] = {}

    def _timed(name: str, fn, default):
        t0 = time.perf_counter()
        try:
            value = fn()
            status[name] = "ok"
            return value
        except Exception as exc:  # noqa: BLE001 - tolerant je Quelle (kein Schein-500)
            status[name] = f"error:{type(exc).__name__}"
            return default
        finally:
            timings[name] = round((time.perf_counter() - t0) * 1000, 1)

    t_all = time.perf_counter()
    customer = _timed("customer", lambda: get_customer(kunden_nr, db, tenant_id), None)
    contacts = _timed("contacts", lambda: list_contacts(kunden_nr, db, tenant_id), [])
    logs = _timed("logs", lambda: list_logs(kunden_nr, db, tenant_id), [])
    financials = _timed("financials", lambda: list_financials(kunden_nr, db, tenant_id), [])
    documents = _timed("documents", lambda: list_documents(kunden_nr, db, tenant_id), [])
    timings["total"] = round((time.perf_counter() - t_all) * 1000, 1)

    return CustomerDashboard(
        customer=customer, contacts=contacts, logs=logs,
        financials=financials, documents=documents,
        meta=DashboardMeta(timings=timings, sourceStatus=status),
    )


# ── NeuroAI-Dossier (anbieterunabhängiges LLM-Gateway + Fallback) ─────────────
def _fallback_summary(cust: Customer, outstanding: float, log_count: int, doc_count: int) -> NeuroSummary:
    """Deterministisches, regelbasiertes Dossier ohne LLM (immer verfügbar)."""
    util = (outstanding / cust.creditLimit * 100) if cust.creditLimit > 0 else 0
    gesperrt = any("gesperrt" in m.lower() for m in cust.alertMessages)
    score = 90
    if util > 90 or gesperrt:
        score = 35
    elif util > 60:
        score = 60
    elif util > 30:
        score = 78
    label = "Stabil" if score >= 85 else ("Beobachten" if score >= 60 else "Risiko")
    opportunities, risks = [], []
    if doc_count == 0:
        opportunities.append("Noch keine Belege erfasst — Erstgeschäft/Sortimentseinstieg anbahnen.")
    if cust.revenueStatus in ("A", "B"):
        opportunities.append(f"Umsatzklasse {cust.revenueStatus}: Cross-/Up-Sell im Vollsortiment prüfen.")
    if outstanding > 0:
        risks.append(f"Offener Saldo EUR {outstanding:,.2f}" + (f" (~{util:.0f}% des KV-Limits)" if cust.creditLimit else "") + ".")
    if gesperrt:
        risks.append("Konto gesperrt — keine Lieferungen ohne Freigabe.")
    if cust.chefAnweisung:
        risks.append(f"Chef-Anweisung beachten: {cust.chefAnweisung}")
    summary = (f"**{cust.name}** ({cust.city}) — Umsatzklasse {cust.revenueStatus}, ABC {cust.abcStatus}. "
               f"Offener Saldo EUR {outstanding:,.2f} bei KV-Limit EUR {cust.creditLimit:,.0f}. "
               f"{log_count} Kontakte, {doc_count} Belege in der Historie.")
    return NeuroSummary(healthScore=score, statusLabel=label, summary=summary,
                        opportunities=opportunities or ["Beziehung stabil halten."],
                        risks=risks or ["Keine akuten Risiken erkennbar."], engine="fallback")


@router.post("/neuro-summary", response_model=NeuroSummary, summary="NeuroAI-Kundendossier")
def neuro_summary(
    body: NeuroSummaryIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> NeuroSummary:
    import json
    import re

    cust = get_customer(body.customerId, db, tenant_id)
    if not cust:
        return NeuroSummary(healthScore=0, statusLabel="Unbekannt", summary="Kunde nicht gefunden.")
    ops = list_financials(body.customerId, db, tenant_id)
    outstanding = sum(o.amount for o in ops if o.status != "PAID")
    logs = CrmKontaktService(db, tenant_id).list_by_kunde(body.customerId)
    docs = list_documents(body.customerId, db, tenant_id)
    fallback = _fallback_summary(cust, outstanding, len(logs), len(docs))

    prompt = (
        "Du bist Vertriebsanalyst im Agrarhandel. Erstelle ein knappes 360°-Kundendossier. "
        'Antworte NUR als JSON: {"healthScore":0-100,"statusLabel":"Stabil|Beobachten|Risiko",'
        '"summary":"2-3 Saetze Markdown","opportunities":["..."],"risks":["..."]}.\n\n'
        f"Kunde: {cust.name}, {cust.city}\n"
        f"Umsatzklasse: {cust.revenueStatus}, ABC: {cust.abcStatus}\n"
        f"KV-Limit: {cust.creditLimit:.0f} EUR, offener Saldo: {outstanding:.2f} EUR\n"
        f"Kontakte (Historie): {len(logs)}, Belege: {len(docs)}\n"
        f"Alarme: {', '.join(cust.alertMessages) or 'keine'}\n"
        f"Chef-Anweisung: {cust.chefAnweisung or 'keine'}\n"
    )
    out = LLMGateway(db, tenant_id).complete_or_none(prompt, max_tokens=600)
    if not out:
        return fallback
    try:
        cleaned = re.sub(r"^```(?:json)?|```$", "", out.strip()).strip()
        data = json.loads(cleaned)
        return NeuroSummary(
            healthScore=int(max(0, min(100, data.get("healthScore", fallback.healthScore)))),
            statusLabel=str(data.get("statusLabel") or fallback.statusLabel),
            summary=str(data.get("summary") or fallback.summary),
            opportunities=[str(x) for x in (data.get("opportunities") or [])][:5] or fallback.opportunities,
            risks=[str(x) for x in (data.get("risks") or [])][:5] or fallback.risks,
            engine="llm",
        )
    except Exception:
        return fallback


_TONE_LABEL = {
    "friendly": "freundlich-persönlich", "formal": "professionell-sachlich",
    "mahnend": "höflich-mahnend (Zahlungserinnerung)", "kontraktverhandlung": "kontraktbezogen-verhandelnd",
}


@router.post("/draft-email", response_model=DraftEmailOut, summary="NeuroComms E-Mail-Entwurf")
def draft_email(
    body: DraftEmailIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> DraftEmailOut:
    cust = get_customer(body.customerId, db, tenant_id)
    if not cust:
        return DraftEmailOut(subject="Kunde nicht gefunden", body="")
    tone = _TONE_LABEL.get(body.tone, "freundlich-persönlich")
    chef = f"\nBeachte verbindlich die Chef-Anweisung: {cust.chefAnweisung}" if cust.chefAnweisung else ""
    prompt = (
        f"Schreibe eine {tone}e Geschäfts-E-Mail auf Deutsch an den Agrarkunden "
        f"{cust.name} ({cust.city}). Antworte NUR als JSON "
        '{"subject":"...","body":"..."} ohne Markdown.' + chef
    )
    out = LLMGateway(db, tenant_id).complete_or_none(prompt, max_tokens=700)
    if out:
        import json
        import re
        try:
            data = json.loads(re.sub(r"^```(?:json)?|```$", "", out.strip()).strip())
            return DraftEmailOut(subject=str(data.get("subject") or ""), body=str(data.get("body") or ""), engine="llm")
        except Exception:
            pass
    # Deterministischer Fallback-Entwurf
    subject = f"Ihre Geschäftsbeziehung mit der Hinrich Folkerts Landhandel GmbH"
    anrede = "Sehr geehrte Damen und Herren,"
    body_txt = (
        f"{anrede}\n\nwir möchten uns für die gute Zusammenarbeit bedanken und stehen Ihnen "
        f"für Ihren Bedarf an Futtermitteln, Saatgut, Dünger und Pflanzenschutz gern zur Verfügung. "
        f"Sprechen Sie uns für ein Angebot an.\n\nMit freundlichen Grüßen\nIhr Außendienst-Team"
    )
    if cust.chefAnweisung:
        body_txt += f"\n\n[Intern beachtet: {cust.chefAnweisung}]"
    return DraftEmailOut(subject=subject, body=body_txt, engine="fallback")
