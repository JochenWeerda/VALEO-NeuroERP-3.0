"""Versioned, non-executing adapter framework for L3 Standard and Unimet."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


@dataclass(frozen=True)
class AdapterSpec:
    key: str
    title: str
    required_contract_fields: tuple[str, ...]


ADAPTER_SPECS = {
    spec.key: spec
    for spec in (
        AdapterSpec(
            "l3_standard",
            "L3 Standard-Schnittstelle",
            ("encoding", "delimiter", "record_types", "sample_hash"),
        ),
        AdapterSpec(
            "unimet",
            "Unimet",
            (
                "encoding",
                "decimal_separator",
                "date_format",
                "record_types",
                "sample_hash",
            ),
        ),
    )
}
PROFILE_STATES = frozenset({"inactive", "ready", "pilot", "blocked"})
BATCH_STATES = frozenset({"received", "quarantine", "staged", "reconciled", "approved"})


class LegacyAdapterError(ValueError):
    pass


class LegacyInterfaceAdapterService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def _spec(self, profile_key: str) -> AdapterSpec:
        spec = ADAPTER_SPECS.get(profile_key)
        if spec is None:
            raise LegacyAdapterError("Adapterprofil ist nicht freigegeben")
        return spec

    def _audit(
        self,
        profile_key: str,
        action: str,
        actor: str,
        reason: str,
        *,
        batch_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.db.execute(
            text("""
              INSERT INTO domain_integration.legacy_adapter_audit
                (id,tenant_id,profile_key,batch_id,action,actor,reason,details)
              VALUES (:id,:tid,:profile_key,:batch_id,:action,:actor,:reason,CAST(:details AS JSONB))
            """),
            {
                "id": str(uuid7()),
                "tid": self.tenant_id,
                "profile_key": profile_key,
                "batch_id": batch_id,
                "action": action,
                "actor": actor,
                "reason": reason,
                "details": json.dumps(details or {}),
            },
        )

    def catalog(self) -> list[dict[str, Any]]:
        configured = {
            row["profile_key"]: dict(row)
            for row in self.db.execute(
                text("""
                  SELECT profile_key,format_version,mapping_version,status,
                         approved_by,approved_at,updated_at
                    FROM domain_integration.legacy_adapter_profiles WHERE tenant_id=:tid
                """),
                {"tid": self.tenant_id},
            )
            .mappings()
            .all()
        }
        return [
            {
                "profile_key": spec.key,
                "title": spec.title,
                "required_contract_fields": list(spec.required_contract_fields),
                "execution_enabled": False,
                **configured.get(spec.key, {"status": "inactive"}),
            }
            for spec in ADAPTER_SPECS.values()
        ]

    def configure(
        self, profile_key: str, payload: dict[str, Any], *, actor: str, reason: str
    ) -> dict[str, Any]:
        spec = self._spec(profile_key)
        contract = payload.get("format_contract") or {}
        mapping = payload.get("field_mapping") or {}
        missing = [
            field for field in spec.required_contract_fields if not contract.get(field)
        ]
        if missing:
            raise LegacyAdapterError(
                f"Formatvertrag unvollstaendig: {', '.join(missing)}"
            )
        if not mapping or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in mapping.items()
        ):
            raise LegacyAdapterError(
                "Feldmapping muss eine nicht leere Source-Target-Map sein"
            )
        status = str(payload.get("status") or "ready")
        if status not in PROFILE_STATES or status == "pilot":
            raise LegacyAdapterError(
                "Pilotaktivierung erfordert externe Kundenfreigabe"
            )
        params = {
            "id": str(uuid7()),
            "tid": self.tenant_id,
            "profile_key": profile_key,
            "format_version": str(payload.get("format_version") or "1"),
            "mapping_version": str(payload.get("mapping_version") or "1"),
            "status": status,
            "contract": json.dumps(contract),
            "mapping": json.dumps(mapping),
        }
        self.db.execute(
            text("""
              INSERT INTO domain_integration.legacy_adapter_profiles
                (id,tenant_id,profile_key,format_version,mapping_version,status,format_contract,field_mapping)
              VALUES (:id,:tid,:profile_key,:format_version,:mapping_version,:status,CAST(:contract AS JSONB),CAST(:mapping AS JSONB))
              ON CONFLICT (tenant_id,profile_key) DO UPDATE SET
                format_version=EXCLUDED.format_version,mapping_version=EXCLUDED.mapping_version,
                status=EXCLUDED.status,format_contract=EXCLUDED.format_contract,
                field_mapping=EXCLUDED.field_mapping,approved_by=NULL,approved_at=NULL,updated_at=NOW()
            """),
            params,
        )
        self._audit(
            profile_key,
            "configured",
            actor,
            reason,
            details={
                "format_version": params["format_version"],
                "mapping_version": params["mapping_version"],
                "status": status,
            },
        )
        self.db.commit()
        return {
            "profile_key": profile_key,
            "status": status,
            "execution_enabled": False,
        }

    def intake(
        self, profile_key: str, external_id: str, payload: dict[str, Any], *, actor: str
    ) -> dict[str, Any]:
        self._spec(profile_key)
        canonical = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=str
        )
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        existing = (
            self.db.execute(
                text("""
              SELECT id,payload_hash,status FROM domain_integration.legacy_adapter_batches
               WHERE tenant_id=:tid AND profile_key=:profile_key AND external_id=:external_id
            """),
                {
                    "tid": self.tenant_id,
                    "profile_key": profile_key,
                    "external_id": external_id,
                },
            )
            .mappings()
            .first()
        )
        if existing:
            if existing["payload_hash"] != digest:
                raise LegacyAdapterError(
                    "Externe ID wurde mit abweichendem Payload wiederverwendet"
                )
            return {
                "id": existing["id"],
                "status": existing["status"],
                "duplicate": True,
                "payload_hash": digest,
            }
        profile = (
            self.db.execute(
                text(
                    "SELECT mapping_version,status FROM domain_integration.legacy_adapter_profiles WHERE tenant_id=:tid AND profile_key=:profile_key"
                ),
                {"tid": self.tenant_id, "profile_key": profile_key},
            )
            .mappings()
            .first()
        )
        configured = bool(profile and profile["status"] in {"ready", "pilot"})
        batch_id = str(uuid7())
        records = (
            payload.get("records") if isinstance(payload.get("records"), list) else []
        )
        status = "received" if configured else "quarantine"
        self.db.execute(
            text("""
              INSERT INTO domain_integration.legacy_adapter_batches
                (id,tenant_id,profile_key,external_id,payload_hash,raw_payload,mapping_version,status,record_count,error_code,error_message)
              VALUES (:id,:tid,:profile_key,:external_id,:hash,CAST(:payload AS JSONB),:mapping_version,:status,:record_count,:error_code,:error_message)
            """),
            {
                "id": batch_id,
                "tid": self.tenant_id,
                "profile_key": profile_key,
                "external_id": external_id,
                "hash": digest,
                "payload": canonical,
                "mapping_version": profile["mapping_version"] if profile else None,
                "status": status,
                "record_count": len(records),
                "error_code": None if configured else "PROFILE_NOT_READY",
                "error_message": None
                if configured
                else "Formatvertrag und Mapping muessen freigegeben sein",
            },
        )
        self._audit(
            profile_key,
            "received",
            actor,
            "Adapter-Payload empfangen",
            batch_id=batch_id,
            details={
                "payload_hash": digest,
                "record_count": len(records),
                "status": status,
            },
        )
        self.db.commit()
        return {
            "id": batch_id,
            "status": status,
            "duplicate": False,
            "payload_hash": digest,
        }

    def stage(self, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
        batch = (
            self.db.execute(
                text("""
              SELECT b.*,p.field_mapping,p.status profile_status
                FROM domain_integration.legacy_adapter_batches b
                JOIN domain_integration.legacy_adapter_profiles p
                  ON p.tenant_id=b.tenant_id AND p.profile_key=b.profile_key
               WHERE b.id=:id AND b.tenant_id=:tid FOR UPDATE
            """),
                {"id": batch_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if (
            not batch
            or batch["status"] not in {"received", "quarantine"}
            or batch["profile_status"] not in {"ready", "pilot"}
        ):
            raise LegacyAdapterError("Batch oder Adapterprofil ist nicht stagingbereit")
        mapping = dict(batch["field_mapping"] or {})
        records = dict(batch["raw_payload"] or {}).get("records") or []
        self.db.execute(
            text(
                "DELETE FROM domain_integration.legacy_adapter_staging WHERE tenant_id=:tid AND batch_id=:id"
            ),
            {"tid": self.tenant_id, "id": batch_id},
        )
        invalid = 0
        for line_no, source in enumerate(records, 1):
            canonical = {
                target: source.get(source_key)
                for source_key, target in mapping.items()
                if source.get(source_key) is not None
            }
            error = None
            if not canonical.get("record_type") or not canonical.get("source_ref"):
                error = "record_type und source_ref sind im kanonischen Mapping erforderlich"
                invalid += 1
            self.db.execute(
                text("""
                  INSERT INTO domain_integration.legacy_adapter_staging
                    (id,tenant_id,batch_id,line_no,record_type,source_ref,canonical_payload,validation_status,error_message)
                  VALUES (:id,:tid,:batch_id,:line_no,:record_type,:source_ref,CAST(:payload AS JSONB),:status,:error)
                """),
                {
                    "id": str(uuid7()),
                    "tid": self.tenant_id,
                    "batch_id": batch_id,
                    "line_no": line_no,
                    "record_type": canonical.get("record_type"),
                    "source_ref": canonical.get("source_ref"),
                    "payload": json.dumps(canonical),
                    "status": "invalid" if error else "valid",
                    "error": error,
                },
            )
        status = "quarantine" if invalid else "staged"
        self.db.execute(
            text(
                "UPDATE domain_integration.legacy_adapter_batches SET status=:status,staged_count=:count,mismatch_count=:invalid,error_code=:error_code,error_message=:error_message,updated_at=NOW() WHERE id=:id AND tenant_id=:tid"
            ),
            {
                "status": status,
                "count": len(records) - invalid,
                "invalid": invalid,
                "error_code": "MAPPING_VALIDATION" if invalid else None,
                "error_message": f"{invalid} ungueltige Zeilen" if invalid else None,
                "id": batch_id,
                "tid": self.tenant_id,
            },
        )
        self._audit(
            batch["profile_key"],
            "staged",
            actor,
            reason,
            batch_id=batch_id,
            details={"valid": len(records) - invalid, "invalid": invalid},
        )
        self.db.commit()
        return {
            "id": batch_id,
            "status": status,
            "staged_count": len(records) - invalid,
            "mismatch_count": invalid,
            "execution_enabled": False,
        }

    def reconcile(self, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
        batch = (
            self.db.execute(
                text(
                    "SELECT * FROM domain_integration.legacy_adapter_batches WHERE id=:id AND tenant_id=:tid FOR UPDATE"
                ),
                {"id": batch_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if not batch or batch["status"] not in {"staged", "quarantine"}:
            raise LegacyAdapterError("Batch ist nicht abstimmbar")
        counts = (
            self.db.execute(
                text(
                    "SELECT COUNT(*) total,COUNT(*) FILTER (WHERE validation_status='valid') valid FROM domain_integration.legacy_adapter_staging WHERE tenant_id=:tid AND batch_id=:id"
                ),
                {"tid": self.tenant_id, "id": batch_id},
            )
            .mappings()
            .one()
        )
        mismatch = abs(int(batch["record_count"]) - int(counts["total"])) + (
            int(counts["total"]) - int(counts["valid"])
        )
        status = "reconciled" if mismatch == 0 else "quarantine"
        self.db.execute(
            text(
                "UPDATE domain_integration.legacy_adapter_batches SET status=:status,staged_count=:valid,mismatch_count=:mismatch,error_code=:error_code,error_message=:error_message,updated_at=NOW() WHERE id=:id AND tenant_id=:tid"
            ),
            {
                "status": status,
                "valid": counts["valid"],
                "mismatch": mismatch,
                "error_code": "RECONCILIATION_MISMATCH" if mismatch else None,
                "error_message": f"{mismatch} Abweichungen" if mismatch else None,
                "id": batch_id,
                "tid": self.tenant_id,
            },
        )
        self._audit(
            batch["profile_key"],
            "reconciled",
            actor,
            reason,
            batch_id=batch_id,
            details={
                "source": batch["record_count"],
                "staged": counts["valid"],
                "mismatch": mismatch,
            },
        )
        self.db.commit()
        return {
            "id": batch_id,
            "status": status,
            "record_count": batch["record_count"],
            "staged_count": counts["valid"],
            "mismatch_count": mismatch,
            "execution_enabled": False,
        }

    def approve(self, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
        result = (
            self.db.execute(
                text(
                    "UPDATE domain_integration.legacy_adapter_batches SET status='approved',updated_at=NOW() WHERE id=:id AND tenant_id=:tid AND status='reconciled' RETURNING profile_key"
                ),
                {"id": batch_id, "tid": self.tenant_id},
            )
            .mappings()
            .first()
        )
        if not result:
            raise LegacyAdapterError(
                "Nur abweichungsfrei abgestimmte Batches sind freigabefaehig"
            )
        self._audit(
            result["profile_key"],
            "approved_for_pilot",
            actor,
            reason,
            batch_id=batch_id,
        )
        self.db.commit()
        return {
            "id": batch_id,
            "status": "approved",
            "execution_enabled": False,
            "next_gate": "customer_format_and_target_adapter_activation",
        }

    def monitor(
        self, *, status: str | None = None, page: int = 1, page_size: int = 50
    ) -> dict[str, Any]:
        if status and status not in BATCH_STATES:
            raise LegacyAdapterError("Unbekannter Batchstatus")
        where = ["tenant_id=:tid"]
        params: dict[str, Any] = {"tid": self.tenant_id}
        if status:
            where.append("status=:status")
            params["status"] = status
        where_sql = " AND ".join(where)
        total = self.db.execute(
            text(
                f"SELECT COUNT(*) FROM domain_integration.legacy_adapter_batches WHERE {where_sql}"
            ),
            params,
        ).scalar_one()
        params.update(limit=page_size, offset=(page - 1) * page_size)
        rows = (
            self.db.execute(
                text(
                    f"SELECT id,profile_key,external_id,payload_hash,mapping_version,status,record_count,staged_count,mismatch_count,error_code,error_message,created_at,updated_at FROM domain_integration.legacy_adapter_batches WHERE {where_sql} ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
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
            "profiles": self.catalog(),
            "execution_enabled": False,
        }
