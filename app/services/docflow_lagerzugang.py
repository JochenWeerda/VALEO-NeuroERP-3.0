"""Lagerzugang des DocFlow-Wareneingangs (BELEG-052 Phase 3b, 10.11.2026).

Bis heute buchte nur der alte Avis-Weg (``wareneingang_avis_service``, gegen ``domain_einkauf.bestellungen``) Ware
ins Lager; ein DocFlow-Wareneingang bewegte keinen Bestand. Jetzt bucht das Kommando ``einlagern`` des offenen
Wareneingangs je Position einen Zugang ``einlagerung`` ins Bestandsbuch und am Artikel - in der Transaktion des
Kommandos, ohne eigenen Commit (wie der Lieferschein ueber die Pickliste ausgeliefert wird). Die Stornierung bucht denselben Bestand als ``abgang`` zurueck (mit Verweis auf den Zugang, GoBD:
nichts wird geloescht).

Abgelehnt wird die Freigabe, wenn das Lager fehlt oder fremd ist, eine Position keinen Artikel des Mandanten trifft
oder ihre Einheit sich nicht in die Lagereinheit des Artikels umrechnen laesst - dann wird gar nichts gebucht.
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.agrar_units import globaler_faktor, normalisiere
from app.core.business_time import business_today
from app.core.exceptions import ValidationFailedError
from app.services.inventory_stock_balance import current_stock

QUELLE = "goods_receipt"


def _lager(db: Session, tenant_id: str, wert: str) -> str:
    wert = str(wert or "").strip()
    if not wert:
        raise ValidationFailedError("Wareneingang ohne Lager: das Ziellager angeben.")
    lager = db.execute(text(
        "SELECT id::text FROM domain_inventory.warehouses WHERE tenant_id = :t AND deleted_at IS NULL "
        "AND (id::text = :w OR warehouse_code = :w) LIMIT 1"), {"t": tenant_id, "w": wert}).scalar()
    if not lager:
        raise ValidationFailedError(f"Lager {wert} gibt es in diesem Mandanten nicht.")
    return str(lager)


def _menge_in_lagereinheit(menge: Decimal, einheit: Optional[str], lagereinheit: Optional[str], pos: Any) -> Decimal:
    if not einheit or not lagereinheit or normalisiere(einheit) == normalisiere(lagereinheit):
        return menge
    faktor = globaler_faktor(einheit, lagereinheit)
    if faktor is None:
        raise ValidationFailedError(
            f"Position {pos}: {einheit} laesst sich nicht in die Lagereinheit {lagereinheit} umrechnen.")
    return menge * faktor


def pruefe_lagerzugang(db: Session, tenant_id: str, positionen: list[dict[str, Any]], lager_wert: str) -> tuple[str, list]:
    """Alles, was gegen den Zugang spricht - ohne zu schreiben. Liefert Lagerkennung und (Position, Artikel, Menge)."""
    lager = _lager(db, tenant_id, lager_wert)
    vorhaben = []
    for pos in positionen:
        menge = Decimal(str(pos.get("quantity") or 0))
        if menge <= 0:
            continue
        nummer = str(pos.get("article_number") or "").strip()
        artikel = db.execute(text(
            "SELECT id::text AS id, unit FROM domain_inventory.articles WHERE tenant_id = :t AND deleted_at IS NULL "
            "AND (article_number = :a OR id::text = :a) LIMIT 1"), {"t": tenant_id, "a": nummer}).mappings().first()
        if not artikel:
            raise ValidationFailedError(
                f"Position {pos.get('line_number')}: Artikel {nummer or '(ohne Nummer)'} gibt es nicht; nichts gebucht.")
        vorhaben.append((pos, dict(artikel), _menge_in_lagereinheit(menge, pos.get("unit"), artikel["unit"],
                                                                    pos.get("line_number"))))
    if not vorhaben:
        raise ValidationFailedError("Der Wareneingang hat keine Position mit Menge.")
    return lager, vorhaben


def einstandspreis(pos: dict[str, Any], menge_lager: Decimal) -> Optional[Decimal]:
    """Einstandspreis je Lagereinheit: Nettowert der Position (Rabatt eingerechnet) geteilt durch die Menge.

    Grundlage des gleitenden Durchschnitts (Nutzerentscheid 24.11.2026, ``app/services/bestandsbewertung.py``).
    Ohne Nettowert bleibt er leer - ein unbekannter Preis ist kein Preis von 0.
    """
    netto = pos.get("line_total_net")
    if netto is None or menge_lager <= 0:
        return None
    wert = Decimal(str(netto))
    if wert <= 0:
        return None
    return (wert / menge_lager).quantize(Decimal("0.000001"))


def buche_lagerzugang(db: Session, tenant_id: str, header: dict[str, Any], positionen: list[dict[str, Any]],
                      lager_wert: str, akteur: Optional[str]) -> str:
    """Zugang je Position mit Menge ins Lager (Kennung oder Lagercode); liefert die Lagerkennung.

    Prueft alles, bevor es schreibt."""
    lager, vorhaben = pruefe_lagerzugang(db, tenant_id, positionen, lager_wert)
    beleg_nr = str(header.get("doc_number") or "")
    heute = business_today()
    for pos, artikel, menge in vorhaben:
        _bewegung(db, tenant_id, artikel, lager, "einlagerung", menge, heute, beleg_nr, str(header["id"]),
                  pos.get("charge") or pos.get("batch_id"), akteur, f"Wareneingang {beleg_nr} Pos. {pos.get('line_number')}",
                  einstand=einstandspreis(pos, menge),
                  schluessel=f"{QUELLE}:{header['id']}:{pos.get('id') or pos.get('line_number')}:einlagerung")
    return lager


def storniere_lagerzugang(db: Session, tenant_id: str, header: dict[str, Any], grund: str,
                          akteur: Optional[str]) -> int:
    """Jeden noch nicht stornierten Zugang des Wareneingangs als Abgang zurueckbuchen."""
    zugaenge = db.execute(text(
        "SELECT m.id::text AS id, m.article_id::text AS article_id, m.warehouse_id::text AS warehouse_id, m.quantity, "
        "m.unit, m.charge, m.unit_cost FROM domain_inventory.inventory_stock_movements m "
        "WHERE m.tenant_id = :t AND m.source_document_type = :q AND m.source_document_id = :h "
        "AND m.movement_type = 'einlagerung' AND NOT EXISTS (SELECT 1 FROM domain_inventory.inventory_stock_movements s "
        "WHERE s.tenant_id = m.tenant_id AND s.storno_ref = m.id::text)"),
        {"t": tenant_id, "q": QUELLE, "h": str(header["id"])}).mappings().all()
    heute = business_today()
    for z in zugaenge:
        _bewegung(db, tenant_id, {"id": z["article_id"], "unit": z["unit"]}, z["warehouse_id"], "abgang",
                  Decimal(str(z["quantity"])), heute, str(header.get("doc_number") or ""), str(header["id"]),
                  z["charge"], akteur, f"Storno Wareneingang {header.get('doc_number')}: {grund}", storno_ref=z["id"],
                  einstand=Decimal(str(z["unit_cost"])) if z["unit_cost"] is not None else None,
                  schluessel=f"storno:{z['id']}")
    return len(zugaenge)


def _bewegung(db: Session, tenant_id: str, artikel: Any, lager: str, art: str, menge: Decimal, datum: Any,
              beleg_nr: str, header_id: str, charge: Any, akteur: Optional[str], notiz: str,
              storno_ref: Optional[str] = None, einstand: Optional[Decimal] = None,
              schluessel: Optional[str] = None) -> str:
    """Eine Bewegung; mit ``schluessel`` hoechstens einmal je Vorgang (bestandsbuchung_schluessel)."""
    from app.services.bestandsbuchung_schluessel import beanspruche, verknuepfe

    if schluessel:
        vorhanden = beanspruche(db, tenant_id, schluessel)
        if vorhanden is not None:
            return vorhanden  # schon gebucht: keine zweite Bewegung, kein zweiter Bestandszugang
    bewegung_id = str(uuid.uuid4())
    vorher = current_stock(db, tenant_id=tenant_id, article_id=artikel["id"], warehouse_id=lager)
    delta = float(menge) if art == "einlagerung" else -float(menge)
    db.execute(text("""
        INSERT INTO domain_inventory.inventory_stock_movements
            (id, tenant_id, article_id, warehouse_id, movement_type, quantity, unit, movement_date, reference_number,
             source_document_type, source_document_id, notes, previous_stock, new_stock, booking_user, auto_created,
             ownership_type, storage_fee_relevant, charge, storno_ref, unit_cost, total_cost)
        VALUES (:id, :t, :a, :w, :art, :m, :e, :d, :nr, :q, :h, :notiz, :vorher, :nachher, :wer, true,
                'owned', false, :charge, :storno, :kosten, :gesamt)
    """), {"id": bewegung_id, "t": tenant_id, "a": artikel["id"], "w": lager, "art": art, "m": menge,
           "e": artikel.get("unit"), "d": datum, "nr": beleg_nr, "q": QUELLE, "h": header_id, "notiz": notiz,
           "vorher": vorher, "nachher": vorher + delta, "wer": akteur, "charge": charge, "storno": storno_ref,
           "kosten": einstand, "gesamt": (einstand * menge).quantize(Decimal("0.01")) if einstand is not None else None})
    # Der Artikelbestand laeuft mit, wie im Buchungsdienst (InventoryService).
    db.execute(text(
        "UPDATE domain_inventory.articles SET current_stock = COALESCE(current_stock, 0) + :m, "
        "available_stock = COALESCE(current_stock, 0) + :m - COALESCE(reserved_stock, 0), updated_at = NOW() "
        "WHERE id::text = :id AND tenant_id = :t"), {"m": delta, "id": artikel["id"], "t": tenant_id})
    if schluessel:
        verknuepfe(db, tenant_id, schluessel, bewegung_id)
    return bewegung_id
