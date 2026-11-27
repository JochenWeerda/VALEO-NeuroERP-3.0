"""Kanonischer Self-Billing-Buchungskern (M3-Konsolidierung).

Ein Weg für Erntefreigabe und API-Adapter: kreditorische Eingangsbuchung über
``buche_eingangsrechnung`` (posted Journal + Personenkonto + genau ein OP).
Idempotenz: vorhandenes journal_entry_id / Unique je Annahme.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.business_time import business_today
from app.core.exceptions import ConflictError, ValidationFailedError
from app.finance.steuerschluessel import Steuerklaerung, Vorsteuergruppe
from app.services.finance_eingangsrechnung_buchung import buche_eingangsrechnung, summen

_CENT = Decimal("0.01")


def _as_date(value: Any) -> date:
    if value is None:
        return business_today()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def build_vorsteuergruppen_from_resolved(
    resolved: dict[str, Any],
    *,
    netto: Decimal,
) -> list[Vorsteuergruppe]:
    """Baut Vorsteuergruppen aus dem Multi-Parameter-Resolver (Stichtag schon geprüft).

    Rundung: ``ROUND_HALF_UP`` wie ``app.finance.steuerschluessel`` und
    ``harvest_calculator.round_money`` — sonst scheitert die Betragsratsche
    (z. B. 5417.50 × 7 % → 379.23 vs. Banker's 379.22).
    """
    satz = Decimal(str(resolved["rate"]))
    aufwand = resolved.get("expense_account")
    if not aufwand:
        raise ValidationFailedError(
            f"Steuerschlüssel {resolved['tax_code']} hat kein Aufwandskonto."
        )
    netto_q = Decimal(str(netto)).quantize(_CENT, rounding=ROUND_HALF_UP)
    steuer = (netto_q * satz / Decimal("100")).quantize(_CENT, rounding=ROUND_HALF_UP)
    return [
        Vorsteuergruppe(
            tax_code=str(resolved["tax_code"]),
            satz=satz,
            netto=netto_q,
            steuer=steuer,
            aufwandskonto=str(aufwand),
            vorsteuerkonto=(str(resolved["vorsteuerkonto"]).strip() if satz > 0 and resolved.get("vorsteuerkonto") else None),
        )
    ]


def buche_self_billing(
    db: Session,
    tenant_id: str,
    *,
    invoice: Any,
    supplier_id: str,
    delivery_date: Any,
    tax_context: dict[str, Any],
    gruppen: list[Vorsteuergruppe],
    posted_by: Optional[str],
    harvest_acceptance_id: Optional[str] = None,
) -> tuple[str, list[Vorsteuergruppe]]:
    """Posted Journal + Personenkonto + OP. Idempotent bei vorhandenem journal_entry_id."""
    existing = getattr(invoice, "journal_entry_id", None)
    if existing:
        raise ConflictError("Self-Billing-Beleg ist bereits verbucht.")

    if harvest_acceptance_id:
        # Zeilensperre gegen parallele Buchung derselben Annahme
        db.execute(
            text(
                "SELECT id FROM domain_inventory.harvest_acceptances "
                "WHERE id = :id AND tenant_id = :t FOR UPDATE"
            ),
            {"id": harvest_acceptance_id, "t": tenant_id},
        )
        already = db.execute(
            text(
                "SELECT journal_entry_id FROM domain_finance.self_billing_invoices "
                "WHERE tenant_id = :t AND harvest_acceptance_id = :h "
                "AND journal_entry_id IS NOT NULL LIMIT 1"
            ),
            {"t": tenant_id, "h": harvest_acceptance_id},
        ).scalar()
        if already:
            raise ConflictError("Für diese Ernte-Annahme existiert bereits eine Self-Billing-Buchung.")

    netto, steuer, brutto = summen(gruppen)
    inv_net = Decimal(str(invoice.total_net_amount_eur))
    inv_vat = Decimal(str(invoice.total_vat_amount_eur))
    inv_gross = Decimal(str(invoice.total_gross_amount_eur))
    if (netto, steuer, brutto) != (inv_net, inv_vat, inv_gross):
        raise ValidationFailedError(
            "Self-Billing-Beleg und kanonische Steuerberechnung widersprechen sich "
            f"(Beleg {inv_net}/{inv_vat}/{inv_gross} vs. {netto}/{steuer}/{brutto})."
        )
    if brutto <= 0:
        raise ValidationFailedError("Self-Billing-Brutto muss positiv sein.")

    tag = _as_date(delivery_date)
    nummer = str(invoice.invoice_number)
    invoice_payload = {
        "number": nummer,
        "date": tag.isoformat(),
        "supplierId": supplier_id,
        "customerId": supplier_id,
        "currency": "EUR",
        "dueDate": tag.isoformat(),
    }
    try:
        journal_id, used = buche_eingangsrechnung(
            db,
            tenant_id,
            invoice_id=str(invoice.id),
            invoice=invoice_payload,
            posted_by=posted_by,
            quelle="self_billing",
            gruppen=gruppen,
        )
    except Steuerklaerung as error:
        raise ValidationFailedError(str(error)) from error

    # Decimal-sichere OP-Beträge: buche_eingangsrechnung schreibt bereits OP;
    # Journal-ID und Steuerkontext an Agrar-Erweiterung hängen.
    db.execute(
        text(
            "UPDATE domain_finance.self_billing_invoices SET "
            "journal_entry_id = :jid, taxation_type = :tt, tax_context = CAST(:ctx AS jsonb), "
            "status = 'booked', updated_at = NOW() "
            "WHERE id = :id AND tenant_id = :t AND journal_entry_id IS NULL"
        ),
        {
            "jid": journal_id,
            "tt": tax_context.get("taxation_type"),
            "ctx": __import__("json").dumps(tax_context, default=str),
            "id": str(invoice.id),
            "t": tenant_id,
        },
    )
    # Entry number uses AP- prefix from buche_eingangsrechnung; keep source self_billing via quelle.
    return journal_id, used


def storno_self_billing(
    db: Session,
    tenant_id: str,
    *,
    invoice: Any,
    reason: str,
) -> dict[str, str]:
    """Storno über Journal-Reverse am Originalkontext — keine Neuberechnung aktueller Sätze."""
    journal_id = getattr(invoice, "journal_entry_id", None)
    if not journal_id:
        raise ValidationFailedError("Self-Billing-Beleg hat keine Journalbuchung zum Stornieren.")

    from app.services.finance_transaction_service import FinanceTransactionService

    fin = FinanceTransactionService(db, tenant_id, commit_on_success=False)
    original, storno = fin.reverse(str(journal_id), reason=reason)

    # OP schließen / stornieren (Originalbetrag; Zahlungen bleiben Fachfrage der OP-Engine)
    db.execute(
        text(
            "UPDATE domain_erp.offene_posten SET op_status = 'storniert', open_amount = 0, offen = 0, "
            "updated_at = NOW() "
            "WHERE tenant_id = :t AND rechnungsnr = :n AND konto_typ = 'kreditoren' "
            "AND op_status = 'offen'"
        ),
        {"t": tenant_id, "n": str(invoice.invoice_number)},
    )
    db.execute(
        text(
            "UPDATE domain_finance.self_billing_invoices SET status = 'cancelled', updated_at = NOW() "
            "WHERE id = :id AND tenant_id = :t"
        ),
        {"id": str(invoice.id), "t": tenant_id},
    )
    return {"journal_entry_id": str(original.id), "reversal_entry_id": str(storno.id)}
