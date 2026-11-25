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

Objektarten: zunaechst ``artikel``. Die Zuordnung L3-Spalte -> kanonisches Feld steht im Adapterprofil
(``field_mapping``); siehe ``docs/migration/m6-spiegelbetrieb-l3.md``.
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
        "SELECT article_number, name, description2, warengruppe, unit, is_active FROM domain_inventory.articles "
        "WHERE tenant_id = :t AND id = :id"), {"t": tenant_id, "id": ziel_id}).mappings().first()
    return dict(zeile) if zeile else None


def _artikel_anlegen(db: Session, tenant_id: str, werte: dict[str, Any]) -> str:
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
    db.execute(text(
        "UPDATE domain_inventory.articles SET article_number = :article_number, name = :name, "
        "description2 = :description2, warengruppe = :warengruppe, unit = :unit, is_active = :is_active, "
        "updated_at = now() WHERE tenant_id = :t AND id = :id"), {"id": ziel_id, "t": tenant_id, **werte})


@dataclass(frozen=True)
class Zielart:
    tabelle: str
    zielwerte: Callable[[Session, str, dict[str, Any]], dict[str, Any]]
    lesen: Callable[[Session, str, str], dict[str, Any] | None]
    anlegen: Callable[[Session, str, dict[str, Any]], str]
    aendern: Callable[[Session, str, str, dict[str, Any]], None]


ZIELARTEN: dict[str, Zielart] = {
    "artikel": Zielart("domain_inventory.articles", _artikel_zielwerte, _artikel_lesen, _artikel_anlegen,
                       _artikel_aendern),
}


# --- Lauf ------------------------------------------------------------------------------------------------------

def _differenzen(alt: dict[str, Any] | None, neu: dict[str, Any]) -> dict[str, Any]:
    alt = alt or {}
    return {feld: {"valeo": alt.get(feld), "l3": wert} for feld, wert in neu.items() if alt.get(feld) != wert}


def _zeile(db: Session, tenant_id: str, batch_id: str, objektart: str, quellschluessel: str,
           payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    art = ZIELARTEN[objektart]
    summe = pruefsumme(payload)
    referenz = db.execute(text(
        "SELECT ziel_id, payload_hash FROM domain_integration.spiegel_quellreferenzen WHERE tenant_id = :t "
        "AND quellsystem = :q AND objektart = :o AND quellschluessel = :k FOR UPDATE"),
        {"t": tenant_id, "q": QUELLSYSTEM, "o": objektart, "k": quellschluessel}).mappings().first()
    if referenz and referenz["payload_hash"] == summe:
        return "unveraendert", {}
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
            if objektart not in ZIELARTEN:
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
    }
