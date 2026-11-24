"""Bestandsbewertung zum gleitenden Durchschnittspreis (Nutzerentscheid 24.11.2026, HGB § 240 Abs. 4 / § 256).

Eine Quelle fuer den Wert eines Bestands: Der Durchschnittspreis je Artikel (ueber alle Lager des Mandanten) entsteht
aus der Bewegungshistorie ``domain_inventory.inventory_stock_movements`` in zeitlicher Folge:

* ein Zugang mit Einstandspreis verschiebt den Durchschnitt: (Bestand * Schnitt + Menge * Preis) / (Bestand + Menge),
* ein Zugang ohne Einstandspreis erhoeht den Bestand zum bisherigen Schnitt (kein Preis ist kein Preis von 0),
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
        if b["art"] in ZUGAENGE and not b["storno_ref"]:
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
