"""Idempotent tank-system intake, validation and delivery-note handover."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


class TankAdapterError(ValueError):
    pass


class TankAdapterService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    @staticmethod
    def _canonical(payload: dict[str, Any]) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)

    def ingest(
        self, adapter_key: str, external_id: str, payload: dict[str, Any], *, actor: str
    ) -> dict[str, Any]:
        if not adapter_key or not external_id:
            raise TankAdapterError("Adapter und External-ID sind erforderlich")
        canonical = self._canonical(payload)
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        intake_id = str(uuid7())
        row = (
            self.db.execute(
                text("""
          INSERT INTO domain_ops.tank_adapter_intake
            (id,tenant_id,adapter_key,external_id,payload,payload_hash,status)
          VALUES (:id,:tid,:adapter_key,:external_id,CAST(:payload AS jsonb),:payload_hash,'received')
          ON CONFLICT (tenant_id,adapter_key,external_id) DO NOTHING RETURNING id,status,payload_hash
        """),
                {
                    "id": intake_id,
                    "tid": self.tenant_id,
                    "adapter_key": adapter_key,
                    "external_id": external_id,
                    "payload": canonical,
                    "payload_hash": digest,
                },
            )
            .mappings()
            .first()
        )
        if row is None:
            existing = (
                self.db.execute(
                    text(
                        "SELECT id,status,payload_hash FROM domain_ops.tank_adapter_intake WHERE tenant_id=:tid AND adapter_key=:adapter_key AND external_id=:external_id"
                    ),
                    {
                        "tid": self.tenant_id,
                        "adapter_key": adapter_key,
                        "external_id": external_id,
                    },
                )
                .mappings()
                .one()
            )
            if existing["payload_hash"] != digest:
                raise TankAdapterError(
                    "External-ID wurde bereits mit abweichendem Payload verwendet"
                )
            return {
                "id": str(existing["id"]),
                "status": existing["status"],
                "idempotent": True,
            }
        self._audit(intake_id, "ingested", actor, "Adaptereingang", digest)
        self.db.commit()
        return {
            "id": intake_id,
            "status": "received",
            "payload_hash": digest,
            "idempotent": False,
        }

    def validate(self, intake_id: str, *, actor: str, reason: str) -> dict[str, Any]:
        item = self._lock(intake_id)
        payload = self._payload(item["payload"])
        errors: list[str] = []
        if not payload.get("kennzeichen"):
            errors.append("Kennzeichen fehlt")
        if not payload.get("artikel"):
            errors.append("Artikel fehlt")
        try:
            if float(payload.get("menge", 0)) <= 0:
                errors.append("Menge muss groesser null sein")
        except (TypeError, ValueError):
            errors.append("Menge ist ungueltig")
        try:
            datetime.fromisoformat(
                str(payload.get("zeitstempel", "")).replace("Z", "+00:00")
            )
        except ValueError:
            errors.append("Zeitstempel ist ungueltig")
        rule = {
            "create_delivery_note": bool(
                payload.get("billable") and payload.get("customer_id")
            ),
            "reason": "billable_customer"
            if payload.get("billable") and payload.get("customer_id")
            else "internal_consumption",
        }
        status = "error" if errors else "validated"
        self.db.execute(
            text(
                "UPDATE domain_ops.tank_adapter_intake SET status=:status,validation_errors=CAST(:errors AS jsonb),rule_result=CAST(:rule AS jsonb),updated_at=NOW() WHERE id=:id AND tenant_id=:tid"
            ),
            {
                "status": status,
                "errors": json.dumps(errors),
                "rule": json.dumps(rule),
                "id": intake_id,
                "tid": self.tenant_id,
            },
        )
        self._audit(
            intake_id,
            "validation_failed" if errors else "validated",
            actor,
            reason,
            item["payload_hash"],
        )
        self.db.commit()
        return {
            "id": intake_id,
            "status": status,
            "validation_errors": errors,
            "rule_result": rule,
        }

    def process(self, intake_id: str, *, actor: str, reason: str) -> dict[str, Any]:
        item = self._lock(intake_id)
        if item["status"] == "processed":
            return {
                "id": intake_id,
                "status": "processed",
                "zapfung_id": item["zapfung_id"],
                "delivery_handover_id": item["delivery_handover_id"],
                "idempotent": True,
            }
        if item["status"] != "validated":
            raise TankAdapterError(
                "Nur validierte Eingaenge koennen verarbeitet werden"
            )
        payload = self._payload(item["payload"])
        rule = self._payload(item["rule_result"])
        zapfung_id = str(uuid7())
        self.db.execute(
            text("""
          INSERT INTO domain_ops.ops_zapfungen
            (id,tenant_id,kennzeichen,fahrzeug_id,fahrer,fahrer_id,artikel,menge,kilometer_stand,zapfsaeule,preis_liter,gesamtpreis,zeitstempel,notiz,created_by)
          VALUES (:id,:tid,:kennzeichen,:fahrzeug_id,:fahrer,:fahrer_id,:artikel,:menge,:kilometer_stand,:zapfsaeule,:preis_liter,:gesamtpreis,:zeitstempel,:notiz,:actor)
        """),
            {
                "id": zapfung_id,
                "tid": self.tenant_id,
                "actor": actor,
                **{
                    key: payload.get(key)
                    for key in (
                        "kennzeichen",
                        "fahrzeug_id",
                        "fahrer",
                        "fahrer_id",
                        "artikel",
                        "menge",
                        "kilometer_stand",
                        "zapfsaeule",
                        "preis_liter",
                        "gesamtpreis",
                        "zeitstempel",
                        "notiz",
                    )
                },
            },
        )
        handover_id = None
        if rule.get("create_delivery_note"):
            handover_id = str(uuid7())
            out_payload = {
                "source_type": "tank_intake",
                "source_ref": intake_id,
                "customer_id": payload.get("customer_id"),
                "article": payload.get("artikel"),
                "quantity": payload.get("menge"),
                "unit": "l",
                "occurred_at": payload.get("zeitstempel"),
                "source_route": f"/tankstelle/adapter-inbox?focus={intake_id}",
            }
            self.db.execute(
                text("""
              INSERT INTO domain_ops.tank_delivery_note_outbox
                (id,tenant_id,intake_id,idempotency_key,payload)
              VALUES (:id,:tid,:intake_id,:key,CAST(:payload AS jsonb))
              ON CONFLICT (tenant_id,idempotency_key) DO NOTHING
            """),
                {
                    "id": handover_id,
                    "tid": self.tenant_id,
                    "intake_id": intake_id,
                    "key": f"tank-delivery-note:{intake_id}",
                    "payload": json.dumps(out_payload),
                },
            )
        self.db.execute(
            text(
                "UPDATE domain_ops.tank_adapter_intake SET status='processed',zapfung_id=:zapfung_id,delivery_handover_id=:handover_id,processed_at=NOW(),updated_at=NOW() WHERE id=:id AND tenant_id=:tid"
            ),
            {
                "zapfung_id": zapfung_id,
                "handover_id": handover_id,
                "id": intake_id,
                "tid": self.tenant_id,
            },
        )
        self._audit(intake_id, "processed", actor, reason, item["payload_hash"])
        self.db.commit()
        return {
            "id": intake_id,
            "status": "processed",
            "zapfung_id": zapfung_id,
            "delivery_handover_id": handover_id,
            "idempotent": False,
        }

    def retry(
        self,
        intake_id: str,
        corrected_payload: dict[str, Any] | None,
        *,
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        item = self._lock(intake_id)
        if item["status"] != "error":
            raise TankAdapterError("Nur Fehlerdatensaetze koennen wiederholt werden")
        payload = corrected_payload or self._payload(item["payload"])
        canonical = self._canonical(payload)
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        self.db.execute(
            text(
                "UPDATE domain_ops.tank_adapter_intake SET payload=CAST(:payload AS jsonb),payload_hash=:digest,status='received',validation_errors='[]'::jsonb,retry_count=retry_count+1,updated_at=NOW() WHERE id=:id AND tenant_id=:tid"
            ),
            {
                "payload": canonical,
                "digest": digest,
                "id": intake_id,
                "tid": self.tenant_id,
            },
        )
        self._audit(intake_id, "retried", actor, reason, digest)
        self.db.commit()
        return {"id": intake_id, "status": "received", "payload_hash": digest}

    def list_page(
        self, *, page: int = 1, page_size: int = 50, status: str | None = None
    ) -> dict[str, Any]:
        where = ["tenant_id=:tid"]
        params: dict[str, Any] = {"tid": self.tenant_id}
        if status:
            where.append("status=:status")
            params["status"] = status
        sql = " AND ".join(where)
        total = self.db.execute(
            text(f"SELECT COUNT(*) FROM domain_ops.tank_adapter_intake WHERE {sql}"),
            params,
        ).scalar_one()
        params.update(limit=page_size, offset=(page - 1) * page_size)
        rows = (
            self.db.execute(
                text(
                    f"SELECT id,adapter_key,external_id,payload_hash,status,validation_errors,rule_result,zapfung_id,delivery_handover_id,retry_count,received_at,processed_at,updated_at FROM domain_ops.tank_adapter_intake WHERE {sql} ORDER BY received_at DESC LIMIT :limit OFFSET :offset"
                ),
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
                text(
                    "SELECT COUNT(*) FILTER (WHERE status='received') received,COUNT(*) FILTER (WHERE status='validated') validated,COUNT(*) FILTER (WHERE status='error') error,COUNT(*) FILTER (WHERE status='processed') processed,COUNT(*) FILTER (WHERE delivery_handover_id IS NOT NULL) delivery_handover FROM domain_ops.tank_adapter_intake WHERE tenant_id=:tid"
                ),
                {"tid": self.tenant_id},
            )
            .mappings()
            .one()
        )
        return {key: int(row[key] or 0) for key in row.keys()}

    def _lock(self, intake_id: str) -> dict[str, Any]:
        row = (
            self.db.execute(
                text(
                    "SELECT id,status,payload,payload_hash,rule_result,zapfung_id,delivery_handover_id FROM domain_ops.tank_adapter_intake WHERE id=:id AND tenant_id=:tid FOR UPDATE"
                ),
                {"id": intake_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            raise LookupError("Tankanlagen-Eingang nicht gefunden")
        return dict(row)

    @staticmethod
    def _payload(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        return {}

    def _audit(
        self,
        intake_id: str,
        action: str,
        actor: str,
        reason: str,
        payload_hash: str | None,
    ) -> None:
        self.db.execute(
            text(
                "INSERT INTO domain_ops.tank_adapter_audit (id,tenant_id,intake_id,action,actor,reason,payload_hash) VALUES (:id,:tid,:intake_id,:action,:actor,:reason,:payload_hash)"
            ),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "intake_id": intake_id,
                "action": action,
                "actor": actor,
                "reason": reason,
                "payload_hash": payload_hash,
            },
        )
