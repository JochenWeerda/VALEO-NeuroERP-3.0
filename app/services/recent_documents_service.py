"""Tenant- and user-scoped recent document projection."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

ROLE_BY_SCREEN_PREFIX = {
    "crm/": "CRM_LESEN",
    "einkauf/": "EINKAUF_LESEN",
    "sales/": "SALES_LESEN",
    "verkauf/": "SALES_LESEN",
    "finance/": "FINANCE_LESEN",
    "lager/": "LAGER_LESEN",
    "inventory/": "LAGER_LESEN",
    "agrar/": "HARVEST_LESEN",
    "futtermittel/": "FUTTERMITTEL_LESEN",
    "qualitaet/": "QUALITAET_LESEN",
}
PRIVILEGED_ROLES = frozenset({"admin", "manager"})


class RecentDocumentError(ValueError):
    pass


def required_role(screen_id: str) -> str:
    for prefix, role in ROLE_BY_SCREEN_PREFIX.items():
        if screen_id.startswith(prefix):
            return role
    raise RecentDocumentError("Dokumentfamilie ist nicht freigegeben")


class RecentDocumentsService:
    def __init__(
        self, db: Session, tenant_id: str, user_id: str, roles: list[str]
    ) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.roles = set(roles)
        if not user_id:
            raise RecentDocumentError("Authentifizierter Benutzer fehlt")

    def _authorize(self, role: str) -> None:
        if role not in self.roles and not self.roles.intersection(PRIVILEGED_ROLES):
            raise RecentDocumentError("Dokumentfamilie ist nicht berechtigt")

    def touch(self, payload: dict[str, Any]) -> dict[str, Any]:
        screen_id = str(payload.get("screen_id") or "").strip()
        role = required_role(screen_id)
        self._authorize(role)
        route = str(payload.get("route") or "").strip()
        if not route.startswith("/") or route.startswith("//") or "://" in route:
            raise RecentDocumentError("Dokumentroute muss intern sein")
        for field in ("document_id", "document_type", "document_number", "title"):
            if not str(payload.get(field) or "").strip():
                raise RecentDocumentError(f"Pflichtfeld fehlt: {field}")
        params = {
            "id": str(uuid7()),
            "tid": self.tenant_id,
            "uid": self.user_id,
            "screen_id": screen_id,
            "document_id": str(payload["document_id"]),
            "document_type": str(payload["document_type"])[:120],
            "document_number": str(payload["document_number"])[:160],
            "partner_id": payload.get("partner_id"),
            "partner_name": str(payload.get("partner_name") or "")[:240] or None,
            "title": str(payload["title"])[:240],
            "route": route[:600],
            "role": role,
        }
        row = (
            self.db.execute(
                text("""
                  INSERT INTO domain_ops.recent_documents
                    (id,tenant_id,user_id,screen_id,document_id,document_type,
                     document_number,partner_id,partner_name,title,route,required_role,
                     opened_at,expires_at)
                  VALUES (:id,:tid,:uid,:screen_id,:document_id,:document_type,
                          :document_number,:partner_id,:partner_name,:title,:route,:role,
                          NOW(),NOW()+INTERVAL '90 days')
                  ON CONFLICT (tenant_id,user_id,screen_id,document_id) DO UPDATE SET
                    document_type=EXCLUDED.document_type,
                    document_number=EXCLUDED.document_number,
                    partner_id=EXCLUDED.partner_id,partner_name=EXCLUDED.partner_name,
                    title=EXCLUDED.title,route=EXCLUDED.route,
                    required_role=EXCLUDED.required_role,opened_at=NOW(),
                    expires_at=NOW()+INTERVAL '90 days'
                  RETURNING id,screen_id,document_id,document_type,document_number,
                            partner_id,partner_name,title,route,opened_at
                """),
                params,
            )
            .mappings()
            .one()
        )
        self.db.execute(
            text("""
              DELETE FROM domain_ops.recent_documents
               WHERE tenant_id=:tid AND user_id=:uid
                 AND (expires_at < NOW() OR id NOT IN (
                    SELECT id FROM domain_ops.recent_documents
                     WHERE tenant_id=:tid AND user_id=:uid
                     ORDER BY opened_at DESC LIMIT 200))
            """),
            {"tid": self.tenant_id, "uid": self.user_id},
        )
        self.db.commit()
        return dict(row)

    def list(
        self, *, page: int = 1, page_size: int = 50, document_type: str | None = None
    ) -> dict[str, Any]:
        allowed_roles = sorted(self.roles)
        privileged = bool(self.roles.intersection(PRIVILEGED_ROLES))
        where = [
            "tenant_id=:tid",
            "user_id=:uid",
            "expires_at>=NOW()",
            "(:privileged OR required_role = ANY(:roles))",
        ]
        params: dict[str, Any] = {
            "tid": self.tenant_id,
            "uid": self.user_id,
            "privileged": privileged,
            "roles": allowed_roles,
        }
        if document_type:
            where.append("document_type=:document_type")
            params["document_type"] = document_type
        where_sql = " AND ".join(where)
        total = self.db.execute(
            text(f"SELECT COUNT(*) FROM domain_ops.recent_documents WHERE {where_sql}"),  # nosec S608 — Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)
            params,
        ).scalar_one()
        params.update(limit=page_size, offset=(page - 1) * page_size)
        rows = (
            self.db.execute(
                text(f"""
                  SELECT id,screen_id,document_id,document_type,document_number,
                         partner_id,partner_name,title,route,opened_at
                    FROM domain_ops.recent_documents WHERE {where_sql}
                   ORDER BY opened_at DESC LIMIT :limit OFFSET :offset
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

    def remove(self, document_id: str | None = None) -> int:
        suffix = " AND id=:id" if document_id else ""
        params = {"tid": self.tenant_id, "uid": self.user_id, "id": document_id}
        result = self.db.execute(
            text(
                f"DELETE FROM domain_ops.recent_documents WHERE tenant_id=:tid AND user_id=:uid{suffix}"
            ),
            params,
        )
        self.db.commit()
        return int(result.rowcount or 0)
