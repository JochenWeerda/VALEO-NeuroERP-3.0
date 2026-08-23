"""Governed operator projection over canonical foreign-goods storage records."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


class ForeignGoodsError(ValueError):
    """Raised for invalid operator transitions."""


class ForeignGoodsWorklistService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def list_page(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        owner_id: str | None = None,
        warehouse_id: str | None = None,
        status: str | None = None,
        query: str | None = None,
    ) -> dict[str, Any]:
        where = ["tenant_id=:tid"]
        params: dict[str, Any] = {"tid": self.tenant_id}
        for column, value in (
            ("eigentuemer_id", owner_id),
            ("warehouse_id", warehouse_id),
            ("status", status),
        ):
            if value:
                where.append(f"{column}=:{column}")
                params[column] = value
        if query:
            where.append(
                "(einlagerungs_nr ILIKE :query OR eigentuemer_name ILIKE :query "
                "OR artikel_nr ILIKE :query OR artikel_bezeichnung ILIKE :query OR charge ILIKE :query)"
            )
            params["query"] = f"%{query}%"
        where_sql = " AND ".join(where)
        total = self.db.execute(
            text(
                f"SELECT COUNT(*) FROM domain_einkauf.fremdwaren_einlagerung WHERE {where_sql}"
            ),
            params,
        ).scalar_one()
        params.update(limit=page_size, offset=(page - 1) * page_size)
        rows = (
            self.db.execute(
                text(f"""
                SELECT id, tenant_id, einlagerungs_nr, eigentuemer_id, eigentuemer_name,
                       warehouse_id, lagerort, artikel_nr, artikel_bezeichnung, charge,
                       einlagerungstyp, menge_eingelagert, menge_aktuell, einheit,
                       einlagerungsdatum, geplante_auslagerung, auslagerungsdatum,
                       gebuehr_pro_tag, gebuehr_einheit, status, notiz, updated_at,
                       '/lager/fremdware?focus=' || id AS source_route
                  FROM domain_einkauf.fremdwaren_einlagerung
                 WHERE {where_sql}
                 ORDER BY CASE WHEN status='ausgelagert' THEN 1 ELSE 0 END,
                          geplante_auslagerung NULLS LAST, einlagerungsdatum DESC
                 LIMIT :limit OFFSET :offset
                """),  # nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
                params,
            )
            .mappings()
            .all()
        )
        return {
            "items": [dict(row) for row in rows],
            "total": int(total),
            "page": page,
            "page_size": page_size,
        }

    def summary(self) -> dict[str, int]:
        row = (
            self.db.execute(
                text("""
                SELECT COUNT(*) FILTER (WHERE status='eingelagert') AS stored,
                       COUNT(*) FILTER (WHERE status='teilausgelagert') AS partial,
                       COUNT(*) FILTER (WHERE status='ausgelagert') AS completed,
                       COUNT(DISTINCT eigentuemer_id) FILTER (WHERE status<>'ausgelagert') AS owners,
                       COUNT(DISTINCT warehouse_id) FILTER (WHERE status<>'ausgelagert') AS warehouses
                  FROM domain_einkauf.fremdwaren_einlagerung WHERE tenant_id=:tid
                """),
                {"tid": self.tenant_id},
            )
            .mappings()
            .one()
        )
        return {key: int(row[key] or 0) for key in row.keys()}

    def transfer(
        self,
        foreign_goods_id: str,
        *,
        warehouse_id: str,
        location: str | None,
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        item = self._lock(foreign_goods_id)
        if item["status"] == "ausgelagert":
            raise ForeignGoodsError("Erledigte Fremdware kann nicht umgebucht werden")
        if item["warehouse_id"] == warehouse_id and item["lagerort"] == location:
            raise ForeignGoodsError("Ziellager und Lagerort sind unveraendert")
        self.db.execute(
            text("""
            UPDATE domain_einkauf.fremdwaren_einlagerung
               SET warehouse_id=:warehouse_id, lagerort=:location, updated_at=NOW()
             WHERE id=:id AND tenant_id=:tid
            """),
            {
                "warehouse_id": warehouse_id,
                "location": location,
                "id": foreign_goods_id,
                "tid": self.tenant_id,
            },
        )
        self._audit(
            item,
            action="transferred",
            actor=actor,
            reason=reason,
            new_warehouse_id=warehouse_id,
            new_location=location,
        )
        self.db.commit()
        return {
            "id": foreign_goods_id,
            "status": item["status"],
            "warehouse_id": warehouse_id,
            "lagerort": location,
        }

    def complete(
        self,
        foreign_goods_id: str,
        *,
        actor: str,
        reason: str,
        remaining_quantity: Decimal = Decimal("0"),
    ) -> dict[str, Any]:
        item = self._lock(foreign_goods_id)
        if item["status"] == "ausgelagert":
            raise ForeignGoodsError("Fremdware ist bereits erledigt")
        if remaining_quantity < 0 or remaining_quantity > Decimal(
            str(item["menge_aktuell"])
        ):
            raise ForeignGoodsError("Restmenge liegt ausserhalb des aktuellen Bestands")
        new_status = "ausgelagert" if remaining_quantity == 0 else "teilausgelagert"
        self.db.execute(
            text("""
            UPDATE domain_einkauf.fremdwaren_einlagerung
               SET menge_aktuell=:quantity, status=:status,
                   auslagerungsdatum=CASE WHEN :status='ausgelagert' THEN CURRENT_DATE ELSE NULL END,
                   updated_at=NOW()
             WHERE id=:id AND tenant_id=:tid
            """),
            {
                "quantity": remaining_quantity,
                "status": new_status,
                "id": foreign_goods_id,
                "tid": self.tenant_id,
            },
        )
        self._audit(
            item,
            action="completed"
            if new_status == "ausgelagert"
            else "partially_completed",
            actor=actor,
            reason=reason,
            new_status=new_status,
            new_quantity=remaining_quantity,
        )
        self.db.commit()
        return {
            "id": foreign_goods_id,
            "status": new_status,
            "menge_aktuell": float(remaining_quantity),
        }

    def _lock(self, foreign_goods_id: str) -> dict[str, Any]:
        row = (
            self.db.execute(
                text("""
                SELECT id,status,warehouse_id,lagerort,menge_aktuell
                  FROM domain_einkauf.fremdwaren_einlagerung
                 WHERE id=:id AND tenant_id=:tid FOR UPDATE
                """),
                {"id": foreign_goods_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            raise LookupError("Fremdwaren-Einlagerung nicht gefunden")
        return dict(row)

    def _audit(
        self,
        item: dict[str, Any],
        *,
        action: str,
        actor: str,
        reason: str,
        new_status: str | None = None,
        new_warehouse_id: str | None = None,
        new_location: str | None = None,
        new_quantity: Decimal | None = None,
    ) -> None:
        self.db.execute(
            text("""
            INSERT INTO domain_einkauf.foreign_goods_audit
              (id,tenant_id,foreign_goods_id,action,old_status,new_status,
               old_warehouse_id,new_warehouse_id,old_location,new_location,
               old_quantity,new_quantity,actor,reason)
            VALUES (:id,:tid,:foreign_goods_id,:action,:old_status,:new_status,
                    :old_warehouse_id,:new_warehouse_id,:old_location,:new_location,
                    :old_quantity,:new_quantity,:actor,:reason)
            """),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "foreign_goods_id": str(item["id"]),
                "action": action,
                "old_status": item["status"],
                "new_status": new_status or item["status"],
                "old_warehouse_id": item["warehouse_id"],
                "new_warehouse_id": new_warehouse_id or item["warehouse_id"],
                "old_location": item["lagerort"],
                "new_location": new_location
                if new_location is not None
                else item["lagerort"],
                "old_quantity": item["menge_aktuell"],
                "new_quantity": new_quantity
                if new_quantity is not None
                else item["menge_aktuell"],
                "actor": actor,
                "reason": reason,
            },
        )
