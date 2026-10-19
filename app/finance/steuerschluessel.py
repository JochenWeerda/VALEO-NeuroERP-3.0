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

import re
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


def verkauf_hindernis(code: str, satz: Decimal, steuerkonto: Optional[str], erloeskonto: Optional[str],
                      reverse_charge: bool) -> Optional[str]:
    """Warum mit dem Schluessel kein Verkaufsbeleg automatisch gebucht wird — oder ``None``."""
    if reverse_charge:
        return f"Steuerschlüssel {code} (Reverse Charge) wird nicht automatisch gebucht."
    if not (erloeskonto or "").strip():
        return f"Für Steuerschlüssel {code} ist kein Erlöskonto hinterlegt."
    if satz > 0 and not (steuerkonto or "").strip():
        return f"Für Steuerschlüssel {code} ist kein Umsatzsteuerkonto hinterlegt."
    return None


def verwendung(code: str, satz: Decimal, steuerkonto: Optional[str], vorsteuerkonto: Optional[str],
               erloeskonto: Optional[str], reverse_charge: bool) -> str:
    """Wofuer der Schluessel automatisch bucht — fuer die Maske, aus derselben Regel wie die Buchung."""
    hindernis = verkauf_hindernis(code, satz, steuerkonto, erloeskonto, reverse_charge)
    teile = ([] if hindernis else ["Verkauf"]) + (["Einkauf"] if (vorsteuerkonto or "").strip() else [])
    return ", ".join(teile) if teile else f"Bucht nicht automatisch: {hindernis}"


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
        hindernis = verkauf_hindernis(code, satz, steuerkonto, erloeskonto, bool(reverse_charge))
        if hindernis:
            raise Steuerklaerung(hindernis)
        netto = netto_je_code[code].quantize(CENT, rounding=ROUND_HALF_UP)
        gruppen.append(Steuergruppe(
            tax_code=code, satz=satz, netto=netto,
            steuer=(netto * satz / Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP),
            erloeskonto=str(erloeskonto).strip(),
            steuerkonto=str(steuerkonto).strip() if satz > 0 else None,
        ))
    return gruppen


# --- Eingangsbelege -----------------------------------------------------------------------------

class Vorsteuergruppe(BaseModel):
    """Alle Positionen eines Eingangsbelegs mit demselben Steuerschluessel und Aufwandskonto."""

    tax_code: str
    satz: Decimal
    netto: Decimal
    steuer: Decimal
    aufwandskonto: str
    vorsteuerkonto: Optional[str] = None


def vorsteuergruppen(db: Session, tenant_id: str, zeilen: list[tuple]) -> list[Vorsteuergruppe]:
    """Netto und Vorsteuer je Steuerschluessel aus Eingangspositionen ``(nr, tax_code, tax_rate, netto, aufwandskonto)``.

    Das Gegenstueck zu ``steuergruppen``: Die Position nennt ihren Steuerschluessel; ein Satz allein genuegt nicht.
    Das Aufwandskonto nennt die Position — oder es kommt aus dem Steuerschluessel. Fehlt beides, wird nicht gebucht.
    """
    if not zeilen:
        raise Steuerklaerung("Der Beleg hat keine Positionen; die Vorsteuer lässt sich nicht bestimmen.")
    ohne = [str(z[0]) for z in zeilen if not (z[1] or "").strip()]
    if ohne:
        raise Steuerklaerung(f"Position {', '.join(ohne)} hat keinen Steuerschlüssel.")

    codes = sorted({str(z[1]).strip() for z in zeilen})
    bekannt: dict[str, tuple] = {}
    for r in db.execute(
        text(
            "SELECT code, steuersatz, debit_account, expense_account, reverse_charge, credit_account "
            "FROM domain_erp.tax_keys "
            "WHERE tenant_id = :tid AND code = ANY(:codes) AND active "
            "AND gueltig_von <= CURRENT_DATE AND (gueltig_bis IS NULL OR gueltig_bis >= CURRENT_DATE)"
        ),
        {"codes": codes, "tid": tenant_id},
    ).fetchall():
        bekannt[str(r[0])] = tuple(r)
    unbekannt = [c for c in codes if c not in bekannt]
    if unbekannt:
        raise Steuerklaerung(f"Steuerschlüssel {', '.join(unbekannt)} ist nicht bekannt oder nicht gültig.")

    summen: dict[tuple[str, str], Decimal] = {}
    for zeile in zeilen:
        nr, code, satz, netto = zeile[0], str(zeile[1]).strip(), zeile[2], zeile[3]
        _code, rate, vorsteuerkonto, aufwand_des_schluessels, reverse_charge, umsatzsteuerkonto = bekannt[code]
        satz_des_schluessels_ = Decimal(str(rate))
        if satz is not None and Decimal(str(satz)) != satz_des_schluessels_:
            raise Steuerklaerung(
                f"Position {nr}: Steuersatz {Decimal(str(satz)).normalize():f} % widerspricht dem "
                f"Steuerschlüssel {code} ({satz_des_schluessels_.normalize():f} %)."
            )
        if reverse_charge:
            raise Steuerklaerung(f"Steuerschlüssel {code} (Reverse Charge) wird nicht automatisch gebucht.")
        if (umsatzsteuerkonto or "").strip() and not (vorsteuerkonto or "").strip():
            raise Steuerklaerung(f"Steuerschlüssel {code} ist ein Umsatzsteuerschlüssel und gilt nicht für Eingangsbelege.")
        if satz_des_schluessels_ > 0 and not (vorsteuerkonto or "").strip():
            raise Steuerklaerung(f"Für Steuerschlüssel {code} ist kein Vorsteuerkonto hinterlegt.")
        aufwand = (str(zeile[4]).strip() if len(zeile) > 4 and zeile[4] else "") or (aufwand_des_schluessels or "").strip()
        if not aufwand:
            raise Steuerklaerung(
                f"Position {nr}: kein Aufwandskonto — weder in der Position noch im Steuerschlüssel {code}."
            )
        summen[(code, aufwand)] = summen.get((code, aufwand), Decimal("0")) + Decimal(str(netto or 0))

    gruppen: list[Vorsteuergruppe] = []
    for (code, aufwand), summe in sorted(summen.items()):
        satz = Decimal(str(bekannt[code][1]))
        netto = summe.quantize(CENT, rounding=ROUND_HALF_UP)
        gruppen.append(Vorsteuergruppe(
            tax_code=code, satz=satz, netto=netto,
            steuer=(netto * satz / Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP),
            aufwandskonto=aufwand,
            vorsteuerkonto=str(bekannt[code][2]).strip() if satz > 0 else None,
        ))
    return gruppen


# --- Auswahl fuer Belege und Stammdaten ---------------------------------------------------------

# Ein Schluessel mit nur einem Vorsteuerkonto gehoert nicht in einen Verkaufsbeleg, einer mit nur einem
# Umsatzsteuerkonto nicht in einen Eingangsbeleg. Schluessel ohne Steuerkonto (steuerfrei) gelten fuer beide.
RICHTUNGEN = {
    "verkauf": "(credit_account IS NOT NULL OR debit_account IS NULL)",
    "einkauf": "(debit_account IS NOT NULL OR credit_account IS NULL)",
}


class Schluesselwahl(BaseModel):
    """Ein Steuerschluessel, wie ihn eine Maske zur Auswahl anbietet."""

    code: str
    bezeichnung: str
    steuersatz: Decimal
    par_24_ustg: bool = False
    reverse_charge: bool = False


def schluessel_auswahl(db: Session, tenant_id: str, richtung: str) -> list[Schluesselwahl]:
    """Die heute gueltigen, aktiven Steuerschluessel des Mandanten fuer Verkaufs- oder Eingangsbelege."""
    if richtung not in RICHTUNGEN:
        raise ValueError(f"Unbekannte Richtung {richtung!r}; erlaubt: verkauf, einkauf.")
    zeilen = db.execute(
        text(
            "SELECT code, bezeichnung, steuersatz, par_24_ustg, reverse_charge FROM domain_erp.tax_keys "
            "WHERE tenant_id = :tid AND active AND gueltig_von <= CURRENT_DATE "
            "AND (gueltig_bis IS NULL OR gueltig_bis >= CURRENT_DATE) "
            # Die Richtung ist eine der beiden festen Bedingungen aus RICHTUNGEN.
            "AND CASE WHEN :richtung = 'verkauf' THEN (credit_account IS NOT NULL OR debit_account IS NULL) "
            "         ELSE (debit_account IS NOT NULL OR credit_account IS NULL) END "
            "ORDER BY LPAD(code, 2, '0')"
        ),
        {"tid": tenant_id, "richtung": richtung},
    ).fetchall()
    return [
        Schluesselwahl(code=str(z[0]), bezeichnung=str(z[1]), steuersatz=Decimal(str(z[2])),
                       par_24_ustg=bool(z[3]), reverse_charge=bool(z[4]))
        for z in zeilen
    ]


def satz_des_schluessels(db: Session, tenant_id: str, code: str, richtung: str) -> Decimal:
    """Der Satz des Schluessels — oder eine ``Steuerklaerung``, wenn er fuer die Richtung nicht gilt.

    Belege und Stammdaten speichern den Satz nur noch als Abbild des Schluessels; angegeben wird der Schluessel.
    """
    code = (code or "").strip()
    for wahl in schluessel_auswahl(db, tenant_id, richtung):
        if wahl.code == code:
            return wahl.steuersatz
    art = "Verkaufsbelege" if richtung == "verkauf" else "Eingangsbelege"
    raise Steuerklaerung(f"Steuerschlüssel {code or '(leer)'} ist für {art} nicht bekannt oder nicht gültig.")


# --- Konten aus dem Kontenplan ------------------------------------------------------------------

# Welche Kontenart ein Feld des Steuerschluessels verlangt, und woran ein passendes Konto zu erkennen ist.
# Umsatzsteuer ist eine Schuld gegenueber dem Finanzamt, Vorsteuer eine Forderung, der Erloes ein Ertrag.
KONTENROLLEN: dict[str, tuple[str, str, str, tuple[str, ...]]] = {
    # Feld: (Name, Kontenart, Kontenart in Worten, Stichworte im Kontonamen)
    "credit_account": ("Umsatzsteuerkonto", "liability", "Verbindlichkeitskonto", ("umsatzsteuer", "ust", "mehrwertsteuer")),
    "debit_account": ("Vorsteuerkonto", "asset", "Aktivkonto", ("vorsteuer", "vst")),
    "revenue_account": ("Erlöskonto", "revenue", "Erlöskonto", ("erlös", "erloes", "erlos", "umsatz")),
    "expense_account": ("Aufwandskonto", "expense", "Aufwandskonto", ("wareneingang", "aufwand", "einkauf")),
}


class Kontovorschlag(BaseModel):
    account_number: str
    account_name: str
    # Warum das Konto vorgeschlagen wird; ``None`` = passt der Art nach, ohne besonderen Hinweis.
    grund: Optional[str] = None


def _konten(db: Session, tenant_id: str, nummern: Optional[list[str]] = None) -> dict[str, tuple[str, str, str]]:
    """Bebuchbare Konten des Mandanten: Nummer -> (Name, Kontenart, Kategorie). Das eigene Konto geht dem gemeinsamen vor."""
    konten: dict[str, tuple[str, str, str]] = {}
    for nr, name, art, kategorie, _eigen in db.execute(
        text(
            "SELECT account_number, account_name, account_type, COALESCE(category, ''), tenant_id = :tid AS eigen "
            "FROM domain_erp.chart_of_accounts "
            "WHERE tenant_id IN (:tid, 'system') AND COALESCE(is_active, true) AND deleted_at IS NULL "
            "AND NOT posting_blocked AND NOT COALESCE(is_summary, false) "
            "AND (CAST(:nummern AS varchar[]) IS NULL OR account_number = ANY(CAST(:nummern AS varchar[]))) "
            "ORDER BY eigen, account_number"
        ),
        {"tid": tenant_id, "nummern": nummern},
    ).fetchall():
        konten[str(nr)] = (str(name), str(art), str(kategorie))
    return konten


def konto_hindernis(db: Session, tenant_id: str, feld: str, nummer: str) -> Optional[str]:
    """Warum das Konto nicht in das Feld des Steuerschluessels gehoert — oder ``None``."""
    name, art, art_text, _stichworte = KONTENROLLEN[feld]
    konto = _konten(db, tenant_id, [nummer]).get(nummer)
    if konto is None:
        return f"{name} {nummer} steht nicht im Kontenplan oder ist gesperrt."
    if konto[1] != art:
        return f"{name} {nummer} ({konto[0]}) ist kein {art_text}."
    return None


def kontenvorschlaege(db: Session, tenant_id: str, satz: Optional[Decimal]) -> dict[str, list[Kontovorschlag]]:
    """Je Feld die Konten der passenden Art, die fachlich naechsten zuerst.

    Vorgeschlagen wird, gewaehlt wird nicht: Die Reihenfolge ist eine Hilfe, kein Vorgabewert.
    """
    satz_text, satz_muster = "", None
    if satz is not None:
        zahl = f"{satz.normalize():f}"
        satz_text = f"{zahl.replace('.', ',')} %"
        # „7 %“ darf „17 %“ nicht treffen; Komma und Punkt gelten beide.
        satz_muster = re.compile(
            rf"(?<![\d.,]){re.escape(zahl).replace(chr(92) + '.', '[.,]')}\s?%" + ("|steuerfrei" if satz == 0 else ""))
    konten = _konten(db, tenant_id)
    ergebnis: dict[str, list[Kontovorschlag]] = {}
    for feld, (_name, art, _art_text, stichworte) in KONTENROLLEN.items():
        gereiht: list[tuple[int, str, Kontovorschlag]] = []
        for nummer, (name, konto_art, kategorie) in konten.items():
            if konto_art != art:
                continue
            klein = name.lower()
            zum_satz = bool(satz_muster and satz_muster.search(klein))
            steuerkonto = feld in ("credit_account", "debit_account")
            zur_rolle = (kategorie == "tax" and steuerkonto) or any(w in klein for w in stichworte)
            if steuerkonto and satz == 0:
                zum_satz = False  # ein steuerfreier Schluessel braucht kein Steuerkonto
            grund = (
                f"passt zum Satz {satz_text}" if zum_satz and zur_rolle
                else "nach Bezeichnung" if zur_rolle
                else None
            )
            gereiht.append((0 if zum_satz and zur_rolle else 1 if zur_rolle else 2, nummer,
                            Kontovorschlag(account_number=nummer, account_name=name, grund=grund)))
        ergebnis[feld] = [v for _rang, _nr, v in sorted(gereiht, key=lambda e: (e[0], e[1]))]
    return ergebnis


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
# Aufwandskonto der Vorsteuerschluessel: Wareneingang zum Satz.
SKR03_AUFWANDSKONTEN = {"8": "3300", "9": "3400"}
# Sammelkonto der Verbindlichkeiten aus Lieferungen und Leistungen je Kontenrahmen.
KREDITORENKONTO = {"SKR03": "1600", "SKR04": "3300"}
SKR03_KONTEN = (
    # Kategorien des Kontenplan-Schemas (``tax`` kennt es nicht; bis 19.10.2026 scheiterte daran das Lesen).
    ("1571", "Abziehbare Vorsteuer 7 %", "asset", "current_assets"),
    ("1576", "Abziehbare Vorsteuer 19 %", "asset", "current_assets"),
    ("1771", "Umsatzsteuer 7 %", "liability", "current_liabilities"),
    ("1776", "Umsatzsteuer 19 %", "liability", "current_liabilities"),
    ("8300", "Erlöse 7 % USt", "revenue", "revenue"),
    ("8400", "Erlöse 19 % USt", "revenue", "revenue"),
    ("3300", "Wareneingang 7 % Vorsteuer", "expense", "cost_of_goods_sold"),
    ("3400", "Wareneingang 19 % Vorsteuer", "expense", "cost_of_goods_sold"),
    ("1600", "Verbindlichkeiten aus Lieferungen und Leistungen", "liability", "current_liabilities"),
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

    Bestehendes bleibt unberuehrt: Ein Schluessel und ein Konto, die der Mandant schon hat, werden nicht
    angefasst. Konten legt er als **eigene** an, auch wenn der gemeinsame Rahmen die Nummer fuehrt — der
    Buchungsdienst bebucht nur eigene Konten. Der Aufrufer schreibt fest.
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
                # Nur eigene Konten zaehlen: Der Buchungsdienst bebucht kein Konto des gemeinsamen Rahmens.
                "WHERE tenant_id = :tid AND account_number = ANY(:nummern)"
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
                " gueltig_von, debit_account, credit_account, revenue_account, expense_account, country, active) "
                "VALUES (:id, :tid, :code, :name, :satz, :pos, :postext, :von, :vst, :ust, :erloes, :aufwand, 'DE', true)"
            ),
            {
                "id": uuid7(), "tid": tenant_id, "code": code, "name": name, "satz": satz, "pos": position,
                "postext": positionstext, "von": gueltig_von, "vst": vorsteuer, "ust": umsatzsteuer, "erloes": erloes,
                "aufwand": SKR03_AUFWANDSKONTEN.get(code),
            },
        )
        angelegt["steuerschluessel"].append(code)
    return angelegt
