"""Controlled inventory count exports, checks, valuation and opening balances."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

BATCH_TYPES = {"count_sheet", "count_import", "control_run", "preliminary_valuation", "opening_balance"}
TRANSITIONS = {"generated": {"reviewed", "rejected"}, "reviewed": {"approved", "rejected"},
               "approved": {"applied"}, "applied": set(), "rejected": set()}


class InventoryAuxiliaryError(ValueError):
    pass


def payload_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class InventoryAuxiliaryService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def create(self, *, count_id: str, batch_type: str, actor: str, reason: str,
               import_rows: list[dict[str, Any]] | None = None, declared_hash: str | None = None) -> dict[str, Any]:
        if batch_type not in BATCH_TYPES:
            raise InventoryAuxiliaryError("Unbekannter Inventur-Nebenlauf")
        count = self.db.execute(text("""
            SELECT id,warehouse_id,status FROM domain_inventory.inventory_counts
             WHERE id=:id AND tenant_id=:tid
        """), {"id": count_id, "tid": self.tenant_id}).mappings().first()
        if count is None:
            raise LookupError("Inventur nicht gefunden")
        if batch_type == "count_import":
            rows = import_rows or []
            if not rows:
                raise InventoryAuxiliaryError("Import enthaelt keine Zeilen")
        else:
            result = self.db.execute(text("""
                SELECT l.id AS line_id,l.article_id,l.expected_qty,l.counted_qty,
                       COALESCE(l.counted_qty,0)-COALESCE(l.expected_qty,0) AS difference,
                       l.batch_number,l.warehouse_id,COALESCE(a.purchase_price,0) AS unit_value
                  FROM domain_inventory.inventory_count_lines l
                  JOIN domain_inventory.articles a ON a.id=l.article_id AND a.tenant_id=:tid
                 WHERE l.inventory_count_id=:id AND l.tenant_id=:tid ORDER BY l.article_id,l.id
            """), {"id": count_id, "tid": self.tenant_id})
            rows = [{key: float(value) if isinstance(value, Decimal) else value for key, value in dict(row).items()}
                    for row in result.mappings().all()]
            for item in rows:
                item["warehouse_id"] = item.get("warehouse_id") or count["warehouse_id"]
        digest = payload_hash(rows)
        if declared_hash and declared_hash != digest:
            raise InventoryAuxiliaryError("Import-Hash stimmt nicht mit dem Inhalt ueberein")
        difference_count = sum(1 for row in rows if abs(float(row.get("difference", 0) or 0)) >= 0.001)
        value = sum(float(row.get("counted_qty", 0) or 0) * float(row.get("unit_value", 0) or 0) for row in rows)
        batch_id = str(uuid7())
        existing = self.db.execute(text("""
            SELECT id,status FROM domain_inventory.inventory_auxiliary_batches
             WHERE tenant_id=:tid AND batch_type=:kind AND inventory_count_id=:count_id AND source_hash=:hash
        """), {"tid": self.tenant_id, "kind": batch_type, "count_id": count_id, "hash": digest}).mappings().first()
        if existing:
            return {"id": existing["id"], "status": existing["status"], "duplicate": True, "source_hash": digest}
        self.db.execute(text("""
            INSERT INTO domain_inventory.inventory_auxiliary_batches
              (id,tenant_id,inventory_count_id,batch_type,status,source_hash,payload,line_count,
               difference_count,preliminary_value,maker,source_route,notes)
            VALUES (:id,:tid,:count_id,:kind,'generated',:hash,CAST(:payload AS JSONB),:line_count,
                    :difference_count,:value,:maker,:route,:notes)
        """), {"id": batch_id, "tid": self.tenant_id, "count_id": count_id, "kind": batch_type,
                 "hash": digest, "payload": json.dumps(rows), "line_count": len(rows),
                 "difference_count": difference_count, "value": value, "maker": actor,
                 "route": f"/lager/inventur?count={count_id}", "notes": reason})
        self._audit(batch_id, "generated", None, "generated", actor, reason)
        self.db.commit()
        return {"id": batch_id, "status": "generated", "duplicate": False, "source_hash": digest,
                "line_count": len(rows), "difference_count": difference_count, "preliminary_value": round(value, 2)}

    def list_page(self, *, page: int = 1, page_size: int = 50, batch_type: str | None = None,
                  status: str | None = None, count_id: str | None = None) -> dict[str, Any]:
        where, params = ["tenant_id=:tid"], {"tid": self.tenant_id}
        for key, value in (("batch_type", batch_type), ("status", status), ("inventory_count_id", count_id)):
            if value:
                where.append(f"{key}=:{key}")
                params[key] = value
        where_sql = " AND ".join(where)
        total = self.db.execute(text(f"SELECT COUNT(*) FROM domain_inventory.inventory_auxiliary_batches WHERE {where_sql}"), params).scalar_one()  # nosec S608 — Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
        params.update(limit=page_size, offset=(page - 1) * page_size)
        rows = self.db.execute(text(f"""
            SELECT id,inventory_count_id,batch_type,status,source_hash,line_count,difference_count,
                   preliminary_value,maker,checker,source_route,notes,created_at,updated_at
              FROM domain_inventory.inventory_auxiliary_batches WHERE {where_sql}
             ORDER BY created_at DESC LIMIT :limit OFFSET :offset
        """), params).mappings().all()  # nosec S608 — Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
        return {"items": [dict(row) for row in rows], "total": int(total), "page": page, "page_size": page_size}

    def summary(self) -> dict[str, int]:
        row = self.db.execute(text("""
            SELECT COUNT(*) FILTER (WHERE status='generated') AS generated,
                   COUNT(*) FILTER (WHERE status='reviewed') AS reviewed,
                   COUNT(*) FILTER (WHERE status='approved') AS approved,
                   COUNT(*) FILTER (WHERE status='applied') AS applied,
                   COUNT(*) FILTER (WHERE difference_count>0 AND status NOT IN ('applied','rejected')) AS with_differences
              FROM domain_inventory.inventory_auxiliary_batches WHERE tenant_id=:tid
        """), {"tid": self.tenant_id}).mappings().one()
        return {key: int(row[key] or 0) for key in row.keys()}

    def transition(self, batch_id: str, *, target: str, actor: str, reason: str) -> dict[str, str]:
        row = self.db.execute(text("""
            SELECT id,status,batch_type,maker,payload,inventory_count_id FROM domain_inventory.inventory_auxiliary_batches
             WHERE id=:id AND tenant_id=:tid FOR UPDATE
        """), {"id": batch_id, "tid": self.tenant_id}).mappings().first()
        if row is None:
            raise LookupError("Inventur-Nebenlauf nicht gefunden")
        current = row["status"]
        if target not in TRANSITIONS.get(current, set()):
            raise InventoryAuxiliaryError(f"Uebergang {current} -> {target} nicht erlaubt")
        if target in {"approved", "applied"} and actor == row["maker"]:
            raise InventoryAuxiliaryError("Vier-Augen-Prinzip: Pruefer muss vom Ersteller abweichen")
        if target == "applied":
            self._apply(row, actor)
        checker = actor if target in {"reviewed", "approved", "applied"} else None
        self.db.execute(text("""
            UPDATE domain_inventory.inventory_auxiliary_batches
               SET status=:status,checker=COALESCE(:checker,checker),updated_at=NOW()
             WHERE id=:id AND tenant_id=:tid
        """), {"status": target, "checker": checker, "id": batch_id, "tid": self.tenant_id})
        self._audit(batch_id, "status_changed", current, target, actor, reason)
        self.db.commit()
        return {"id": batch_id, "status": target}

    def _apply(self, row: Any, actor: str) -> None:
        payload = row["payload"] if isinstance(row["payload"], list) else json.loads(row["payload"])
        if row["batch_type"] == "count_import":
            for item in payload:
                self.db.execute(text("""
                    UPDATE domain_inventory.inventory_count_lines
                       SET counted_qty=:qty,difference=:qty-COALESCE(expected_qty,0)
                     WHERE id=:line_id AND inventory_count_id=:count_id AND tenant_id=:tid
                """), {"qty": item["counted_qty"], "line_id": item["line_id"],
                         "count_id": row["inventory_count_id"], "tid": self.tenant_id})
        elif row["batch_type"] == "opening_balance":
            for item in payload:
                reference = f"OPEN-{row['id'][:12]}-{item['line_id'][:8]}"
                exists = self.db.execute(text("""
                    SELECT 1 FROM domain_inventory.inventory_stock_movements
                     WHERE tenant_id=:tid AND reference_number=:ref
                """), {"tid": self.tenant_id, "ref": reference}).first()
                if exists:
                    continue
                qty = float(item.get("counted_qty", 0) or 0)
                self.db.execute(text("""
                    INSERT INTO domain_inventory.inventory_stock_movements
                      (id,article_id,warehouse_id,movement_type,quantity,unit,charge,reference_number,
                       movement_date,movement_time,notes,booking_user,auto_created,ownership_type,tenant_id,
                       previous_stock,new_stock,created_at)
                    VALUES (:id,:article_id,:warehouse_id,'opening_balance',:qty,'t',:charge,:ref,
                            CURRENT_DATE,NOW()::time,'Freigegebener Bestandsvortrag',:actor,true,'owned',:tid,0,:qty,NOW())
                """), {"id": str(uuid7()), "article_id": item["article_id"], "warehouse_id": item["warehouse_id"],
                         "qty": qty, "charge": item.get("batch_number"), "ref": reference,
                         "actor": actor, "tid": self.tenant_id})
                self.db.execute(text("""
                    UPDATE domain_inventory.articles
                       SET current_stock=:qty,available_stock=:qty,updated_at=NOW()
                     WHERE id=:article_id AND tenant_id=:tid
                """), {"qty": qty, "article_id": item["article_id"], "tid": self.tenant_id})

    def _audit(self, batch_id: str, action: str, old: str | None, new: str | None, actor: str, reason: str) -> None:
        self.db.execute(text("""
            INSERT INTO domain_inventory.inventory_auxiliary_audit
              (id,tenant_id,batch_id,action,old_value,new_value,actor,reason)
            VALUES (:id,:tid,:batch_id,:action,:old,:new,:actor,:reason)
        """), {"id": str(uuid7()), "tid": self.tenant_id, "batch_id": batch_id,
                 "action": action, "old": old, "new": new, "actor": actor, "reason": reason})
