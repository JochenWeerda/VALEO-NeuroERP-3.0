"""Spiegelbetrieb L3 -> VALEO: Uebernahme freigegebener Adapter-Batches in die Fachtabellen (M6, 25.11.2026).

Baut auf der vorhandenen Adapterstrecke auf (``legacy_interface_adapter_service``: Annahme, Staging, Mengenabgleich,
Freigabe) - keine zweite Importstrecke. Grundsaetze:

- **L3 bleibt fuehrend, keine Rueckwirkung.** Gelesen wird nur das Staging in VALEO; dieses Modul kennt keinen Weg
  zu L3.
- **Wiederholbar und idempotent.** Je Quelldatensatz (Quellsystem, Objektart, Quellschluessel) gibt es genau eine
  Quellreferenz mit der Pruefsumme des zuletzt uebernommenen Inhalts. Gleicher Inhalt -> "unveraendert", geaenderter
  Inhalt -> Zielobjekt aktualisiert und Felddifferenzen protokolliert.
- **Nichts erfinden, nichts still zusammenfuehren.** Unbekannte Stammdatenbezuege (Artikelgruppe, Mengeneinheit) und
  ein Zielobjekt, das schon ohne Quellreferenz existiert, werden Fehlerzeilen im Protokoll statt Annahmen.
- **Eine Zeile scheitert allein.** Jede Zeile laeuft in einem eigenen Sicherungspunkt.

Objektarten: ``artikel``, ``kunde``, ``lieferant``, ``bestand``. Die Zuordnung L3-Spalte -> kanonisches Feld steht im
Adapterprofil (``field_mapping``); siehe ``docs/migration/m6-spiegelbetrieb-l3.md``.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.services.legacy_interface_adapter_service import LegacyAdapterError, LegacyInterfaceAdapterService

QUELLSYSTEM = "l3"


class ZeilenFehler(ValueError):
    """Fachlicher Fehler einer Quellzeile - landet im Protokoll, bricht den Lauf nicht ab."""


def pruefsumme(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def _text(payload: dict[str, Any], feld: str, *, pflicht: bool = False) -> str | None:
    wert = payload.get(feld)
    wert = None if wert is None else str(wert).strip() or None
    if pflicht and wert is None:
        raise ZeilenFehler(f"Pflichtfeld {feld} fehlt")
    return wert


def _ja(payload: dict[str, Any], feld: str) -> bool:
    return str(payload.get(feld) or "").strip().lower() in {"1", "j", "ja", "true", "x"}


# --- Objektart artikel -----------------------------------------------------------------------------------------

ARTIKEL_FELDER = ("article_number", "name", "description2", "warengruppe", "unit", "is_active")


def _artikel_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    gruppe = _text(p, "artikelgruppe")
    if gruppe is not None and db.execute(text(
            "SELECT 1 FROM domain_shared.warengruppen WHERE tenant_id = :t AND gruppe_nr = :g"),
            {"t": tenant_id, "g": gruppe}).first() is None:
        raise ZeilenFehler(f"Artikelgruppe {gruppe} ist im Mandanten nicht angelegt")
    einheit = None
    me_nr = _text(p, "mengeneinheit_nr")
    if me_nr is not None:
        einheit = db.execute(text(
            "SELECT einheit_kuerzel FROM domain_shared.artikel_mengeneinheiten "
            "WHERE tenant_id = :t AND nummer = :n"), {"t": tenant_id, "n": int(me_nr) if me_nr.isdigit() else -1}
        ).scalar()
        if einheit is None:
            raise ZeilenFehler(f"Mengeneinheit Nr. {me_nr} ist im Mengeneinheiten-Stamm nicht angelegt")
    return {
        "article_number": _text(p, "artikelnummer", pflicht=True),
        "name": _text(p, "bezeichnung", pflicht=True),
        "description2": _text(p, "bezeichnung2"),
        "warengruppe": gruppe,
        "unit": einheit,
        "is_active": not _ja(p, "gesperrt"),
    }


def _artikel_lesen(db: Session, tenant_id: str, ziel_id: str) -> dict[str, Any] | None:
    zeile = db.execute(text(
        "SELECT article_number, name, description2, warengruppe, unit, is_active, deleted_at "
        "FROM domain_inventory.articles WHERE tenant_id = :t AND id = :id"),
        {"t": tenant_id, "id": ziel_id}).mappings().first()
    return dict(zeile) if zeile else None


def _artikel_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
    # Auch soft-geloeschte Zeilen: Unique (tenant_id, article_number) bleibt; kein stilles Wiederbeleben ohne Referenz.
    if db.execute(text("SELECT 1 FROM domain_inventory.articles WHERE tenant_id = :t AND article_number = :n"),
                  {"t": tenant_id, "n": werte["article_number"]}).first():
        raise ZeilenFehler(f"Artikel {werte['article_number']} existiert bereits ohne L3-Quellreferenz - "
                           "Zuordnung fachlich klaeren")
    ziel_id = str(uuid7())
    db.execute(text(
        "INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, description2, warengruppe, "
        "unit, is_active) VALUES (:id, :t, :article_number, :name, :description2, :warengruppe, :unit, :is_active)"),
        {"id": ziel_id, "t": tenant_id, **werte})
    return ziel_id


def _artikel_aendern(db: Session, tenant_id: str, ziel_id: str, werte: dict[str, Any]) -> None:
    # L3 fuehrend: Soft-Delete in VALEO wird bei erneutem Abzug zurueckgenommen (deleted_at = NULL).
    db.execute(text(
        "UPDATE domain_inventory.articles SET article_number = :article_number, name = :name, "
        "description2 = :description2, warengruppe = :warengruppe, unit = :unit, is_active = :is_active, "
        "deleted_at = NULL, updated_at = now() WHERE tenant_id = :t AND id = :id"),
        {"id": ziel_id, "t": tenant_id, **werte})


# --- Objektart kunde (L3 KUNDEN mit Anschrift aus ADRESSEN, im Abzug verbunden) ------------------------------------
#
# Ziel ist der Kundenstamm domain_crm.customers (fuehrt die Debitoren im Uebergang, Entscheidung 01.11.2026). Die
# L3-Debitorennummer ist nicht die Kundennummer: Sie wird das Konto des Geschaeftspartners
# (business_partners.debtor_account, ADR Stufe 3b) - Nutzerentscheid 25.11.2026: L3-Nummern uebernehmen, damit offene
# Posten und Journal Konto fuer Konto gegen L3 abgleichbar sind. Der Partner entsteht ueber die Partnerbruecke
# (BusinessPartnerService.partner_fuer_rolle); ein schon vergebenes, abweichendes Konto oder eine im Mandanten
# vergebene Nummer wird Fehlerzeile.

KUNDE_FELDER = ("customer_number", "company_name", "address", "postal_code", "city", "country", "tax_id", "phone",
                "email", "is_active", "debitorkonto")


def _kunde_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    strasse = _text(p, "strasse")
    return {
        "customer_number": _text(p, "kundennummer", pflicht=True),
        "company_name": _text(p, "name", pflicht=True),
        "address": json.dumps({"street": strasse}, ensure_ascii=False) if strasse else None,
        "postal_code": _text(p, "plz"),
        "city": _text(p, "ort"),
        "country": _text(p, "land"),
        "tax_id": _text(p, "ust_id"),
        "phone": _text(p, "telefon"),
        "email": _text(p, "email"),
        "is_active": not _ja(p, "gesperrt"),
        "debitorkonto": _text(p, "debitorkonto"),
    }


def _kunde_lesen(db: Session, tenant_id: str, ziel_id: str) -> dict[str, Any] | None:
    zeile = db.execute(text(
        "SELECT c.customer_number, c.company_name, c.address, c.postal_code, c.city, c.country, c.tax_id, c.phone, "
        "c.email, c.is_active, c.deleted_at, bp.debtor_account AS debitorkonto FROM domain_crm.customers c "
        "LEFT JOIN domain_crm.business_partners bp ON bp.partner_id::text = c.business_partner_id::text "
        "AND bp.tenant_id = c.tenant_id WHERE c.tenant_id = :t AND c.id = :id"),
        {"t": tenant_id, "id": ziel_id}).mappings().first()
    if not zeile:
        return None
    werte = dict(zeile)
    if werte["address"] is not None:  # jsonb kommt als dict; Vergleich mit dem serialisierten Zielwert
        werte["address"] = json.dumps(werte["address"], ensure_ascii=False)
    return werte


def _kunde_partner(db: Session, tenant_id: str, werte: dict[str, Any], partner_id: str | None) -> str:
    from app.core.exceptions import ConflictError
    from app.services.business_partner_service import BusinessPartnerService

    strasse = json.loads(werte["address"]).get("street") if werte["address"] else None
    try:
        return BusinessPartnerService(db, tenant_id).partner_fuer_rolle(
            "kunde", name=werte["company_name"], vat_id=werte["tax_id"], street=strasse,
            postal_code=werte["postal_code"], city=werte["city"], country=werte["country"], email=werte["email"],
            phone=werte["phone"], partner_id=partner_id, konto=werte["debitorkonto"])
    except ConflictError as fehler:
        raise ZeilenFehler(f"Debitorenkonto: {fehler}") from fehler


def _kunde_spalten(werte: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in werte.items() if k != "debitorkonto"}


def _kunde_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
    if db.execute(text("SELECT 1 FROM domain_crm.customers WHERE tenant_id = :t AND customer_number = :n"),
                  {"t": tenant_id, "n": werte["customer_number"]}).first():
        raise ZeilenFehler(f"Kunde {werte['customer_number']} existiert bereits ohne L3-Quellreferenz - "
                           "Zuordnung fachlich klaeren")
    ziel_id = str(uuid7())
    db.execute(text(
        "INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, address, postal_code, city, "
        "country, tax_id, phone, email, is_active) VALUES (:id, :t, :customer_number, :company_name, "
        "CAST(:address AS JSONB), :postal_code, :city, :country, :tax_id, :phone, :email, :is_active)"),
        {"id": ziel_id, "t": tenant_id, **_kunde_spalten(werte)})
    partner = _kunde_partner(db, tenant_id, werte, None)
    db.execute(text("UPDATE domain_crm.customers SET business_partner_id = :p WHERE tenant_id = :t AND id = :id"),
               {"p": partner, "t": tenant_id, "id": ziel_id})
    return ziel_id


def _kunde_aendern(db: Session, tenant_id: str, ziel_id: str, werte: dict[str, Any]) -> None:
    partner = db.execute(text("SELECT business_partner_id FROM domain_crm.customers WHERE tenant_id = :t AND id = :id"),
                         {"t": tenant_id, "id": ziel_id}).scalar()
    partner = _kunde_partner(db, tenant_id, werte, str(partner) if partner else None)
    db.execute(text("UPDATE domain_crm.customers SET business_partner_id = :p WHERE tenant_id = :t AND id = :id"),
               {"p": partner, "t": tenant_id, "id": ziel_id})
    db.execute(text(
        "UPDATE domain_crm.customers SET customer_number = :customer_number, company_name = :company_name, "
        "address = CAST(:address AS JSONB), postal_code = :postal_code, city = :city, country = :country, "
        "tax_id = :tax_id, phone = :phone, email = :email, is_active = :is_active, deleted_at = NULL, "
        "updated_at = now() WHERE tenant_id = :t AND id = :id"), {"id": ziel_id, "t": tenant_id, **_kunde_spalten(werte)})


# --- Objektart bestand (L3 WWS_ARTBESTAND/WWS_LAGERBESTAND je Artikel und Lager) ---------------------------------
#
# Erster Abzug: Anfangsbestand als Bestandsvortrag ueber den kanonischen Buchungsdienst (Schluessel
# ``spiegel:bestand:<Quellschluessel>`` -> nie doppelt). Jeder weitere Abzug bucht NICHT: Im Spiegelbetrieb vollzieht
# VALEO die Bewegungen ueber eigene Belege nach; eine stille Korrektur verdeckte genau die Abweichungen, die der
# Spiegelbetrieb finden soll. Weicht der VALEO-Lagerbestand (Saldo aus dem Bestandsjournal) vom L3-Bestand ab, steht
# das als "geaendert" mit Felddifferenz ``menge`` im Protokoll - die Uebernahme laesst den Bestand unveraendert.


def _menge_text(menge) -> str:
    """Kanonische Mengendarstellung ohne Exponent und ohne Nachkommanullen: 10.000 -> "10", 12.50 -> "12.5"."""
    from decimal import Decimal

    text_ = format(Decimal(menge).normalize(), "f")
    return "0" if Decimal(text_) == 0 else text_


def _bestand_bezug(db: Session, tenant_id: str, p: dict[str, Any]) -> tuple[str, str]:
    nummer = _text(p, "artikelnummer", pflicht=True)
    lager = _text(p, "lager", pflicht=True)
    artikel = db.execute(text("SELECT id FROM domain_inventory.articles WHERE tenant_id = :t AND article_number = :n "
                              "AND deleted_at IS NULL"), {"t": tenant_id, "n": nummer}).scalar()
    if artikel is None:
        raise ZeilenFehler(f"Artikel {nummer} ist in VALEO nicht vorhanden - zuerst Artikel uebernehmen")
    lager_id = db.execute(text("SELECT id FROM domain_inventory.warehouses WHERE tenant_id = :t "
                               "AND warehouse_code = :c"), {"t": tenant_id, "c": lager}).scalar()
    if lager_id is None:
        raise ZeilenFehler(f"Lager {lager} ist in VALEO nicht angelegt")
    return str(artikel), str(lager_id)


def _bestand_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    from decimal import Decimal, InvalidOperation

    artikel, lager = _bestand_bezug(db, tenant_id, p)
    roh = _text(p, "menge", pflicht=True)
    try:
        menge = Decimal(roh.replace(",", ".")) if "," in roh and "." not in roh else Decimal(roh)
    except InvalidOperation as fehler:
        raise ZeilenFehler(f"Menge {roh!r} ist keine Zahl") from fehler
    return {"article_id": artikel, "warehouse_id": lager, "menge": _menge_text(menge),
            "einheit": _text(p, "einheit")}


def _lagersaldo(db: Session, tenant_id: str, artikel: str, lager: str) -> str:
    from decimal import Decimal

    from app.services.inventory_movement_direction import direction_sql

    richtung = direction_sql("sm.movement_type", "sm.quantity")
    saldo = db.execute(text(
        f"SELECT COALESCE(SUM({richtung}), 0) FROM domain_inventory.inventory_stock_movements sm "  # nosec B608 - Fragment aus Modulkonstante
        "WHERE sm.tenant_id = :t AND sm.article_id = :a AND sm.warehouse_id = :w"),
        {"t": tenant_id, "a": artikel, "w": lager}).scalar()
    return _menge_text(Decimal(str(saldo or 0)))


def _bestand_lesen(db: Session, tenant_id: str, ziel_id: str) -> dict[str, Any] | None:
    bewegung = db.execute(text("SELECT article_id, warehouse_id, unit FROM domain_inventory.inventory_stock_movements "
                               "WHERE tenant_id = :t AND id = :id"), {"t": tenant_id, "id": ziel_id}).mappings().first()
    if not bewegung:
        return None
    return {"article_id": str(bewegung["article_id"]), "warehouse_id": str(bewegung["warehouse_id"]),
            "menge": _lagersaldo(db, tenant_id, str(bewegung["article_id"]), str(bewegung["warehouse_id"])),
            "einheit": bewegung["unit"]}


def _bestand_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
    from decimal import Decimal

    from app.domains.inventory.application.services.inventory_service import InventoryService

    vorhanden = _lagersaldo(db, tenant_id, werte["article_id"], werte["warehouse_id"])
    if Decimal(vorhanden) != 0:
        raise ZeilenFehler(f"Lager hat in VALEO bereits Bestand {vorhanden} ohne L3-Quellreferenz - "
                           "Anfangsbestand fachlich klaeren")
    try:
        bewegung = InventoryService(db).process_stock_movement(
            werte["article_id"], werte["warehouse_id"], "opening_balance", Decimal(werte["menge"]),
            unit=werte["einheit"], reference_number="L3-Spiegel Anfangsbestand", booking_user="l3_spiegel",
            auto_created=True, notes="Anfangsbestand aus L3-Spiegelabzug", tenant_id=tenant_id,
            buchungsschluessel=f"spiegel:bestand:{werte['article_id']}:{werte['warehouse_id']}", commit=False,
            source_document_type="l3_spiegel", unterdeckung_pruefen=False)
    except ValueError as fehler:
        raise ZeilenFehler(f"Anfangsbestand nicht buchbar: {fehler}") from fehler
    return str(bewegung.id)


def _bestand_aendern(db: Session, tenant_id: str, ziel_id: str, werte: dict[str, Any]) -> None:
    """Keine Buchung: Abweichungen bleiben sichtbar (siehe oben)."""


# --- Objektart lieferant (L3 KUNDEN mit KREDITORKTO; Anschrift aus ADRESSEN, im Abzug verbunden) -------------------
#
# Ziel ist der fuehrende Kreditorenstamm domain_einkauf.lieferanten (ADR Geschaeftspartnerstamm). Die L3-Kreditorennummer
# wird das Konto des Geschaeftspartners (creditor_account) - Nutzerentscheid 25.11.2026, wie bei den Kunden. Lieferant
# und Kunde mit gleicher USt-IdNr. und gleichem Namen teilen ueber die Partnerbruecke einen Partner (Landwirt).
# lieferantennummer ist ohne Eindeutigkeitsregel in der DB: die Uebernahme prueft sie selbst.


def _lieferant_zielwerte(db: Session, tenant_id: str, p: dict[str, Any]) -> dict[str, Any]:
    return {
        "lieferantennummer": _text(p, "lieferantennummer", pflicht=True),
        "firmenname": _text(p, "name", pflicht=True),
        "strasse": _text(p, "strasse"),
        "plz": _text(p, "plz"),
        "ort": _text(p, "ort"),
        "land": _text(p, "land"),
        "ust_id": _text(p, "ust_id"),
        "telefon": _text(p, "telefon"),
        "email": _text(p, "email"),
        "aktiv": not _ja(p, "gesperrt"),
        "kreditorkonto": _text(p, "kreditorkonto"),
    }


def _lieferant_lesen(db: Session, tenant_id: str, ziel_id: str) -> dict[str, Any] | None:
    zeile = db.execute(text(
        "SELECT l.lieferantennummer, l.firmenname, l.strasse, l.plz, l.ort, l.land, l.ust_id, l.telefon, l.email, "
        "l.aktiv, bp.creditor_account AS kreditorkonto FROM domain_einkauf.lieferanten l "
        "LEFT JOIN domain_crm.business_partners bp ON bp.partner_id::text = l.partner_id AND bp.tenant_id = l.tenant_id "
        "WHERE l.tenant_id = :t AND l.id::text = :id"), {"t": tenant_id, "id": ziel_id}).mappings().first()
    return dict(zeile) if zeile else None


def _lieferant_partner(db: Session, tenant_id: str, werte: dict[str, Any], partner_id: str | None) -> str:
    from app.core.exceptions import ConflictError
    from app.services.business_partner_service import BusinessPartnerService

    try:
        return BusinessPartnerService(db, tenant_id).partner_fuer_rolle(
            "lieferant", name=werte["firmenname"], vat_id=werte["ust_id"], street=werte["strasse"],
            postal_code=werte["plz"], city=werte["ort"], country=werte["land"], email=werte["email"],
            phone=werte["telefon"], partner_id=partner_id, konto=werte["kreditorkonto"])
    except ConflictError as fehler:
        raise ZeilenFehler(f"Kreditorenkonto: {fehler}") from fehler


def _lieferant_spalten(werte: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in werte.items() if k != "kreditorkonto"}


def _lieferant_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
    if db.execute(text("SELECT 1 FROM domain_einkauf.lieferanten WHERE tenant_id = :t AND lieferantennummer = :n"),
                  {"t": tenant_id, "n": werte["lieferantennummer"]}).first():
        raise ZeilenFehler(f"Lieferant {werte['lieferantennummer']} existiert bereits ohne L3-Quellreferenz - "
                           "Zuordnung fachlich klaeren")
    ziel_id = str(uuid7())
    partner = _lieferant_partner(db, tenant_id, werte, None)
    db.execute(text(
        "INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, partner_id, firmenname, strasse, plz, "
        "ort, land, ust_id, telefon, email, aktiv) VALUES (CAST(:id AS uuid), :t, :lieferantennummer, :partner, "
        ":firmenname, :strasse, :plz, :ort, :land, :ust_id, :telefon, :email, :aktiv)"),
        {"id": ziel_id, "t": tenant_id, "partner": partner, **_lieferant_spalten(werte)})
    return ziel_id


def _lieferant_aendern(db: Session, tenant_id: str, ziel_id: str, werte: dict[str, Any]) -> None:
    partner = db.execute(text("SELECT partner_id FROM domain_einkauf.lieferanten WHERE tenant_id = :t "
                              "AND id::text = :id"), {"t": tenant_id, "id": ziel_id}).scalar()
    partner = _lieferant_partner(db, tenant_id, werte, str(partner) if partner else None)
    db.execute(text(
        "UPDATE domain_einkauf.lieferanten SET lieferantennummer = :lieferantennummer, partner_id = :partner, "
        "firmenname = :firmenname, strasse = :strasse, plz = :plz, ort = :ort, land = :land, ust_id = :ust_id, "
        "telefon = :telefon, email = :email, aktiv = :aktiv, updated_at = now() WHERE tenant_id = :t AND id::text = :id"),
        {"id": ziel_id, "t": tenant_id, "partner": partner, **_lieferant_spalten(werte)})


#: Quellfelder ohne VALEO-Ziel je Objektart - im Differenzbericht ausgewiesen, nicht verworfen.
NICHT_ZUGEORDNET: dict[str, dict[str, str]] = {
}


@dataclass(frozen=True)
class Zielart:
    tabelle: str
    zielwerte: Callable[[Session, str, dict[str, Any]], dict[str, Any]]
    lesen: Callable[[Session, str, str], dict[str, Any] | None]
    anlegen: Callable[[Session, str, dict[str, Any]], str]
    aendern: Callable[[Session, str, str, dict[str, Any]], None]
    #: Auch bei unveraendertem L3-Inhalt gegen VALEO vergleichen (Bestand: VALEO-Seite kann abweichen).
    immer_vergleichen: bool = False


ZIELARTEN: dict[str, Zielart] = {
    "artikel": Zielart("domain_inventory.articles", _artikel_zielwerte, _artikel_lesen, _artikel_anlegen,
                       _artikel_aendern),
    "kunde": Zielart("domain_crm.customers", _kunde_zielwerte, _kunde_lesen, _kunde_anlegen, _kunde_aendern),
    "lieferant": Zielart("domain_einkauf.lieferanten", _lieferant_zielwerte, _lieferant_lesen, _lieferant_anlegen,
                         _lieferant_aendern),
    "bestand": Zielart("domain_inventory.inventory_stock_movements", _bestand_zielwerte, _bestand_lesen,
                       _bestand_anlegen, _bestand_aendern, immer_vergleichen=True),
}



def alle_zielarten() -> dict[str, Zielart]:
    """Stammdaten-Objektarten dieses Moduls und die Preis-Objektarten (``spiegel_preise``, verzoegert importiert)."""
    from app.services.spiegel_preise import zielarten as preis_zielarten

    return {**ZIELARTEN, **preis_zielarten()}


# --- Lauf ------------------------------------------------------------------------------------------------------

def _differenzen(alt: dict[str, Any] | None, neu: dict[str, Any]) -> dict[str, Any]:
    alt = {k: v for k, v in (alt or {}).items() if k != "deleted_at"}
    return {feld: {"valeo": alt.get(feld), "l3": wert} for feld, wert in neu.items() if alt.get(feld) != wert}


def _zeile(db: Session, tenant_id: str, batch_id: str, objektart: str, quellschluessel: str,
           payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    art = alle_zielarten()[objektart]
    summe = pruefsumme(payload)
    referenz = db.execute(text(
        "SELECT ziel_id, payload_hash FROM domain_integration.spiegel_quellreferenzen WHERE tenant_id = :t "
        "AND quellsystem = :q AND objektart = :o AND quellschluessel = :k FOR UPDATE"),
        {"t": tenant_id, "q": QUELLSYSTEM, "o": objektart, "k": quellschluessel}).mappings().first()
    if referenz and referenz["payload_hash"] == summe:
        alt = art.lesen(db, tenant_id, referenz["ziel_id"])
        if alt is None:
            raise ZeilenFehler("Zielobjekt der Quellreferenz fehlt in VALEO - geloescht? fachlich klaeren")
        if art.immer_vergleichen:
            differenzen = _differenzen(alt, art.zielwerte(db, tenant_id, payload))
            return ("geaendert" if differenzen else "unveraendert"), differenzen
        if not alt.get("deleted_at"):
            return "unveraendert", {}
        # Soft-Delete in VALEO, gleicher L3-Inhalt: wiederbeleben (L3 fuehrend).
        werte = art.zielwerte(db, tenant_id, payload)
        differenzen = _differenzen(alt, werte)
        differenzen["deleted_at"] = {"valeo": str(alt["deleted_at"]), "l3": None}
        art.aendern(db, tenant_id, referenz["ziel_id"], werte)
        db.execute(text(
            "UPDATE domain_integration.spiegel_quellreferenzen SET batch_id = :b, zuletzt_am = now() "
            "WHERE tenant_id = :t AND quellsystem = :q AND objektart = :o AND quellschluessel = :k"),
            {"t": tenant_id, "q": QUELLSYSTEM, "o": objektart, "k": quellschluessel, "b": batch_id})
        return "geaendert", differenzen
    werte = art.zielwerte(db, tenant_id, payload)
    if referenz is None:
        ziel_id = art.anlegen(db, tenant_id, werte)
        db.execute(text(
            "INSERT INTO domain_integration.spiegel_quellreferenzen (tenant_id, quellsystem, objektart, "
            "quellschluessel, ziel_tabelle, ziel_id, payload_hash, batch_id) VALUES (:t, :q, :o, :k, :z, :id, :h, :b)"),
            {"t": tenant_id, "q": QUELLSYSTEM, "o": objektart, "k": quellschluessel, "z": art.tabelle,
             "id": ziel_id, "h": summe, "b": batch_id})
        return "neu", {}
    alt = art.lesen(db, tenant_id, referenz["ziel_id"])
    if alt is None:
        raise ZeilenFehler("Zielobjekt der Quellreferenz fehlt in VALEO - geloescht? fachlich klaeren")
    differenzen = _differenzen(alt, werte)
    if alt.get("deleted_at"):
        differenzen["deleted_at"] = {"valeo": str(alt["deleted_at"]), "l3": None}
    art.aendern(db, tenant_id, referenz["ziel_id"], werte)
    db.execute(text(
        "UPDATE domain_integration.spiegel_quellreferenzen SET payload_hash = :h, batch_id = :b, "
        "version = version + 1, zuletzt_am = now() WHERE tenant_id = :t AND quellsystem = :q AND objektart = :o "
        "AND quellschluessel = :k"),
        {"t": tenant_id, "q": QUELLSYSTEM, "o": objektart, "k": quellschluessel, "h": summe, "b": batch_id})
    return ("geaendert" if differenzen else "unveraendert"), differenzen


def uebernehme(db: Session, tenant_id: str, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
    """Uebernimmt einen freigegebenen Batch. Wiederholbar; Ergebnis je Zeile im Protokoll."""
    batch = db.execute(text(
        "SELECT profile_key, status FROM domain_integration.legacy_adapter_batches "
        "WHERE id = :id AND tenant_id = :t FOR UPDATE"), {"id": batch_id, "t": tenant_id}).mappings().first()
    if not batch or batch["status"] != "approved":
        raise LegacyAdapterError("Nur freigegebene Batches sind uebernahmefaehig")
    if batch["profile_key"] != "l3_spiegel":
        raise LegacyAdapterError("Nur Batches mit Profil l3_spiegel sind uebernahmefaehig")
    zeilen = db.execute(text(
        "SELECT line_no, record_type, source_ref, canonical_payload FROM domain_integration.legacy_adapter_staging "
        "WHERE tenant_id = :t AND batch_id = :b AND validation_status = 'valid' ORDER BY line_no"),
        {"t": tenant_id, "b": batch_id}).mappings().all()
    zaehler = {"neu": 0, "geaendert": 0, "unveraendert": 0, "fehler": 0}
    for z in zeilen:
        objektart = str(z["record_type"] or "")
        differenzen: dict[str, Any] = {}
        fehler = None
        sicherung = db.begin_nested()
        try:
            if objektart not in alle_zielarten():
                raise ZeilenFehler(f"Objektart {objektart or '-'} ist fuer die Uebernahme nicht freigegeben")
            payload = dict(z["canonical_payload"] or {})
            payload.pop("record_type", None)
            payload.pop("source_ref", None)
            ergebnis, differenzen = _zeile(db, tenant_id, batch_id, objektart, str(z["source_ref"]), payload)
            sicherung.commit()
        except ZeilenFehler as exc:
            sicherung.rollback()
            ergebnis, fehler = "fehler", str(exc)
        except IntegrityError as exc:  # z. B. Artikelnummer in L3 auf eine vergebene Nummer geaendert
            sicherung.rollback()
            ergebnis, fehler = "fehler", f"Datenbankregel verletzt: {exc.orig.__class__.__name__}"

        zaehler[ergebnis] += 1
        db.execute(text(
            "INSERT INTO domain_integration.spiegel_protokoll (id, tenant_id, batch_id, line_no, objektart, "
            "quellschluessel, ergebnis, differenzen, fehler) VALUES (:id, :t, :b, :n, :o, :k, :e, "
            "CAST(:d AS JSONB), :f)"),
            {"id": str(uuid7()), "t": tenant_id, "b": batch_id, "n": z["line_no"], "o": objektart or "-",
             "k": z["source_ref"], "e": ergebnis, "d": json.dumps(differenzen, default=str), "f": fehler})
    LegacyInterfaceAdapterService(db, tenant_id)._audit(
        batch["profile_key"], "mirror_applied", actor, reason, batch_id=batch_id, details=zaehler)
    db.commit()
    return {"batch_id": batch_id, **zaehler}


def differenzbericht(db: Session, tenant_id: str, batch_id: str) -> dict[str, Any]:
    """Letztes Ergebnis je Quellzeile eines Batches: Summen, Fehler und geaenderte Felder."""
    zeilen = db.execute(text(
        "SELECT DISTINCT ON (line_no) line_no, objektart, quellschluessel, ergebnis, differenzen, fehler "
        "FROM domain_integration.spiegel_protokoll WHERE tenant_id = :t AND batch_id = :b "
        "ORDER BY line_no, erstellt_am DESC, id DESC"), {"t": tenant_id, "b": batch_id}).mappings().all()
    summen = {"neu": 0, "geaendert": 0, "unveraendert": 0, "fehler": 0}
    for z in zeilen:
        summen[z["ergebnis"]] += 1
    return {
        "batch_id": batch_id,
        "summen": summen,
        "fehler": [{"zeile": z["line_no"], "quellschluessel": z["quellschluessel"], "fehler": z["fehler"]}
                   for z in zeilen if z["ergebnis"] == "fehler"],
        "geaendert": [{"zeile": z["line_no"], "quellschluessel": z["quellschluessel"], "felder": z["differenzen"]}
                      for z in zeilen if z["ergebnis"] == "geaendert"],
        "nicht_zugeordnet": {art: NICHT_ZUGEORDNET[art] for art in sorted({z["objektart"] for z in zeilen})
                             if art in NICHT_ZUGEORDNET},
    }
