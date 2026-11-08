"""Eingangsrechnung buchen: Aufwand und Vorsteuer je Steuerschluessel im Soll, Kreditor brutto im Haben.

Bis zum 13.10.2026 buchten beide Wege (REST ``/finance/ap/invoices/{id}/post`` und der Kernel-Handler)
seitenverkehrt — Kreditor im Soll, Aufwand und Vorsteuer im Haben —, mit den Kontonummern „3300“ und „6000“
an der Stelle von Konten, mit den Summen aus dem gespeicherten Beleg und mit **einem** Vorsteuerkonto nach
dem hoechsten Satz der Rechnung, notfalls 1576. Scheiterte die Buchung, setzte der REST-Weg die Rechnung
trotzdem auf „verbucht“.

Hier gilt dasselbe wie fuer Gutschrift und Ausgangsrechnung: Die Position nennt ihren Steuerschluessel
(``app.finance.steuerschluessel``), gerechnet wird auf dem Server, und ohne eindeutige Angabe wird nicht
gebucht (``Steuerklaerung``). Journal und offener Posten liegen in der Transaktion des Aufrufers.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.finance.steuerschluessel import (
    KREDITORENKONTO,
    Steuerklaerung,
    Vorsteuergruppe,
    kontenrahmen,
    vorsteuergruppen,
)
from app.services.finance_transaction_service import FinanceTransactionService
from app.core.business_time import business_today


def positionen(invoice: dict[str, Any]) -> list[tuple]:
    """Die Positionen des Belegs als ``(nr, Steuerschluessel, Satz, Netto, Aufwandskonto)``."""
    kopfkonto = str(invoice.get("expenseAccountId") or "").strip() or None
    return [
        (
            nr,
            line.get("taxCode"),
            line.get("vatRate"),
            Decimal(str(line.get("qty") or 0)) * Decimal(str(line.get("price") or 0)),
            str(line.get("expenseAccount") or "").strip() or kopfkonto,
        )
        for nr, line in enumerate(invoice.get("lines") or [], 1)
    ]


def summen(gruppen: list[Vorsteuergruppe]) -> tuple[Decimal, Decimal, Decimal]:
    netto = sum((g.netto for g in gruppen), Decimal("0"))
    steuer = sum((g.steuer for g in gruppen), Decimal("0"))
    return netto, steuer, netto + steuer


def kreditorenkonto(db: Session, tenant_id: str, invoice: dict[str, Any]) -> str:
    """Das Verbindlichkeitskonto: das der Rechnung, sonst das Sammelkonto des Kontenrahmens."""
    eigenes = str(invoice.get("supplierAccountId") or "").strip()
    if eigenes:
        return eigenes
    rahmen = kontenrahmen(db, tenant_id)
    if rahmen not in KREDITORENKONTO:
        raise Steuerklaerung(
            "Kein Kreditorenkonto: Die Rechnung nennt keines, und der Kontenrahmen des Mandanten ist nicht festgelegt."
        )
    return KREDITORENKONTO[rahmen]


def buche_eingangsrechnung(
    db: Session,
    tenant_id: str,
    *,
    invoice_id: str,
    invoice: dict[str, Any],
    posted_by: Optional[str],
    quelle: str = "ap_invoice",
    gruppen: Optional[list[Vorsteuergruppe]] = None,
) -> tuple[str, list[Vorsteuergruppe]]:
    """Legt Journal und offenen Posten an (ohne Commit). Wirft ``Steuerklaerung``, wenn nicht gebucht werden darf.

    ``gruppen``: vom belegfuehrenden Weg schon ermittelt (DocFlow gibt die Steuer des Belegs mit, damit Beleg
    und Buchung auf den Cent stimmen); sonst aus den Positionen der Rechnung.
    """
    if gruppen is None:
        gruppen = vorsteuergruppen(db, tenant_id, positionen(invoice))
    _netto, _steuer, brutto = summen(gruppen)
    if brutto <= Decimal("0"):
        raise Steuerklaerung("Der Rechnungsbetrag ist nicht positiv.")
    nummer = str(invoice.get("number") or invoice_id)
    tag = date.fromisoformat(str(invoice.get("date") or business_today().isoformat())[:10])

    fin = FinanceTransactionService(db, tenant_id, commit_on_success=False)
    zeilen: list[dict[str, Any]] = []
    for gruppe in gruppen:
        zeilen.append({
            "account_id": fin.account_id_for_number(gruppe.aufwandskonto),
            "debit_amount": float(gruppe.netto), "credit_amount": 0,
            "description": f"Aufwand Steuerschluessel {gruppe.tax_code}",
        })
        if gruppe.steuer > Decimal("0"):
            zeilen.append({
                "account_id": fin.account_id_for_number(gruppe.vorsteuerkonto),
                "debit_amount": float(gruppe.steuer), "credit_amount": 0,
                "description": f"Vorsteuer {gruppe.satz.normalize():f} % Steuerschluessel {gruppe.tax_code}",
            })
    zeilen.append({
        "account_id": fin.account_id_for_number(kreditorenkonto(db, tenant_id, invoice)),
        "debit_amount": 0, "credit_amount": float(brutto),
        "description": f"Verbindlichkeit {nummer}",
    })
    journal = fin.create(
        entry_number=f"AP-{nummer}"[:20],
        description=f"Eingangsrechnung {nummer}",
        entry_date=tag,
        lines=zeilen,
        reference=nummer,
        source=quelle,
        document_type="AP_INVOICE",
        period=tag.strftime("%Y-%m"),
    )
    fin.post(str(journal.id), posted_by)

    faellig = str(invoice.get("dueDate") or (datetime.combine(tag, datetime.min.time()) + timedelta(days=30)).date())[:10]
    # Bis zum 13.10.2026 nannte die Anlage die Spalte ``op_betrag``, die es nicht gibt; der Fehler wurde
    # verschluckt, und eine gebuchte Eingangsrechnung hatte keinen offenen Posten.
    db.execute(
        text(
            """
            INSERT INTO domain_erp.offene_posten
            (id, tenant_id, rechnungsnr, datum, rechnungsdatum, faelligkeit, due_date,
             konto_typ, lieferant_id, lieferant_name, waehrung, betrag, open_amount, offen,
             op_status, zahlbar, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :rechnungsnr, :datum, :datum, :faelligkeit, :faelligkeit,
             'kreditoren', :lieferant_id, :lieferant_name, :waehrung, :betrag, :betrag, :betrag,
             'offen', TRUE, NOW(), NOW())
            """
        ),
        {
            "id": f"OP-AP-{invoice_id}", "tenant_id": tenant_id, "rechnungsnr": nummer, "datum": tag,
            "faelligkeit": date.fromisoformat(faellig), "betrag": brutto,
            "lieferant_id": str(invoice.get("customerId") or invoice.get("supplierId") or ""),
            "lieferant_name": str(invoice.get("supplierName") or invoice.get("customerName") or ""),
            "waehrung": str(invoice.get("currency") or "EUR"),
        },
    )
    return str(journal.id), gruppen
