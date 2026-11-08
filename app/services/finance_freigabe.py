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

import hashlib
import re
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.core.freigabe import HAUPTBUCHBUCHUNG, STANDARDGRENZEN, ZAHLUNGSLAUF, Befund, anforderung
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
            befunde=self._ap_befunde(subject_id, invoice, brutto),
        )


    def _ap_befunde(self, subject_id: str, invoice: dict[str, Any], brutto: Decimal) -> list[Befund]:
        """Wiederkehrende Finanzrechnungen bucht die Buchhaltung selbst (FIN-CONTROL-001). Auffaellig ist eine
        moegliche Dublette (sperrt) und eine Abweichung von mehr als 10 % vom ueblichen Betrag des Lieferanten.
        """
        lieferant = invoice.get("customerId") or invoice.get("supplierId")
        if not lieferant:
            return []
        andere = self.db.execute(
            text(
                "SELECT doc_number, CAST(data AS jsonb)->>'date', CAST(data AS jsonb)->>'totalGross', "
                "CAST(data AS jsonb)->>'status' FROM documents WHERE doc_type = 'ap_invoice' AND doc_number <> :nr "
                "AND CAST(data AS jsonb)->>'tenantId' = :t "
                "AND COALESCE(CAST(data AS jsonb)->>'customerId', CAST(data AS jsonb)->>'supplierId') = :s"
            ),
            {"nr": subject_id, "t": self.tenant_id, "s": str(lieferant)},
        ).fetchall()
        befunde: list[Befund] = []
        for nummer, datum, betrag, stand in andere:
            if stand != "STORNIERT" and brutto > 0 and _d(betrag) == brutto and str(datum) == str(invoice.get("date")):
                befunde.append(Befund("dublette", "kritisch", f"Mögliche Dublette der Eingangsrechnung {nummer}."))
                break
        gebucht = [_d(b) for _n, _d_, b, stand in andere if stand == "VERBUCHT" and _d(b) > 0]
        if gebucht:
            ueblich = sum(gebucht, Decimal("0")) / len(gebucht)
            if abs(brutto - ueblich) > ueblich * Decimal("0.10"):
                befunde.append(Befund(
                    "abweichung_ueblich", "warnung",
                    f"Eingangsrechnung {brutto} EUR weicht um mehr als 10 % vom üblichen Betrag "
                    f"({ueblich.quantize(Decimal('0.01'))} EUR) dieses Lieferanten ab."))
        return befunde


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
            befunde=[Befund(
                "gutschrift_ohne_bezug", "kritisch",
                f"Gutschrift über {self.grenze('sales_credit_memo')} EUR ohne Bezugsrechnung (Forderungsverzicht ohne Beleg).",
            )] if not rechnung and _d(zeile["total_amount"]) > (self.grenze("sales_credit_memo") or Decimal("0")) else [],
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


_FINANZ_LESEN = frozenset({"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin"})
_FINANZ_SCHREIBEN = frozenset({"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin"})
_FINANZ_LEITUNG = frozenset({"FINANCE_ADMIN", "admin"})
# Der Controller ueberwacht die Ausnahmen: Er gibt kritische Befunde frei, bucht aber nicht (FIN-CONTROL-001).
_CONTROLLING = frozenset({"controller", "CONTROLLING"})


class HauptbuchFreigabe(FreigabeEngine):
    """Manuelle Hauptbuchbuchung (``domain_erp.journal_entries``)."""

    SUBJEKT = "journal_entry"

    def vorgang(self, subject_id: str, aktion: str) -> Vorgang:
        kopf = self.db.execute(
            text(
                "SELECT id, entry_number, reference, document_number, status, total_debit, source, entry_date, posting_date "
                "FROM domain_erp.journal_entries WHERE id = :id AND tenant_id = :t"
            ),
            {"id": subject_id, "t": self.tenant_id},
        ).mappings().first()
        if not kopf:
            raise EntityNotFoundError("JournalEntry", subject_id)
        zeilen = self.db.execute(
            text(
                "SELECT account_id, debit_amount, credit_amount FROM domain_erp.journal_entry_lines "
                "WHERE journal_entry_id = :id ORDER BY line_number, id"
            ),
            {"id": subject_id},
        ).fetchall()
        # Wer die Buchung angelegt hat, steht im FiBu-Audit; die Buchung selbst fuehrt ihn nicht.
        ersteller = self.db.execute(
            text(
                "SELECT user_id FROM domain_shared.audit_logs WHERE tenant_id = :t AND entity_type = 'journal_entry' "
                "AND entity_id = :id AND action = 'create' ORDER BY timestamp LIMIT 1"
            ),
            {"t": self.tenant_id, "id": subject_id},
        ).scalar()
        stand = str(kopf["status"] or "")
        return Vorgang(
            subject_id=str(kopf["id"]), belegart=HAUPTBUCHBUCHUNG, brutto=_d(kopf["total_debit"]), gebucht=stand == "posted",
            beendet=stand == "reversed", ersteller=str(ersteller) if ersteller else None,
            inhalt={
                "nummer": kopf["entry_number"], "bezug": kopf["reference"], "herkunft": kopf["source"],
                "datum": str(kopf["entry_date"]), "buchungsdatum": str(kopf["posting_date"]),
                "zeilen": [[str(z[0]), str(_d(z[1])), str(_d(z[2]))] for z in zeilen],
            },
            befunde=self._konten_befunde(subject_id) if aktion == "post" else [],
        )

    def geschuetzte_konten(self) -> set[str]:
        """Konten, die nur ueber Belege bebucht werden: Forderungen, Verbindlichkeiten, Steuerkonten.

        Der Mandant kann die Liste setzen (``kontrolle.geschuetzte_konten``, kommagetrennt).
        """
        eigene = self.db.execute(
            text("SELECT property_value FROM domain_shared.system_properties WHERE tenant_id = :t AND property_key = :k"),
            {"t": self.tenant_id, "k": "kontrolle.geschuetzte_konten"},
        ).scalar()
        if eigene is not None:
            return {k.strip() for k in str(eigene).split(",") if k.strip()}
        konten = {"1400"}
        for zeile in self.db.execute(
            text("SELECT debit_account, credit_account FROM domain_erp.tax_keys WHERE tenant_id = :t"), {"t": self.tenant_id}
        ).fetchall():
            konten |= {str(k).strip() for k in zeile if k and str(k).strip()}
        try:
            from app.services.finance_eingangsrechnung_buchung import kreditorenkonto

            konten.add(str(kreditorenkonto(self.db, self.tenant_id, {})))
        except Exception:  # noqa: BLE001 — ohne Kontenrahmen gibt es kein Kreditorenkonto zu schuetzen
            pass
        return konten

    def _konten_befunde(self, entry_id: str) -> list[Befund]:
        bebucht = {str(z[0]) for z in self.db.execute(
            text(
                "SELECT k.account_number FROM domain_erp.journal_entry_lines l "
                "JOIN domain_erp.chart_of_accounts k ON k.id = l.account_id WHERE l.journal_entry_id = :id"
            ),
            {"id": entry_id},
        ).fetchall()}
        treffer = sorted(bebucht & self.geschuetzte_konten())
        if not treffer:
            return []
        return [Befund(
            "geschuetztes_konto", "kritisch",
            f"Manuelle Buchung auf geschütztem Konto {', '.join(treffer)} (sonst nur über Belege bebucht).")]

    def leserollen(self, v: Vorgang) -> frozenset[str]:
        return _FINANZ_LESEN

    def anfragerollen(self, v: Vorgang, aktion: str) -> frozenset[str]:
        return _FINANZ_SCHREIBEN

    def freigaberollen(self, v: Vorgang, risiko: str) -> frozenset[str]:
        return (_FINANZ_LEITUNG if risiko == "R4" else _FINANZ_SCHREIBEN) | _CONTROLLING


class ZahlungslaufFreigabe(FreigabeEngine):
    """Zahlungslauf (``domain_erp.payment_runs``). Freigabe ist die Zahlungsfreigabe (R4)."""

    SUBJEKT = "payment_run"

    def vorgang(self, subject_id: str, aktion: str) -> Vorgang:
        lauf = self.db.execute(
            text(
                "SELECT id, run_number, execution_date, initiator_iban, total_amount, payment_count, status, created_by "
                "FROM domain_erp.payment_runs WHERE id = :id AND tenant_id = :t"
            ),
            {"id": subject_id, "t": self.tenant_id},
        ).mappings().first()
        if not lauf:
            raise EntityNotFoundError("PaymentRun", subject_id)
        posten = self.db.execute(
            text(
                "SELECT creditor_id, iban, amount, op_id, invoice_number FROM domain_erp.payment_run_items "
                "WHERE payment_run_id = :id AND tenant_id = :t ORDER BY id"
            ),
            {"id": subject_id, "t": self.tenant_id},
        ).fetchall()
        stand = str(lauf["status"] or "")
        return Vorgang(
            subject_id=str(lauf["id"]), belegart=ZAHLUNGSLAUF, brutto=_d(lauf["total_amount"]), gebucht=stand == "executed",
            beendet=stand in ("cancelled", "storniert"), ersteller=(str(lauf["created_by"]).strip() or None) if lauf["created_by"] else None,
            # Wohin wie viel geht: Aendert sich ein Empfaenger, eine IBAN oder ein Betrag, gilt die Freigabe nicht mehr.
            inhalt={
                "nummer": lauf["run_number"], "ausfuehrung": str(lauf["execution_date"]), "auftraggeber": lauf["initiator_iban"],
                "summe": str(_d(lauf["total_amount"])), "anzahl": int(lauf["payment_count"] or 0),
                "zahlungen": [[str(z[0]), z[1], str(_d(z[2])), str(z[3]), z[4]] for z in posten],
            },
        )

    def leserollen(self, v: Vorgang) -> frozenset[str]:
        return _FINANZ_LESEN

    def anfragerollen(self, v: Vorgang, aktion: str) -> frozenset[str]:
        return _FINANZ_SCHREIBEN

    def freigaberollen(self, v: Vorgang, risiko: str) -> frozenset[str]:
        return _FINANZ_LEITUNG


def verlange_hauptbuchbuchung(db: Session, tenant_id: str, entry_id: str, akteur: Optional[str] = None) -> None:
    """Vor dem Buchen einer manuellen Hauptbuchbuchung: die Freigabe einer zweiten Person, sonst 409."""
    engine = HauptbuchFreigabe(db, tenant_id)
    try:
        vorgang = engine.vorgang(entry_id, "post")
    except EntityNotFoundError:
        return  # Der Buchungsweg meldet die fehlende Buchung selbst.
    verlange_oder_409(engine, vorgang, "post", akteur)


def verlange_hauptbuchstorno(db: Session, tenant_id: str, entry_id: str, akteur: Optional[str] = None) -> None:
    """Vor dem Storno einer Hauptbuchbuchung.

    Die Buchung eines Belegs wird ueber den Beleg storniert: Sonst bliebe er „gebucht", waehrend seine Buchung
    zurueckgenommen ist. Jede andere gebuchte Buchung braucht die Freigabe einer zweiten Person mit erhoehter
    Berechtigung.
    """
    engine = HauptbuchFreigabe(db, tenant_id)
    try:
        vorgang = engine.vorgang(entry_id, "reverse")
    except EntityNotFoundError:
        return
    for bezug in (vorgang.inhalt.get("bezug"), vorgang.inhalt.get("nummer")):
        if bezug and gehoert_docflow(db, tenant_id, str(bezug)):
            raise HTTPException(
                status_code=409,
                detail=f"Die Buchung gehört zum Beleg {bezug} und wird über den Belegweg storniert.",
            )
    verlange_oder_409(engine, vorgang, "reverse", akteur)


class BuchungsimportFreigabe(FreigabeEngine):
    """Massenimport von Hauptbuchbuchungen. Der Vorgang ist der Abdruck von Mandant, Periode und Datei.

    Die Datei liegt nicht auf dem Server: Der Probelauf nennt ihren Abdruck, die zweite Person gibt genau diesen
    frei, und der Import laeuft nur mit einer Datei, die denselben Abdruck hat.
    """

    SUBJEKT = "journal_import"

    def vorgang(self, subject_id: str, aktion: str) -> Vorgang:
        if not re.fullmatch(r"[0-9a-f]{64}", subject_id or ""):
            raise EntityNotFoundError("JournalImport", subject_id)
        befunde = [Befund("massenimport", "warnung", "Massenimport von Hauptbuchbuchungen.")]
        # Dieselbe Datei fuer dieselbe Periode noch einmal: eine Dublette, unabhaengig vom Betrag.
        schon = self.db.execute(
            text(
                "SELECT 1 FROM domain_docflow.control_findings WHERE tenant_id = :t AND subject_type = :s "
                "AND subject_id = :id AND action = 'post' LIMIT 1"
            ),
            {"t": self.tenant_id, "s": self.SUBJEKT, "id": subject_id},
        ).first()
        if schon:
            befunde.append(Befund("dublette", "kritisch", "Diese Datei wurde für diese Periode bereits importiert."))
        return Vorgang(subject_id=subject_id, belegart=HAUPTBUCHBUCHUNG, brutto=Decimal("0"), gebucht=False,
                       inhalt={"abdruck": subject_id}, befunde=befunde)

    def leserollen(self, v: Vorgang) -> frozenset[str]:
        return _FINANZ_LESEN

    def anfragerollen(self, v: Vorgang, aktion: str) -> frozenset[str]:
        return _FINANZ_LEITUNG  # der Massenimport ist der Finanzleitung vorbehalten

    def freigaberollen(self, v: Vorgang, risiko: str) -> frozenset[str]:
        return _FINANZ_LEITUNG | _CONTROLLING


def importabdruck(tenant_id: str, period: str, inhalt: bytes) -> str:
    return hashlib.sha256(f"{tenant_id}|{period}|".encode("utf-8") + inhalt).hexdigest()


def verlange_buchungsimport(db: Session, tenant_id: str, abdruck: str, akteur: Optional[str] = None) -> None:
    """Vor dem Massenimport: die Freigabe einer zweiten Person fuer genau diese Datei, sonst 409."""
    engine = BuchungsimportFreigabe(db, tenant_id)
    verlange_oder_409(engine, engine.vorgang(abdruck, "post"), "post", akteur)


class _EinkaufsmemoFreigabe(FreigabeEngine):
    """Lieferantengutschrift bzw. -belastung des Einkaufs (Dokumentspeicher)."""

    SPEICHER = ""

    def vorgang(self, subject_id: str, aktion: str) -> Vorgang:
        from app.documents.router_helpers import get_from_store, get_repository

        memo = get_from_store(self.SPEICHER, subject_id, get_repository(self.db))
        return self.vorgang_aus(subject_id, memo)

    def vorgang_aus(self, subject_id: str, memo: Optional[dict[str, Any]]) -> Vorgang:
        # Ein Beleg ohne Mandant (vor dem 13.10.2026 angelegt) gehoert niemandem nachweislich und wird nicht gebucht.
        if not memo or str(memo.get("tenantId") or "") != self.tenant_id:
            raise EntityNotFoundError("PurchaseMemo", subject_id)
        return Vorgang(
            subject_id=subject_id, belegart="purchase_credit_memo", brutto=_d(memo.get("grossAmount")),
            gebucht=bool(memo.get("booked")), ersteller=memo.get("createdBy"),
            # Buchungs- und Verrechnungsstand gehoeren nicht zum Abdruck: Eine Freigabe gilt fuer den Geschaeftsvorfall.
            inhalt={
                "nummer": memo.get("number"), "lieferant": memo.get("supplierId"), "rechnung": memo.get("invoiceId"),
                "abrechnung": memo.get("settlementId"), "grund": memo.get("reason"),
                "summen": [str(_d(memo.get(k))) for k in ("netAmount", "taxAmount", "grossAmount")],
                "positionen": memo.get("items") or [],
            },
            # Die Abrechnungskorrektur der Ernte ist ein normaler Vorgang; ab der Schwelle sieht sie der Controller.
            befunde=[Befund(
                "agrar_korrektur", "warnung",
                f"Abrechnungskorrektur {_d(memo.get('grossAmount'))} EUR ab {STANDARDGRENZEN['agrar_korrektur']} EUR.",
            )] if memo.get("settlementId") and _d(memo.get("grossAmount")) >= STANDARDGRENZEN["agrar_korrektur"] else [],
        )


class EinkaufsgutschriftFreigabe(_EinkaufsmemoFreigabe):
    SUBJEKT = "einkauf_credit_memo"
    SPEICHER = "credit_memo"


class EinkaufsbelastungFreigabe(_EinkaufsmemoFreigabe):
    SUBJEKT = "einkauf_debit_memo"
    SPEICHER = "debit_memo"


def verlange_einkaufsmemo(db: Session, tenant_id: str, memo_type: str, memo_id: str, memo: Optional[dict[str, Any]],
                          akteur: Optional[str] = None) -> None:
    """Vor dem Buchen oder Verrechnen einer Lieferantengutschrift oder -belastung.

    Die Freigabe gilt fuer den Geschaeftsvorfall: Wurde sie beim Buchen verbraucht und ist der Inhalt unveraendert,
    deckt sie auch die Verrechnung (und umgekehrt).
    """
    engine = (EinkaufsgutschriftFreigabe if memo_type == "credit_memo" else EinkaufsbelastungFreigabe)(db, tenant_id)
    try:
        vorgang = engine.vorgang_aus(memo_id, memo)
    except EntityNotFoundError as fehlt:
        raise HTTPException(status_code=404, detail="Beleg nicht gefunden") from fehlt
    abdruck = engine.abdruck(vorgang, "post")
    if any(f["action"] == "post" and f["status"] == "consumed" and f["fingerprint"] == abdruck for f in engine.liste(memo_id)):
        return
    verlange_oder_409(engine, vorgang, "post", akteur)


SUBJEKTE: dict[str, type[FreigabeEngine]] = {}


def engine_fuer(subject_type: str, db: Session, tenant_id: str) -> FreigabeEngine:
    """Die Engine des Bereichs — fuer den gemeinsamen Freigabeweg."""
    if not SUBJEKTE:
        from app.services.docflow_freigabe import DocflowFreigabe

        for klasse in (DocflowFreigabe, EingangsrechnungFreigabe, VerkaufsgutschriftFreigabe,
                       AusgangsrechnungStornoFreigabe, HauptbuchFreigabe, ZahlungslaufFreigabe,
                       BuchungsimportFreigabe, EinkaufsgutschriftFreigabe, EinkaufsbelastungFreigabe):
            SUBJEKTE[klasse.SUBJEKT] = klasse
    klasse = SUBJEKTE.get(subject_type)
    if klasse is None:
        raise HTTPException(status_code=404, detail="Vorgangsart nicht bekannt")
    return klasse(db, tenant_id)
