"""Finance bucht, was die belegfuehrenden Domaenen freigeben: Gutschriften und Storno der Eingangsrechnung.

Architekturentscheidung vom 13.10.2026: Einkauf und Verkauf fuehren den Beleg (DocFlow), Finance ist die
Buchungsautoritaet. Der Beleg nennt je Position den Steuerschluessel; Konten und Seiten bestimmt Finance.

Ausgangsrechnung: ``SalesPostingService``. Eingangsrechnung: ``finance_eingangsrechnung_buchung``. Hier:

* Verkaufsgutschrift  — Soll Erloes netto und Umsatzsteuer je Schluessel, Haben Forderungen brutto
* Einkaufsgutschrift  — Soll Kreditor brutto, Haben Aufwand netto und Vorsteuer je Schluessel
* Storno der Eingangsrechnung — Gegenbuchung, offener Posten storniert

Alles ohne eigenen Commit: Der Aufrufer schreibt Buchung, Nachweis und Belegstatus gemeinsam fest.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationFailedError
from app.finance.steuerschluessel import Steuergruppe, Steuerklaerung, Vorsteuergruppe
from app.services.finance_eingangsrechnung_buchung import kreditorenkonto
from app.services.finance_transaction_service import FinanceTransactionService

FORDERUNGEN = "1400"  # wie SalesPostingService.ACCOUNT_RECEIVABLES


def _tag(wert: Any) -> date:
    return date.fromisoformat(str(wert or date.today().isoformat())[:10])


def _mindere_op(db: Session, tenant_id: str, konto_typ: str, rechnungsnummer: Optional[str], brutto: Decimal) -> None:
    """Mindert den offenen Posten der Rechnung, auf die sich die Gutschrift bezieht — nur diesen, um den Bruttobetrag."""
    if not rechnungsnummer:
        return
    db.execute(
        text(
            """
            UPDATE domain_erp.offene_posten
            SET offen = GREATEST(0, offen - :betrag),
                open_amount = GREATEST(0, COALESCE(open_amount, offen) - :betrag),
                op_status = CASE WHEN offen - :betrag <= 0 THEN 'geschlossen' ELSE 'teilweise' END,
                updated_at = NOW()
            WHERE tenant_id = :tid AND konto_typ = :typ AND rechnungsnr = :rechnung
              AND op_status NOT IN ('geschlossen', 'ausgeziffert', 'storniert')
            """
        ),
        {"tid": tenant_id, "typ": konto_typ, "betrag": brutto, "rechnung": rechnungsnummer},
    )


def buche_verkaufsgutschrift(
    db: Session, tenant_id: str, *, nummer: str, datum: Any, gruppen: list[Steuergruppe],
    rechnungsnummer: Optional[str], posted_by: Optional[str],
) -> str:
    """Erloes netto und Umsatzsteuer je Steuerschluessel im Soll, Forderungen brutto im Haben."""
    brutto = sum((g.netto + g.steuer for g in gruppen), Decimal("0"))
    if brutto <= Decimal("0"):
        raise Steuerklaerung("Der Gutschriftbetrag ist nicht positiv.")
    fin = FinanceTransactionService(db, tenant_id, commit_on_success=False)
    zeilen: list[dict[str, Any]] = []
    for g in gruppen:
        zeilen.append({"account_id": fin.account_id_for_number(g.erloeskonto), "debit_amount": float(g.netto),
                       "credit_amount": 0, "description": f"Erloesminderung Steuerschluessel {g.tax_code}"})
        if g.steuer > Decimal("0"):
            zeilen.append({"account_id": fin.account_id_for_number(g.steuerkonto), "debit_amount": float(g.steuer),
                           "credit_amount": 0,
                           "description": f"Umsatzsteuerberichtigung {g.satz.normalize():f} % Steuerschluessel {g.tax_code}"})
    zeilen.append({"account_id": fin.account_id_for_number(FORDERUNGEN), "debit_amount": 0, "credit_amount": float(brutto),
                   "description": f"Forderungsminderung {nummer}"})
    tag = _tag(datum)
    journal = fin.create(
        entry_number=f"GS-{nummer}"[:20], description=f"Gutschrift {nummer}", entry_date=tag, lines=zeilen,
        reference=nummer, source="sales_credit_memo", document_type="AR_CREDIT_MEMO", period=tag.strftime("%Y-%m"),
    )
    fin.post(str(journal.id), posted_by)
    _mindere_op(db, tenant_id, "debitoren", rechnungsnummer, brutto)
    return str(journal.id)


def buche_einkaufsgutschrift(
    db: Session, tenant_id: str, *, nummer: str, datum: Any, gruppen: list[Vorsteuergruppe],
    rechnungsnummer: Optional[str], posted_by: Optional[str], beleg: Optional[dict[str, Any]] = None,
) -> str:
    """Kreditor brutto im Soll, Aufwand netto und Vorsteuer je Steuerschluessel im Haben."""
    brutto = sum((g.netto + g.steuer for g in gruppen), Decimal("0"))
    if brutto <= Decimal("0"):
        raise Steuerklaerung("Der Gutschriftbetrag ist nicht positiv.")
    fin = FinanceTransactionService(db, tenant_id, commit_on_success=False)
    zeilen: list[dict[str, Any]] = [{
        "account_id": fin.account_id_for_number(kreditorenkonto(db, tenant_id, beleg or {})),
        "debit_amount": float(brutto), "credit_amount": 0, "description": f"Verbindlichkeitsminderung {nummer}"}]
    for g in gruppen:
        zeilen.append({"account_id": fin.account_id_for_number(g.aufwandskonto), "debit_amount": 0,
                       "credit_amount": float(g.netto), "description": f"Aufwandsminderung Steuerschluessel {g.tax_code}"})
        if g.steuer > Decimal("0"):
            zeilen.append({"account_id": fin.account_id_for_number(g.vorsteuerkonto), "debit_amount": 0,
                           "credit_amount": float(g.steuer),
                           "description": f"Vorsteuerberichtigung {g.satz.normalize():f} % Steuerschluessel {g.tax_code}"})
    tag = _tag(datum)
    journal = fin.create(
        entry_number=f"EG-{nummer}"[:20], description=f"Einkaufsgutschrift {nummer}", entry_date=tag, lines=zeilen,
        reference=nummer, source="purchase_credit_memo", document_type="AP_CREDIT_MEMO", period=tag.strftime("%Y-%m"),
    )
    fin.post(str(journal.id), posted_by)
    _mindere_op(db, tenant_id, "kreditoren", rechnungsnummer, brutto)
    return str(journal.id)


def storniere_eingangsrechnung(db: Session, tenant_id: str, *, nummer: str, grund: str) -> dict[str, str]:
    """Gegenbuchung zur gebuchten Eingangsrechnung; ihr offener Posten wird storniert."""
    satz = db.execute(
        text(
            "SELECT id, status FROM domain_erp.journal_entries WHERE tenant_id = :t AND reference = :n "
            "AND source IN ('ap_invoice', 'ap_invoice_kernel', 'einkauf_rechnungseingang', 'purchase_invoice') "
            "ORDER BY created_at LIMIT 1"
        ),
        {"t": tenant_id, "n": nummer},
    ).mappings().first()
    if not satz:
        raise ValidationFailedError(f"Zur Eingangsrechnung {nummer} gibt es keine Buchung.")
    if str(satz["status"]) != "posted":
        raise ValidationFailedError(f"Die Buchung der Eingangsrechnung {nummer} ist bereits {satz['status']}.")
    fin = FinanceTransactionService(db, tenant_id, commit_on_success=False)
    original, storno = fin.reverse(str(satz["id"]), reason=grund)
    db.execute(
        text(
            "UPDATE domain_erp.offene_posten SET op_status = 'storniert', open_amount = 0, offen = 0, updated_at = NOW() "
            "WHERE tenant_id = :t AND rechnungsnr = :n AND konto_typ = 'kreditoren'"
        ),
        {"t": tenant_id, "n": nummer},
    )
    return {"journal_entry_id": str(original.id), "reversal_entry_id": str(storno.id)}
