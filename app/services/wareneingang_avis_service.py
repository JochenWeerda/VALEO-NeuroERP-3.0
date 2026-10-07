"""Wareneingang aus dem Anlieferavis — Bestellung beliefert, Ware im Lager.

Bis zum 07.10.2026 gab es aus dem Avis keinen Wareneingang: Die Maskenaktion
meldete Erfolg ohne Buchung, danach war sie eine benannte Luecke. Der vorhandene
WE-Dienst (``proc_wareneingang_service``) bucht gegen eine Stummel-Tabelle ohne
Bestellnummer und ohne Lagerzugang.

Hier gilt, in **einem** Commit:

* Das Avis fuehrt ueber ``bestell_nr`` zur kanonischen Bestellung
  (``domain_einkauf.bestellungen``), beides im Mandanten.
* Je Position mit offener Menge: ``menge_geliefert``/``menge_offen`` fortgeschrieben
  und ein Lagerzugang ``einlagerung`` gebucht — im Bestandsbuch
  (``inventory_stock_movements``) **und** am Artikel (``current_stock``), wie es der
  Buchungsdienst tut.
* Bestellung ``geliefert``, Avis ``ERHALTEN``.

Abgelehnt: fremdes Avis oder Lager, Avis ohne Bestellbezug, nichts mehr offen
(kein zweiter Wareneingang), eine Position ohne Artikel (sie liesse sich nicht
einlagern — dann wird gar nichts gebucht). Teillieferungen bleiben beim Abgleich
Eingangslieferschein ↔ Bestellung.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.business_time import business_today

from app.services.inventory_stock_balance import current_stock


class WareneingangAvisError(Exception):
    """Der Wareneingang ist so nicht buchbar; die Nachricht nennt den Grund."""


def _avis_und_bestellung(db: Session, avis_id: str, tenant_id: str) -> tuple[dict, dict]:
    avis = db.execute(
        text("SELECT id, avis_nummer, bestell_nr, status FROM einkauf_anlieferavis "
             "WHERE id = :id AND tenant_id = :tid FOR UPDATE"),
        {"id": avis_id, "tid": tenant_id},
    ).mappings().first()
    if not avis:
        raise WareneingangAvisError("Anlieferavis nicht gefunden.")
    bestellung = db.execute(
        text("SELECT id, bestellnummer, status FROM domain_einkauf.bestellungen "
             "WHERE bestellnummer = :nr AND tenant_id = :tid FOR UPDATE"),
        {"nr": avis["bestell_nr"] or "", "tid": tenant_id},
    ).mappings().first()
    if not bestellung:
        raise WareneingangAvisError(
            f"Zum Avis {avis['avis_nummer']} gibt es keine Bestellung {avis['bestell_nr'] or '(ohne Nummer)'}."
        )
    return dict(avis), dict(bestellung)


def pruefe_wareneingang(db: Session, avis_id: str, tenant_id: str, lager_id: str, lieferschein_nr: str) -> list:
    """Alles, was gegen die Buchung spricht — ohne zu schreiben. Liefert die offenen Positionen."""
    if not str(lieferschein_nr or "").strip():
        raise WareneingangAvisError("Lieferschein-Nr. fehlt.")
    if not db.execute(
        text("SELECT 1 FROM domain_inventory.warehouses WHERE id = :id AND tenant_id = :tid"),
        {"id": lager_id or "", "tid": tenant_id},
    ).scalar():
        raise WareneingangAvisError("Lager nicht gefunden.")
    _, bestellung = _avis_und_bestellung(db, avis_id, tenant_id)
    offen = db.execute(
        text("SELECT id, pos_nr, article_id, artikel_bezeichnung, menge, menge_geliefert, menge_offen, einheit "
             "FROM domain_einkauf.bestellung_positionen "
             "WHERE bestellung_id = :b AND COALESCE(menge_offen, 0) > 0 ORDER BY pos_nr LIMIT 500"),
        {"b": bestellung["id"]},
    ).mappings().fetchmany(500)
    if not offen:
        raise WareneingangAvisError(
            f"Bestellung {bestellung['bestellnummer']} hat nichts mehr offen; ein Wareneingang ist schon gebucht."
        )
    ohne_artikel = [str(p["pos_nr"]) for p in offen if not p["article_id"]]
    if ohne_artikel:
        raise WareneingangAvisError(
            f"Position {', '.join(ohne_artikel)} ohne Artikel kann nicht eingelagert werden; nichts gebucht."
        )
    return [dict(p) for p in offen]


def buche_wareneingang_aus_avis(
    db: Session, avis_id: str, tenant_id: str, lager_id: str, lieferschein_nr: str, operator: str | None = None,
) -> dict[str, Any]:
    """Bucht den Wareneingang; der Aufrufer committet nicht — dieser Dienst schon."""
    avis, bestellung = _avis_und_bestellung(db, avis_id, tenant_id)
    positionen = pruefe_wareneingang(db, avis_id, tenant_id, lager_id, lieferschein_nr)
    heute = business_today()
    for pos in positionen:
        menge = Decimal(str(pos["menge_offen"]))
        artikel = str(pos["article_id"])
        vorher = current_stock(db, tenant_id=tenant_id, article_id=artikel, warehouse_id=lager_id)
        db.execute(
            text("""
                INSERT INTO domain_inventory.inventory_stock_movements
                    (id, tenant_id, article_id, warehouse_id, movement_type, quantity, unit,
                     movement_date, reference_number, source_document_type, source_document_id,
                     notes, previous_stock, new_stock, booking_user, auto_created,
                     ownership_type, storage_fee_relevant)
                VALUES (:id, :tid, :artikel, :lager, 'einlagerung', :menge, :einheit,
                        :datum, :ls, 'WARENEINGANG', :avis, :notiz, :vorher, :nachher, :wer, false,
                        'owned', false)
            """),
            {
                "id": str(uuid.uuid4()), "tid": tenant_id, "artikel": artikel, "lager": lager_id,
                "menge": menge, "einheit": pos["einheit"], "datum": heute, "ls": lieferschein_nr.strip(),
                "avis": avis_id, "notiz": f"Wareneingang Avis {avis['avis_nummer']}, Bestellung "
                                         f"{bestellung['bestellnummer']} Pos. {pos['pos_nr']}",
                "vorher": vorher, "nachher": vorher + float(menge), "wer": operator,
            },
        )
        # Der Artikelbestand laeuft mit, wie im Buchungsdienst (InventoryService).
        db.execute(
            text("UPDATE domain_inventory.articles SET current_stock = COALESCE(current_stock, 0) + :m, "
                 "available_stock = COALESCE(current_stock, 0) + :m - COALESCE(reserved_stock, 0), "
                 "updated_at = NOW() WHERE id = :id AND tenant_id = :tid"),
            {"m": menge, "id": artikel, "tid": tenant_id},
        )
        db.execute(
            text("UPDATE domain_einkauf.bestellung_positionen SET menge_geliefert = COALESCE(menge_geliefert, 0) + :m, "
                 "menge_offen = 0, status = 'geliefert' WHERE id = :id"),
            {"m": menge, "id": pos["id"]},
        )
    db.execute(
        text("UPDATE domain_einkauf.bestellungen SET status = 'geliefert', lieferdatum_ist = :heute "
             "WHERE id = :id AND tenant_id = :tid"),
        {"heute": heute, "id": bestellung["id"], "tid": tenant_id},
    )
    db.execute(
        text("UPDATE einkauf_anlieferavis SET status = 'ERHALTEN', updated_at = NOW() "
             "WHERE id = :id AND tenant_id = :tid"),
        {"id": avis_id, "tid": tenant_id},
    )
    db.commit()
    return {
        "avis_id": avis_id,
        "bestellung_id": str(bestellung["id"]),
        "bestellnummer": bestellung["bestellnummer"],
        "positionen": len(positionen),
        "lieferschein_nr": lieferschein_nr.strip(),
    }
