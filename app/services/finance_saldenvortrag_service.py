"""Saldenvortrag ins neue Geschaeftsjahr (M3, 23.11.2026).

Voraussetzung: Alle zwoelf Perioden des Jahres sind gesperrt (Monatsabschluss). Dann entsteht genau eine
Eroeffnungsbuchung am 01.01. des Folgejahres ueber den kanonischen Buchungsdienst:

* jedes Bestandskonto (Aktiva, Passiva, Eigenkapital) mit seinem Saldo gegen 9000 "Saldenvortraege Sachkonten",
* das Jahresergebnis (Saldo aller Erfolgskonten) auf Gewinnvortrag bzw. Verlustvortrag gegen 9000.

9000 gleicht sich damit aus. Gebucht ist, was im Journal ``posted`` oder ``reversed`` steht (ein Storno zaehlt mit
seinem Original). Ein zweiter Vortrag fuer dasselbe Jahr wird abgewiesen; fehlt ein Konto, wird nichts gebucht.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.core.finance_periods import gesperrter_zustand
from app.finance.steuerschluessel import kontenrahmen

#: Kontenrahmen -> (Saldenvortrag Sachkonten, Gewinnvortrag, Verlustvortrag)
VORTRAGSKONTEN = {"SKR03": ("9000", "0860", "0868"), "SKR04": ("9000", "2970", "2978")}
BESTAND = ("asset", "liability", "equity")
ERFOLG = ("revenue", "expense")
NULL = Decimal("0.00")


@dataclass
class Saldenvortrag:
    jahr: int
    journal_entry_id: str
    konten: int
    jahresergebnis: Decimal
    zeilen: list[dict] = field(default_factory=list)


def _salden(db: Session, tenant_id: str, jahr: int) -> list[tuple[str, str, Decimal]]:
    """(Kontonummer, Kontoart, Soll minus Haben) aller gebuchten Zeilen bis Ende ``jahr``."""
    zeilen = db.execute(text(
        "SELECT coa.account_number, LOWER(coa.account_type), "
        "COALESCE(SUM(jel.debit_amount - jel.credit_amount), 0) "
        "FROM domain_erp.journal_entry_lines jel "
        "JOIN domain_erp.journal_entries je ON je.id = jel.journal_entry_id AND je.tenant_id = jel.tenant_id "
        "JOIN domain_erp.chart_of_accounts coa ON coa.id = jel.account_id AND coa.tenant_id = je.tenant_id "
        "WHERE je.tenant_id = :t AND je.status IN ('posted', 'reversed') AND je.period <= :bis "
        "GROUP BY coa.account_number, coa.account_type ORDER BY coa.account_number"),
        {"t": tenant_id, "bis": f"{jahr}-12"}).fetchall()
    return [(str(nr), str(art or ""), Decimal(str(saldo)).quantize(Decimal("0.01"))) for nr, art, saldo in zeilen]


def trage_salden_vor(db: Session, tenant_id: str, jahr: int, *, actor: str | None = None) -> Saldenvortrag:
    from app.services.finance_transaction_service import FinanceTransactionService

    offen = [f"{jahr}-{monat:02d}" for monat in range(1, 13)
             if not gesperrter_zustand(db, tenant_id, f"{jahr}-{monat:02d}")]
    if offen:
        raise ConflictError(f"Saldenvortrag {jahr} erst nach dem Abschluss aller Perioden; offen: {', '.join(offen)}")
    referenz = f"SV-{jahr}"
    if db.execute(text("SELECT 1 FROM domain_erp.journal_entries WHERE tenant_id = :t AND source = 'saldenvortrag' "
                       "AND reference = :r AND status IN ('posted', 'reversed', 'draft') LIMIT 1"),
                  {"t": tenant_id, "r": referenz}).first():
        raise ConflictError(f"Saldenvortrag {jahr} ist bereits gebucht.")
    rahmen = kontenrahmen(db, tenant_id)
    if rahmen not in VORTRAGSKONTEN:
        raise ConflictError("Kontenrahmen des Mandanten nicht eingerichtet")
    sv_konto, gewinn_konto, verlust_konto = VORTRAGSKONTEN[rahmen]

    salden = _salden(db, tenant_id, jahr)
    unbekannt = sorted({nr for nr, art, saldo in salden if saldo != NULL and art not in BESTAND + ERFOLG})
    if unbekannt:
        raise ConflictError(f"Konten ohne Kontoart (Bestand/Erfolg) - Saldenvortrag nicht bestimmbar: {', '.join(unbekannt)}")
    zeilen: list[tuple[str, Decimal]] = [(nr, saldo) for nr, art, saldo in salden if art in BESTAND and saldo != NULL
                                         and nr != sv_konto]
    ergebnis = -sum((saldo for nr, art, saldo in salden if art in ERFOLG), NULL)  # Gewinn positiv
    if ergebnis != NULL:
        # Gewinn steht im Haben des Gewinnvortrags (Soll minus Haben negativ), Verlust im Soll des Verlustvortrags.
        zeilen.append((gewinn_konto if ergebnis > NULL else verlust_konto, -ergebnis))
    if not zeilen:
        raise ConflictError(f"Keine Salden zum Vortragen fuer {jahr}.")
    gegen = -sum((betrag for _, betrag in zeilen), NULL)

    dienst = FinanceTransactionService(db, tenant_id, commit_on_success=False)
    konto = dienst.account_id_for_number
    buchungszeilen = []
    for nummer, betrag in [*zeilen, (sv_konto, gegen)]:
        if betrag == NULL:
            continue
        buchungszeilen.append({"account_id": konto(nummer), "description": f"Saldenvortrag {jahr} {nummer}",
                               "debit_amount": str(betrag) if betrag > NULL else "0",
                               "credit_amount": str(-betrag) if betrag < NULL else "0"})
    stichtag = datetime(jahr + 1, 1, 1)
    eintrag = dienst.create(f"SV-{jahr}-{tenant_id[:8]}", f"Saldenvortrag {jahr} in das Geschaeftsjahr {jahr + 1}",
                            stichtag, buchungszeilen, reference=referenz, source="saldenvortrag",
                            document_type="saldenvortrag", period=f"{jahr + 1}-01", posting_date=stichtag)
    dienst.post(eintrag.id, posted_by=actor)
    db.commit()
    return Saldenvortrag(jahr=jahr, journal_entry_id=str(eintrag.id), konten=len(zeilen), jahresergebnis=ergebnis,
                         zeilen=[{"konto": n, "saldo": float(b)} for n, b in zeilen])
