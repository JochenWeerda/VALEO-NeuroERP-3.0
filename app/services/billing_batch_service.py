"""Billing-batch orchestration over canonical invoice and self-billing sources."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

BATCH_TYPES = {
    "sales_invoice",
    "purchase_invoice",
    "self_billing_sales",
    "self_billing_purchase",
}


class BillingBatchError(ValueError):
    pass


class BillingBatchService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def create(self, payload: dict[str, Any], *, actor: str) -> dict[str, Any]:
        if payload.get("batch_type") not in BATCH_TYPES:
            raise BillingBatchError("Unbekannter Rechnungstapeltyp")
        lines = payload.get("lines") or []
        if not lines:
            raise BillingBatchError("Rechnungstapel enthaelt keine Zeilen")
        batch_id = str(uuid7())
        number = payload.get("batch_number") or f"RB-{batch_id[:8].upper()}"
        total = sum(Decimal(str(line.get("amount", 0))) for line in lines)
        self.db.execute(
            text("""
            INSERT INTO domain_finance.billing_batches
              (id,tenant_id,batch_number,batch_type,status,description,maker,currency,total_lines,total_amount)
            VALUES (:id,:tid,:number,:kind,'draft',:description,:maker,:currency,:total_lines,:total_amount)
        """),
            {
                "id": batch_id,
                "tid": self.tenant_id,
                "number": number,
                "kind": payload["batch_type"],
                "description": payload.get("description"),
                "maker": actor,
                "currency": payload.get("currency") or "EUR",
                "total_lines": len(lines),
                "total_amount": total,
            },
        )
        for line in lines:
            line_id = str(uuid7())
            key = (
                line.get("idempotency_key")
                or f"{payload['batch_type']}:{line['source_type']}:{line['source_ref']}"
            )
            self.db.execute(
                text("""
                INSERT INTO domain_finance.billing_batch_lines
                  (id,tenant_id,batch_id,source_type,source_ref,source_number,source_route,evidence_route,
                   amount,status,validation_error,idempotency_key)
                VALUES (:id,:tid,:batch_id,:source_type,:source_ref,:source_number,:source_route,:evidence_route,
                        :amount,'pending',:validation_error,:key)
            """),
                {
                    "id": line_id,
                    "tid": self.tenant_id,
                    "batch_id": batch_id,
                    "source_type": line["source_type"],
                    "source_ref": line["source_ref"],
                    "source_number": line.get("source_number") or line["source_ref"],
                    "source_route": line.get("source_route"),
                    "evidence_route": line.get("evidence_route"),
                    "amount": line.get("amount", 0),
                    "validation_error": line.get("validation_error"),
                    "key": key,
                },
            )
        self._audit(
            batch_id,
            None,
            "created",
            None,
            "draft",
            actor,
            payload.get("reason") or "Stapel angelegt",
        )
        self.db.commit()
        return {
            "id": batch_id,
            "batch_number": number,
            "status": "draft",
            "total_lines": len(lines),
            "total_amount": float(total),
        }

    def list_page(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        batch_type: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        where, params = ["tenant_id=:tid"], {"tid": self.tenant_id}
        for key, value in (("batch_type", batch_type), ("status", status)):
            if value:
                where.append(f"{key}=:{key}")
                params[key] = value
        where_sql = " AND ".join(where)
        total = self.db.execute(
            text(
                f"SELECT COUNT(*) FROM domain_finance.billing_batches WHERE {where_sql}"  # nosec S608 - reviewed-safe: WHERE-Fragmente aus festen Literalen, Werte nur gebunden
            ),
            params,
        ).scalar_one()
        params.update(limit=page_size, offset=(page - 1) * page_size)
        rows = (
            self.db.execute(
                text(f"""
            SELECT id,batch_number,batch_type,status,description,maker,checker,currency,total_lines,
                   processed_lines,failed_lines,total_amount,created_at,updated_at
              FROM domain_finance.billing_batches WHERE {where_sql}
             ORDER BY created_at DESC LIMIT :limit OFFSET :offset
        """),  # nosec S608 - reviewed-safe: WHERE-Fragmente aus festen Literalen, Werte nur gebunden
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

    def list_lines(
        self,
        *,
        status: str | None = None,
        batch_id: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        where, params = ["tenant_id=:tid"], {"tid": self.tenant_id, "limit": limit}
        if status:
            where.append("status=:status")
            params["status"] = status
        if batch_id:
            where.append("batch_id=:batch_id")
            params["batch_id"] = batch_id
        rows = (
            self.db.execute(
                text(f"""
            SELECT id,batch_id,source_type,source_ref,source_number,source_route,evidence_route,amount,
                   status,validation_error,retry_count,processed_at,created_at
              FROM domain_finance.billing_batch_lines WHERE {" AND ".join(where)}
             ORDER BY created_at DESC LIMIT :limit
        """),  # nosec S608 - reviewed-safe: WHERE-Fragmente aus festen Literalen, Werte nur gebunden
                params,
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def summary(self) -> dict[str, int]:
        row = (
            self.db.execute(
                text("""
            SELECT COUNT(*) FILTER (WHERE status='draft') AS draft,
                   COUNT(*) FILTER (WHERE status='validated') AS validated,
                   COUNT(*) FILTER (WHERE status='released') AS released,
                   COUNT(*) FILTER (WHERE status='running') AS running,
                   COUNT(*) FILTER (WHERE status='partial_failed') AS partial_failed,
                   COALESCE(SUM(failed_lines),0) AS failed_lines
              FROM domain_finance.billing_batches WHERE tenant_id=:tid
        """),
                {"tid": self.tenant_id},
            )
            .mappings()
            .one()
        )
        return {key: int(row[key] or 0) for key in row.keys()}

    def validate(self, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
        batch = self._lock(batch_id)
        if batch["status"] not in {"draft", "validated"}:
            raise BillingBatchError("Nur Entwurfsstapel koennen geprueft werden")
        self.db.execute(
            text("""
            UPDATE domain_finance.billing_batch_lines SET status=CASE WHEN validation_error IS NULL THEN 'pending' ELSE 'failed' END
             WHERE batch_id=:id AND tenant_id=:tid
        """),
            {"id": batch_id, "tid": self.tenant_id},
        )
        failed = self.db.execute(
            text("""
            SELECT COUNT(*) FROM domain_finance.billing_batch_lines WHERE batch_id=:id AND tenant_id=:tid AND status='failed'
        """),
            {"id": batch_id, "tid": self.tenant_id},
        ).scalar_one()
        self.db.execute(
            text("""
            UPDATE domain_finance.billing_batches SET status='validated',failed_lines=:failed,updated_at=NOW()
             WHERE id=:id AND tenant_id=:tid
        """),
            {"failed": failed, "id": batch_id, "tid": self.tenant_id},
        )
        self._audit(
            batch_id, None, "validated", batch["status"], "validated", actor, reason
        )
        self.db.commit()
        return {"id": batch_id, "status": "validated", "failed_lines": int(failed)}

    def release(self, batch_id: str, *, actor: str, reason: str) -> dict[str, str]:
        batch = self._lock(batch_id)
        if batch["status"] != "validated":
            raise BillingBatchError("Stapel ist nicht geprueft")
        if actor == batch["maker"]:
            raise BillingBatchError("Vier-Augen-Prinzip: Freigeber muss abweichen")
        if int(batch["failed_lines"] or 0) > 0:
            raise BillingBatchError("Fehlerzeilen muessen vor Freigabe geklaert werden")
        self.db.execute(
            text(
                "UPDATE domain_finance.billing_batches SET status='released',checker=:actor,updated_at=NOW() WHERE id=:id AND tenant_id=:tid"
            ),
            {"actor": actor, "id": batch_id, "tid": self.tenant_id},
        )
        self._audit(batch_id, None, "released", "validated", "released", actor, reason)
        self.db.commit()
        return {"id": batch_id, "status": "released"}

    def execute(self, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
        batch = self._lock(batch_id)
        if batch["status"] != "released":
            raise BillingBatchError("Stapel ist nicht freigegeben")
        self.db.execute(
            text("""
            UPDATE domain_finance.billing_batch_lines SET status='processed',processed_at=NOW()
             WHERE batch_id=:id AND tenant_id=:tid AND status='pending'
        """),
            {"id": batch_id, "tid": self.tenant_id},
        )
        counts = (
            self.db.execute(
                text("""
            SELECT COUNT(*) FILTER (WHERE status='processed') AS processed,
                   COUNT(*) FILTER (WHERE status='failed') AS failed
              FROM domain_finance.billing_batch_lines WHERE batch_id=:id AND tenant_id=:tid
        """),
                {"id": batch_id, "tid": self.tenant_id},
            )
            .mappings()
            .one()
        )
        target = "partial_failed" if counts["failed"] else "completed"
        self.db.execute(
            text("""
            UPDATE domain_finance.billing_batches SET status=:status,processed_lines=:processed,
                   failed_lines=:failed,updated_at=NOW() WHERE id=:id AND tenant_id=:tid
        """),
            {
                "status": target,
                "processed": counts["processed"],
                "failed": counts["failed"],
                "id": batch_id,
                "tid": self.tenant_id,
            },
        )
        self._audit(batch_id, None, "executed", "released", target, actor, reason)
        self.db.commit()
        return {
            "id": batch_id,
            "status": target,
            "processed_lines": int(counts["processed"]),
            "failed_lines": int(counts["failed"]),
        }

    def retry(self, line_id: str, *, actor: str, reason: str) -> dict[str, str]:
        line = (
            self.db.execute(
                text("""
            SELECT id,batch_id,status FROM domain_finance.billing_batch_lines WHERE id=:id AND tenant_id=:tid FOR UPDATE
        """),
                {"id": line_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if line is None:
            raise LookupError("Stapelzeile nicht gefunden")
        if line["status"] != "failed":
            raise BillingBatchError("Nur Fehlerzeilen koennen wiederholt werden")
        self.db.execute(
            text("""
            UPDATE domain_finance.billing_batch_lines SET status='pending',validation_error=NULL,
                   retry_count=retry_count+1,processed_at=NULL WHERE id=:id AND tenant_id=:tid
        """),
            {"id": line_id, "tid": self.tenant_id},
        )
        self.db.execute(
            text("""
                UPDATE domain_finance.billing_batches
                   SET failed_lines=(SELECT COUNT(*) FROM domain_finance.billing_batch_lines
                                      WHERE batch_id=:batch_id AND tenant_id=:tid AND status='failed'),
                       updated_at=NOW()
                 WHERE id=:batch_id AND tenant_id=:tid
            """),
            {"batch_id": line["batch_id"], "tid": self.tenant_id},
        )
        self._audit(
            line["batch_id"], line_id, "retried", "failed", "pending", actor, reason
        )
        self.db.commit()
        return {"id": line_id, "status": "pending"}

    def _lock(self, batch_id: str) -> Any:
        row = (
            self.db.execute(
                text(
                    "SELECT id,status,maker,failed_lines FROM domain_finance.billing_batches WHERE id=:id AND tenant_id=:tid FOR UPDATE"
                ),
                {"id": batch_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            raise LookupError("Rechnungstapel nicht gefunden")
        return row

    def _audit(
        self,
        batch_id: str,
        line_id: str | None,
        action: str,
        old: str | None,
        new: str | None,
        actor: str,
        reason: str,
    ) -> None:
        self.db.execute(
            text("""
            INSERT INTO domain_finance.billing_batch_audit
              (id,tenant_id,batch_id,line_id,action,old_value,new_value,actor,reason)
            VALUES (:id,:tid,:batch_id,:line_id,:action,:old,:new,:actor,:reason)
        """),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "batch_id": batch_id,
                "line_id": line_id,
                "action": action,
                "old": old,
                "new": new,
                "actor": actor,
                "reason": reason,
            },
        )
