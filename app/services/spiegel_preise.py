"""Spiegelbetrieb L3 -> VALEO: Preise (M6, 26.11.2026) - preisliste, artikelpreis, kundenpreis, kundenrabatt.

Quellen (L3, Spaltenbedeutung am Abzug bestaetigen):
- ``WWS_PREISTAB1`` (PREISTABNR, BEZEICHNUNG) -> ``domain_pricing.price_lists``
- ``WWS_ARTPREIS1``/``WWS_ARTPREIS2`` (ARTIKELNR, PREISTABNR, DATUMVON, DATUMBIS, ABMENGE, PREIS bzw. BASISPREIS)
  -> ``domain_pricing.price_list_items``
- ``WWS_KUNDEN_PREISE`` (KUNDENNR, ARTIKELNR, GUELTIGVON, GUELTIGBIS, PREIS) -> ``domain_crm.business_partner_price_agreements``

**Preisbezug.** Die Preisfindung (``preisfindung_service.preisliste``) liest ``unit_price`` als Preis je Grundeinheit.
L3 fuehrt Preise je Preiseinheit (z. B. je 100 kg, Diesel je 100 l). Der Abzug liefert deshalb ``preis_je`` mit; der
Einzelpreis ist ``preis / preis_je``. Ist er mit den vier Nachkommastellen von ``unit_price`` nicht verlustfrei
darstellbar, wird die Zeile ein Fehler statt eines gerundeten Preises (Lehre aus dem Diesel-Golden-Master: Belege
rechnen mit dem Preis, wie er gilt). Die Kunden-Preisvereinbarung fuehrt einen eigenen Preisbezug (``price_unit``)
und uebernimmt den Preis unveraendert.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.services.spiegel_uebernahme import QUELLSYSTEM, ZeilenFehler, _text

VIER_STELLEN = Decimal("0.0001")


def _zahl(p: dict[str, Any], feld: str, *, pflicht: bool = False) -> Decimal | None:
    roh = _text(p, feld, pflicht=pflicht)
    if roh is None:
        return None
    wert = roh.replace(",", ".") if "," in roh and "." not in roh else roh
    try:
        return Decimal(wert)
    except InvalidOperation as fehler:
        raise ZeilenFehler(f"{feld} {roh!r} ist keine Zahl") from fehler


def _datum(p: dict[str, Any], feld: str) -> str | None:
    """ISO-Datum; L3 liefert TT.MM.JJJJ oder JJJJ-MM-TT."""
    roh = _text(p, feld)
    if roh is None:
        return None
    if len(roh) >= 10 and roh[2] == "." and roh[5] == ".":
        return f"{roh[6:10]}-{roh[3:5]}-{roh[0:2]}"
    return roh[:10]


def _text_zahl(wert: Decimal | None) -> str | None:
    return None if wert is None else format(wert.normalize(), "f")


def _artikel_id(db: Session, tenant_id: str, nummer: str) -> str:
    artikel = db.execute(text("SELECT id FROM domain_inventory.articles WHERE tenant_id = :t AND article_number = :n "
                              "AND deleted_at IS NULL"), {"t": tenant_id, "n": nummer}).scalar()
    if artikel is None:
        raise ZeilenFehler(f"Artikel {nummer} ist in VALEO nicht vorhanden - zuerst Artikel uebernehmen")
    return str(artikel)


# --- preisliste --------------------------------------------------------------------------------------------------

def _preisliste_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    nummer = _text(p, "preistabelle", pflicht=True)
    return {"name": _text(p, "bezeichnung") or f"L3-Preistabelle {nummer}",
            "description": f"L3-Preistabelle {nummer}", "is_active": True}


def _preisliste_lesen(db: Session, tenant_id: str, ziel_id: str) -> dict[str, Any] | None:
    zeile = db.execute(text("SELECT name, description, is_active FROM domain_pricing.price_lists "
                            "WHERE tenant_id = :t AND id = :id"), {"t": tenant_id, "id": ziel_id}).mappings().first()
    return dict(zeile) if zeile else None


def _preisliste_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
    ziel_id = str(uuid7())
    db.execute(text("INSERT INTO domain_pricing.price_lists (id, tenant_id, name, description, currency, is_active) "
                    "VALUES (:id, :t, :name, :description, 'EUR', :is_active)"), {"id": ziel_id, "t": tenant_id, **werte})
    return ziel_id


def _preisliste_aendern(db: Session, tenant_id: str, ziel_id: str, werte: dict[str, Any]) -> None:
    db.execute(text("UPDATE domain_pricing.price_lists SET name = :name, description = :description, "
                    "is_active = :is_active, updated_at = now() WHERE tenant_id = :t AND id = :id"),
               {"id": ziel_id, "t": tenant_id, **werte})


# --- artikelpreis ------------------------------------------------------------------------------------------------

def _preisliste_id(db: Session, tenant_id: str, nummer: str) -> str:
    ziel = db.execute(text(
        "SELECT ziel_id FROM domain_integration.spiegel_quellreferenzen WHERE tenant_id = :t AND quellsystem = :q "
        "AND objektart = 'preisliste' AND quellschluessel = :k"), {"t": tenant_id, "q": QUELLSYSTEM, "k": nummer}).scalar()
    if ziel is None:
        raise ZeilenFehler(f"Preistabelle {nummer} ist nicht uebernommen - zuerst Preistabellen uebernehmen")
    return str(ziel)


def _einzelpreis_werte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    """Artikel, verlustfreier Einzelpreis (Preis / Preisbezug) und Gueltigkeit einer Preiszeile."""
    nummer = _text(p, "artikelnummer", pflicht=True)
    preis = _zahl(p, "preis", pflicht=True)
    preis_je = _zahl(p, "preis_je") or Decimal("1")
    if preis_je <= 0:
        raise ZeilenFehler("Preisbezug muss groesser als 0 sein")
    einzel = preis / preis_je
    if einzel != einzel.quantize(VIER_STELLEN):
        raise ZeilenFehler(f"Preis {preis} je {preis_je} ist als Einzelpreis nicht verlustfrei mit vier Nachkommastellen "
                           "darstellbar - Preisbezug fachlich klaeren")
    return {"article_id": _artikel_id(db, tenant_id, nummer), "article_number": nummer,
            "unit_price": _text_zahl(einzel), "valid_from": _datum(p, "gueltig_von"),
            "valid_until": _datum(p, "gueltig_bis")}


def _artikelpreis_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    werte = _einzelpreis_werte(db, tenant_id, p)
    return {**werte, "price_list_id": _preisliste_id(db, tenant_id, _text(p, "preistabelle", pflicht=True)),
            "min_quantity": _text_zahl(_zahl(p, "ab_menge") or Decimal("0"))}


def _artikelpreis_lesen(db: Session, tenant_id: str, ziel_id: str) -> dict[str, Any] | None:
    zeile = db.execute(text(
        "SELECT price_list_id, article_id, article_number, unit_price, min_quantity, valid_from, valid_until "
        "FROM domain_pricing.price_list_items WHERE tenant_id = :t AND id = :id"),
        {"t": tenant_id, "id": ziel_id}).mappings().first()
    if not zeile:
        return None
    werte = dict(zeile)
    for feld in ("unit_price", "min_quantity"):
        werte[feld] = _text_zahl(Decimal(str(werte[feld]))) if werte[feld] is not None else None
    for feld in ("valid_from", "valid_until"):
        werte[feld] = werte[feld].isoformat() if werte[feld] is not None else None
    return werte


def _artikelpreis_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
    ziel_id = str(uuid7())
    db.execute(text(
        "INSERT INTO domain_pricing.price_list_items (id, tenant_id, price_list_id, article_id, article_number, "
        "unit_price, min_quantity, valid_from, valid_until) VALUES (:id, :t, :price_list_id, :article_id, "
        ":article_number, :unit_price, :min_quantity, :valid_from, :valid_until)"),
        {"id": ziel_id, "t": tenant_id, **werte})
    return ziel_id


def _artikelpreis_aendern(db: Session, tenant_id: str, ziel_id: str, werte: dict[str, Any]) -> None:
    db.execute(text(
        "UPDATE domain_pricing.price_list_items SET price_list_id = :price_list_id, article_id = :article_id, "
        "article_number = :article_number, unit_price = :unit_price, min_quantity = :min_quantity, "
        "valid_from = :valid_from, valid_until = :valid_until WHERE tenant_id = :t AND id = :id"),
        {"id": ziel_id, "t": tenant_id, **werte})


# --- kundenpreis -------------------------------------------------------------------------------------------------

def _kundenpreis_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    kunde = _text(p, "kundennummer", pflicht=True)
    partner = db.execute(text("SELECT business_partner_id FROM domain_crm.customers WHERE tenant_id = :t "
                              "AND customer_number = :n AND deleted_at IS NULL"), {"t": tenant_id, "n": kunde}).scalar()
    if partner is None:
        raise ZeilenFehler(f"Kunde {kunde} ist nicht uebernommen oder ohne Geschaeftspartner - zuerst Kunden uebernehmen")
    nummer = _text(p, "artikelnummer", pflicht=True)
    _artikel_id(db, tenant_id, nummer)
    preis = _zahl(p, "preis", pflicht=True)
    if preis < 0:
        raise ZeilenFehler("Kundenpreis darf nicht negativ sein")
    preis_je = _zahl(p, "preis_je")
    return {"partner_id": str(partner), "article_number": nummer, "price_net": _text_zahl(preis),
            "price_unit": _text_zahl(preis_je) if preis_je is not None else None,
            "valid_from": _datum(p, "gueltig_von"), "valid_to": _datum(p, "gueltig_bis")}


def _kundenpreis_lesen(db: Session, tenant_id: str, ziel_id: str) -> dict[str, Any] | None:
    zeile = db.execute(text(
        "SELECT partner_id, article_number, price_net, price_unit, valid_from, valid_to "
        "FROM domain_crm.business_partner_price_agreements WHERE tenant_id = :t AND id = :id"),
        {"t": tenant_id, "id": ziel_id}).mappings().first()
    if not zeile:
        return None
    werte = dict(zeile)
    werte["price_net"] = _text_zahl(Decimal(str(werte["price_net"]))) if werte["price_net"] is not None else None
    werte["price_unit"] = str(werte["price_unit"]) if werte["price_unit"] is not None else None
    for feld in ("valid_from", "valid_to"):
        werte[feld] = werte[feld].isoformat() if werte[feld] is not None else None
    return werte


def _kundenpreis_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
    ziel_id = str(uuid7())
    db.execute(text(
        "INSERT INTO domain_crm.business_partner_price_agreements (id, tenant_id, partner_id, article_number, "
        "price_net, price_unit, valid_from, valid_to, source_type, created_by) VALUES (:id, :t, :partner_id, "
        ":article_number, :price_net, :price_unit, :valid_from, :valid_to, 'import', 'l3_spiegel')"),
        {"id": ziel_id, "t": tenant_id, **werte})
    return ziel_id


def _kundenpreis_aendern(db: Session, tenant_id: str, ziel_id: str, werte: dict[str, Any]) -> None:
    db.execute(text(
        "UPDATE domain_crm.business_partner_price_agreements SET partner_id = :partner_id, "
        "article_number = :article_number, price_net = :price_net, price_unit = :price_unit, valid_from = :valid_from, "
        "valid_to = :valid_to, updated_by = 'l3_spiegel', updated_at = now() WHERE tenant_id = :t AND id = :id"),
        {"id": ziel_id, "t": tenant_id, **werte})


# --- kundenrabatt -----------------------------------------------------------------------------------------------
#
# L3 ``WWS_KUNDRABATT`` (KUNDENNR, ARTIKELNR, RABATT, RABATTART, GUELTIGAB, GUELTIGBIS, LISTENR) -> Rabattstufe
# ``customer_article_discount`` der Preiskaskade (``business_partner_discount_items``). Uebernommen werden nur
# Prozentrabatte: Welche RABATTART-Codes Prozent bedeuten, ist am Abzug zu bestaetigen; die Abzugsabfrage liefert
# ``rabatt_prozent`` nur fuer diese Zeilen. Betragsrabatte und Zu-/Abschlaege (ZUABSCHLAGNR) bleiben offen.


def _kundenrabatt_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    kunde = _text(p, "kundennummer", pflicht=True)
    partner = db.execute(text("SELECT business_partner_id FROM domain_crm.customers WHERE tenant_id = :t "
                              "AND customer_number = :n AND deleted_at IS NULL"), {"t": tenant_id, "n": kunde}).scalar()
    if partner is None:
        raise ZeilenFehler(f"Kunde {kunde} ist nicht uebernommen oder ohne Geschaeftspartner - zuerst Kunden uebernehmen")
    nummer = _text(p, "artikelnummer", pflicht=True)
    _artikel_id(db, tenant_id, nummer)
    prozent = _zahl(p, "rabatt_prozent", pflicht=True)
    if not Decimal("0") <= prozent <= Decimal("100"):
        raise ZeilenFehler(f"Rabatt {prozent} % liegt nicht zwischen 0 und 100")
    return {"partner_id": str(partner), "article_number": nummer, "discount_percent": _text_zahl(prozent),
            "valid_from": _datum(p, "gueltig_von"), "valid_to": _datum(p, "gueltig_bis"),
            "discount_list_number": _text(p, "rabattliste")}


def _kundenrabatt_lesen(db: Session, tenant_id: str, ziel_id: str) -> dict[str, Any] | None:
    zeile = db.execute(text(
        "SELECT partner_id, article_number, discount_percent, valid_from, valid_to, discount_list_number "
        "FROM domain_crm.business_partner_discount_items WHERE tenant_id = :t AND id = :id"),
        {"t": tenant_id, "id": ziel_id}).mappings().first()
    if not zeile:
        return None
    werte = dict(zeile)
    werte["discount_percent"] = _text_zahl(Decimal(str(werte["discount_percent"])))
    for feld in ("valid_from", "valid_to"):
        werte[feld] = werte[feld].isoformat() if werte[feld] is not None else None
    return werte


def _kundenrabatt_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
    ziel_id = str(uuid7())
    db.execute(text(
        "INSERT INTO domain_crm.business_partner_discount_items (id, tenant_id, partner_id, article_number, "
        "discount_percent, valid_from, valid_to, discount_list_number, source_type, created_by) VALUES (:id, :t, "
        ":partner_id, :article_number, :discount_percent, :valid_from, :valid_to, :discount_list_number, 'import', "
        "'l3_spiegel')"), {"id": ziel_id, "t": tenant_id, **werte})
    return ziel_id


def _kundenrabatt_aendern(db: Session, tenant_id: str, ziel_id: str, werte: dict[str, Any]) -> None:
    db.execute(text(
        "UPDATE domain_crm.business_partner_discount_items SET partner_id = :partner_id, "
        "article_number = :article_number, discount_percent = :discount_percent, valid_from = :valid_from, "
        "valid_to = :valid_to, discount_list_number = :discount_list_number, updated_by = 'l3_spiegel', "
        "updated_at = now() WHERE tenant_id = :t AND id = :id"), {"id": ziel_id, "t": tenant_id, **werte})


# --- aktion / aktionspreis ---------------------------------------------------------------------------------------
#
# L3 ``WWS_AKTIONSPREISE`` (AKTIONNR, DATUMVON, DATUMBIS, ARTIKELNR, PREISNETTO, LAGER, KUNDENSELEKTION). Eine Aktion
# wird eine Preisliste vom Typ ``aktion`` mit Laufzeit; die Preiskaskade wendet sie nur an, wenn sie guenstiger ist
# (Nutzerentscheid 26.11.2026). Auf ein Lager oder eine Kundenauswahl beschraenkte L3-Aktionen kann VALEO nicht
# abbilden - sie wuerden fuer alle gelten und werden deshalb Fehlerzeilen.


def _aktion_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    nummer = _text(p, "aktion", pflicht=True)
    return {"name": _text(p, "bezeichnung") or f"L3-Aktion {nummer}", "description": f"L3-Aktion {nummer}",
            "valid_from": _datum(p, "gueltig_von"), "valid_until": _datum(p, "gueltig_bis"), "is_active": True}


def _aktion_lesen(db: Session, tenant_id: str, ziel_id: str) -> dict[str, Any] | None:
    zeile = db.execute(text("SELECT name, description, valid_from, valid_until, is_active FROM domain_pricing.price_lists "
                            "WHERE tenant_id = :t AND id = :id"), {"t": tenant_id, "id": ziel_id}).mappings().first()
    if not zeile:
        return None
    werte = dict(zeile)
    for feld in ("valid_from", "valid_until"):
        werte[feld] = werte[feld].isoformat() if werte[feld] is not None else None
    return werte


def _aktion_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
    ziel_id = str(uuid7())
    db.execute(text("INSERT INTO domain_pricing.price_lists (id, tenant_id, name, description, currency, price_list_type, "
                    "valid_from, valid_until, is_active) VALUES (:id, :t, :name, :description, 'EUR', 'aktion', "
                    ":valid_from, :valid_until, :is_active)"), {"id": ziel_id, "t": tenant_id, **werte})
    return ziel_id


def _aktion_aendern(db: Session, tenant_id: str, ziel_id: str, werte: dict[str, Any]) -> None:
    db.execute(text("UPDATE domain_pricing.price_lists SET name = :name, description = :description, "
                    "valid_from = :valid_from, valid_until = :valid_until, is_active = :is_active, updated_at = now() "
                    "WHERE tenant_id = :t AND id = :id"), {"id": ziel_id, "t": tenant_id, **werte})


def _aktionspreis_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    if _text(p, "lager") or _text(p, "kundenselektion"):
        raise ZeilenFehler("Aktion ist auf Lager oder Kundenauswahl beschraenkt - in VALEO nicht abbildbar, "
                           "wuerde fuer alle gelten")
    aktion = _text(p, "aktion", pflicht=True)
    ziel = db.execute(text(
        "SELECT ziel_id FROM domain_integration.spiegel_quellreferenzen WHERE tenant_id = :t AND quellsystem = :q "
        "AND objektart = 'aktion' AND quellschluessel = :k"), {"t": tenant_id, "q": QUELLSYSTEM, "k": aktion}).scalar()
    if ziel is None:
        raise ZeilenFehler(f"Aktion {aktion} ist nicht uebernommen - zuerst Aktionen uebernehmen")
    werte = _einzelpreis_werte(db, tenant_id, p)
    return {**werte, "price_list_id": str(ziel), "min_quantity": "0"}


def zielarten() -> dict[str, Any]:
    from app.services.spiegel_uebernahme import Zielart

    return {
        "preisliste": Zielart("domain_pricing.price_lists", _preisliste_zielwerte, _preisliste_lesen,
                              _preisliste_anlegen, _preisliste_aendern),
        "artikelpreis": Zielart("domain_pricing.price_list_items", _artikelpreis_zielwerte, _artikelpreis_lesen,
                                _artikelpreis_anlegen, _artikelpreis_aendern),
        "kundenpreis": Zielart("domain_crm.business_partner_price_agreements", _kundenpreis_zielwerte,
                               _kundenpreis_lesen, _kundenpreis_anlegen, _kundenpreis_aendern),
        "kundenrabatt": Zielart("domain_crm.business_partner_discount_items", _kundenrabatt_zielwerte,
                                _kundenrabatt_lesen, _kundenrabatt_anlegen, _kundenrabatt_aendern),
        "aktion": Zielart("domain_pricing.price_lists", _aktion_zielwerte, _aktion_lesen, _aktion_anlegen,
                          _aktion_aendern),
        "aktionspreis": Zielart("domain_pricing.price_list_items", _aktionspreis_zielwerte, _artikelpreis_lesen,
                                _artikelpreis_anlegen, _artikelpreis_aendern),
    }
