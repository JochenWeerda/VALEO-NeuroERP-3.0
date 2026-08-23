"""Role-scoped ERP mail workspace on top of the canonical IMAP ingest."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


class MailWorkspaceError(ValueError):
    pass


class MailWorkspaceService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def ingest(
        self,
        *,
        message_id: str,
        role_key: str,
        direction: str,
        from_address: str | None,
        to_addresses: list[str],
        subject: str | None,
        body_text: str,
        received_at: datetime | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if not message_id:
            raise MailWorkspaceError("Message-ID ist erforderlich")
        item_id = str(uuid7())
        row = (
            self.db.execute(
                text("""
          INSERT INTO domain_crm.mail_workspace_messages
            (id,tenant_id,role_key,message_id,direction,status,from_address,to_addresses,
             subject,body_text,received_at)
          VALUES (:id,:tid,:role_key,:message_id,:direction,'received',:from_address,
                  CAST(:to_addresses AS jsonb),:subject,:body_text,:received_at)
          ON CONFLICT (tenant_id,message_id) DO NOTHING RETURNING id
        """),
                {
                    "id": item_id,
                    "tid": self.tenant_id,
                    "role_key": role_key,
                    "message_id": message_id,
                    "direction": direction,
                    "from_address": from_address,
                    "to_addresses": json.dumps(to_addresses),
                    "subject": subject,
                    "body_text": body_text,
                    "received_at": received_at or datetime.now(UTC),
                },
            )
            .mappings()
            .first()
        )
        if row is None:
            existing = (
                self.db.execute(
                    text(
                        "SELECT id,status FROM domain_crm.mail_workspace_messages WHERE tenant_id=:tid AND message_id=:message_id"
                    ),
                    {"tid": self.tenant_id, "message_id": message_id},
                )
                .mappings()
                .one()
            )
            return {
                "id": str(existing["id"]),
                "status": existing["status"],
                "idempotent": True,
            }
        for attachment in attachments or []:
            content = attachment.get("content") or b""
            if not isinstance(content, bytes):
                content = bytes(content)
            self.db.execute(
                text("""
              INSERT INTO domain_crm.mail_workspace_attachments
                (id,tenant_id,message_id,filename,mime_type,size_bytes,sha256,content)
              VALUES (:id,:tid,:message_id,:filename,:mime_type,:size_bytes,:sha256,:content)
              ON CONFLICT (tenant_id,message_id,filename,sha256) DO NOTHING
            """),
                {
                    "id": str(uuid7()),
                    "tid": self.tenant_id,
                    "message_id": item_id,
                    "filename": str(attachment.get("filename") or "anlage.bin")[:255],
                    "mime_type": attachment.get("mime_type"),
                    "size_bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "content": content,
                },
            )
        self._audit(
            item_id,
            "ingested",
            "AUTO",
            "IMAP-Ingest",
            self._hash({"message_id": message_id}),
        )
        self.db.commit()
        return {"id": item_id, "status": "received", "idempotent": False}

    def list_page(
        self,
        *,
        allowed_roles: set[str],
        page: int = 1,
        page_size: int = 50,
        status: str | None = None,
    ) -> dict[str, Any]:
        if not allowed_roles:
            raise PermissionError("Kein Rollenpostfach freigegeben")
        params: dict[str, Any] = {"tid": self.tenant_id, "roles": sorted(allowed_roles)}
        where = ["tenant_id=:tid", "role_key = ANY(:roles)"]
        if status:
            where.append("status=:status")
            params["status"] = status
        where_sql = " AND ".join(where)
        total = self.db.execute(
            text(
                f"SELECT COUNT(*) FROM domain_crm.mail_workspace_messages WHERE {where_sql}"
            ),
            params,
        ).scalar_one()
        params.update(limit=page_size, offset=(page - 1) * page_size)
        rows = (
            self.db.execute(
                text(f"""
          SELECT id,role_key,message_id,direction,status,from_address,to_addresses,subject,
                 contact_id,document_type,document_ref,document_route,assigned_to,provider_ref,
                 error_message,received_at,sent_at,created_at,updated_at,
                 (SELECT COUNT(*) FROM domain_crm.mail_workspace_attachments a
                   WHERE a.tenant_id=:tid AND a.message_id=m.id) AS attachment_count
            FROM domain_crm.mail_workspace_messages m WHERE {where_sql}
           ORDER BY COALESCE(received_at,created_at) DESC LIMIT :limit OFFSET :offset
        """),  # nosec S608 — Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
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

    def create_draft(
        self, payload: dict[str, Any], *, role_key: str, actor: str, reason: str
    ) -> dict[str, Any]:
        item_id = str(uuid7())
        message_id = payload.get("message_id") or f"draft-{item_id}@valeo.local"
        recipients = list(payload.get("to_addresses") or [])
        if not recipients or not payload.get("subject"):
            raise MailWorkspaceError("Empfaenger und Betreff sind erforderlich")
        self.db.execute(
            text("""
          INSERT INTO domain_crm.mail_workspace_messages
            (id,tenant_id,role_key,message_id,direction,status,from_address,to_addresses,subject,body_text,contact_id,document_type,document_ref,document_route,assigned_to)
          VALUES (:id,:tid,:role_key,:message_id,'outgoing','draft',:from_address,CAST(:to_addresses AS jsonb),:subject,:body_text,:contact_id,:document_type,:document_ref,:document_route,:actor)
        """),
            {
                "id": item_id,
                "tid": self.tenant_id,
                "role_key": role_key,
                "message_id": message_id,
                "from_address": payload.get("from_address"),
                "to_addresses": json.dumps(recipients),
                "subject": payload["subject"],
                "body_text": payload.get("body_text") or "",
                "contact_id": payload.get("contact_id"),
                "document_type": payload.get("document_type"),
                "document_ref": payload.get("document_ref"),
                "document_route": payload.get("document_route"),
                "actor": actor,
            },
        )
        self._audit(item_id, "drafted", actor, reason, self._hash(payload))
        self.db.commit()
        return {"id": item_id, "status": "draft", "message_id": message_id}

    def list_attachments(
        self, *, allowed_roles: set[str], limit: int = 200
    ) -> list[dict[str, Any]]:
        if not allowed_roles:
            raise PermissionError("Kein Rollenpostfach freigegeben")
        rows = (
            self.db.execute(
                text("""
          SELECT a.id,a.message_id,a.filename,a.mime_type,a.size_bytes,a.sha256,
                 a.transfer_status,a.dms_document_id,a.created_at,m.subject,m.role_key
            FROM domain_crm.mail_workspace_attachments a
            JOIN domain_crm.mail_workspace_messages m ON m.id=a.message_id AND m.tenant_id=a.tenant_id
           WHERE a.tenant_id=:tid AND m.role_key = ANY(:roles)
           ORDER BY a.created_at DESC LIMIT :limit
        """),
                {
                    "tid": self.tenant_id,
                    "roles": sorted(allowed_roles),
                    "limit": min(limit, 500),
                },
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def assign(
        self,
        message_id: str,
        payload: dict[str, Any],
        *,
        allowed_roles: set[str],
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        item = self._lock(message_id, allowed_roles)
        self.db.execute(
            text("""
          UPDATE domain_crm.mail_workspace_messages SET contact_id=:contact_id,document_type=:document_type,
            document_ref=:document_ref,document_route=:document_route,assigned_to=:assigned_to,updated_at=NOW()
           WHERE id=:id AND tenant_id=:tid
        """),
            {
                "id": message_id,
                "tid": self.tenant_id,
                "contact_id": payload.get("contact_id"),
                "document_type": payload.get("document_type"),
                "document_ref": payload.get("document_ref"),
                "document_route": payload.get("document_route"),
                "assigned_to": payload.get("assigned_to") or actor,
            },
        )
        self._audit(message_id, "assigned", actor, reason, self._hash(payload))
        self.db.commit()
        return {"id": message_id, "status": item["status"], **payload}

    def queue_send(
        self, message_id: str, *, allowed_roles: set[str], actor: str, reason: str
    ) -> dict[str, str]:
        item = self._lock(message_id, allowed_roles)
        if item["status"] not in {"draft", "error"}:
            raise MailWorkspaceError(
                "Nur Entwuerfe oder Fehler koennen versendet werden"
            )
        provider_ref = f"mail-outbox:{uuid7()}"
        self.db.execute(
            text("""
          UPDATE domain_crm.mail_workspace_messages SET status='queued',provider_ref=:provider_ref,
            error_message=NULL,updated_at=NOW() WHERE id=:id AND tenant_id=:tid
        """),
            {"provider_ref": provider_ref, "id": message_id, "tid": self.tenant_id},
        )
        self._audit(
            message_id,
            "queued",
            actor,
            reason,
            self._hash({"provider_ref": provider_ref}),
        )
        self.db.commit()
        return {"id": message_id, "status": "queued", "provider_ref": provider_ref}

    def transfer_attachment(
        self, attachment_id: str, *, allowed_roles: set[str], actor: str, reason: str
    ) -> dict[str, str]:
        row = (
            self.db.execute(
                text("""
          SELECT a.id,a.message_id,m.role_key,a.transfer_status,a.sha256,a.dms_document_id FROM domain_crm.mail_workspace_attachments a
          JOIN domain_crm.mail_workspace_messages m ON m.id=a.message_id AND m.tenant_id=a.tenant_id
          WHERE a.id=:id AND a.tenant_id=:tid FOR UPDATE
        """),
                {"id": attachment_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if row is None or row["role_key"] not in allowed_roles:
            raise PermissionError("Anlage nicht freigegeben")
        if row["transfer_status"] == "transferred":
            return {
                "id": attachment_id,
                "status": "transferred",
                "dms_document_id": str(row.get("dms_document_id") or ""),
            }
        document_id = f"mail-attachment:{uuid7()}"
        self.db.execute(
            text(
                "UPDATE domain_crm.mail_workspace_attachments SET transfer_status='transferred',dms_document_id=:document_id,transferred_at=NOW() WHERE id=:id AND tenant_id=:tid"
            ),
            {"document_id": document_id, "id": attachment_id, "tid": self.tenant_id},
        )
        self._audit(
            str(row["message_id"]),
            "attachment_transferred",
            actor,
            reason,
            str(row["sha256"]),
        )
        self.db.commit()
        return {
            "id": attachment_id,
            "status": "transferred",
            "dms_document_id": document_id,
        }

    def _lock(self, message_id: str, allowed_roles: set[str]) -> dict[str, Any]:
        row = (
            self.db.execute(
                text(
                    "SELECT id,status,role_key FROM domain_crm.mail_workspace_messages WHERE id=:id AND tenant_id=:tid FOR UPDATE"
                ),
                {"id": message_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            raise LookupError("Mail nicht gefunden")
        if row["role_key"] not in allowed_roles:
            raise PermissionError("Rollenpostfach-Zugriff verweigert")
        return dict(row)

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()

    def _audit(
        self,
        message_id: str | None,
        action: str,
        actor: str,
        reason: str,
        payload_hash: str | None,
    ) -> None:
        self.db.execute(
            text(
                "INSERT INTO domain_crm.mail_workspace_audit (id,tenant_id,message_id,action,actor,reason,payload_hash) VALUES (:id,:tid,:message_id,:action,:actor,:reason,:payload_hash)"
            ),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "message_id": message_id,
                "action": action,
                "actor": actor,
                "reason": reason,
                "payload_hash": payload_hash,
            },
        )
