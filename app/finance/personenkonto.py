"""Personenkonten im Hauptbuch (M3, Nutzerentscheid 26.11.2026).

Jede Buchungszeile auf ein Sammelkonto Forderungen bzw. Verbindlichkeiten aus Lieferungen und Leistungen
(``steuerschluessel.DEBITORENKONTO``/``KREDITORENKONTO`` des Kontenrahmens des Mandanten) fuehrt das Personenkonto
des Geschaeftspartners in ``journal_entry_lines.partner_konto``. Daraus entstehen die Saldenliste je Debitor/Kreditor
und der monatliche Saldenabgleich gegen L3.

Buchungswege mit Personenkonto: Ausgangsrechnung, Eingangsrechnung, Verkaufs- und Einkaufsgutschrift, Ernte-
Abrechnung (Kreditor), Storno (die Gegenbuchung kopiert das Personenkonto), Genossenschaft (Auseinandersetzungsguthaben
ueber die Mitgliedschaft am Partner), Fracht (Spediteur als Lieferant). Die Selbstfakturierung bucht nicht ins Journal
(Weg defekt, s. Workboard M3-PERSONENKONTEN-WEGE).

Konto-Ermittlung: Kunde -> ``customers.business_partner_id`` -> ``business_partners.debtor_account``; Lieferant ->
``lieferanten.partner_id`` -> ``business_partners.creditor_account``. Ohne Partner oder Konto ergibt sich ``None`` -
die Buchung bleibt moeglich, die Zeile erscheint dann in der Saldenliste unter "ohne Personenkonto" (sichtbar statt
still verteilt).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.finance.steuerschluessel import DEBITORENKONTO, KREDITORENKONTO, kontenrahmen


def sammelkonten(db: Session, tenant_id: str, *tabellen: dict[str, str]) -> list[str]:
    """Sammelkonten des Kontenrahmens des Mandanten (z. B. SKR03: 1400 und 1600) - leer ohne festgelegten Rahmen.

    Nie alle Rahmen zugleich: 1200 ist im SKR04 Forderungen, im SKR03 aber Bank.
    """
    rahmen = kontenrahmen(db, tenant_id)
    return sorted({tabelle[rahmen] for tabelle in (tabellen or (DEBITORENKONTO, KREDITORENKONTO))
                   if rahmen in tabelle})


def debitorkonto_fuer_kunde(db: Session, tenant_id: str, kunden_id: Optional[str]) -> Optional[str]:
    if not kunden_id:
        return None
    konto = db.execute(text(
        "SELECT bp.debtor_account FROM domain_crm.customers c JOIN domain_crm.business_partners bp "
        "ON bp.partner_id::text = c.business_partner_id::text AND bp.tenant_id = c.tenant_id "
        "WHERE c.tenant_id = :t AND (c.id::text = :k OR c.customer_number = :k) LIMIT 1"),
        {"t": tenant_id, "k": str(kunden_id)}).scalar()
    return str(konto) if konto else None


def kreditorkonto_fuer_lieferant(db: Session, tenant_id: str, lieferant_id: Optional[str]) -> Optional[str]:
    if not lieferant_id:
        return None
    konto = db.execute(text(
        "SELECT bp.creditor_account FROM domain_einkauf.lieferanten l JOIN domain_crm.business_partners bp "
        "ON bp.partner_id::text = l.partner_id AND bp.tenant_id = l.tenant_id "
        "WHERE l.tenant_id = :t AND (l.id::text = :k OR l.lieferantennummer = :k OR l.partner_id = :k) LIMIT 1"),
        {"t": tenant_id, "k": str(lieferant_id)}).scalar()
    if konto:
        return str(konto)
    # Self-Billing / Partner ohne Lieferantenstamm: direktes Kreditorenkonto am business_partner
    konto = db.execute(
        text(
            "SELECT creditor_account FROM domain_crm.business_partners "
            "WHERE tenant_id = :t AND partner_id::text = :k LIMIT 1"
        ),
        {"t": tenant_id, "k": str(lieferant_id)},
    ).scalar()
    return str(konto) if konto else None


def kreditorkonto_fuer_mitglied(db: Session, tenant_id: str, mitglieds_nr: Optional[str]) -> Optional[str]:
    """Kreditorenkonto des Geschaeftspartners hinter einer Genossenschafts-Mitgliedsnummer
    (``business_partner_cooperative_memberships.membership_number``) - Auseinandersetzungsguthaben (§ 73 GenG)."""
    if not mitglieds_nr:
        return None
    konto = db.execute(text(
        "SELECT bp.creditor_account FROM domain_crm.business_partner_cooperative_memberships m "
        "JOIN domain_crm.business_partners bp ON bp.partner_id = m.partner_id AND bp.tenant_id = m.tenant_id "
        "WHERE m.tenant_id = :t AND m.membership_number = :n LIMIT 1"),
        {"t": tenant_id, "n": str(mitglieds_nr)}).scalar()
    return str(konto) if konto else None


def saldenliste(db: Session, tenant_id: str, *, bis: Optional[date] = None) -> dict[str, Any]:
    """Saldo je Personenkonto aus gebuchten Zeilen der Sammelkonten (Soll - Haben), bis einschliesslich ``bis``."""
    konten_liste = sammelkonten(db, tenant_id)
    if not konten_liste:
        return {"stichtag": bis.isoformat() if bis else None, "personenkonten": {}, "ohne_personenkonto": {},
                "hinweis": "Kontenrahmen des Mandanten nicht festgelegt - keine Sammelkonten"}
    zeilen = db.execute(text(
        "SELECT coa.account_number AS sammelkonto, jel.partner_konto, "
        "COALESCE(SUM(jel.debit_amount), 0) - COALESCE(SUM(jel.credit_amount), 0) AS saldo "
        "FROM domain_erp.journal_entry_lines jel "
        "JOIN domain_erp.journal_entries je ON je.id = jel.journal_entry_id AND je.tenant_id = jel.tenant_id "
        "JOIN domain_erp.chart_of_accounts coa ON coa.id = jel.account_id "
        "WHERE jel.tenant_id = :t AND je.status IN ('posted', 'reversed') AND coa.account_number = ANY(:konten) "
        "AND (CAST(:bis AS date) IS NULL OR je.posting_date <= CAST(:bis AS date)) "
        "GROUP BY 1, 2 ORDER BY 1, 2 NULLS LAST"),
        {"t": tenant_id, "konten": konten_liste, "bis": bis}).mappings().all()
    konten: dict[str, dict[str, str]] = {}
    ohne: dict[str, str] = {}
    for z in zeilen:
        saldo = Decimal(str(z["saldo"])).quantize(Decimal("0.01"))
        if z["partner_konto"]:
            konten[str(z["partner_konto"])] = {"sammelkonto": str(z["sammelkonto"]), "saldo": str(saldo)}
        elif saldo:
            ohne[str(z["sammelkonto"])] = str(saldo)
    return {"stichtag": bis.isoformat() if bis else None, "personenkonten": konten, "ohne_personenkonto": ohne}
