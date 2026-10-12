"""
Sales Credit Notes (Gutschriften) and Returns (Retouren) endpoints.
SALES-DLV-02/03/04: Retouren, Gutschriften, Versand
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Literal, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.customer_sales_eligibility import (
    assert_customer_allowed_for_delivery,
    assert_customer_allowed_for_invoice,
)
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.core.fibu_audit import log_fibu_audit

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema, StatusResponse
from app.documents.router_helpers import get_repository, get_from_store, save_to_store


router = APIRouter(prefix="/sales", tags=["sales", "credit-notes", "returns"])


def _resolve_sales_payload_tenant(payload_tenant_id: Optional[str], tenant_id: str) -> str:
    requested_tenant = (payload_tenant_id or "").strip()
    if requested_tenant and requested_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="Payload belongs to a different tenant")
    return tenant_id


# ---------------------------------------------------------------------------
# Credit Notes
# ---------------------------------------------------------------------------

class CreditNoteLineInput(BaseModel):
    article_number: Optional[str] = None
    description: str
    quantity: Decimal = Field(ge=Decimal("0"))
    unit_price: Decimal = Field(ge=Decimal("0"))
    # Steuerschluessel der Position (``vat_codes.id``). Ohne ihn wird die Gutschrift nicht gebucht.
    tax_code: Optional[str] = None
    # Kein Vorgabewert: Ein Satz, den niemand angegeben hat, ist keine Angabe.
    tax_rate: Optional[Decimal] = None


class CreditNoteLineOut(CreditNoteLineInput):
    id: str
    line_total: Decimal


class CreditNoteBase(BaseModel):
    credit_note_number: str = Field(..., min_length=1, max_length=64)
    customer_id: str
    customer_name: Optional[str] = None
    invoice_reference: Optional[str] = None
    reason: str = Field(..., min_length=1, max_length=500)
    # Brutto. Netto und Umsatzsteuer stehen daneben, sobald sie sich aus den Positionen ergeben.
    total_amount: Decimal = Decimal("0")
    net_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    # Kaufmaennische Rechnungskorrektur (Erloesminderung) oder Gutschrift nach Paragraf 14 UStG
    # (Abrechnung durch den Leistungsempfaenger — keine Erloesminderung).
    correction_type: Literal["rechnungskorrektur", "gutschrift_14_ustg"] = "rechnungskorrektur"
    currency: str = "EUR"
    status: str = "draft"
    notes: Optional[str] = None
    lines: List[CreditNoteLineInput] = Field(default_factory=list)


class CreditNoteCreate(CreditNoteBase):
    tenant_id: Optional[str] = None


class CreditNoteOut(CreditNoteBase):
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Umsatzsteuer der Gutschrift
# ---------------------------------------------------------------------------

CENT = Decimal("0.01")
FORDERUNGSKONTO = "1400"


class Steuerklaerung(Exception):
    """Die Umsatzsteuer der Gutschrift laesst sich nicht eindeutig bestimmen — ein Mensch muss pruefen."""


class Steuergruppe(BaseModel):
    """Alle Positionen eines Steuerschluessels: Netto, Steuer und die Konten dazu."""

    tax_code: str
    satz: Decimal
    netto: Decimal
    steuer: Decimal
    erloeskonto: str
    steuerkonto: Optional[str] = None


def steuergruppen(db: Session, tenant_id: str, zeilen: list[tuple]) -> list[Steuergruppe]:
    """Netto und Umsatzsteuer je Steuerschluessel aus den Positionen ``(nr, tax_code, tax_rate, netto)``.

    Nichts wird angenommen: Fehlt der Schluessel, ist er unbekannt, widerspricht ihm der Satz der
    Position oder fehlt ein Konto, gibt es eine ``Steuerklaerung`` statt einer Buchung. Die Steuer wird
    je Steuersatz auf die Summe der Nettobetraege gerechnet, nicht je Position.
    """
    if not zeilen:
        raise Steuerklaerung("Die Gutschrift hat keine Positionen; die Umsatzsteuer lässt sich nicht bestimmen.")
    ohne = [str(nr) for nr, code, _satz, _netto in zeilen if not (code or "").strip()]
    if ohne:
        raise Steuerklaerung(f"Position {', '.join(ohne)} hat keinen Steuerschlüssel.")

    codes = sorted({str(code).strip() for _nr, code, _satz, _netto in zeilen})
    bekannt = {
        str(r[0]): r
        for r in db.execute(
            text(
                "SELECT id, rate, skr03_account, skr03_revenue_account, is_reverse_charge FROM vat_codes "
                "WHERE id = ANY(:codes) AND (tenant_id = :tid OR tenant_id IS NULL) AND is_active "
                "AND valid_from <= NOW() AND (valid_to IS NULL OR valid_to > NOW())"
            ),
            {"codes": codes, "tid": tenant_id},
        ).fetchall()
    }
    unbekannt = [c for c in codes if c not in bekannt]
    if unbekannt:
        raise Steuerklaerung(f"Steuerschlüssel {', '.join(unbekannt)} ist nicht bekannt oder nicht gültig.")

    netto_je_code: dict[str, Decimal] = {c: Decimal("0") for c in codes}
    for nr, code, satz, netto in zeilen:
        code = str(code).strip()
        satz_des_schluessels = Decimal(str(bekannt[code][1]))
        if satz is not None and Decimal(str(satz)) != satz_des_schluessels:
            raise Steuerklaerung(
                f"Position {nr}: Steuersatz {Decimal(str(satz)).normalize():f} % widerspricht dem "
                f"Steuerschlüssel {code} ({satz_des_schluessels.normalize():f} %)."
            )
        netto_je_code[code] += Decimal(str(netto or 0))

    gruppen: list[Steuergruppe] = []
    for code in codes:
        _id, rate, steuerkonto, erloeskonto, reverse_charge = bekannt[code]
        satz = Decimal(str(rate))
        if reverse_charge:
            raise Steuerklaerung(f"Steuerschlüssel {code} (Reverse Charge) wird nicht automatisch gebucht.")
        if not (erloeskonto or "").strip():
            raise Steuerklaerung(f"Für Steuerschlüssel {code} ist kein Erlöskonto hinterlegt.")
        if satz > 0 and not (steuerkonto or "").strip():
            raise Steuerklaerung(f"Für Steuerschlüssel {code} ist kein Umsatzsteuerkonto hinterlegt.")
        netto = netto_je_code[code].quantize(CENT, rounding=ROUND_HALF_UP)
        gruppen.append(Steuergruppe(
            tax_code=code, satz=satz, netto=netto,
            steuer=(netto * satz / Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP),
            erloeskonto=str(erloeskonto).strip(),
            steuerkonto=str(steuerkonto).strip() if satz > 0 else None,
        ))
    return gruppen


@router.post("/credit-notes", response_model=CreditNoteOut, status_code=201, summary="Credit note anlegen")
async def create_credit_note(
    payload: CreditNoteCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a sales credit note (Gutschrift)."""
    tid = _resolve_sales_payload_tenant(payload.tenant_id, tenant_id)
    assert_customer_allowed_for_invoice(db, tid, payload.customer_id)
    cn_id = uuid7()

    # Netto und Umsatzsteuer aus den Positionen. Ein Entwurf darf unvollstaendig sein — dann bleiben
    # Netto und Steuer leer, und gebucht wird er so nicht. Ein Widerspruch wird gleich abgelehnt.
    netto: Optional[Decimal] = None
    steuer: Optional[Decimal] = None
    total = payload.total_amount
    if payload.lines:
        zeilen = [(i, z.tax_code, z.tax_rate, z.quantity * z.unit_price) for i, z in enumerate(payload.lines, 1)]
        netto = sum((z[3] for z in zeilen), Decimal("0")).quantize(CENT, rounding=ROUND_HALF_UP)
        total = netto
        try:
            gruppen = steuergruppen(db, tid, zeilen)
        except Steuerklaerung as klaerung:
            if "widerspricht" in str(klaerung):
                raise HTTPException(status_code=422, detail=str(klaerung)) from klaerung
        else:
            netto = sum((g.netto for g in gruppen), Decimal("0"))
            steuer = sum((g.steuer for g in gruppen), Decimal("0"))
            total = netto + steuer

    db.execute(
        text("""
            INSERT INTO domain_sales.sales_credit_notes
            (id, tenant_id, credit_note_number, customer_id, customer_name,
             invoice_reference, reason, total_amount, net_amount, tax_amount, correction_type,
             currency, status, notes, created_at, updated_at)
            VALUES (:id, :tid, :cn, :cid, :cname, :iref, :reason,
                    :total, :netto, :steuer, :art, :cur, :status, :notes, NOW(), NOW())
        """),
        {
            "id": cn_id, "tid": tid, "cn": payload.credit_note_number,
            "cid": payload.customer_id, "cname": payload.customer_name,
            "iref": payload.invoice_reference, "reason": payload.reason,
            "total": total, "netto": netto, "steuer": steuer, "art": payload.correction_type,
            "cur": payload.currency, "status": payload.status, "notes": payload.notes,
        },
    )

    for i, line in enumerate(payload.lines, 1):
        line_id = uuid7()
        db.execute(
            text("""
                INSERT INTO domain_sales.sales_credit_note_lines
                (id, credit_note_id, line_number, article_number, description,
                 quantity, unit_price, tax_code, tax_rate, line_total)
                VALUES (:id, :cnid, :ln, :anr, :desc, :qty, :up, :code, :tax,
                        :total)
            """),
            {
                "id": line_id, "cnid": cn_id, "ln": i,
                "anr": line.article_number, "desc": line.description,
                "qty": line.quantity, "up": line.unit_price,
                "code": (line.tax_code or "").strip() or None, "tax": line.tax_rate,
                "total": line.quantity * line.unit_price,
            },
        )

    db.commit()

    # Belegbruch schließen: Original-Rechnung als GUTGESCHRIEBEN markieren
    if payload.invoice_reference:
        try:
            repo = get_repository(db)
            inv = get_from_store("sales_invoice", payload.invoice_reference, repo)
            if inv and inv.get("status") not in ("STORNIERT", "GUTGESCHRIEBEN"):
                inv["status"] = "GUTGESCHRIEBEN"
                save_to_store("sales_invoice", payload.invoice_reference, inv, repo)
        except Exception:  # noqa: BLE001 — Rechnungsstatus-Update nicht kritisch
            pass

    log_fibu_audit(
        db, tid, "create", "sales_credit_note", cn_id,
        {"credit_note_number": payload.credit_note_number, "total": float(total)},
        request=request,
    )
    return CreditNoteOut(
        id=cn_id, tenant_id=tid,
        credit_note_number=payload.credit_note_number,
        customer_id=payload.customer_id, customer_name=payload.customer_name,
        invoice_reference=payload.invoice_reference, reason=payload.reason,
        total_amount=total, net_amount=netto, tax_amount=steuer,
        correction_type=payload.correction_type, currency=payload.currency,
        status=payload.status, notes=payload.notes, lines=payload.lines,
    )


@router.get("/credit-notes", response_model=List[CreditNoteOut], summary="Credit notes auflisten")
async def list_credit_notes(
    tenant_id: str = Depends(get_tenant_id),
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List sales credit notes."""
    where = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if status:
        where.append("status = :status")
        params["status"] = status
    if customer_id:
        where.append("customer_id = :cid")
        params["cid"] = customer_id

    rows = db.execute(
        text(f"""
            SELECT id, tenant_id, credit_note_number, customer_id, customer_name,
                   invoice_reference, reason, total_amount, currency, status, notes,
                   created_at, updated_at, net_amount, tax_amount, correction_type
            FROM domain_sales.sales_credit_notes
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
        """),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    ).fetchall()
    return [
        CreditNoteOut(
            id=str(r[0]), tenant_id=r[1], credit_note_number=r[2],
            customer_id=r[3], customer_name=r[4], invoice_reference=r[5],
            reason=r[6], total_amount=Decimal(str(r[7])),
            currency=r[8], status=r[9], notes=r[10],
            created_at=r[11], updated_at=r[12],
            net_amount=r[13], tax_amount=r[14], correction_type=r[15],
        )
        for r in rows
    ]


@router.delete("/credit-notes/{cn_id}", status_code=204, response_class=Response, response_model=None, summary="Credit note löschen")
async def delete_credit_note(
    cn_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("SELECT id, status FROM domain_sales.sales_credit_notes WHERE id = :id AND tenant_id = :tid"),
        {"id": cn_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Gutschrift nicht gefunden")
    if row[1] not in ("draft", "ENTWURF", None):
        raise HTTPException(status_code=400, detail="Nur Entwürfe können gelöscht werden")
    db.execute(
        text("DELETE FROM domain_sales.sales_credit_notes WHERE id = :id AND tenant_id = :tid"),
        {"id": cn_id, "tid": tenant_id},
    )
    db.commit()


@router.post("/credit-notes/{cn_id}/post", response_model=StatusResponse, summary="Credit note erstellen")
async def post_credit_note(
    cn_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Gutschrift buchen: Erloes netto, Umsatzsteuer getrennt, Forderung brutto — in einer Transaktion.

    Soll  Erloeskonto je Steuerschluessel   Netto
    Soll  Umsatzsteuerkonto je Schluessel   Steuer
    Haben Forderungen                       Brutto

    Die Steuer kommt aus den Positionen und ihrem Steuerschluessel. Fehlt eine Angabe oder widersprechen
    sich Angaben, wird nicht gebucht (409) — die Gutschrift bleibt Entwurf und geht zur Pruefung.

    Bis 12.10.2026 wurde der Kopf zuerst festgeschrieben; die Zeilen trugen Kontonummern statt
    Konto-IDs, scheiterten am Fremdschluessel, und der Fehler wurde verschluckt. Der Gesamtbetrag ging
    ungeteilt gegen das Erloeskonto.
    """
    row = db.execute(
        text(
            "SELECT id, tenant_id, credit_note_number, customer_id, total_amount, status, invoice_reference, "
            "correction_type FROM domain_sales.sales_credit_notes WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": cn_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Gutschrift nicht gefunden")
    if row[5] == "posted":
        raise HTTPException(status_code=400, detail="Gutschrift bereits gebucht")

    assert_customer_allowed_for_invoice(db, tenant_id, str(row[3]))

    def zur_pruefung(grund: str) -> HTTPException:
        return HTTPException(status_code=409, detail=f"Gutschrift nicht gebucht, bitte prüfen: {grund}")

    if row[7] != "rechnungskorrektur":
        raise zur_pruefung(
            "Eine Gutschrift nach § 14 UStG ist eine Abrechnung durch den Leistungsempfänger und keine "
            "Erlösminderung; sie wird nicht über diesen Weg gebucht."
        )

    zeilen = [
        tuple(z) for z in db.execute(
            text(
                "SELECT line_number, tax_code, tax_rate, line_total FROM domain_sales.sales_credit_note_lines "
                "WHERE credit_note_id = :id ORDER BY line_number"
            ),
            {"id": cn_id},
        ).fetchall()
    ]
    try:
        gruppen = steuergruppen(db, tenant_id, zeilen)
    except Steuerklaerung as klaerung:
        raise zur_pruefung(str(klaerung)) from klaerung

    netto = sum((g.netto for g in gruppen), Decimal("0"))
    steuer = sum((g.steuer for g in gruppen), Decimal("0"))
    brutto = netto + steuer
    beleg = Decimal(str(row[4] or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
    if beleg != brutto:
        raise zur_pruefung(
            f"Der Belegbetrag {beleg:.2f} weicht vom Brutto der Positionen {brutto:.2f} ab "
            f"(netto {netto:.2f}, Umsatzsteuer {steuer:.2f})."
        )
    if brutto <= 0:
        raise zur_pruefung("Der Betrag der Gutschrift ist null.")

    # Konten des Mandanten, sonst die des gemeinsamen Rahmens.
    nummern = sorted(
        {FORDERUNGSKONTO}
        | {g.erloeskonto for g in gruppen}
        | {g.steuerkonto for g in gruppen if g.steuerkonto and g.steuer > 0}
    )
    konten: dict[str, str] = {}
    for nummer, konto_id, _eigen in db.execute(
        text(
            "SELECT account_number, id, (tenant_id = :tid) AS eigen FROM domain_erp.chart_of_accounts "
            "WHERE account_number = ANY(:nummern) AND tenant_id IN (:tid, 'system') AND is_active "
            "ORDER BY eigen"
        ),
        {"tid": tenant_id, "nummern": nummern},
    ).fetchall():
        konten[str(nummer)] = str(konto_id)
    fehlend = [n for n in nummern if n not in konten]
    if fehlend:
        raise zur_pruefung(f"Konto {', '.join(fehlend)} fehlt im Kontenplan.")

    buchungszeilen: list[dict] = []
    for g in gruppen:
        if g.netto > 0:
            buchungszeilen.append({
                "konto": konten[g.erloeskonto], "soll": g.netto, "haben": Decimal("0"), "code": g.tax_code,
                "text": f"Gutschrift Erlöskorrektur netto ({g.tax_code})"})
        if g.steuerkonto and g.steuer > 0:
            buchungszeilen.append({
                "konto": konten[g.steuerkonto], "soll": g.steuer, "haben": Decimal("0"), "code": g.tax_code,
                "text": f"Gutschrift Umsatzsteuerberichtigung ({g.tax_code})"})
    buchungszeilen.append({
        "konto": konten[FORDERUNGSKONTO], "soll": Decimal("0"), "haben": brutto, "code": None,
        "text": "Gutschrift Forderungsminderung"})

    je_id = uuid7()
    try:
        db.execute(
            text("""
                INSERT INTO domain_erp.journal_entries
                (id, tenant_id, entry_number, entry_date, posting_date, description,
                 source, status, total_debit, total_credit, reference, created_at, updated_at)
                VALUES (:id, :tid, :en, NOW(), NOW(), :desc,
                        'sales_credit_note', 'posted', :total, :total, :ref, NOW(), NOW())
            """),
            {
                "id": je_id, "tid": row[1],
                "en": f"GS-{row[2]}", "desc": f"Gutschrift {row[2]}",
                "total": brutto, "ref": row[2],
            },
        )
        for nr, zeile in enumerate(buchungszeilen, 1):
            db.execute(
                text("""
                    INSERT INTO domain_erp.journal_entry_lines
                        (id, tenant_id, journal_entry_id, account_id, description, debit, credit,
                         tax_code, line_number, created_at)
                    VALUES (:id, :tid, :jeid, :konto, :text, :soll, :haben, :code, :nr, NOW())
                """),
                {"id": uuid7(), "tid": row[1], "jeid": je_id, "nr": nr, **zeile},
            )
        db.execute(
            text(
                "UPDATE domain_sales.sales_credit_notes SET status = 'posted', net_amount = :netto, "
                "tax_amount = :steuer, updated_at = NOW() WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": cn_id, "tid": tenant_id, "netto": netto, "steuer": steuer},
        )
        # Gemindert wird nur der offene Posten der Rechnung, auf die sich die Gutschrift bezieht —
        # um den Bruttobetrag. (Vorher: jeder offene Posten des Kunden, jeweils um den vollen Betrag.)
        rechnung = (row[6] or "").strip()
        if rechnung:
            db.execute(
                text("""
                    UPDATE domain_erp.offene_posten
                    SET offen = GREATEST(0, offen - :betrag),
                        op_status = CASE WHEN offen - :betrag <= 0 THEN 'geschlossen' ELSE 'teilweise' END
                    WHERE tenant_id = :tid AND konto_typ = 'debitoren' AND rechnungsnr = :rechnung
                      AND op_status NOT IN ('geschlossen', 'ausgeziffert')
                """),
                {"tid": row[1], "betrag": brutto, "rechnung": rechnung},
            )
        db.commit()
    except Exception:
        # Nichts bleibt halb stehen; die Kontosperre uebersetzt der zentrale Behandler (409).
        db.rollback()
        raise

    log_fibu_audit(
        db, row[1], "post", "sales_credit_note", cn_id,
        {"total": float(brutto), "net": float(netto), "tax": float(steuer)}, request=request,
    )
    return StatusResponse(
        success=True,
        message=(
            f"Gutschrift {row[2]} gebucht (Buchung GS-{row[2]}): netto {netto:.2f}, "
            f"Umsatzsteuer {steuer:.2f}, brutto {brutto:.2f}."
        ),
    )


# ---------------------------------------------------------------------------
# Returns / Retouren
# ---------------------------------------------------------------------------

class ReturnBase(BaseModel):
    return_number: str = Field(..., min_length=1, max_length=64)
    customer_id: str
    customer_name: Optional[str] = None
    delivery_note_reference: Optional[str] = None
    invoice_reference: Optional[str] = None
    reason: str = Field(..., min_length=1, max_length=500)
    return_type: str = "full"
    status: str = "open"
    notes: Optional[str] = None


class ReturnCreate(ReturnBase):
    tenant_id: Optional[str] = None


class ReturnOut(ReturnBase):
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@router.post("/returns", response_model=ReturnOut, status_code=201, summary="Return anlegen")
async def create_return(
    payload: ReturnCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a return/Retoure."""
    tid = _resolve_sales_payload_tenant(payload.tenant_id, tenant_id)
    assert_customer_allowed_for_delivery(db, tid, payload.customer_id)
    ret_id = uuid7()
    db.execute(
        text("""
            INSERT INTO domain_sales.sales_returns
            (id, tenant_id, return_number, customer_id, customer_name,
             delivery_note_reference, invoice_reference, reason,
             return_type, status, notes, created_at, updated_at)
            VALUES (:id, :tid, :rn, :cid, :cname, :dnref, :iref, :reason,
                    :rtype, :status, :notes, NOW(), NOW())
        """),
        {
            "id": ret_id, "tid": tid, "rn": payload.return_number,
            "cid": payload.customer_id, "cname": payload.customer_name,
            "dnref": payload.delivery_note_reference,
            "iref": payload.invoice_reference,
            "reason": payload.reason, "rtype": payload.return_type,
            "status": payload.status, "notes": payload.notes,
        },
    )
    db.commit()

    # Belegbruch schließen: Lieferschein und Rechnung als retourniert markieren
    if payload.delivery_note_reference:
        try:
            db.execute(
                text("""
                    UPDATE domain_sales.delivery_notes
                    SET status = 'returned', updated_at = NOW()
                    WHERE (id = :ref OR delivery_note_number = :ref)
                      AND tenant_id = :tid
                      AND status NOT IN ('returned', 'BERECHNET')
                """),
                {"ref": payload.delivery_note_reference, "tid": tid},
            )
            db.commit()
        except Exception:  # noqa: BLE001 — Lieferschein-Update nicht kritisch
            pass

    if payload.invoice_reference:
        try:
            repo = get_repository(db)
            inv = get_from_store("sales_invoice", payload.invoice_reference, repo)
            if inv and inv.get("status") not in ("STORNIERT", "GUTGESCHRIEBEN"):
                inv["status"] = "GUTGESCHRIEBEN"
                save_to_store("sales_invoice", payload.invoice_reference, inv, repo)
        except Exception:  # noqa: BLE001 — Rechnungsstatus-Update nicht kritisch
            pass

    return ReturnOut(id=ret_id, tenant_id=tid, **payload.model_dump(exclude={"tenant_id"}))


@router.get("/returns", response_model=List[ReturnOut], summary="Returns auflisten")
async def list_returns(
    tenant_id: str = Depends(get_tenant_id),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List returns."""
    where = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if status:
        where.append("status = :status")
        params["status"] = status

    rows = db.execute(
        text(f"""
            SELECT id, tenant_id, return_number, customer_id, customer_name,
                   delivery_note_reference, invoice_reference, reason,
                   return_type, status, notes, created_at, updated_at
            FROM domain_sales.sales_returns
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
        """),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    ).fetchall()
    return [
        ReturnOut(
            id=str(r[0]), tenant_id=r[1], return_number=r[2],
            customer_id=r[3], customer_name=r[4],
            delivery_note_reference=r[5], invoice_reference=r[6],
            reason=r[7], return_type=r[8], status=r[9], notes=r[10],
            created_at=r[11], updated_at=r[12],
        )
        for r in rows
    ]


@router.delete("/returns/{return_id}", status_code=204, response_class=Response, response_model=None, summary="Return löschen")
async def delete_return(
    return_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("SELECT id, status FROM domain_sales.sales_returns WHERE id = :id AND tenant_id = :tid"),
        {"id": return_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Retoure nicht gefunden")
    if row[1] == "completed":
        raise HTTPException(status_code=400, detail="Abgeschlossene Retouren können nicht gelöscht werden")
    db.execute(
        text("DELETE FROM domain_sales.sales_returns WHERE id = :id AND tenant_id = :tid"),
        {"id": return_id, "tid": tenant_id},
    )
    db.commit()


@router.patch("/returns/{return_id}/status", response_model=StatusResponse, summary="Return status aktualisieren")
async def update_return_status(
    return_id: str,
    new_status: str = Query(..., description="New status: open, processing, completed, cancelled"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Update return status."""
    valid = {"open", "processing", "completed", "cancelled"}
    if new_status not in valid:
        raise HTTPException(status_code=400, detail=f"Status muss einer von {valid} sein")
    existing = db.execute(
        text("SELECT id FROM domain_sales.sales_returns WHERE id = :id AND tenant_id = :tid"),
        {"id": return_id, "tid": tenant_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Retoure nicht gefunden")
    db.execute(
        text(
            "UPDATE domain_sales.sales_returns SET status = :s, updated_at = NOW() "
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": return_id, "s": new_status, "tid": tenant_id},
    )
    db.commit()
    return {"ok": True, "return_id": return_id, "status": new_status}
