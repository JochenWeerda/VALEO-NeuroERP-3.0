"""Integrationsmonitor: Importvorschau, Quarantaene und kontrollierte Uebernahme
(FEED-INT-034).

Die Validierung ist der bestehende Adapter selbst (Code-SSOT) — Vorschau und
Jobanlage rufen ihn ohne Persistenz auf; fehlerhafte Payloads landen mit
verstaendlichem Befund in der Quarantaene statt verworfen zu werden. Die
Uebernahme laeuft ueber denselben idempotenten Importpfad wie der Direktimport
(payload_hash-/external_id-Dublettenvertrag bleibt unveraendert).
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.integrations.adapters import (
    agrirouter_to_feeding_log,
    icar_ade_to_cow_profile,
    laboratory_to_feed_ingredient,
    payload_hash,
)
from app.core.uuid7 import uuid7

ADAPTERS = {
    "agrirouter": agrirouter_to_feeding_log,
    "icar-ade": icar_ade_to_cow_profile,
    "laboratory": laboratory_to_feed_ingredient,
}


class ImportJobStateError(ValueError):
    """Uebergang ist im aktuellen Jobstatus nicht zulaessig."""


class FeedingImportMonitorService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    # ── Vorschau (ohne Persistenz) ──────────────────────────────────────────

    def preview(self, adapter: str, payload: dict[str, Any]) -> dict[str, Any]:
        if adapter not in ADAPTERS:
            raise LookupError(f"Unbekannter Adapter: {adapter}")
        try:
            mapped = ADAPTERS[adapter](payload)
            return {"adapter": adapter, "valid": True, "findings": [],
                    "mapped": {"external_id": mapped.get("external_id"),
                               "target_model": mapped.get("target_model"),
                               "target": mapped.get("target")}}
        except ValueError as exc:
            return {"adapter": adapter, "valid": False,
                    "findings": [{"severity": "high", "message": str(exc)}],
                    "mapped": None}

    # ── Jobanlage: validiert oder Quarantaene ───────────────────────────────

    def create_job(self, adapter: str, payload: dict[str, Any]) -> dict[str, Any]:
        result = self.preview(adapter, payload)
        status = "validated" if result["valid"] else "quarantined"
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_import_jobs
            (id,tenant_id,adapter,payload,payload_hash,status,findings,mapped_excerpt,created_by)
          VALUES (:id,:tenant_id,:adapter,CAST(:payload AS jsonb),:payload_hash,:status,
                  CAST(:findings AS jsonb),CAST(:mapped AS jsonb),:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id, "adapter": adapter,
               "payload": json.dumps(payload, ensure_ascii=False),
               "payload_hash": payload_hash(payload), "status": status,
               "findings": json.dumps(result["findings"], ensure_ascii=False),
               "mapped": json.dumps(result["mapped"] or {}, ensure_ascii=False),
               "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)

    def quarantine_external(self, *, adapter: str, payload: dict[str, Any],
                            findings: list[dict[str, Any]]) -> dict[str, Any]:
        """Extern erkannten Konflikt (z. B. Mischwagen-Rueckmeldung auf veraltete
        Planversion, FEED-INT-035) sichtbar in die Quarantaene stellen —
        nichts geht verloren, Entscheidung faellt im Monitor."""
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_import_jobs
            (id,tenant_id,adapter,payload,payload_hash,status,findings,mapped_excerpt,created_by)
          VALUES (:id,:tenant_id,:adapter,CAST(:payload AS jsonb),:payload_hash,'quarantined',
                  CAST(:findings AS jsonb),'{}'::jsonb,:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id, "adapter": adapter,
               "payload": json.dumps(payload, ensure_ascii=False),
               "payload_hash": payload_hash(payload),
               "findings": json.dumps(findings, ensure_ascii=False),
               "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)

    def list_jobs(self, *, status: str | None = None) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT id,tenant_id,adapter,status,findings,mapped_excerpt,result_ref,
                 decision_reason,decided_by,decided_at,created_by,created_at
          FROM domain_agrar.feeding_import_jobs
          WHERE tenant_id=:tenant_id AND (:status IS NULL OR status=:status)
          ORDER BY created_at DESC
        """), {"tenant_id": self.tenant_id, "status": status}).mappings().all()
        return [dict(row) for row in rows]

    def _job(self, job_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_import_jobs
          WHERE tenant_id=:tenant_id AND id=:job_id
        """), {"tenant_id": self.tenant_id, "job_id": job_id}).mappings().first()
        if not row:
            raise LookupError("Importauftrag nicht gefunden.")
        return dict(row)

    # ── Entscheidungen ──────────────────────────────────────────────────────

    def accept(self, job_id: str) -> dict[str, Any]:
        job = self._job(job_id)
        if job["status"] != "validated":
            raise ImportJobStateError(
                f"Uebernahme nur aus Status 'validated' moeglich (aktuell: {job['status']}).")
        mapped = ADAPTERS[job["adapter"]](job["payload"])
        external_id = str(mapped["external_id"])

        # Idempotenter Importpfad: bestehender Datensatz gewinnt (Dublettenvertrag).
        existing = self.db.execute(text("""
          SELECT id FROM domain_agrar.rations_integration_imports
          WHERE tenant_id=:tenant_id AND adapter=:adapter AND external_id=:external_id
        """), {"tenant_id": self.tenant_id, "adapter": job["adapter"],
               "external_id": external_id}).first()
        if existing:
            result_ref = existing[0]
        else:
            result_ref = str(uuid7())
            self.db.execute(text("""
              INSERT INTO domain_agrar.rations_integration_imports
                (id,tenant_id,adapter,external_id,source_version,payload_hash,target_model,result)
              VALUES (:id,:tenant_id,:adapter,:external_id,:source_version,:payload_hash,
                      :target_model,CAST(:result AS jsonb))
            """), {"id": result_ref, "tenant_id": self.tenant_id, "adapter": job["adapter"],
                   "external_id": external_id, "source_version": mapped.get("source_version"),
                   "payload_hash": job["payload_hash"], "target_model": mapped["target_model"],
                   "result": json.dumps(mapped, ensure_ascii=False)})

        row = self.db.execute(text("""
          UPDATE domain_agrar.feeding_import_jobs
          SET status='accepted', result_ref=:result_ref, decided_by=:actor, decided_at=now()
          WHERE tenant_id=:tenant_id AND id=:job_id
          RETURNING *
        """), {"tenant_id": self.tenant_id, "job_id": job_id,
               "result_ref": result_ref, "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)

    def reject(self, job_id: str, reason: str) -> dict[str, Any]:
        job = self._job(job_id)
        if job["status"] in {"accepted", "rejected"}:
            raise ImportJobStateError(
                f"Auftrag ist bereits entschieden (Status: {job['status']}).")
        row = self.db.execute(text("""
          UPDATE domain_agrar.feeding_import_jobs
          SET status='rejected', decision_reason=:reason, decided_by=:actor, decided_at=now()
          WHERE tenant_id=:tenant_id AND id=:job_id
          RETURNING *
        """), {"tenant_id": self.tenant_id, "job_id": job_id,
               "reason": reason, "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)
