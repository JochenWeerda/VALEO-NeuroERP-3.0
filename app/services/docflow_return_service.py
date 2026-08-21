"""Document-return worklist on top of canonical Docflow headers and artifacts."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

_SHIPPING_TRANSITIONS = {
    "not_sent": {"sent", "failed"},
    "failed": {"sent"},
    "sent": {"delivered", "failed"},
    "delivered": set(),
}
_RETURN_TRANSITIONS = {
    "expected": {"received", "waived"},
    "received": {"verified", "rejected"},
    "rejected": {"received", "waived"},
    "verified": {"closed"},
    "waived": {"closed"},
    "closed": set(),
}
_SORT_COLUMNS = {
    "created_at": "r.created_at",
    "due_at": "r.due_at",
    "assigned_user": "r.assigned_user",
    "shipping_status": "r.shipping_status",
    "return_status": "r.return_status",
    "doc_number": "h.doc_number",
}


def valid_return_transition(kind: str, current: str, target: str) -> bool:
    transitions = _SHIPPING_TRANSITIONS if kind == "shipping" else _RETURN_TRANSITIONS if kind == "return" else {}
    return target in transitions.get(current, set())


class DocumentReturnError(ValueError):
    pass


class DocflowReturnService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def create_case(self, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
        header = self.db.execute(
            text("SELECT id, doc_number FROM domain_docflow.document_headers WHERE tenant_id=:tid AND (id=:doc OR doc_number=:doc) AND deleted_at IS NULL LIMIT 1"),
            {"tid": self.tenant_id, "doc": payload["document_ref"]},
        ).mappings().first()
        if header is None:
            raise DocumentReturnError("Ursprungsdokument nicht gefunden")
        artifact_id = payload.get("artifact_id")
        if artifact_id:
            artifact_exists = self.db.execute(
                text("""
                    SELECT 1 FROM domain_docflow.document_artifacts
                     WHERE id=:artifact AND header_id=:header AND tenant_id=:tid
                """),
                {"artifact": artifact_id, "header": str(header["id"]), "tid": self.tenant_id},
            ).scalar_one_or_none()
            if artifact_exists is None:
                raise DocumentReturnError("Artefakt gehoert nicht zum Mandanten und Ursprungsdokument")
        case_id = str(uuid7())
        self.db.execute(
            text("""
                INSERT INTO domain_docflow.document_return_cases
                    (id, tenant_id, header_id, artifact_id, subject_type, subject_ref,
                     contact_ref, assigned_user, tags, due_at, source_route)
                VALUES (:id,:tid,:header,:artifact,:subject_type,:subject_ref,:contact,
                        :assigned_user,CAST(:tags AS jsonb),:due_at,:source_route)
            """),
            {
                "id": case_id, "tid": self.tenant_id, "header": str(header["id"]),
                "artifact": artifact_id, "subject_type": payload.get("subject_type", "process"),
                "subject_ref": payload.get("subject_ref"), "contact": payload.get("contact_ref"),
                "assigned_user": payload.get("assigned_user") or actor,
                "tags": json.dumps(payload.get("tags") or []), "due_at": payload.get("due_at"),
                "source_route": payload.get("source_route"),
            },
        )
        self._audit(case_id, "created", None, "expected", actor, payload.get("reason") or "Ruecklauf angelegt")
        self.db.commit()
        return {"id": case_id, "doc_number": header["doc_number"], "shipping_status": "not_sent", "return_status": "expected"}

    def transition(self, case_id: str, *, kind: str, target: str, actor: str, reason: str) -> dict[str, Any]:
        row = self.db.execute(
            text("SELECT id, shipping_status, return_status FROM domain_docflow.document_return_cases WHERE id=:id AND tenant_id=:tid FOR UPDATE"),
            {"id": case_id, "tid": self.tenant_id},
        ).mappings().first()
        if row is None:
            raise LookupError("Ruecklauffall nicht gefunden")
        field = "shipping_status" if kind == "shipping" else "return_status" if kind == "return" else None
        if field is None:
            raise DocumentReturnError("kind muss shipping oder return sein")
        current = str(row[field])
        if not valid_return_transition(kind, current, target):
            raise DocumentReturnError(f"Unzulaessiger Statuswechsel {current} -> {target}")
        timestamp = ", sent_at=NOW()" if kind == "shipping" and target == "sent" else ", returned_at=NOW()" if kind == "return" and target == "received" else ""
        self.db.execute(
            text(f"UPDATE domain_docflow.document_return_cases SET {field}=:target, updated_at=NOW(){timestamp} WHERE id=:id AND tenant_id=:tid"),  # nosec B608 -- field and timestamp are closed constants
            {"target": target, "id": case_id, "tid": self.tenant_id},
        )
        self._audit(case_id, f"{kind}_status", current, target, actor, reason)
        self.db.commit()
        return {"id": case_id, field: target}

    def _audit(self, case_id: str, action: str, old: str | None, new: str | None, actor: str, reason: str) -> None:
        self.db.execute(
            text("INSERT INTO domain_docflow.document_return_audit (id,tenant_id,case_id,action,old_value,new_value,actor,reason) VALUES (:id,:tid,:case,:action,:old,:new,:actor,:reason)"),
            {"id": str(uuid7()), "tid": self.tenant_id, "case": case_id, "action": action, "old": old, "new": new, "actor": actor[:120], "reason": reason[:500]},
        )

    def list_page(self, *, page: int = 1, page_size: int = 25, assigned_user: str | None = None,
                  contact_ref: str | None = None, subject_type: str | None = None,
                  date_from: str | None = None, date_to: str | None = None, status: str | None = None,
                  q: str | None = None, sort: str = "created_at", sort_dir: str = "desc") -> dict[str, Any]:
        filters = ["r.tenant_id=:tid"]
        params: dict[str, Any] = {"tid": self.tenant_id, "limit": page_size, "offset": (page - 1) * page_size}
        for value, clause, key in [
            (assigned_user, "r.assigned_user=:assigned_user", "assigned_user"),
            (contact_ref, "r.contact_ref=:contact_ref", "contact_ref"),
            (subject_type, "r.subject_type=:subject_type", "subject_type"),
        ]:
            if value:
                filters.append(clause)
                params[key] = value
        if date_from:
            filters.append("r.created_at >= CAST(:date_from AS date)")
            params["date_from"] = date_from
        if date_to:
            filters.append("r.created_at < CAST(:date_to AS date) + INTERVAL '1 day'")
            params["date_to"] = date_to
        if status:
            filters.append("(r.return_status=:status OR r.shipping_status=:status)")
            params["status"] = status
        if q:
            filters.append("(h.doc_number ILIKE :q OR COALESCE(r.subject_ref,'') ILIKE :q OR COALESCE(r.contact_ref,'') ILIKE :q)")
            params["q"] = f"%{q}%"
        where = " AND ".join(filters)
        order = _SORT_COLUMNS.get(sort, "r.created_at")
        direction = "ASC" if sort_dir == "asc" else "DESC"
        total = self.db.execute(text(f"SELECT COUNT(*) FROM domain_docflow.document_return_cases r JOIN domain_docflow.document_headers h ON h.id=r.header_id AND h.tenant_id=r.tenant_id WHERE {where}"), params).scalar_one()  # nosec B608
        rows = self.db.execute(text(f"""
            SELECT r.id,h.doc_number,r.subject_type,r.subject_ref,r.contact_ref,r.assigned_user,
                   r.tags,r.shipping_status,r.return_status,r.due_at,r.sent_at,r.returned_at,
                   r.source_route,r.created_at,a.file_name,a.storage_key
              FROM domain_docflow.document_return_cases r
              JOIN domain_docflow.document_headers h ON h.id=r.header_id AND h.tenant_id=r.tenant_id
              LEFT JOIN domain_docflow.document_artifacts a ON a.id=r.artifact_id AND a.tenant_id=r.tenant_id
             WHERE {where} ORDER BY {order} {direction},r.id DESC LIMIT :limit OFFSET :offset
        """), params).mappings().all()  # nosec B608
        return {"items": [dict(row) for row in rows], "total": int(total), "page": page, "page_size": page_size}

    def summary(self) -> dict[str, int]:
        row = self.db.execute(
            text("""
                SELECT COUNT(*) AS total,
                       COUNT(*) FILTER (WHERE shipping_status='not_sent') AS not_sent,
                       COUNT(*) FILTER (WHERE return_status='expected') AS expected,
                       COUNT(*) FILTER (WHERE return_status='received') AS received,
                       COUNT(*) FILTER (WHERE due_at < NOW() AND return_status NOT IN ('closed','waived')) AS overdue
                  FROM domain_docflow.document_return_cases WHERE tenant_id=:tid
            """),
            {"tid": self.tenant_id},
        ).mappings().one()
        return {key: int(value or 0) for key, value in row.items()}

    def case_evidence(self, case_id: str) -> dict[str, Any]:
        row = self.db.execute(
            text("""
                SELECT r.id,h.doc_number,r.source_route,a.id AS artifact_id,a.file_name,
                       a.artifact_type,a.content_hash_sha256,a.storage_key
                  FROM domain_docflow.document_return_cases r
                  JOIN domain_docflow.document_headers h ON h.id=r.header_id AND h.tenant_id=r.tenant_id
                  LEFT JOIN domain_docflow.document_artifacts a ON a.id=r.artifact_id AND a.tenant_id=r.tenant_id
                 WHERE r.id=:id AND r.tenant_id=:tid
            """),
            {"id": case_id, "tid": self.tenant_id},
        ).mappings().first()
        if row is None:
            raise LookupError("Ruecklauffall nicht gefunden")
        audit = self.db.execute(
            text("""
                SELECT id,action,old_value,new_value,actor,reason,created_at
                  FROM domain_docflow.document_return_audit
                 WHERE case_id=:id AND tenant_id=:tid ORDER BY created_at,id
            """),
            {"id": case_id, "tid": self.tenant_id},
        ).mappings().all()
        return {**dict(row), "preview_available": bool(row.get("storage_key")), "audit": [dict(item) for item in audit]}
