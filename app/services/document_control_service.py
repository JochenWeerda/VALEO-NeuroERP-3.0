"""Central document-control exception worklist (Beleg-Kontrolle)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

EXCEPTION_TYPES = {
    "open_purchase_order",
    "missing_inbound_document",
    "blocked_delivery_note",
    "uninvoiced_delivery_note",
}
STATUS_TRANSITIONS = {
    "open": {"assigned", "in_progress", "resolved", "waived"},
    "assigned": {"in_progress", "resolved", "waived", "open"},
    "in_progress": {"resolved", "waived", "assigned"},
    "resolved": set(),
    "waived": set(),
}
_SORT_COLUMNS = {
    "created_at": "created_at",
    "due_at": "due_at",
    "exception_type": "exception_type",
    "status": "status",
    "assigned_user": "assigned_user",
    "partner_ref": "partner_ref",
    "document_number": "document_number",
}


def valid_status_transition(current: str, target: str) -> bool:
    return target in STATUS_TRANSITIONS.get(current, set())


class DocumentControlError(ValueError):
    pass


class DocumentControlService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def register_exception(self, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
        exception_type = payload.get("exception_type")
        if exception_type not in EXCEPTION_TYPES:
            raise DocumentControlError("Unbekannter Ausnahme-Typ")
        source_key = payload.get("source_key") or f"{exception_type}:{payload.get('document_ref')}"
        existing = self.db.execute(
            text("""
                SELECT id, status FROM domain_ops.document_control_exceptions
                 WHERE tenant_id=:tid AND source_key=:source_key
            """),
            {"tid": self.tenant_id, "source_key": source_key},
        ).mappings().first()
        if existing is not None:
            return {"id": existing["id"], "status": existing["status"], "duplicate": True}

        case_id = str(uuid7())
        self.db.execute(
            text("""
                INSERT INTO domain_ops.document_control_exceptions
                    (id, tenant_id, exception_type, status, document_ref, document_number,
                     partner_ref, partner_name, assigned_user, due_at, source_route, source_key, notes)
                VALUES
                    (:id,:tid,:exception_type,'open',:document_ref,:document_number,
                     :partner_ref,:partner_name,:assigned_user,:due_at,:source_route,:source_key,:notes)
            """),
            {
                "id": case_id,
                "tid": self.tenant_id,
                "exception_type": exception_type,
                "document_ref": payload["document_ref"],
                "document_number": payload.get("document_number") or payload["document_ref"],
                "partner_ref": payload.get("partner_ref"),
                "partner_name": payload.get("partner_name"),
                "assigned_user": payload.get("assigned_user"),
                "due_at": payload.get("due_at"),
                "source_route": payload.get("source_route"),
                "source_key": source_key,
                "notes": payload.get("notes"),
            },
        )
        self._audit(case_id, "registered", None, "open", actor, payload.get("reason") or "Ausnahme registriert")
        self.db.commit()
        return {"id": case_id, "status": "open", "duplicate": False}

    def upsert_projected(self, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
        """Idempotent projection upsert; never reopens resolved/waived cases."""
        exception_type = payload.get("exception_type")
        if exception_type not in EXCEPTION_TYPES:
            raise DocumentControlError("Unbekannter Ausnahme-Typ")
        source_key = payload.get("source_key") or f"proj:{exception_type}:{payload.get('document_ref')}"
        existing = self.db.execute(
            text("""
                SELECT id, status FROM domain_ops.document_control_exceptions
                 WHERE tenant_id=:tid AND source_key=:source_key
            """),
            {"tid": self.tenant_id, "source_key": source_key},
        ).mappings().first()
        if existing is not None:
            if existing["status"] in {"resolved", "waived"}:
                return {"id": existing["id"], "status": existing["status"], "projection": "skipped"}
            self.db.execute(
                text("""
                    UPDATE domain_ops.document_control_exceptions
                       SET document_number=:document_number,
                           partner_ref=:partner_ref,
                           partner_name=:partner_name,
                           source_route=:source_route,
                           notes=:notes,
                           updated_at=NOW()
                     WHERE id=:id AND tenant_id=:tid
                """),
                {
                    "document_number": payload.get("document_number") or payload["document_ref"],
                    "partner_ref": payload.get("partner_ref"),
                    "partner_name": payload.get("partner_name"),
                    "source_route": payload.get("source_route"),
                    "notes": payload.get("notes"),
                    "id": existing["id"],
                    "tid": self.tenant_id,
                },
            )
            self._audit(
                existing["id"],
                "projected_refresh",
                existing["status"],
                existing["status"],
                actor,
                payload.get("reason") or "Live-Projektion aktualisiert",
            )
            self.db.commit()
            return {"id": existing["id"], "status": existing["status"], "projection": "refreshed"}

        created = self.register_exception({**payload, "source_key": source_key}, actor=actor)
        return {**created, "projection": "created"}

    def list_page(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        exception_type: str | None = None,
        status: str | None = None,
        assigned_user: str | None = None,
        partner_ref: str | None = None,
        q: str | None = None,
        sort: str = "due_at",
        sort_dir: str = "asc",
    ) -> dict[str, Any]:
        where = ["tenant_id=:tid"]
        params: dict[str, Any] = {"tid": self.tenant_id}
        if exception_type:
            where.append("exception_type=:exception_type")
            params["exception_type"] = exception_type
        if status:
            where.append("status=:status")
            params["status"] = status
        if assigned_user:
            where.append("assigned_user=:assigned_user")
            params["assigned_user"] = assigned_user
        if partner_ref:
            where.append("partner_ref=:partner_ref")
            params["partner_ref"] = partner_ref
        if q:
            where.append("(document_number ILIKE :q OR partner_name ILIKE :q OR partner_ref ILIKE :q OR notes ILIKE :q)")
            params["q"] = f"%{q}%"
        where_sql = " AND ".join(where)
        sort_col = _SORT_COLUMNS.get(sort, "due_at")
        direction = "ASC" if sort_dir.lower() == "asc" else "DESC"
        total = self.db.execute(
            text(f"SELECT COUNT(*) FROM domain_ops.document_control_exceptions WHERE {where_sql}"),  # nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
            params,
        ).scalar_one()
        params["limit"] = page_size
        params["offset"] = (page - 1) * page_size
        rows = self.db.execute(
            text(f"""
                SELECT id, exception_type, status, document_ref, document_number, partner_ref, partner_name,
                       assigned_user, due_at, source_route, notes, created_at, updated_at
                  FROM domain_ops.document_control_exceptions
                 WHERE {where_sql}
                 ORDER BY {sort_col} {direction} NULLS LAST, created_at DESC
                 LIMIT :limit OFFSET :offset
            """),  # nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
            params,
        ).mappings().all()
        return {"items": [dict(row) for row in rows], "total": int(total), "page": page, "page_size": page_size}

    def summary(self) -> dict[str, int]:
        rows = self.db.execute(
            text("""
                SELECT
                  COUNT(*) FILTER (WHERE status IN ('open','assigned','in_progress')) AS open_total,
                  COUNT(*) FILTER (WHERE exception_type='open_purchase_order' AND status NOT IN ('resolved','waived')) AS open_purchase_order,
                  COUNT(*) FILTER (WHERE exception_type='missing_inbound_document' AND status NOT IN ('resolved','waived')) AS missing_inbound_document,
                  COUNT(*) FILTER (WHERE exception_type='blocked_delivery_note' AND status NOT IN ('resolved','waived')) AS blocked_delivery_note,
                  COUNT(*) FILTER (WHERE exception_type='uninvoiced_delivery_note' AND status NOT IN ('resolved','waived')) AS uninvoiced_delivery_note,
                  COUNT(*) FILTER (WHERE due_at < NOW() AND status NOT IN ('resolved','waived')) AS overdue
                FROM domain_ops.document_control_exceptions
                WHERE tenant_id=:tid
            """),
            {"tid": self.tenant_id},
        ).mappings().one()
        return {key: int(rows[key] or 0) for key in rows.keys()}

    def assign(self, case_id: str, *, assigned_user: str, actor: str, reason: str, due_at: Any | None = None) -> dict[str, Any]:
        row = self._lock(case_id)
        old = row["status"]
        target = "assigned" if old == "open" else old
        if old == "open" and not valid_status_transition(old, "assigned"):
            raise DocumentControlError("Statuswechsel nicht erlaubt")
        self.db.execute(
            text("""
                UPDATE domain_ops.document_control_exceptions
                   SET assigned_user=:assigned_user,
                       due_at=COALESCE(:due_at, due_at),
                       status=:status,
                       updated_at=NOW()
                 WHERE id=:id AND tenant_id=:tid
            """),
            {
                "assigned_user": assigned_user,
                "due_at": due_at,
                "status": target if old == "open" else old,
                "id": case_id,
                "tid": self.tenant_id,
            },
        )
        self._audit(case_id, "assigned", old, target if old == "open" else old, actor, reason)
        self.db.commit()
        return {"id": case_id, "assigned_user": assigned_user, "status": target if old == "open" else old}

    def transition(self, case_id: str, *, target: str, actor: str, reason: str) -> dict[str, Any]:
        row = self._lock(case_id)
        current = row["status"]
        if not valid_status_transition(current, target):
            raise DocumentControlError(f"Uebergang {current} -> {target} nicht erlaubt")
        self.db.execute(
            text("""
                UPDATE domain_ops.document_control_exceptions
                   SET status=:status, updated_at=NOW()
                 WHERE id=:id AND tenant_id=:tid
            """),
            {"status": target, "id": case_id, "tid": self.tenant_id},
        )
        self._audit(case_id, "status_changed", current, target, actor, reason)
        self.db.commit()
        return {"id": case_id, "status": target}

    def _lock(self, case_id: str) -> Any:
        row = self.db.execute(
            text("""
                SELECT id, status, assigned_user FROM domain_ops.document_control_exceptions
                 WHERE id=:id AND tenant_id=:tid FOR UPDATE
            """),
            {"id": case_id, "tid": self.tenant_id},
        ).mappings().first()
        if row is None:
            raise LookupError("Ausnahmefall nicht gefunden")
        return row

    def _audit(self, case_id: str, action: str, old_value: str | None, new_value: str | None, actor: str, reason: str) -> None:
        self.db.execute(
            text("""
                INSERT INTO domain_ops.document_control_audit
                    (id, tenant_id, case_id, action, old_value, new_value, actor, reason)
                VALUES (:id,:tid,:case_id,:action,:old_value,:new_value,:actor,:reason)
            """),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "case_id": case_id,
                "action": action,
                "old_value": old_value,
                "new_value": new_value,
                "actor": actor,
                "reason": reason,
            },
        )
