"""
Sales Credit Notes (Gutschriften) and Returns (Retouren) endpoints.
SALES-DLV-02/03/04: Retouren, Gutschriften, Versand
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, List, Optional

from fastapi import Body, Response, APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.finance_roles import beleg_read, beleg_write
from app.core.database import get_db
from app.core.exceptions import kontosperre_meldung
from app.services.customer_sales_eligibility import (
    assert_customer_allowed_for_delivery,
    assert_customer_allowed_for_invoice,
)
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.core.fibu_audit import log_fibu_audit
from app.finance.steuerschluessel import CENT, Steuerklaerung, steuergruppen
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema, StatusResponse
from app.api.v1.schemas.sales_credit_notes_schemas import (
    CreditNoteLineInput,
    CreditNoteLineOut,
    CreditNoteCreate,
    CreditNoteOut,
    SteuerVorschauIn,
    SteuerVorschauGruppe,
    SteuerVorschauOut,
    CreditNoteDetailOut,
)
from app.documents.router_helpers import eigener_beleg, get_repository, save_to_store


router = APIRouter(prefix="/sales", tags=["sales", "credit-notes", "returns"])


def _resolve_sales_payload_tenant(payload_tenant_id: Optional[str], tenant_id: str) -> str:
    requested_tenant = (payload_tenant_id or "").strip()
    if requested_tenant and requested_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="Payload belongs to a different tenant")
    return tenant_id


# ---------------------------------------------------------------------------
# Credit Notes
# ---------------------------------------------------------------------------

FORDERUNGSKONTO = "1400"


def _zeilen(lines: List[CreditNoteLineInput]) -> list[tuple]:
    return [(i, z.tax_code, z.tax_rate, z.quantity * z.unit_price) for i, z in enumerate(lines, 1)]


def _lege_an(db: Session, tid: str, payload: CreditNoteCreate) -> dict:
    """Schreibt Gutschrift und Positionen als Entwurf (ohne Festschreiben) und gibt die Betraege zurueck.

    Netto und Umsatzsteuer kommen aus den Positionen. Ein Entwurf darf unvollstaendig sein — dann bleiben
    Netto und Steuer leer, und gebucht wird er so nicht. Ein Widerspruch wird gleich abgelehnt.
    """
    assert_customer_allowed_for_invoice(db, tid, payload.customer_id)
    cn_id = uuid7()

    netto: Optional[Decimal] = None
    steuer: Optional[Decimal] = None
    total = payload.total_amount
    if payload.lines:
        zeilen = _zeilen(payload.lines)
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
        db.execute(
            text("""
                INSERT INTO domain_sales.sales_credit_note_lines
                (id, credit_note_id, line_number, article_number, description,
                 quantity, unit_price, tax_code, tax_rate, line_total)
                VALUES (:id, :cnid, :ln, :anr, :desc, :qty, :up, :code, :tax,
                        :total)
            """),
            {
                "id": uuid7(), "cnid": cn_id, "ln": i,
                "anr": line.article_number, "desc": line.description,
                "qty": line.quantity, "up": line.unit_price,
                "code": (line.tax_code or "").strip() or None, "tax": line.tax_rate,
                "total": line.quantity * line.unit_price,
            },
        )
    return {"id": cn_id, "total": total, "netto": netto, "steuer": steuer}


@router.post("/credit-notes", response_model=CreditNoteOut, status_code=201, summary="Credit note anlegen",
             dependencies=[Depends(beleg_write)])
async def create_credit_note(
    payload: CreditNoteCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a sales credit note (Gutschrift)."""
    tid = _resolve_sales_payload_tenant(payload.tenant_id, tenant_id)
    angelegt = _lege_an(db, tid, payload)
    cn_id, total, netto, steuer = angelegt["id"], angelegt["total"], angelegt["netto"], angelegt["steuer"]
    db.commit()

    # Belegbruch schließen: Original-Rechnung als GUTGESCHRIEBEN markieren
    if payload.invoice_reference:
        try:
            repo = get_repository(db)
            inv = eigener_beleg("sales_invoice", payload.invoice_reference, tid, repo)
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


@router.post("/credit-notes/steuer-vorschau", response_model=SteuerVorschauOut,
             summary="Umsatzsteuer der Positionen berechnen (liest nur)", dependencies=[Depends(beleg_read)])
async def steuer_vorschau(
    payload: SteuerVorschauIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Rechnet Netto, Umsatzsteuer und Brutto je Steuerschluessel — mit derselben Stelle wie die Buchung.

    Die Maske rechnet nicht selbst. Laesst sich die Steuer nicht bestimmen, steht der Grund in
    ``pruefgrund``, und Steuer und Brutto bleiben leer.
    """
    zeilen = _zeilen(payload.lines)
    netto = sum((z[3] for z in zeilen), Decimal("0")).quantize(CENT, rounding=ROUND_HALF_UP)
    try:
        gruppen = steuergruppen(db, tenant_id, zeilen)
    except Steuerklaerung as klaerung:
        return SteuerVorschauOut(geklaert=False, pruefgrund=str(klaerung), netto=netto)
    steuer = sum((g.steuer for g in gruppen), Decimal("0"))
    return SteuerVorschauOut(
        geklaert=True, netto=netto, steuer=steuer, brutto=netto + steuer,
        gruppen=[
            SteuerVorschauGruppe(tax_code=g.tax_code, satz=g.satz, netto=g.netto, steuer=g.steuer,
                                 brutto=g.netto + g.steuer)
            for g in gruppen
        ],
    )


_LISTE_SPALTEN = (
    "id, tenant_id, credit_note_number, customer_id, customer_name, invoice_reference, reason, "
    "total_amount, currency, status, notes, created_at, updated_at, net_amount, tax_amount, correction_type"
)


def _aus_zeile(r, lines: Optional[list] = None) -> dict:
    return {
        "id": str(r[0]), "tenant_id": r[1], "credit_note_number": r[2],
        "customer_id": r[3], "customer_name": r[4], "invoice_reference": r[5],
        "reason": r[6], "total_amount": Decimal(str(r[7] or 0)),
        "currency": r[8], "status": r[9], "notes": r[10],
        "created_at": r[11], "updated_at": r[12],
        "net_amount": r[13], "tax_amount": r[14], "correction_type": r[15],
        "lines": lines or [],
    }


@router.get("/credit-notes", response_model=List[CreditNoteOut], summary="Credit notes auflisten",
            dependencies=[Depends(beleg_read)])
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
            SELECT {_LISTE_SPALTEN}
            FROM domain_sales.sales_credit_notes
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
        """),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    ).fetchall()
    return [CreditNoteOut(**_aus_zeile(r)) for r in rows]


# ---------------------------------------------------------------------------
# Buchungsvorschlaege von Agenten: Ein Mensch prueft und gibt frei
# ---------------------------------------------------------------------------

VORSCHLAG_ART = "sales_credit_note_buchung"


class BuchungsvorschlagOut(BaseModel):
    """Vorschlag eines Agenten, eine Gutschrift zu buchen — mit dem, was gebucht wuerde."""

    proposal_id: str
    credit_note_id: str
    credit_note_number: str
    netto: Decimal
    steuer: Decimal
    brutto: Decimal
    approval_status: str
    vorgeschlagen_von: Optional[str] = None
    vorgeschlagen_am: Optional[datetime] = None
    geprueft_von: Optional[str] = None
    geprueft_am: Optional[datetime] = None
    ablehnungsgrund: Optional[str] = None
    gebucht: bool = False


def _schnappschuss(wert: Any) -> dict[str, Any]:
    if isinstance(wert, str):
        wert = json.loads(wert)
    return wert if isinstance(wert, dict) else {}


def _vorschlag(db: Session, tenant_id: str, proposal_id: str, *, sperren: bool = False):
    """Der Buchungsvorschlag des Mandanten — einen fremden oder einen anderer Art gibt es hier nicht."""
    zeile = db.execute(
        text(
            "SELECT proposal_id, approval_status, context_snapshot, created_at, reviewed_by, reviewed_at, "
            "execution_result FROM public.agent_proposals "
            "WHERE proposal_id = :id AND tenant_id = :tid AND action_type = :art"
            + (" FOR UPDATE" if sperren else "")
        ),  # nosec B608  # reviewed-safe: only fixed FOR UPDATE/empty suffix; id, tenant and action are bound parameters
        {"id": proposal_id, "tid": tenant_id, "art": VORSCHLAG_ART},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Buchungsvorschlag nicht gefunden")
    return zeile


def _vorschlag_out(zeile) -> BuchungsvorschlagOut:
    snap = _schnappschuss(zeile["context_snapshot"])
    return BuchungsvorschlagOut(
        proposal_id=str(zeile["proposal_id"]),
        credit_note_id=str(snap.get("credit_note_id") or ""),
        credit_note_number=str(snap.get("credit_note_number") or ""),
        netto=Decimal(str(snap.get("netto") or 0)),
        steuer=Decimal(str(snap.get("steuer") or 0)),
        brutto=Decimal(str(snap.get("brutto") or 0)),
        approval_status=str(zeile["approval_status"]),
        vorgeschlagen_von=snap.get("actor_id"),
        vorgeschlagen_am=zeile["created_at"],
        geprueft_von=zeile["reviewed_by"],
        geprueft_am=zeile["reviewed_at"],
        ablehnungsgrund=snap.get("rejection_reason"),
        gebucht=zeile["execution_result"] is not None,
    )


def _pruefe_vorschlag(db: Session, tenant_id: str, proposal_id: str, pruefer: str) -> dict[str, Any]:
    """Was vor Freigabe oder Ablehnung gelten muss. Gibt den Schnappschuss zurueck oder lehnt ab."""
    zeile = _vorschlag(db, tenant_id, proposal_id)
    if zeile["approval_status"] != "pending":
        raise HTTPException(status_code=409, detail=f"Der Vorschlag ist bereits {zeile['approval_status']}.")
    snap = _schnappschuss(zeile["context_snapshot"])
    # Vier Augen: Wer vorgeschlagen hat, gibt nicht frei.
    if str(snap.get("actor_id") or "") == pruefer:
        raise HTTPException(status_code=409, detail="Wer den Vorschlag gemacht hat, kann ihn nicht selbst prüfen.")
    return snap


def _entscheide(db: Session, tenant_id: str, proposal_id: str, *, status: str, pruefer: str,
                ereignis: str, grund: Optional[str] = None) -> None:
    """Schreibt die Entscheidung. Der Schnappschuss behaelt, was der Agent vorgeschlagen hat."""
    zeile = _vorschlag(db, tenant_id, proposal_id, sperren=True)
    if zeile["approval_status"] != "pending":
        raise HTTPException(status_code=409, detail=f"Der Vorschlag ist bereits {zeile['approval_status']}.")
    snap = _schnappschuss(zeile["context_snapshot"])
    jetzt = datetime.now(timezone.utc).isoformat()
    snap["audit_events"] = [*(snap.get("audit_events") or []), {"event": ereignis, "by": pruefer, "occurred_at": jetzt}]
    if grund:
        snap["rejection_reason"] = grund
    db.execute(
        text(
            "UPDATE public.agent_proposals SET approval_status = :status, reviewed_at = NOW(), reviewed_by = :wer, "
            "context_snapshot = CAST(:snap AS json) WHERE proposal_id = :id AND tenant_id = :tid"
        ),
        {"status": status, "wer": pruefer, "snap": json.dumps(snap), "id": proposal_id, "tid": tenant_id},
    )


def _pruefer(nutzer: dict) -> str:
    """Die Kennung des angemeldeten Menschen — aus der geprueften Anmeldung, nie aus der Anfrage."""
    return str(nutzer.get("sub") or "").strip()


@router.get("/credit-notes/buchungsvorschlaege", response_model=List[BuchungsvorschlagOut],
            summary="Buchungsvorschlaege von Agenten zu Gutschriften", dependencies=[Depends(beleg_read)])
async def list_buchungsvorschlaege(
    tenant_id: str = Depends(get_tenant_id),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    where = "tenant_id = :tid AND action_type = :art"
    params: dict[str, Any] = {"tid": tenant_id, "art": VORSCHLAG_ART}
    if status:
        where += " AND approval_status = :status"
        params["status"] = status
    zeilen = db.execute(
        text(
            "SELECT proposal_id, approval_status, context_snapshot, created_at, reviewed_by, reviewed_at, "
            f"execution_result FROM public.agent_proposals WHERE {where} "  # nosec B608
            "ORDER BY created_at DESC LIMIT 200"
        ),
        params,
    ).mappings()
    return [_vorschlag_out(z) for z in zeilen]


@router.post("/credit-notes/buchungsvorschlaege/{proposal_id}/actions/freigeben", response_model=MaskActionResult,
             summary="Buchungsvorschlag eines Agenten freigeben (nur Mensch)")
async def action_vorschlag_freigeben(
    proposal_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: dict = Depends(beleg_write),
) -> MaskActionResult:
    """CE fuer sales/gutschrift:vorschlag_freigeben. Freigeben bucht nicht — danach bucht der Agent.

    Geprueft wird vor der Freigabe, ob die Gutschrift noch so gebucht wuerde, wie der Agent sie
    vorgeschlagen hat. Hat sie sich geaendert oder laesst sie sich nicht mehr buchen, gibt es keine
    Freigabe, sondern den Grund.
    """
    pruefer = _pruefer(nutzer)

    async def pruefe(pruef_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> list[dict[str, Any]]:
        snap = _pruefe_vorschlag(pruef_db, tid, entity_id, pruefer)
        plan = _buchungsplan(pruef_db, tid, str(snap.get("credit_note_id") or ""))
        if Decimal(str(snap.get("brutto") or 0)) != plan["brutto"]:
            return [{"field": "_entity", "severity": "blocking", "message": (
                f"Die Gutschrift hat sich seit dem Vorschlag geändert (vorgeschlagen {Decimal(str(snap.get('brutto') or 0)):.2f}, "
                f"jetzt {plan['brutto']:.2f}). Bitte neu vorschlagen lassen.")}]
        return []

    async def gib_frei(schreib_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> str:
        _entscheide(schreib_db, tid, entity_id, status="approved", pruefer=pruefer, ereignis="proposal_approved")
        return "Buchungsvorschlag freigegeben. Gebucht wird durch den Agenten aus diesem Vorschlag."

    return await run_delegated_mask_action(
        db, action_key="vorschlag_freigeben", entity_type="agent_proposal", entity_id=proposal_id,
        tenant_id=tenant_id, body=body, check_fn=pruefe, delegate_fn=gib_frei,
        outbox_event_type="sales.credit_note.posting_approved",
    )


@router.post("/credit-notes/buchungsvorschlaege/{proposal_id}/actions/ablehnen", response_model=MaskActionResult,
             summary="Buchungsvorschlag eines Agenten ablehnen (nur Mensch)")
async def action_vorschlag_ablehnen(
    proposal_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: dict = Depends(beleg_write),
) -> MaskActionResult:
    """CE fuer sales/gutschrift:vorschlag_ablehnen. Braucht einen Grund; die Gutschrift bleibt Entwurf."""
    pruefer = _pruefer(nutzer)
    grund = str(body.get("_auditReason") or "").strip()

    async def pruefe(pruef_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> list[dict[str, Any]]:
        _pruefe_vorschlag(pruef_db, tid, entity_id, pruefer)
        return []

    async def lehne_ab(schreib_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> str:
        _entscheide(schreib_db, tid, entity_id, status="rejected", pruefer=pruefer,
                    ereignis="proposal_rejected", grund=grund)
        return "Buchungsvorschlag abgelehnt. Die Gutschrift bleibt Entwurf."

    return await run_delegated_mask_action(
        db, action_key="vorschlag_ablehnen", entity_type="agent_proposal", entity_id=proposal_id,
        tenant_id=tenant_id, body=body, check_fn=pruefe, delegate_fn=lehne_ab,
        outbox_event_type="sales.credit_note.posting_rejected", require_audit_reason=True,
    )


@router.get("/credit-notes/{cn_id}", response_model=CreditNoteDetailOut, summary="Credit note mit Positionen",
            dependencies=[Depends(beleg_read)])
async def get_credit_note(
    cn_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(f"SELECT {_LISTE_SPALTEN} FROM domain_sales.sales_credit_notes "  # nosec B608
             "WHERE id = :id AND tenant_id = :tid"),
        {"id": cn_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Gutschrift nicht gefunden")
    lines = [
        CreditNoteLineOut(
            id=str(z[0]), article_number=z[1], description=z[2] or "", quantity=z[3], unit_price=z[4],
            tax_code=z[5], tax_rate=z[6], line_total=z[7],
        )
        for z in db.execute(
            text(
                "SELECT id, article_number, description, quantity, unit_price, tax_code, tax_rate, line_total "
                "FROM domain_sales.sales_credit_note_lines WHERE credit_note_id = :id ORDER BY line_number"
            ),
            {"id": cn_id},
        ).fetchall()
    ]
    return CreditNoteDetailOut(**_aus_zeile(row, lines))


@router.delete("/credit-notes/{cn_id}", status_code=204, response_class=Response, response_model=None,
               summary="Credit note löschen", dependencies=[Depends(beleg_write)])
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
        text("DELETE FROM domain_sales.sales_credit_note_lines WHERE credit_note_id = :id"), {"id": cn_id})
    db.execute(
        text("DELETE FROM domain_sales.sales_credit_notes WHERE id = :id AND tenant_id = :tid"),
        {"id": cn_id, "tid": tenant_id},
    )
    db.commit()


def _buchungsplan(db: Session, tenant_id: str, cn_id: str) -> dict:
    """Liest und prueft alles, was die Buchung braucht — schreibt nichts.

    Die Steuer kommt aus den Positionen und ihrem Steuerschluessel. Fehlt eine Angabe oder widersprechen
    sich Angaben, gibt es 409 „bitte pruefen“: Die Gutschrift bleibt Entwurf.
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
    return {
        "id": cn_id, "mandant": row[1], "nummer": row[2], "rechnung": (row[6] or "").strip(),
        "netto": netto, "steuer": steuer, "brutto": brutto, "zeilen": buchungszeilen,
    }


def _buche(db: Session, plan: dict, tenant_id: str) -> str:
    """Schreibt Buchungskopf, Zeilen, Status und OP-Minderung — ohne Festschreiben. Gibt den Satz zurueck.

    Jede Gutschrift braucht die Freigabe einer zweiten Person (APPROVAL-001); sie wird hier verbraucht, in der
    Transaktion der Buchung. Die Stelle gilt fuer jeden Weg, der eine Gutschrift bucht.
    """
    from app.services import finance_freigabe

    finance_freigabe.verlange_gutschrift(db, tenant_id, str(plan["id"]))
    je_id = uuid7()
    db.execute(
        text("""
            INSERT INTO domain_erp.journal_entries
            (id, tenant_id, entry_number, entry_date, posting_date, description,
             source, status, total_debit, total_credit, reference, created_at, updated_at)
            VALUES (:id, :tid, :en, NOW(), NOW(), :desc,
                    'sales_credit_note', 'posted', :total, :total, :ref, NOW(), NOW())
        """),
        {
            "id": je_id, "tid": plan["mandant"],
            "en": f"GS-{plan['nummer']}", "desc": f"Gutschrift {plan['nummer']}",
            "total": plan["brutto"], "ref": plan["nummer"],
        },
    )
    for nr, zeile in enumerate(plan["zeilen"], 1):
        db.execute(
            text("""
                INSERT INTO domain_erp.journal_entry_lines
                    (id, tenant_id, journal_entry_id, account_id, description, debit, credit,
                     tax_code, line_number, created_at)
                VALUES (:id, :tid, :jeid, :konto, :text, :soll, :haben, :code, :nr, NOW())
            """),
            {"id": uuid7(), "tid": plan["mandant"], "jeid": je_id, "nr": nr, **zeile},
        )
    db.execute(
        text(
            "UPDATE domain_sales.sales_credit_notes SET status = 'posted', net_amount = :netto, "
            "tax_amount = :steuer, updated_at = NOW() WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": plan["id"], "tid": tenant_id, "netto": plan["netto"], "steuer": plan["steuer"]},
    )
    # Gemindert wird nur der offene Posten der Rechnung, auf die sich die Gutschrift bezieht —
    # um den Bruttobetrag. (Vorher: jeder offene Posten des Kunden, jeweils um den vollen Betrag.)
    if plan["rechnung"]:
        db.execute(
            text("""
                UPDATE domain_erp.offene_posten
                SET offen = GREATEST(0, offen - :betrag),
                    op_status = CASE WHEN offen - :betrag <= 0 THEN 'geschlossen' ELSE 'teilweise' END
                WHERE tenant_id = :tid AND konto_typ = 'debitoren' AND rechnungsnr = :rechnung
                  AND op_status NOT IN ('geschlossen', 'ausgeziffert')
            """),
            {"tid": plan["mandant"], "betrag": plan["brutto"], "rechnung": plan["rechnung"]},
        )
    return (
        f"Gutschrift {plan['nummer']} gebucht (Buchung GS-{plan['nummer']}): netto {plan['netto']:.2f}, "
        f"Umsatzsteuer {plan['steuer']:.2f}, brutto {plan['brutto']:.2f}."
    )


@router.post("/credit-notes/{cn_id}/post", response_model=StatusResponse, summary="Credit note erstellen",
             dependencies=[Depends(beleg_write)])
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

    Bis 12.10.2026 wurde der Kopf zuerst festgeschrieben; die Zeilen trugen Kontonummern statt
    Konto-IDs, scheiterten am Fremdschluessel, und der Fehler wurde verschluckt. Der Gesamtbetrag ging
    ungeteilt gegen das Erloeskonto.
    """
    plan = _buchungsplan(db, tenant_id, cn_id)
    try:
        meldung = _buche(db, plan, tenant_id)
        db.commit()
    except Exception:
        # Nichts bleibt halb stehen; die Kontosperre uebersetzt der zentrale Behandler (409).
        db.rollback()
        raise

    log_fibu_audit(
        db, plan["mandant"], "post", "sales_credit_note", cn_id,
        {"total": float(plan["brutto"]), "net": float(plan["netto"]), "tax": float(plan["steuer"])},
        request=request,
    )
    return StatusResponse(success=True, message=meldung)


# ---------------------------------------------------------------------------
# Masken-Kommandos (ScreenDefinition sales/gutschrift)
# ---------------------------------------------------------------------------

@router.post("/credit-notes/actions/speichern", response_model=MaskActionResult,
             summary="Gutschrift als Entwurf speichern (Masken-CommandEndpoint)",
             dependencies=[Depends(beleg_write)])
async def action_gutschrift_speichern(
    body: dict[str, Any] = Body(default_factory=dict),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> MaskActionResult:
    """CE fuer sales/gutschrift:speichern. Trockenlauf prueft, schreibt nichts; Mandant aus der Anmeldung."""
    nummer = str(body.get("credit_note_number") or "").strip() or "neu"

    def _eingabe(payload: dict[str, Any]) -> CreditNoteCreate:
        return CreditNoteCreate.model_validate({**payload, "status": "draft", "tenant_id": None})

    async def pruefe(pruef_db: Session, payload: dict[str, Any], _entity_id: str, tid: str) -> list[dict[str, Any]]:
        try:
            eingabe = _eingabe(payload)
        except ValidationError as fehler:
            return [
                {"field": ".".join(str(t) for t in f["loc"]), "message": f["msg"], "severity": "blocking"}
                for f in fehler.errors()
            ]
        if not eingabe.lines:
            return [{"field": "lines", "message": "Mindestens eine Position erfassen.", "severity": "blocking"}]
        if pruef_db.execute(
            text("SELECT 1 FROM domain_sales.sales_credit_notes WHERE tenant_id = :tid AND credit_note_number = :nr"),
            {"tid": tid, "nr": eingabe.credit_note_number},
        ).first():
            return [{"field": "credit_note_number", "severity": "blocking",
                     "message": f"Gutschriftnummer {eingabe.credit_note_number} ist bereits vergeben."}]
        assert_customer_allowed_for_invoice(pruef_db, tid, eingabe.customer_id)
        try:
            steuergruppen(pruef_db, tid, _zeilen(eingabe.lines))
        except Steuerklaerung as klaerung:
            # Ein Entwurf darf ohne Steuerschluessel gespeichert werden; ein Widerspruch nicht.
            if "widerspricht" in str(klaerung):
                return [{"field": "lines", "message": str(klaerung), "severity": "blocking"}]
        return []

    async def lege_an(schreib_db: Session, payload: dict[str, Any], _entity_id: str, tid: str) -> str:
        eingabe = _eingabe(payload)
        angelegt = _lege_an(schreib_db, tid, eingabe)
        steuer = "offen" if angelegt["steuer"] is None else f"{angelegt['steuer']:.2f}"
        return (
            f"Gutschrift {eingabe.credit_note_number} als Entwurf gespeichert: "
            f"netto {angelegt['netto']:.2f}, Umsatzsteuer {steuer}."
        )

    return await run_delegated_mask_action(
        db, action_key="speichern", entity_type="sales_credit_note", entity_id=nummer, tenant_id=tenant_id,
        body=body, check_fn=pruefe, delegate_fn=lege_an, outbox_event_type="sales.credit_note.saved",
    )


@router.post("/credit-notes/{cn_id}/actions/buchen", response_model=MaskActionResult,
             summary="Gutschrift buchen (Masken-CommandEndpoint)", dependencies=[Depends(beleg_write)])
async def action_gutschrift_buchen(
    cn_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> MaskActionResult:
    """CE fuer sales/gutschrift:buchen. Der Trockenlauf nennt den Pruefgrund, ohne zu buchen."""

    async def pruefe(pruef_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> list[dict[str, Any]]:
        _buchungsplan(pruef_db, tid, entity_id)
        return []

    async def buche(schreib_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> str:
        plan = _buchungsplan(schreib_db, tid, entity_id)
        try:
            return _buche(schreib_db, plan, tid)
        except IntegrityError as fehler:
            sperre = kontosperre_meldung(fehler)
            if sperre:
                raise HTTPException(status_code=409, detail=sperre) from fehler
            raise

    return await run_delegated_mask_action(
        db, action_key="buchen", entity_type="sales_credit_note", entity_id=cn_id, tenant_id=tenant_id,
        body=body, check_fn=pruefe, delegate_fn=buche, outbox_event_type="sales.credit_note.posted",
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
            inv = eigener_beleg("sales_invoice", payload.invoice_reference, tid, repo)
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
