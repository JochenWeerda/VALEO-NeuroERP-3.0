"""FEED-CHAIN-004: Einzelfuttermittel ↔ domain_inventory.articles + Bewegungsbelege."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.infrastructure.models.futtermittel_models import Einzelfuttermittel


class FeedInventoryLinkError(ValueError):
    """Fachlicher Fehler bei Feed-Lager-Verknüpfung."""


def _movement_reference(production_order_id: str, ef_id: str, movement_type: str) -> str:
    """Kurzreferenz (max. 50 Zeichen) für idempotente Bewegungsbuchung."""
    p = production_order_id.replace("-", "")[:12]
    e = ef_id.replace("-", "")[:12]
    suffix = "O" if movement_type == "out" else "I"
    return f"FP{p}{e}{suffix}"


class FeedInventoryLinkService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def resolve_warehouse_id(self) -> str | None:
        row = self.db.execute(
            text("""
                SELECT id FROM domain_inventory.warehouses
                WHERE tenant_id = :tid AND COALESCE(is_active, true) = true
                ORDER BY created_at NULLS LAST
                LIMIT 1
            """),
            {"tid": self.tenant_id},
        ).first()
        return str(row[0]) if row else None

    def get_link(self, einzelfutter_id: str) -> dict[str, Any]:
        ef = (
            self.db.query(Einzelfuttermittel)
            .filter(
                Einzelfuttermittel.id == einzelfutter_id,
                Einzelfuttermittel.tenant_id == self.tenant_id,
            )
            .first()
        )
        if ef is None:
            raise FeedInventoryLinkError("Einzelfuttermittel nicht gefunden")
        article_id = getattr(ef, "inventory_article_id", None)
        article = None
        if article_id:
            article = self.db.execute(
                text(
                    "SELECT id, article_number, name FROM domain_inventory.articles "
                    "WHERE id = :id AND tenant_id = :tid"
                ),
                {"id": article_id, "tid": self.tenant_id},
            ).mappings().first()
        return {
            "einzelfutter_id": ef.id,
            "artikel_nummer": ef.artikel_nummer,
            "name": ef.name,
            "inventory_article_id": article_id,
            "article": dict(article) if article else None,
            "verfuegbar_t": float(ef.verfuegbar_t or 0),
        }

    def ensure_article_link(self, einzelfutter_id: str) -> dict[str, Any]:
        ef = (
            self.db.query(Einzelfuttermittel)
            .filter(
                Einzelfuttermittel.id == einzelfutter_id,
                Einzelfuttermittel.tenant_id == self.tenant_id,
            )
            .with_for_update()
            .first()
        )
        if ef is None:
            raise FeedInventoryLinkError("Einzelfuttermittel nicht gefunden")

        if getattr(ef, "inventory_article_id", None):
            return {"ok": True, "created": False, "article_id": ef.inventory_article_id}

        existing = self.db.execute(
            text("""
                SELECT id FROM domain_inventory.articles
                WHERE tenant_id = :tid AND article_number = :nr
                LIMIT 1
            """),
            {"tid": self.tenant_id, "nr": ef.artikel_nummer},
        ).first()
        if existing:
            article_id = str(existing[0])
            self.db.execute(
                text("""
                    UPDATE domain_shared.futtermittel_einzelfutter
                    SET inventory_article_id = :aid, updated_at = NOW()
                    WHERE id = :id AND tenant_id = :tid
                """),
                {"aid": article_id, "id": ef.id, "tid": self.tenant_id},
            )
            self.db.flush()
            return {"ok": True, "created": False, "article_id": article_id, "matched": True}

        article_id = str(uuid7())
        self.db.execute(
            text("""
                INSERT INTO domain_inventory.articles
                    (id, article_number, name, description, unit, category,
                     sales_price, currency, current_stock, available_stock,
                     lager_silo, tenant_id, is_active, created_at,
                     lagerartikel, mhd_erforderlich, lagerorte, chargenpflicht,
                     qs_pruefung_erforderlich, bio_kennzeichnung, gmp_plus_relevanz)
                VALUES
                    (:id, :nr, :name, :desc, 't', 'futtermittel',
                     0, 'EUR', 0, 0,
                     true, :tid, true, NOW(),
                     true, false, '[]'::jsonb, false, false, false, false)
            """),
            {
                "id": article_id,
                "nr": ef.artikel_nummer,
                "name": ef.name,
                "desc": f"Einzelfuttermittel {ef.art}",
                "tid": self.tenant_id,
            },
        )
        self.db.execute(
            text("""
                UPDATE domain_shared.futtermittel_einzelfutter
                SET inventory_article_id = :aid, updated_at = NOW()
                WHERE id = :id AND tenant_id = :tid
            """),
            {"aid": article_id, "id": ef.id, "tid": self.tenant_id},
        )
        self.db.flush()
        return {"ok": True, "created": True, "article_id": article_id}

    def list_links(self, *, limit: int = 100) -> dict[str, Any]:
        rows = self.db.execute(
            text("""
                SELECT ef.id, ef.artikel_nummer, ef.name, ef.inventory_article_id,
                       ef.verfuegbar_t, a.article_number AS inv_article_number
                FROM domain_shared.futtermittel_einzelfutter ef
                LEFT JOIN domain_inventory.articles a
                  ON a.id = ef.inventory_article_id AND a.tenant_id = ef.tenant_id
                WHERE ef.tenant_id = :tid AND ef.aktiv = true
                ORDER BY ef.artikel_nummer
                LIMIT :lim
            """),
            {"tid": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        mapped = sum(1 for r in rows if r.get("inventory_article_id"))
        return {
            "items": [dict(r) for r in rows],
            "total": len(rows),
            "mapped_count": mapped,
            "unmapped_count": len(rows) - mapped,
        }

    def book_snapshot_movements(
        self,
        *,
        snapshot: list[dict],
        direction: int,
        production_order_id: str,
        booked_by: str,
        warehouse_id: str | None = None,
    ) -> dict[str, Any]:
        """Schreibt inventory_stock_movements für Verbrauchs-Snapshot (fail-soft ohne Mapping)."""
        wh = warehouse_id or self.resolve_warehouse_id()
        if not wh:
            return {"ok": False, "reason": "no_warehouse", "movements": []}

        movement_type = "out" if direction < 0 else "in"
        booked: list[dict[str, Any]] = []
        skipped: list[dict[str, str]] = []

        for row in snapshot:
            ef_id = row.get("einzelfutter_id")
            if not ef_id:
                skipped.append({"reason": "no_einzelfutter_id", "name": str(row.get("name"))})
                continue
            try:
                link = self.ensure_article_link(str(ef_id))
            except FeedInventoryLinkError as exc:
                skipped.append({"reason": str(exc), "einzelfutter_id": str(ef_id)})
                continue

            article_id = link["article_id"]
            qty = abs(Decimal(str(row.get("menge_t") or "0")))
            if qty <= 0:
                continue

            ref = _movement_reference(production_order_id, str(ef_id), movement_type)
            existing = self.db.execute(
                text("""
                    SELECT id FROM domain_inventory.inventory_stock_movements
                    WHERE tenant_id = :tid
                      AND reference_number = :ref
                      AND source_document_type = 'feed_production'
                      AND source_document_id = :doc
                    LIMIT 1
                """),
                {
                    "tid": self.tenant_id,
                    "ref": ref,
                    "doc": f"{production_order_id}:{ef_id}",
                },
            ).first()
            if existing:
                booked.append({"idempotent": True, "movement_id": str(existing[0])})
                continue

            movement_id = str(uuid7())
            signed_qty = float(qty) if direction > 0 else float(-qty)
            self.db.execute(
                text("""
                    INSERT INTO domain_inventory.inventory_stock_movements
                        (id, article_id, warehouse_id, movement_type, quantity, unit, charge,
                         reference_number, movement_date, movement_time,
                         notes, booking_user, auto_created, ownership_type, tenant_id,
                         source_document_type, source_document_id,
                         previous_stock, new_stock, storage_fee_relevant, created_at)
                    VALUES
                        (:id, :article_id, :warehouse_id, :movement_type, :quantity, 't', NULL,
                         :ref, :dt, NOW()::time,
                         :notes, :user, true, 'owned', :tid,
                         'feed_production', :doc,
                         0, 0, false, NOW())
                """),
                {
                    "id": movement_id,
                    "article_id": article_id,
                    "warehouse_id": wh,
                    "movement_type": movement_type,
                    "quantity": float(qty),
                    "ref": ref,
                    "dt": date.today(),
                    "notes": f"Produktion {production_order_id}: {row.get('name')} {signed_qty:+.3f}t",
                    "user": booked_by,
                    "tid": self.tenant_id,
                    "doc": f"{production_order_id}:{ef_id}",
                },
            )
            delta = signed_qty
            self.db.execute(
                text("""
                    UPDATE domain_inventory.articles
                    SET current_stock = COALESCE(current_stock, 0) + :delta,
                        available_stock = COALESCE(available_stock, 0) + :delta,
                        updated_at = NOW()
                    WHERE id = :aid AND tenant_id = :tid
                """),
                {"delta": delta, "aid": article_id, "tid": self.tenant_id},
            )
            booked.append({"movement_id": movement_id, "article_id": article_id, "quantity_t": float(qty)})

        return {"ok": True, "warehouse_id": wh, "movements": booked, "skipped": skipped}
