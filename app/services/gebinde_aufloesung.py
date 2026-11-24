"""Gebinderechnung mit Stammdaten - der eine Weg fuer Einkauf, Verkauf, Lager, Waage, Fakturierung, Bewertung.

Verbindet den Stamm (``domain_shared.artikel_mengeneinheiten`` + ``artikel_gebindefaktoren``) mit dem reinen Rechenkern
``app/core/gebinde_rechnung.py``. Kein Fachmodul rechnet Gebinde selbst: es ruft ``berechne_position`` und haelt das
Ergebnis mit ``schreibe_abbild`` an der Belegposition fest. Storno und Retoure lesen das Abbild
(``abbild_der_position``), nie den inzwischen geaenderten Stamm.

Fachentscheid 24.11.2026: Faktorherkunft = Einstiegsstufe mit festen Suchpfaden; Faktoren nur auf Stufen im Suchpfad
pflegbar (serverseitig hier geprueft); fehlend und ungueltig getrennt; kein Ersatzwert.

Abbilder (Nutzervorgabe 24.11.2026): Jede geaenderte Berechnung einer Position wird eine neue, unveraenderliche
Version; die Position bleibt bearbeitbar (z. B. Verwiegung aendert die Menge), bis der Beleg verbindlich gebucht ist
(posted, completed, reversed, cancelled). Ab dann sperrt die Datenbank.

Stufenzuordnung in VALEO: 1 Mengeneinheit = der Stammsatz selbst; 3 Artikel = ``domain_inventory.articles``
(Fremdschluessel mit Mandant). 2 Artikelstamm und 4 Artikel-Auspraegung haben noch kein VALEO-Gegenstueck und sind
deshalb nicht pflegbar (``StufeNichtZugeordnet``); ihr Suchpfad laeuft ueber die vorhandenen Stufen weiter nach unten.
"""
from __future__ import annotations

import json
from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.gebinde_rechnung import (
    BENOETIGTE_FAKTOREN, Faktorherkunft, GebindeNichtRechenbar, Gebindeberechnung, Gebindetyp, _faktoren, _typ,
    berechne_gebinde, pruefe_faktorpflege,
)
from app.core.uuid7 import uuid7

FAKTORSPALTEN = ("faktor1", "faktor2", "faktor3", "faktor4")
GEBUCHT = ("posted", "completed", "reversed", "cancelled")
#: Stufen mit VALEO-Gegenstueck. Erweitern erst nach fachlicher Zuordnung von Artikelstamm/Auspraegung.
ZUGEORDNETE_STUFEN = (Faktorherkunft.ARTIKEL,)


class MengeneinheitUnbekannt(LookupError):
    pass


class StufeNichtZugeordnet(GebindeNichtRechenbar):
    """a.eins-Stufe ohne VALEO-Gegenstueck (Artikelstamm, Auspraegung) - nicht pflegbar, bis zugeordnet."""


class ArtikelUnbekannt(GebindeNichtRechenbar):
    pass


class BelegGebucht(GebindeNichtRechenbar):
    """Die Position gehoert zu einem verbindlich gebuchten Beleg; ihr Abbild ist festgeschrieben."""


def _einheit(db: Session, tenant_id: str, kuerzel: str):
    zeile = db.execute(text(
        "SELECT einheit_kuerzel, gebindetyp, faktorherkunft, ergebniseinheit, dezimalstellen, lvs_relevanz, "
        "faktor1, faktor2, faktor3, faktor4 FROM domain_shared.artikel_mengeneinheiten "
        "WHERE tenant_id = :t AND einheit_kuerzel = :k AND aktiv"), {"t": tenant_id, "k": kuerzel}).mappings().first()
    if zeile is None:
        raise MengeneinheitUnbekannt(f"Mengeneinheit {kuerzel!r} ist nicht angelegt oder nicht aktiv.")
    return zeile


def _satz(zeile) -> Optional[list[Optional[Decimal]]]:
    werte = [zeile[s] for s in FAKTORSPALTEN]
    return None if all(w is None for w in werte) else werte


def pruefe_einheit_vollstaendig(gebindetyp: int, faktorherkunft: Optional[int],
                                faktoren_me: Sequence[Optional[Decimal]]) -> None:
    """Pflegepruefung am Stamm: Typ aktiv, Herkunft bei Gebinde Pflicht; ME-Faktoren, wenn hinterlegt, gueltig und
    vollstaendig (bei Herkunft 1 sind sie die einzige Quelle und damit Pflicht)."""
    gt = _typ(gebindetyp)
    if gt == Gebindetyp.KEIN_GEBINDE:
        if any(f is not None for f in faktoren_me):
            raise GebindeNichtRechenbar("Ohne Gebinde (Typ 0) keine Gebindefaktoren.")
        return
    if faktorherkunft is None:
        raise GebindeNichtRechenbar("Ein Gebinde braucht eine Faktorherkunft (1-4).")
    Faktorherkunft(int(faktorherkunft))
    hinterlegt = any(f is not None for f in faktoren_me)
    if hinterlegt or int(faktorherkunft) == Faktorherkunft.MENGENEINHEIT:
        _faktoren(gt, list(faktoren_me))


def setze_artikelfaktoren(db: Session, tenant_id: str, kuerzel: str, artikel_id: str,
                          faktoren: Sequence[Optional[Decimal]], akteur: Optional[str] = None) -> None:
    """Faktoren der Stufe 3 (Artikel) pflegen - nur, wenn die Faktorherkunft der Einheit diese Stufe zulaesst."""
    zeile = _einheit(db, tenant_id, kuerzel)
    gt = _typ(zeile["gebindetyp"])
    if gt == Gebindetyp.KEIN_GEBINDE:
        raise GebindeNichtRechenbar(f"{kuerzel} ist kein Gebinde - keine Artikelfaktoren.")
    pruefe_faktorpflege(zeile["faktorherkunft"], Faktorherkunft.ARTIKEL)
    werte = (list(faktoren) + [None] * 4)[:4]
    _faktoren(gt, werte)  # vollstaendig und gueltig fuer den Typ, sonst Fehler
    if any(w is not None for w in werte[BENOETIGTE_FAKTOREN[gt]:]):
        raise GebindeNichtRechenbar(f"Gebindetyp {int(gt)} nutzt nur {BENOETIGTE_FAKTOREN[gt]} Faktor(en).")
    try:
        with db.begin_nested():
            db.execute(text(
                "INSERT INTO domain_shared.artikel_gebindefaktoren (id, tenant_id, einheit_kuerzel, stufe, artikel_id, "
                "faktor1, faktor2, faktor3, faktor4, geaendert_von) VALUES (:id, :t, :k, 3, :a, :f1, :f2, :f3, :f4, :v) "
                "ON CONFLICT (tenant_id, einheit_kuerzel, stufe, artikel_id) DO UPDATE SET faktor1 = EXCLUDED.faktor1, "
                "faktor2 = EXCLUDED.faktor2, faktor3 = EXCLUDED.faktor3, faktor4 = EXCLUDED.faktor4, "
                "geaendert_von = EXCLUDED.geaendert_von, updated_at = now()"),
                {"id": uuid7(), "t": tenant_id, "k": kuerzel, "a": artikel_id, "f1": werte[0], "f2": werte[1],
                 "f3": werte[2], "f4": werte[3], "v": akteur})
    except IntegrityError as fehler:  # Fremdschluessel: Artikel nicht in diesem Mandanten
        raise ArtikelUnbekannt(f"Artikel {artikel_id} ist in diesem Mandanten nicht angelegt.") from fehler


def pruefe_stufe_zugeordnet(stufe: int) -> None:
    if Faktorherkunft(int(stufe)) == Faktorherkunft.MENGENEINHEIT:
        raise GebindeNichtRechenbar("Faktoren der Stufe Mengeneinheit stehen am Stammsatz der Einheit.")
    if Faktorherkunft(int(stufe)) not in ZUGEORDNETE_STUFEN:
        raise StufeNichtZugeordnet(
            f"Stufe {Faktorherkunft(int(stufe)).name.lower()} hat in VALEO noch kein Gegenstueck und ist nicht pflegbar.")


def entferne_artikelfaktoren(db: Session, tenant_id: str, kuerzel: str, artikel_id: str) -> bool:
    return bool(db.execute(text(
        "DELETE FROM domain_shared.artikel_gebindefaktoren WHERE tenant_id = :t AND einheit_kuerzel = :k "
        "AND stufe = 3 AND artikel_id = :a"), {"t": tenant_id, "k": kuerzel, "a": artikel_id}).rowcount)


def stufen_ausserhalb(db: Session, tenant_id: str, kuerzel: str, faktorherkunft: Optional[int]) -> list[int]:
    """Stufen mit gepflegten Faktoren, die eine neue Faktorherkunft nicht mehr zuliesse (vor dem Umstellen pruefen)."""
    grenze = int(faktorherkunft or Faktorherkunft.MENGENEINHEIT)
    return [int(r[0]) for r in db.execute(text(
        "SELECT DISTINCT stufe FROM domain_shared.artikel_gebindefaktoren WHERE tenant_id = :t AND einheit_kuerzel = :k "
        "AND stufe > :g ORDER BY stufe"), {"t": tenant_id, "k": kuerzel, "g": grenze}).fetchall()]


def berechne_position(db: Session, tenant_id: str, kuerzel: str, anzahl: Decimal, *,
                      artikel_id: Optional[str] = None) -> Gebindeberechnung:
    """Anzahl in der Gebinde-Mengeneinheit -> Ergebnismenge, Faktoren nach dem Suchpfad der Faktorherkunft."""
    zeile = _einheit(db, tenant_id, kuerzel)
    stufen: dict[Faktorherkunft, Optional[list]] = {Faktorherkunft.MENGENEINHEIT: _satz(zeile)}
    if artikel_id:
        satz = db.execute(text(
            "SELECT faktor1, faktor2, faktor3, faktor4 FROM domain_shared.artikel_gebindefaktoren "
            "WHERE tenant_id = :t AND einheit_kuerzel = :k AND stufe = 3 AND artikel_id = :a"),
            {"t": tenant_id, "k": kuerzel, "a": str(artikel_id)}).mappings().first()
        if satz is not None:
            stufen[Faktorherkunft.ARTIKEL] = _satz(satz)
    herkunft = zeile["faktorherkunft"] or Faktorherkunft.MENGENEINHEIT
    return berechne_gebinde(zeile["gebindetyp"], Decimal(str(anzahl)), herkunft, stufen,
                            rundung=int(zeile["dezimalstellen"] or 0), einheit=zeile["einheit_kuerzel"],
                            ergebniseinheit=zeile["ergebniseinheit"])


def _position(db: Session, tenant_id: str, position_id: str):
    zeile = db.execute(text(
        "SELECT i.gebinde_berechnung, h.status FROM domain_docflow.document_items i "
        "JOIN domain_docflow.document_headers h ON h.id = i.header_id AND h.tenant_id = i.tenant_id "
        "WHERE i.id = :id AND i.tenant_id = :t FOR UPDATE OF i"), {"id": position_id, "t": tenant_id}).mappings().first()
    if zeile is None:
        raise GebindeNichtRechenbar(f"Belegposition {position_id} nicht gefunden.")
    return zeile


def schreibe_abbild(db: Session, tenant_id: str, position_id: str, berechnung: Gebindeberechnung,
                    akteur: Optional[str] = None) -> int:
    """Abbild an der Position festhalten und die Versionsnummer liefern.

    Gleiches Abbild wie das geltende: keine neue Version (Wiederholung ist harmlos). Abweichendes Abbild auf einem
    bearbeitbaren Beleg: neue Version. Auf einem gebuchten Beleg: ``BelegGebucht`` - Korrektur nur ueber Storno.
    Die Position wird dabei gesperrt (FOR UPDATE), parallele Schreiber laufen nacheinander.
    """
    neu = berechnung.als_dict()
    position = _position(db, tenant_id, position_id)
    aktuell = db.execute(text(
        "SELECT version, abbild FROM domain_docflow.document_item_gebinde_abbilder "
        "WHERE position_id = :p AND tenant_id = :t ORDER BY version DESC LIMIT 1"),
        {"p": position_id, "t": tenant_id}).mappings().first()
    if aktuell is not None and aktuell["abbild"] == neu:
        return int(aktuell["version"])
    if position["status"] in GEBUCHT:
        raise BelegGebucht(f"Position {position_id}: Beleg ist gebucht ({position['status']}), Abbild festgeschrieben.")
    version = 1 if aktuell is None else int(aktuell["version"]) + 1
    db.execute(text(
        "INSERT INTO domain_docflow.document_item_gebinde_abbilder (id, tenant_id, position_id, version, abbild, "
        "erstellt_von) VALUES (:id, :t, :p, :v, CAST(:j AS jsonb), :a)"),
        {"id": uuid7(), "t": tenant_id, "p": position_id, "v": version, "j": json.dumps(neu), "a": akteur})
    db.execute(text(
        "UPDATE domain_docflow.document_items SET gebinde_berechnung = CAST(:j AS jsonb) WHERE id = :p AND tenant_id = :t"),
        {"j": json.dumps(neu), "p": position_id, "t": tenant_id})
    return version


def abbild_der_position(db: Session, tenant_id: str, position_id: str) -> Optional[dict]:
    """Geltendes Abbild - Grundlage fuer Storno, Retoure und Nachberechnung."""
    return db.execute(text(
        "SELECT gebinde_berechnung FROM domain_docflow.document_items WHERE id = :id AND tenant_id = :t"),
        {"id": position_id, "t": tenant_id}).scalar()


def abbild_versionen(db: Session, tenant_id: str, position_id: str) -> list[dict]:
    return [dict(z) for z in db.execute(text(
        "SELECT version, abbild, erstellt_von, erstellt_am FROM domain_docflow.document_item_gebinde_abbilder "
        "WHERE position_id = :p AND tenant_id = :t ORDER BY version LIMIT 1000"),
        {"p": position_id, "t": tenant_id}).mappings().fetchmany(1000)]
