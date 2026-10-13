"""Die Buchungswege neben DocFlow an der zentralen Approval Engine (APPROVAL-001).

Drei Wege buchen, ohne dass der Beleg in DocFlow steht: die Eingangsrechnung der Finanzbuchhaltung
(``/finance/ap/invoices``), die Verkaufsgutschrift (``/sales/credit-notes``) und der alte Rechnungsweg
(``/finance/invoices``). Ohne diese Datei waeren sie Umgehungswege um die Freigabe.

* Eingangsrechnung und Verkaufsgutschrift haben einen gespeicherten Vorgang und schliessen sich an die Engine an:
  anfragen und entscheiden ueber ``/api/v1/approvals/…``.
* Der alte Rechnungsweg legt an und bucht in einem Schritt; dort gibt es nichts, was freigegeben werden koennte.
  Er bucht deshalb nur, was die Matrix dem Rollenrecht ueberlaesst (``nur_mit_rollenrecht``). Sein Storno geht
  durch die Engine (Vorgang ist die Buchung); eine DocFlow-Rechnung storniert er nicht.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.core.freigabe import anforderung
from app.finance.steuerschluessel import Steuerklaerung, vorsteuergruppen
from app.services.finance_eingangsrechnung_buchung import positionen, summen
from app.services.freigabe_engine import FreigabeEngine, Vorgang


def _d(wert: Any) -> Decimal:
    return Decimal(str(wert or 0))


class EingangsrechnungFreigabe(FreigabeEngine):
    """Eingangsrechnung der Finanzbuchhaltung (Dokumentspeicher ``ap_invoice``)."""

    SUBJEKT = "finance_ap_invoice"

    def vorgang(self, subject_id: str, aktion: str) -> Vorgang:
        from app.documents.router_helpers import get_from_store, get_repository

        invoice = get_from_store("ap_invoice", subject_id, get_repository(self.db))
        if not invoice or str(invoice.get("tenantId") or invoice.get("tenant_id") or "") != self.tenant_id:
            raise EntityNotFoundError("APInvoice", subject_id)
        return self.vorgang_aus(subject_id, invoice)

    def vorgang_aus(self, subject_id: str, invoice: dict[str, Any]) -> Vorgang:
        zeilen = positionen(invoice)
        try:
            brutto = summen(vorsteuergruppen(self.db, self.tenant_id, zeilen))[2]
        except Steuerklaerung:
            # Nicht buchbar; fuer die Grenze zaehlt dann der hoehere von Netto und angegebenem Brutto.
            brutto = max(sum((z[3] for z in zeilen), Decimal("0")), _d(invoice.get("totalGross")))
        stand = str(invoice.get("status") or "")
        return Vorgang(
            subject_id=subject_id, belegart="purchase_invoice", brutto=brutto, gebucht=stand == "VERBUCHT",
            beendet=stand == "STORNIERT", ersteller=invoice.get("createdBy"),
            inhalt={
                "nummer": invoice.get("number"), "lieferant": invoice.get("customerId") or invoice.get("supplierId"),
                "datum": invoice.get("date"), "waehrung": invoice.get("currency"),
                "aufwandskonto": invoice.get("expenseAccountId"),
                "positionen": [[str(z[0]), z[1], str(z[2]), str(z[3]), z[4]] for z in zeilen],
            },
            # Eine Finanzrechnung hat weder Bestellung noch Wareneingang, gegen die sie abgeglichen werden koennte.
            abgleich_in_ordnung=False, abgleich_hinweis="Finanzrechnung ohne Bestellung oder Wareneingang",
        )


class VerkaufsgutschriftFreigabe(FreigabeEngine):
    """Verkaufsgutschrift (``domain_sales.sales_credit_notes``)."""

    SUBJEKT = "sales_credit_note"

    def vorgang(self, subject_id: str, aktion: str) -> Vorgang:
        zeile = self.db.execute(
            text(
                "SELECT id, credit_note_number, customer_id, invoice_reference, total_amount, net_amount, tax_amount, "
                "status, correction_type, currency FROM domain_sales.sales_credit_notes WHERE id = :id AND tenant_id = :t"
            ),
            {"id": subject_id, "t": self.tenant_id},
        ).mappings().first()
        if not zeile:
            raise EntityNotFoundError("SalesCreditNote", subject_id)
        rechnung = (zeile["invoice_reference"] or "").strip()
        # Stueckelung: alle Gutschriften zur selben Rechnung zaehlen zusammen.
        gesamt = self.db.execute(
            text(
                "SELECT COALESCE(SUM(total_amount), 0) FROM domain_sales.sales_credit_notes "
                "WHERE tenant_id = :t AND invoice_reference = :r AND status NOT IN ('cancelled', 'storniert')"
            ),
            {"t": self.tenant_id, "r": rechnung},
        ).scalar() if rechnung else None
        stand = str(zeile["status"] or "")
        return Vorgang(
            subject_id=str(zeile["id"]), belegart="sales_credit_memo", brutto=_d(zeile["total_amount"]),
            gebucht=stand == "posted", beendet=stand in ("cancelled", "storniert"),
            inhalt={
                "nummer": zeile["credit_note_number"], "kunde": zeile["customer_id"], "rechnung": rechnung,
                "summen": [str(_d(zeile[k])) for k in ("net_amount", "tax_amount", "total_amount")],
                "art": zeile["correction_type"], "waehrung": zeile["currency"],
            },
            brutto_des_vorgangs=_d(gesamt) if gesamt is not None else None,
        )


class AusgangsrechnungStornoFreigabe(FreigabeEngine):
    """Storno einer Ausgangsrechnung des alten Rechnungswegs — der Vorgang ist ihre Buchung im Mandanten.

    Der Dokumentspeicher dieses Wegs kennt keinen Mandanten; die Buchung schon. Gibt es im Mandanten keine Buchung
    zu der Nummer, gibt es hier auch keinen Vorgang.
    """

    SUBJEKT = "finance_sales_invoice"

    def vorgang(self, subject_id: str, aktion: str) -> Vorgang:
        zeile = self.db.execute(
            text(
                "SELECT id, status, total_debit FROM domain_erp.journal_entries WHERE tenant_id = :t "
                "AND source = 'sales_invoice' AND (document_number = :nr OR reference = :nr) ORDER BY created_at LIMIT 1"
            ),
            {"t": self.tenant_id, "nr": subject_id},
        ).first()
        if not zeile:
            raise EntityNotFoundError("SalesInvoicePosting", subject_id)
        return Vorgang(
            subject_id=subject_id, belegart="sales_invoice", brutto=_d(zeile[2]), gebucht=str(zeile[1]) == "posted",
            beendet=str(zeile[1]) == "reversed", inhalt={"buchung": str(zeile[0]), "nummer": subject_id, "betrag": str(_d(zeile[2]))},
        )


def gehoert_docflow(db: Session, tenant_id: str, nummer: str) -> bool:
    """Ob eine Rechnungsnummer ein DocFlow-Beleg des Mandanten ist — dann wird sie nur dort gebucht und storniert."""
    return bool(db.execute(
        text(
            "SELECT 1 FROM domain_docflow.document_headers WHERE tenant_id = :t AND doc_number = :nr "
            # Der alte Rechnungsweg legt fuer sein Archivstueck einen Kopf mit dieser Herkunft an; das ist kein Beleg.
            "AND deleted_at IS NULL AND source_system <> 'gobd_artifact' LIMIT 1"
        ),
        {"t": tenant_id, "nr": nummer},
    ).first())


def nur_mit_rollenrecht(db: Session, tenant_id: str, belegart: str, aktion: str, *, brutto: Any, gebucht: bool) -> None:
    """Fuer Wege ohne gespeicherten Vorgang: 409, sobald die Matrix eine zweite Person verlangt."""
    bedarf = anforderung(belegart, aktion, brutto=_d(brutto), gebucht=gebucht,
                         grenze=FreigabeEngine(db, tenant_id).grenze(belegart))
    if bedarf.zweitfreigabe:
        raise HTTPException(
            status_code=409,
            detail=f"Freigabe erforderlich ({bedarf.risiko}): {bedarf.grund} Dieser Weg kann sie nicht einholen — "
                   "den Beleg über den Belegweg (DocFlow) führen.",
        )


def verlange_oder_409(engine: FreigabeEngine, vorgang: Vorgang, aktion: str, akteur: Optional[str]) -> None:
    """Wie ``verlange_fuer``, fuer Endpunkte: Die fehlende Freigabe ist 409."""
    from app.core.exceptions import ConflictError

    try:
        engine.verlange_fuer(vorgang, aktion, akteur)
    except ConflictError as fehlt:
        raise HTTPException(status_code=409, detail=str(fehlt.detail)) from fehlt


def verlange_gutschrift(db: Session, tenant_id: str, gutschrift_id: str, akteur: Optional[str] = None) -> None:
    """Vor dem Buchen einer Verkaufsgutschrift: die Freigabe einer zweiten Person, sonst 409."""
    engine = VerkaufsgutschriftFreigabe(db, tenant_id)
    verlange_oder_409(engine, engine.vorgang(gutschrift_id, "post"), "post", akteur)


def verlange_storno_ausgangsrechnung(db: Session, tenant_id: str, nummer: str, akteur: Optional[str] = None) -> None:
    """Vor dem Storno ueber den alten Rechnungsweg.

    Eine DocFlow-Rechnung wird nur ueber DocFlow storniert: Der alte Weg fand ihre Buchung ueber die Nummer und
    haette sie ohne Beleg, Statushistorie und Freigabe zurueckgenommen. Jede andere gebuchte Rechnung braucht die
    Freigabe einer zweiten Person mit erhoehter Berechtigung.
    """
    if gehoert_docflow(db, tenant_id, nummer):
        raise HTTPException(
            status_code=409,
            detail=f"Rechnung {nummer} ist ein DocFlow-Beleg und wird über den Belegweg storniert.",
        )
    engine = AusgangsrechnungStornoFreigabe(db, tenant_id)
    verlange_oder_409(engine, engine.vorgang(nummer, "reverse"), "reverse", akteur)


SUBJEKTE: dict[str, type[FreigabeEngine]] = {}


def engine_fuer(subject_type: str, db: Session, tenant_id: str) -> FreigabeEngine:
    """Die Engine des Bereichs — fuer den gemeinsamen Freigabeweg."""
    if not SUBJEKTE:
        from app.services.docflow_freigabe import DocflowFreigabe

        for klasse in (DocflowFreigabe, EingangsrechnungFreigabe, VerkaufsgutschriftFreigabe,
                       AusgangsrechnungStornoFreigabe):
            SUBJEKTE[klasse.SUBJEKT] = klasse
    klasse = SUBJEKTE.get(subject_type)
    if klasse is None:
        raise HTTPException(status_code=404, detail="Vorgangsart nicht bekannt")
    return klasse(db, tenant_id)
