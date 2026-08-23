"""Tenant-scoped production control projection over canonical ERP sources."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

OPERATION_TYPES = {"production_order", "mill_run", "stock_transfer", "batch_posting", "rework"}
STATUS_TRANSITIONS = {
    "queued": {"released", "cancelled"},
    "released": {"running", "cancelled"},
    "running": {"paused", "completed", "rework", "cancelled"},
    "paused": {"running", "rework", "cancelled"},
    "rework": {"released", "running", "completed", "cancelled"},
    "completed": {"rework"},
    "cancelled": set(),
}
_SORT_COLUMNS = {
    "planned_at": "planned_at", "created_at": "created_at", "status": "status",
    "operation_type": "operation_type", "source_number": "source_number",
    "work_center": "work_center", "assigned_user": "assigned_user",
}


def valid_status_transition(current: str, target: str) -> bool:
    return target in STATUS_TRANSITIONS.get(current, set())


class ProductionControlError(ValueError):
    pass


class ProductionControlService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def register(self, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
        operation_type = payload.get("operation_type")
        if operation_type not in OPERATION_TYPES:
            raise ProductionControlError("Unbekannter Produktionsvorgang")
        existing = self.db.execute(text("""
            SELECT id, status FROM domain_ops.production_operations
             WHERE tenant_id=:tid AND source_type=:source_type AND source_ref=:source_ref
        """), {"tid": self.tenant_id, "source_type": payload["source_type"], "source_ref": payload["source_ref"]}).mappings().first()
        if existing:
            return {"id": existing["id"], "status": existing["status"], "duplicate": True}
        operation_id = str(uuid7())
        self.db.execute(text("""
            INSERT INTO domain_ops.production_operations
              (id,tenant_id,operation_type,status,source_type,source_ref,source_number,source_route,
               work_center,article_ref,article_name,batch_ref,quantity,unit,assigned_user,planned_at,notes)
            VALUES
              (:id,:tid,:operation_type,'queued',:source_type,:source_ref,:source_number,:source_route,
               :work_center,:article_ref,:article_name,:batch_ref,:quantity,:unit,:assigned_user,:planned_at,:notes)
        """), {"id": operation_id, "tid": self.tenant_id, **{key: payload.get(key) for key in (
            "operation_type", "source_type", "source_ref", "source_number", "source_route", "work_center",
            "article_ref", "article_name", "batch_ref", "quantity", "unit", "assigned_user", "planned_at", "notes")}})
        self._audit(operation_id, "registered", None, "queued", actor, payload.get("reason") or "Vorgang registriert")
        self.db.commit()
        return {"id": operation_id, "status": "queued", "duplicate": False}

    def sync_production_orders(self, *, actor: str, reason: str) -> dict[str, int]:
        result = self.db.execute(text("""
            INSERT INTO domain_ops.production_operations
              (id,tenant_id,operation_type,status,source_type,source_ref,source_number,source_route,
               article_name,batch_ref,quantity,unit,planned_at,notes)
            SELECT gen_random_uuid()::text, p.tenant_id, 'production_order',
              CASE p.status WHEN 'erstellt' THEN 'queued' WHEN 'freigegeben' THEN 'released'
                WHEN 'in_produktion' THEN 'running' WHEN 'fertig' THEN 'completed'
                WHEN 'storniert' THEN 'cancelled' ELSE 'queued' END,
              'mischfutterauftrag', p.id, p.chargen_id,
              '/produktion/mischfutter-produktion', p.rezept_name, p.chargen_id,
              p.menge_t, 't', p.created_at, p.bemerkung
              FROM domain_shared.futtermittel_produktionsauftraege p
             WHERE p.tenant_id=:tid
            ON CONFLICT (tenant_id, source_type, source_ref) DO UPDATE SET
              source_number=EXCLUDED.source_number, article_name=EXCLUDED.article_name,
              batch_ref=EXCLUDED.batch_ref, quantity=EXCLUDED.quantity, notes=EXCLUDED.notes,
              updated_at=NOW()
        """), {"tid": self.tenant_id})
        self.db.execute(text("""
            INSERT INTO domain_ops.production_operation_audit
              (id,tenant_id,operation_id,action,old_value,new_value,actor,reason)
            SELECT gen_random_uuid()::text, o.tenant_id, o.id, 'source_synced', o.status, o.status, :actor, :reason
              FROM domain_ops.production_operations o
             WHERE o.tenant_id=:tid AND o.source_type='mischfutterauftrag'
        """), {"tid": self.tenant_id, "actor": actor, "reason": reason})
        self.db.commit()
        return {"synchronized": int(result.rowcount or 0)}

    def list_page(self, *, page: int = 1, page_size: int = 50, operation_type: str | None = None,
                  status: str | None = None, work_center: str | None = None, assigned_user: str | None = None,
                  q: str | None = None, sort: str = "planned_at", sort_dir: str = "asc") -> dict[str, Any]:
        where = ["tenant_id=:tid"]
        params: dict[str, Any] = {"tid": self.tenant_id}
        for column, value in (("operation_type", operation_type), ("status", status),
                              ("work_center", work_center), ("assigned_user", assigned_user)):
            if value:
                where.append(f"{column}=:{column}")
                params[column] = value
        if q:
            where.append("(source_number ILIKE :q OR article_name ILIKE :q OR batch_ref ILIKE :q OR notes ILIKE :q)")
            params["q"] = f"%{q}%"
        where_sql = " AND ".join(where)
        total = self.db.execute(text(f"SELECT COUNT(*) FROM domain_ops.production_operations WHERE {where_sql}"), params).scalar_one()  # nosec S608 — Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
        params.update(limit=page_size, offset=(page - 1) * page_size)
        sort_col = _SORT_COLUMNS.get(sort, "planned_at")
        direction = "ASC" if sort_dir.lower() == "asc" else "DESC"
        rows = self.db.execute(text(f"""
            SELECT id,operation_type,status,source_type,source_ref,source_number,source_route,work_center,
                   article_ref,article_name,batch_ref,quantity,unit,assigned_user,planned_at,notes,created_at,updated_at
              FROM domain_ops.production_operations WHERE {where_sql}
             ORDER BY {sort_col} {direction} NULLS LAST, created_at DESC LIMIT :limit OFFSET :offset
        """), params).mappings().all()  # nosec S608 — Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
        return {"items": [dict(row) for row in rows], "total": int(total), "page": page, "page_size": page_size}

    def summary(self) -> dict[str, int]:
        row = self.db.execute(text("""
            SELECT COUNT(*) FILTER (WHERE status IN ('queued','released')) AS waiting,
                   COUNT(*) FILTER (WHERE status='running') AS running,
                   COUNT(*) FILTER (WHERE status IN ('paused','rework')) AS attention,
                   COUNT(*) FILTER (WHERE status='completed') AS completed,
                   COUNT(*) FILTER (WHERE operation_type='mill_run' AND status NOT IN ('completed','cancelled')) AS mill_runs
              FROM domain_ops.production_operations WHERE tenant_id=:tid
        """), {"tid": self.tenant_id}).mappings().one()
        return {key: int(row[key] or 0) for key in row.keys()}

    def transition(self, operation_id: str, *, target: str, actor: str, reason: str) -> dict[str, str]:
        row = self.db.execute(text("""
            SELECT id,status FROM domain_ops.production_operations
             WHERE id=:id AND tenant_id=:tid FOR UPDATE
        """), {"id": operation_id, "tid": self.tenant_id}).mappings().first()
        if row is None:
            raise LookupError("Produktionsvorgang nicht gefunden")
        current = row["status"]
        if not valid_status_transition(current, target):
            raise ProductionControlError(f"Uebergang {current} -> {target} nicht erlaubt")
        self.db.execute(text("""
            UPDATE domain_ops.production_operations SET status=:status,updated_at=NOW()
             WHERE id=:id AND tenant_id=:tid
        """), {"status": target, "id": operation_id, "tid": self.tenant_id})
        self._audit(operation_id, "status_changed", current, target, actor, reason)
        self.db.commit()
        return {"id": operation_id, "status": target}

    def audit(self, operation_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
            SELECT action,old_value,new_value,actor,reason,created_at
              FROM domain_ops.production_operation_audit
             WHERE tenant_id=:tid AND operation_id=:id ORDER BY created_at DESC
        """), {"tid": self.tenant_id, "id": operation_id}).mappings().all()
        return [dict(row) for row in rows]

    def _audit(self, operation_id: str, action: str, old_value: str | None, new_value: str | None,
               actor: str, reason: str) -> None:
        self.db.execute(text("""
            INSERT INTO domain_ops.production_operation_audit
              (id,tenant_id,operation_id,action,old_value,new_value,actor,reason)
            VALUES (:id,:tid,:operation_id,:action,:old_value,:new_value,:actor,:reason)
        """), {"id": str(uuid7()), "tid": self.tenant_id, "operation_id": operation_id,
                 "action": action, "old_value": old_value, "new_value": new_value,
                 "actor": actor, "reason": reason})
