"""SPEC-P1-06 Welle 8 — Bestandssaldo fuer die NOT-NULL-Snapshotspalten.

``domain_inventory.inventory_stock_movements`` fuehrt ``previous_stock`` und
``new_stock`` als NOT NULL ohne Default. Jeder Schreibpfad muss sie also selbst
liefern; ``create_lagerbewegung`` tut das laengst, die Storno- und
Inventurdifferenz-Pfade bisher nicht.

Vokabular-Befund: die Tabelle traegt zwei Bewegungsvokabulare nebeneinander —
kleingeschriebene Belegtypen (``wareneingang``/``warenausgang``/``umbuchung_*``)
aus ``POST /lager/bewegungen`` und grossgeschriebene Richtungen
(``ZUGANG``/``ABGANG``) aus den Korrekturdiensten. Diese Funktion kennt beide.
``GET /lager/bestaende`` aggregiert bis heute mit ``ELSE quantity`` und zaehlt
``ABGANG`` damit positiv; das ist ein eigener Fehler im Lese-Modell und wird
hier bewusst nicht mitverbogen, weil die Snapshotspalten und die Aggregation
unabhaengig voneinander sind.
"""
from __future__ import annotations

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

INBOUND_TYPES = ("wareneingang", "inventur", "umbuchung_eingang", "ZUGANG")
OUTBOUND_TYPES = ("warenausgang", "umbuchung_ausgang", "ABGANG")

_BALANCE_SQL = text(
    """
    SELECT COALESCE(SUM(CASE
        WHEN movement_type IN :inbound THEN quantity
        WHEN movement_type IN :outbound THEN -quantity
        ELSE quantity END), 0)
    FROM domain_inventory.inventory_stock_movements
    WHERE tenant_id = :tenant_id
      AND article_id = :article_id
      AND warehouse_id = :warehouse_id
    """
).bindparams(
    bindparam("inbound", expanding=True),
    bindparam("outbound", expanding=True),
)


def current_stock(
    db: Session,
    *,
    tenant_id: str,
    article_id: str,
    warehouse_id: str,
) -> float:
    """Aktueller Buchbestand einer Artikel-/Lager-Kombination."""
    value = db.execute(
        _BALANCE_SQL,
        {
            "tenant_id": tenant_id,
            "article_id": article_id,
            "warehouse_id": warehouse_id,
            "inbound": list(INBOUND_TYPES),
            "outbound": list(OUTBOUND_TYPES),
        },
    ).scalar()
    return float(value or 0)


def signed_delta(movement_type: str, quantity: float) -> float:
    """Vorzeichenbehafteter Bestandseffekt einer Bewegung."""
    if movement_type in OUTBOUND_TYPES:
        return -abs(quantity)
    return abs(quantity)
