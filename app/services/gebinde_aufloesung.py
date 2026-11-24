"""Gebinderechnung mit Stammdaten - der eine Weg fuer Einkauf, Verkauf, Lager, Waage, Fakturierung, Bewertung.

Verbindet den Stamm (``domain_shared.artikel_mengeneinheiten`` + ``artikel_gebindefaktoren``) mit dem reinen Rechenkern
``app/core/gebinde_rechnung.py``. Kein Fachmodul rechnet Gebinde selbst: es ruft ``berechne_position`` und haelt das
Abbild mit ``halte_fest`` an der Belegposition fest. Storno und Nachberechnung lesen das Abbild (``abbild_der_position``),
nie den inzwischen geaenderten Stamm.

Fachentscheid 24.11.2026: Faktorherkunft = Einstiegsstufe mit festen Suchpfaden; Faktoren nur auf Stufen im Suchpfad
pflegbar (serverseitig hier geprueft); fehlend und ungueltig getrennt; kein Ersatzwert.

Stufenzuordnung in VALEO: 1 Mengeneinheit = der Stammsatz selbst, 3 Artikel = ``domain_inventory.articles.id``.
2 Artikelstamm und 4 Artikel-Auspraegung haben noch kein festes VALEO-Gegenstueck; ihr Bezug ist eine freie Kennung,
die der Aufrufer mitgibt (offen, s. Fachdokument Abschnitt 4).
"""
from __future__ import annotations

import json
from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.gebinde_rechnung import (
    BENOETIGTE_FAKTOREN, Faktorherkunft, GebindeNichtRechenbar, Gebindeberechnung, Gebindetyp, _faktoren, _typ,
    berechne_gebinde, pruefe_faktorpflege,
)
from app.core.uuid7 import uuid7

FAKTORSPALTEN = ("faktor1", "faktor2", "faktor3", "faktor4")


class MengeneinheitUnbekannt(LookupError):
    pass


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


def setze_stufenfaktoren(db: Session, tenant_id: str, kuerzel: str, stufe: int, bezug_id: str,
                         faktoren: Sequence[Optional[Decimal]], akteur: Optional[str] = None) -> None:
    """Faktoren einer Stufe 2-4 pflegen - nur, wenn die Faktorherkunft der Einheit diese Stufe zulaesst."""
    zeile = _einheit(db, tenant_id, kuerzel)
    gt = _typ(zeile["gebindetyp"])
    if gt == Gebindetyp.KEIN_GEBINDE:
        raise GebindeNichtRechenbar(f"{kuerzel} ist kein Gebinde - keine Stufenfaktoren.")
    if int(stufe) == Faktorherkunft.MENGENEINHEIT:
        raise GebindeNichtRechenbar("Faktoren der Stufe Mengeneinheit stehen am Stammsatz der Einheit.")
    pruefe_faktorpflege(zeile["faktorherkunft"], stufe)
    werte = (list(faktoren) + [None] * 4)[:4]
    _faktoren(gt, werte)  # vollstaendig und gueltig fuer den Typ, sonst Fehler
    if any(w is not None for w in werte[BENOETIGTE_FAKTOREN[gt]:]):
        raise GebindeNichtRechenbar(f"Gebindetyp {int(gt)} nutzt nur {BENOETIGTE_FAKTOREN[gt]} Faktor(en).")
    db.execute(text(
        "INSERT INTO domain_shared.artikel_gebindefaktoren (id, tenant_id, einheit_kuerzel, stufe, bezug_id, "
        "faktor1, faktor2, faktor3, faktor4, geaendert_von) VALUES (:id, :t, :k, :s, :b, :f1, :f2, :f3, :f4, :a) "
        "ON CONFLICT (tenant_id, einheit_kuerzel, stufe, bezug_id) DO UPDATE SET faktor1 = EXCLUDED.faktor1, "
        "faktor2 = EXCLUDED.faktor2, faktor3 = EXCLUDED.faktor3, faktor4 = EXCLUDED.faktor4, "
        "geaendert_von = EXCLUDED.geaendert_von, updated_at = now()"),
        {"id": uuid7(), "t": tenant_id, "k": kuerzel, "s": int(stufe), "b": bezug_id, "f1": werte[0],
         "f2": werte[1], "f3": werte[2], "f4": werte[3], "a": akteur})


def entferne_stufenfaktoren(db: Session, tenant_id: str, kuerzel: str, stufe: int, bezug_id: str) -> bool:
    return bool(db.execute(text(
        "DELETE FROM domain_shared.artikel_gebindefaktoren WHERE tenant_id = :t AND einheit_kuerzel = :k "
        "AND stufe = :s AND bezug_id = :b"), {"t": tenant_id, "k": kuerzel, "s": int(stufe), "b": bezug_id}).rowcount)


def stufen_ausserhalb(db: Session, tenant_id: str, kuerzel: str, faktorherkunft: Optional[int]) -> list[int]:
    """Stufen mit gepflegten Faktoren, die eine neue Faktorherkunft nicht mehr zuliesse (vor dem Umstellen pruefen)."""
    grenze = int(faktorherkunft or Faktorherkunft.MENGENEINHEIT)
    return [int(r[0]) for r in db.execute(text(
        "SELECT DISTINCT stufe FROM domain_shared.artikel_gebindefaktoren WHERE tenant_id = :t AND einheit_kuerzel = :k "
        "AND stufe > :g ORDER BY stufe"), {"t": tenant_id, "k": kuerzel, "g": grenze}).fetchall()]


def berechne_position(db: Session, tenant_id: str, kuerzel: str, anzahl: Decimal, *,
                      artikel_id: Optional[str] = None, artikelstamm_id: Optional[str] = None,
                      auspraegung_id: Optional[str] = None) -> Gebindeberechnung:
    """Anzahl in der Gebinde-Mengeneinheit -> Ergebnismenge, Faktoren nach dem Suchpfad der Faktorherkunft."""
    zeile = _einheit(db, tenant_id, kuerzel)
    stufen: dict[Faktorherkunft, Optional[list]] = {Faktorherkunft.MENGENEINHEIT: _satz(zeile)}
    bezuege = {Faktorherkunft.ARTIKELSTAMM: artikelstamm_id, Faktorherkunft.ARTIKEL: artikel_id,
               Faktorherkunft.AUSPRAEGUNG: auspraegung_id}
    for stufe, bezug in bezuege.items():
        if not bezug:
            continue
        satz = db.execute(text(
            "SELECT faktor1, faktor2, faktor3, faktor4 FROM domain_shared.artikel_gebindefaktoren "
            "WHERE tenant_id = :t AND einheit_kuerzel = :k AND stufe = :s AND bezug_id = :b"),
            {"t": tenant_id, "k": kuerzel, "s": int(stufe), "b": str(bezug)}).mappings().first()
        if satz is not None:
            stufen[stufe] = _satz(satz)
    herkunft = zeile["faktorherkunft"] or Faktorherkunft.MENGENEINHEIT
    return berechne_gebinde(zeile["gebindetyp"], Decimal(str(anzahl)), herkunft, stufen,
                            rundung=int(zeile["dezimalstellen"] or 0), einheit=zeile["einheit_kuerzel"],
                            ergebniseinheit=zeile["ergebniseinheit"])


def halte_fest(db: Session, tenant_id: str, position_id: str, berechnung: Gebindeberechnung) -> None:
    """Abbild an die Belegposition schreiben - genau einmal. Ein zweites, anderes Abbild weist die Datenbank ab."""
    geschrieben = db.execute(text(
        "UPDATE domain_docflow.document_items SET gebinde_berechnung = CAST(:j AS jsonb) "
        "WHERE id = :id AND tenant_id = :t AND gebinde_berechnung IS NULL"),
        {"j": json.dumps(berechnung.als_dict()), "id": position_id, "t": tenant_id}).rowcount
    if not geschrieben:
        vorhanden = abbild_der_position(db, tenant_id, position_id)
        if vorhanden != berechnung.als_dict():
            raise GebindeNichtRechenbar(f"Position {position_id}: Gebinderechnung ist bereits festgeschrieben.")


def abbild_der_position(db: Session, tenant_id: str, position_id: str) -> Optional[dict]:
    return db.execute(text(
        "SELECT gebinde_berechnung FROM domain_docflow.document_items WHERE id = :id AND tenant_id = :t"),
        {"id": position_id, "t": tenant_id}).scalar()
