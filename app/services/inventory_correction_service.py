"""DOM-INV-004.4 — Bestandskorrektur-Storno-Service."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.inventory_stock_balance import current_stock, signed_delta
from app.services.inventory_movement_direction import signed_quantity

logger = logging.getLogger(__name__)


class CorrectionError(Exception):
    """Raised when correction storno constraints are violated."""


def storno_korrektur(
    db: Session,
    korrektur_id: str,
    tenant_id: str,
    bemerkung: Optional[str] = None,
) -> Dict[str, Any]:
    """Storniere eine Lagerbewegung durch eine Gegenbuchung (idempotent).

    Die Gegenbuchung traegt genau die **negierte bestandswirksame Menge** des
    Originals; die Richtung kommt aus ``inventory_movement_direction`` und gilt damit
    fuer jedes Bewegungsvokabular. Bis 07.10.2026 kannte dieser Dienst nur
    ``ZUGANG``/``ABGANG``: Ein Storno eines ``in`` erhoehte den Bestand ein zweites
    Mal.

    Abgelehnt werden: fremde und mandantenlose Bewegungen, ein Storno eines Stornos,
    bestandsneutrale Bewegungen (nichts zu stornieren) und ein Storno, der den
    Bestand negativ machte (die Ware ist schon weiter verbraucht).
    Idempotent: Gibt es den Storno schon, wird er zurueckgegeben.
    """
    original = db.execute(
        text(
            "SELECT * FROM domain_inventory.inventory_stock_movements "
            "WHERE id = :id AND tenant_id = :tid FOR UPDATE"
        ),
        {"id": korrektur_id, "tid": tenant_id},
    ).mappings().first()
    if not original:
        raise CorrectionError(f"Bewegung {korrektur_id} nicht gefunden")

    orig = dict(original)

    if (orig.get("source_document_type") or "").upper() == "STORNO":
        raise CorrectionError(
            f"Korrektur {korrektur_id} ist selbst ein Storno und kann nicht storniert werden"
        )

    # idempotency: check if storno already exists
    existing_storno = db.execute(
        text(
            "SELECT * FROM domain_inventory.inventory_stock_movements "
            "WHERE storno_ref = :ref AND source_document_type = 'STORNO' AND tenant_id = :tid "
            "LIMIT 1"
        ),
        {"ref": korrektur_id, "tid": tenant_id},
    ).mappings().first()
    if existing_storno:
        logger.info("storno_korrektur: Storno bereits vorhanden für %s — idempotent return", korrektur_id)
        return {**dict(existing_storno), "idempotent": True}

    # Gegenbuchung: negierte bestandswirksame Menge, als zugang/abgang mit positiver
    # Menge - so liest sie jede Auswertung ueber die Richtungstabelle richtig.
    storno_id = str(uuid.uuid4())
    wirkung = signed_quantity(orig.get("movement_type"), float(orig.get("quantity") or 0))
    if wirkung == 0:
        raise CorrectionError(
            f"Bewegung {korrektur_id} ({orig.get('movement_type')}) ist bestandsneutral; "
            "es gibt nichts zu stornieren."
        )
    # Grossschreibung wie bisher in diesem Dienst; die Richtungstabelle liest beides.
    storno_movement_type = "ABGANG" if wirkung > 0 else "ZUGANG"
    orig_qty = abs(wirkung)

    # previous_stock/new_stock sind NOT NULL ohne Default, ebenso auto_created,
    # ownership_type und storage_fee_relevant.
    article_id = str(orig.get("article_id") or "")
    warehouse_id = str(orig.get("warehouse_id") or "")
    prev_stock = current_stock(
        db,
        tenant_id=tenant_id,
        article_id=article_id,
        warehouse_id=warehouse_id,
    )
    new_stock = prev_stock + signed_delta(storno_movement_type, orig_qty)
    if new_stock < 0:
        raise CorrectionError(
            f"Storno von {korrektur_id} machte den Bestand negativ ({new_stock:g}); "
            "die Ware ist bereits weiter gebucht."
        )

    db.execute(
        text("""
            INSERT INTO domain_inventory.inventory_stock_movements
                (id, tenant_id, article_id, warehouse_id, movement_type,
                 quantity, unit, source_document_type, source_document_id,
                 storno_ref, notes, previous_stock, new_stock,
                 auto_created, ownership_type, storage_fee_relevant)
            VALUES (:id, :tenant_id, :article_id, :warehouse_id, :movement_type,
                    :quantity, :unit, 'STORNO', :storno_ref,
                    :storno_ref, :notes, :previous_stock, :new_stock,
                    true, :ownership_type, false)
        """),
        {
            "id": storno_id,
            "tenant_id": tenant_id,
            "article_id": article_id,
            "warehouse_id": warehouse_id,
            "movement_type": storno_movement_type,
            "quantity": orig_qty,
            "unit": orig.get("unit", "kg"),
            "storno_ref": korrektur_id,
            "notes": bemerkung or f"Storno von {korrektur_id}",
            "previous_stock": prev_stock,
            "new_stock": new_stock,
            "ownership_type": orig.get("ownership_type") or "owned",
        },
    )
    # Der Artikelbestand laeuft mit, wie beim Buchen (InventoryService). Bis
    # 07.10.2026 korrigierte der Storno nur das Bestandsbuch; der Artikel behielt
    # den alten Bestand — zwei Wahrheiten fuer dieselbe Ware.
    db.execute(
        text(
            "UPDATE domain_inventory.articles "
            "SET current_stock = COALESCE(current_stock, 0) + :delta, "
            "    available_stock = COALESCE(current_stock, 0) + :delta - COALESCE(reserved_stock, 0), "
            "    updated_at = NOW() "
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"delta": -wirkung, "id": article_id, "tid": tenant_id},
    )
    # mark original as storniert
    db.execute(
        text(
            "UPDATE domain_inventory.inventory_stock_movements "
            "SET storno_ref = :storno_id WHERE id = :orig_id"
        ),
        {"storno_id": storno_id, "orig_id": korrektur_id},
    )
    db.commit()
    logger.info("storno_korrektur: Storno %s für Korrektur %s angelegt", storno_id, korrektur_id)
    return {
        "id": storno_id,
        "storno_ref": korrektur_id,
        "tenant_id": tenant_id,
        "article_id": orig.get("article_id"),
        "warehouse_id": orig.get("warehouse_id"),
        "movement_type": storno_movement_type,
        "quantity": orig_qty,
        "source_document_type": "STORNO",
        "source_document_id": korrektur_id,
        "previous_stock": prev_stock,
        "new_stock": new_stock,
        "unit": orig.get("unit", "kg"),
        "idempotent": False,
    }
