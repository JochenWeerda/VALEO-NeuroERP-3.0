"""Steuerschluessel: die eine Stelle, aus der Belege ihre Umsatzsteuer und ihre Konten nehmen.

Quelle ist ``domain_erp.tax_keys`` — die Tabelle hinter der Maske „Steuerschluessel“, aus der auch
Eingangsrechnung, Umsatzsteuer-Voranmeldung und DATEV-Ausgabe lesen. Bis zum 12.10.2026 gab es
daneben ``vat_codes``, die sonst niemand benutzte; die Gutschrift hing einen halben Tag lang daran.

Ein Steuerschluessel gehoert einem Mandanten und traegt: Satz, Umsatzsteuerkonto (``credit_account``),
Vorsteuerkonto (``debit_account``), Erloeskonto (``revenue_account``), Gueltigkeit und die Kennzeichen
Reverse Charge, innergemeinschaftlich, Export, Paragraf 24 UStG.

Nichts wird angenommen: Fehlt eine Angabe oder widersprechen sich Angaben, gibt es eine
``Steuerklaerung`` — der Beleg wird nicht gebucht, sondern einem Menschen vorgelegt.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

CENT = Decimal("0.01")
KONTENRAHMEN_SCHLUESSEL = "finance.kontenrahmen"


class Steuerklaerung(Exception):
    """Die Umsatzsteuer eines Belegs laesst sich nicht eindeutig bestimmen — ein Mensch muss pruefen."""


class Steuergruppe(BaseModel):
    """Alle Positionen eines Steuerschluessels: Netto, Steuer und die Konten dazu."""

    tax_code: str
    satz: Decimal
    netto: Decimal
    steuer: Decimal
    erloeskonto: str
    steuerkonto: Optional[str] = None


def steuergruppen(db: Session, tenant_id: str, zeilen: list[tuple]) -> list[Steuergruppe]:
    """Netto und Umsatzsteuer je Steuerschluessel aus Verkaufspositionen ``(nr, tax_code, tax_rate, netto)``.

    Die Steuer wird je Steuerschluessel auf die Summe der Nettobetraege gerechnet, nicht je Position.
    """
    if not zeilen:
        raise Steuerklaerung("Der Beleg hat keine Positionen; die Umsatzsteuer lässt sich nicht bestimmen.")
    ohne = [str(nr) for nr, code, _satz, _netto in zeilen if not (code or "").strip()]
    if ohne:
        raise Steuerklaerung(f"Position {', '.join(ohne)} hat keinen Steuerschlüssel.")

    codes = sorted({str(code).strip() for _nr, code, _satz, _netto in zeilen})
    bekannt: dict[str, tuple] = {}
    for r in db.execute(
        text(
            "SELECT code, steuersatz, credit_account, revenue_account, reverse_charge FROM domain_erp.tax_keys "
            "WHERE tenant_id = :tid AND code = ANY(:codes) AND active "
            "AND gueltig_von <= CURRENT_DATE AND (gueltig_bis IS NULL OR gueltig_bis >= CURRENT_DATE)"
        ),
        {"codes": codes, "tid": tenant_id},
    ).fetchall():
        bekannt[str(r[0])] = tuple(r)
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
        _code, rate, steuerkonto, erloeskonto, reverse_charge = bekannt[code]
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


# --- Grundausstattung SKR03 ----------------------------------------------------------------------

# Nur die vier Regelfaelle. Steuerfreie Umsaetze, innergemeinschaftliche Lieferungen, Export und die
# Durchschnittssaetze nach Paragraf 24 UStG ordnet die Buchhaltung selbst ein — ein geratenes Konto
# waere eine stillschweigende Annahme.
SKR03_STEUERSCHLUESSEL = (
    # code, Bezeichnung, Satz, UStVA-Position, UStVA-Text, Vorsteuerkonto, Umsatzsteuerkonto, Erloeskonto
    ("2", "Umsatzsteuer 7 %", Decimal("7"), "86", "Steuerpflichtige Umsätze 7 %", None, "1771", "8300"),
    ("3", "Umsatzsteuer 19 %", Decimal("19"), "81", "Steuerpflichtige Umsätze 19 %", None, "1776", "8400"),
    ("8", "Vorsteuer 7 %", Decimal("7"), "66", "Abziehbare Vorsteuer", "1571", None, None),
    ("9", "Vorsteuer 19 %", Decimal("19"), "66", "Abziehbare Vorsteuer", "1576", None, None),
)
SKR03_KONTEN = (
    ("1571", "Abziehbare Vorsteuer 7 %", "asset", "tax"),
    ("1576", "Abziehbare Vorsteuer 19 %", "asset", "tax"),
    ("1771", "Umsatzsteuer 7 %", "liability", "tax"),
    ("1776", "Umsatzsteuer 19 %", "liability", "tax"),
    ("8300", "Erlöse 7 % USt", "revenue", "revenue"),
    ("8400", "Erlöse 19 % USt", "revenue", "revenue"),
)


def kontenrahmen(db: Session, tenant_id: str) -> Optional[str]:
    """Der Kontenrahmen des Mandanten (``SKR03``) — oder ``None``, wenn keiner festgelegt ist."""
    wert = db.execute(
        text(
            "SELECT property_value FROM domain_shared.system_properties "
            "WHERE tenant_id = :tid AND property_key = :key"
        ),
        {"tid": tenant_id, "key": KONTENRAHMEN_SCHLUESSEL},
    ).scalar()
    return str(wert).strip() or None if wert is not None else None


def richte_skr03_ein(db: Session, tenant_id: str, gueltig_von: date = date(2021, 1, 1)) -> dict[str, list[str]]:
    """Legt fuer den Mandanten den Kontenrahmen SKR03, die vier Regel-Steuerschluessel und fehlende Konten an.

    Bestehendes bleibt unberuehrt: Ein Schluessel, den es fuer den Mandanten schon gibt, und ein Konto,
    das er oder der gemeinsame Rahmen schon hat, werden nicht angefasst. Der Aufrufer schreibt fest.
    """
    angelegt: dict[str, list[str]] = {"steuerschluessel": [], "konten": []}

    db.execute(
        text(
            "INSERT INTO domain_shared.system_properties "
            "(id, tenant_id, property_key, property_value, property_type, category, description) "
            "VALUES (:id, :tid, :key, 'SKR03', 'string', 'finance', 'Kontenrahmen des Mandanten') "
            "ON CONFLICT (tenant_id, property_key) DO UPDATE SET property_value = 'SKR03'"
        ),
        {"id": uuid7(), "tid": tenant_id, "key": KONTENRAHMEN_SCHLUESSEL},
    )

    vorhanden = {
        str(r[0]) for r in db.execute(
            text(
                "SELECT account_number FROM domain_erp.chart_of_accounts "
                "WHERE tenant_id IN (:tid, 'system') AND account_number = ANY(:nummern)"
            ),
            {"tid": tenant_id, "nummern": [k[0] for k in SKR03_KONTEN]},
        ).fetchall()
    }
    for nummer, name, art, kategorie in SKR03_KONTEN:
        if nummer in vorhanden:
            continue
        db.execute(
            text(
                "INSERT INTO domain_erp.chart_of_accounts "
                "(id, tenant_id, account_number, account_name, account_type, category, is_active, created_at, updated_at) "
                "VALUES (:id, :tid, :nr, :name, :art, :kat, true, NOW(), NOW())"
            ),
            {"id": uuid7(), "tid": tenant_id, "nr": nummer, "name": name, "art": art, "kat": kategorie},
        )
        angelegt["konten"].append(nummer)

    schon = {
        str(r[0]) for r in db.execute(
            text("SELECT code FROM domain_erp.tax_keys WHERE tenant_id = :tid"), {"tid": tenant_id}
        ).fetchall()
    }
    for code, name, satz, position, positionstext, vorsteuer, umsatzsteuer, erloes in SKR03_STEUERSCHLUESSEL:
        if code in schon:
            continue
        db.execute(
            text(
                "INSERT INTO domain_erp.tax_keys "
                "(id, tenant_id, code, bezeichnung, steuersatz, ustva_position, ustva_bezeichnung, "
                " gueltig_von, debit_account, credit_account, revenue_account, country, active) "
                "VALUES (:id, :tid, :code, :name, :satz, :pos, :postext, :von, :vst, :ust, :erloes, 'DE', true)"
            ),
            {
                "id": uuid7(), "tid": tenant_id, "code": code, "name": name, "satz": satz, "pos": position,
                "postext": positionstext, "von": gueltig_von, "vst": vorsteuer, "ust": umsatzsteuer, "erloes": erloes,
            },
        )
        angelegt["steuerschluessel"].append(code)
    return angelegt
