"""Bestandsbewertung zum gleitenden Durchschnittspreis (Nutzerentscheid 24.11.2026, HGB § 240 Abs. 4 / § 256).

Eine Quelle fuer den Wert eines Bestands: Der Durchschnittspreis je Artikel (ueber alle Lager des Mandanten) entsteht
aus der Bewegungshistorie ``domain_inventory.inventory_stock_movements`` in zeitlicher Folge:

* ein Zugang mit Einstandspreis verschiebt den Durchschnitt: (Bestand * Schnitt + Menge * Preis) / (Bestand + Menge),
* ein Zugang ohne Einstandspreis erhoeht den Bestand zum bisherigen Schnitt (kein Preis ist kein Preis von 0),
* eine Korrektur (``adjustment``) mit positiver Menge ist ein Zugang zum bisherigen Schnitt, mit negativer ein Abgang,
* ein Abgang mindert den Bestand, der Schnitt bleibt,
* der Storno eines Zugangs nimmt Menge und Wert zum Preis des Zugangs zurueck.

Ohne einen einzigen Zugang mit Einstandspreis gibt es keinen Durchschnitt (``None``) - dann wird nicht bewertet und
nicht gebucht. Mengen in anderer Einheit als der Lagereinheit des Artikels werden ueber ``app/core/agrar_units.py``
umgerechnet; laesst sich eine Einheit nicht umrechnen, ist der Durchschnitt nicht bestimmbar.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.agrar_units import globaler_faktor, normalisiere

ZUGAENGE = {"einlagerung", "wareneingang", "in", "zugang", "receipt", "korrektur_zugang"}
NULL = Decimal("0")


class BewertungNichtBestimmbar(Exception):
    """Eine Bewegung laesst sich nicht in die Lagereinheit umrechnen - kein Durchschnitt."""


@dataclass(frozen=True)
class Durchschnitt:
    artikel_id: str
    einheit: Optional[str]
    preis: Optional[Decimal]  # je Lagereinheit; None = kein Zugang mit Einstandspreis
    bestand: Decimal


def _in_lagereinheit(menge: Decimal, einheit: Optional[str], lagereinheit: Optional[str]) -> Decimal:
    if not einheit or not lagereinheit or normalisiere(einheit) == normalisiere(lagereinheit):
        return menge
    faktor = globaler_faktor(einheit, lagereinheit)
    if faktor is None:
        raise BewertungNichtBestimmbar(f"{einheit} laesst sich nicht in die Lagereinheit {lagereinheit} umrechnen")
    return menge * faktor


def gleitender_durchschnitt(db: Session, tenant_id: str, artikel_id: str,
                            stichtag: Optional[date] = None) -> Durchschnitt:
    lagereinheit = db.execute(text(
        "SELECT unit FROM domain_inventory.articles WHERE tenant_id = :t AND id::text = :a"),
        {"t": tenant_id, "a": artikel_id}).scalar()
    bewegungen = db.execute(text(
        "SELECT id::text AS id, LOWER(movement_type) AS art, quantity, unit, unit_cost, storno_ref "
        "FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t AND article_id::text = :a "
        "AND COALESCE(ownership_type, 'owned') = 'owned' "
        "AND (CAST(:stichtag AS date) IS NULL OR movement_date <= :stichtag) "
        "ORDER BY movement_date, created_at, id"),
        {"t": tenant_id, "a": artikel_id, "stichtag": stichtag}).mappings().all()

    bestand, schnitt, bepreist = NULL, NULL, False
    zugangspreis: dict[str, Optional[Decimal]] = {}
    for b in bewegungen:
        roh = abs(Decimal(str(b["quantity"] or 0)))
        menge = _in_lagereinheit(roh, b["unit"], lagereinheit)
        preis = None
        if b["unit_cost"] is not None and Decimal(str(b["unit_cost"])) > 0 and menge > 0:
            # Einstandspreis gilt je Einheit der Bewegung; je Lagereinheit = Wert / Menge in Lagereinheit.
            preis = Decimal(str(b["unit_cost"])) * roh / menge
        roh_signiert = Decimal(str(b["quantity"] or 0))
        ist_zugang = b["art"] in ZUGAENGE or (b["art"] == "adjustment" and roh_signiert > 0)
        if ist_zugang and not b["storno_ref"]:
            zugangspreis[b["id"]] = preis
            if preis is not None:
                neu = bestand + menge
                schnitt = ((bestand * schnitt) + (menge * preis)) / neu if neu > 0 else preis
                bepreist = True
            bestand += menge
        elif b["storno_ref"] and zugangspreis.get(b["storno_ref"]) is not None:
            rest = bestand - menge
            if rest > 0:
                schnitt = ((bestand * schnitt) - (menge * zugangspreis[b["storno_ref"]])) / rest
            bestand = rest
        else:
            bestand -= menge
    return Durchschnitt(artikel_id=artikel_id, einheit=lagereinheit,
                        preis=schnitt.quantize(Decimal("0.000001")) if bepreist else None, bestand=bestand)


def bewerte(db: Session, tenant_id: str, artikel_id: str, menge: Decimal, einheit: Optional[str],
            stichtag: Optional[date] = None) -> Optional[Decimal]:
    """Wert einer Menge zum gleitenden Durchschnitt (auf Cent) - oder ``None``, wenn kein Durchschnitt bekannt ist."""
    schnitt = gleitender_durchschnitt(db, tenant_id, artikel_id, stichtag)
    if schnitt.preis is None:
        return None
    return (_in_lagereinheit(Decimal(str(menge)), einheit, schnitt.einheit) * schnitt.preis).quantize(Decimal("0.01"))



class BuchungNichtMoeglich(Exception):
    """Kein Buchungsentwurf: Bewertung oder Kontenzuordnung fehlt. Die Meldung nennt den Grund."""


def _lagerkonten(db: Session, tenant_id: str, artikel_id: str) -> Optional[dict]:
    """Hinterlegte Lagerkonten der Warengruppe des Artikels - ohne Ersatzkonten (keine erfundenen Werte)."""
    return db.execute(text(
        "SELECT lkz.bestandskonto, lkz.gegenkonto_zugang, lkz.gegenkonto_abgang "
        "FROM domain_einkauf.lager_kontenzuordnung lkz "
        "JOIN domain_inventory.articles a ON a.warengruppe = lkz.artikelgruppe AND a.tenant_id = lkz.tenant_id "
        "WHERE lkz.tenant_id = :t AND a.id::text = :a AND COALESCE(lkz.aktiv, true) "
        "ORDER BY lkz.niederlassung_id NULLS LAST LIMIT 1"), {"t": tenant_id, "a": artikel_id}).mappings().first()


def entwerfe_bestandsbuchung(db: Session, tenant_id: str, referenz: str, beschreibung: str, datum: date,
                             mengen: list[tuple[str, Decimal, Optional[str]]]) -> str:
    """Buchungsentwurf (Status draft) fuer Bestandsaenderungen, bewertet zum gleitenden Durchschnitt.

    ``mengen``: (Artikel, Menge mit Vorzeichen, Einheit); positiv = Zugang (Soll Bestand an Gegenkonto Zugang),
    negativ = Abgang (Soll Gegenkonto Abgang an Bestand). Alles oder nichts: fehlt fuer einen Artikel die Bewertung
    oder die Kontenzuordnung, entsteht kein Entwurf (``BuchungNichtMoeglich``). Gebucht wird ueber den Freigabeweg
    des Hauptbuchs, nicht hier (APPROVAL-001: manuelle Hauptbuchbuchung braucht die Freigabe).
    Wird vor dem Schreiben der Bewegungen aufgerufen, damit der Durchschnitt den Stand vor der Aenderung zeigt.
    """
    from app.services.finance_transaction_service import FinanceTransactionService

    buchung = FinanceTransactionService(db, tenant_id, commit_on_success=False)
    zeilen = []
    for artikel_id, menge, einheit in mengen:
        menge = Decimal(str(menge))
        if menge == 0:
            continue
        try:
            wert = bewerte(db, tenant_id, artikel_id, abs(menge), einheit, datum)
        except BewertungNichtBestimmbar as fehler:
            raise BuchungNichtMoeglich(f"Artikel {artikel_id}: {fehler}") from fehler
        if wert is None:
            raise BuchungNichtMoeglich(f"Artikel {artikel_id}: kein gleitender Durchschnitt (kein bepreister Zugang).")
        if wert == 0:
            continue
        konten = _lagerkonten(db, tenant_id, artikel_id)
        gegen = (konten or {}).get("gegenkonto_zugang" if menge > 0 else "gegenkonto_abgang")
        if not konten or not gegen:
            raise BuchungNichtMoeglich(f"Artikel {artikel_id}: keine Lagerkonten-Zuordnung fuer die Warengruppe.")
        bestand = buchung.account_id_for_number(str(konten["bestandskonto"]))
        gegenkonto = buchung.account_id_for_number(str(gegen))
        soll, haben = (bestand, gegenkonto) if menge > 0 else (gegenkonto, bestand)
        text_ = f"{beschreibung[:150]} {artikel_id[:8]}"
        zeilen += [{"account_id": soll, "debit_amount": wert, "credit_amount": NULL, "description": text_},
                   {"account_id": haben, "debit_amount": NULL, "credit_amount": wert, "description": text_}]
    if not zeilen:
        raise BuchungNichtMoeglich("Keine Wertaenderung.")
    eintrag = buchung.create(entry_number=referenz, description=beschreibung[:200], entry_date=datum,
                             reference=referenz, source="bestandsbewertung", lines=zeilen)
    return str(eintrag.id)
