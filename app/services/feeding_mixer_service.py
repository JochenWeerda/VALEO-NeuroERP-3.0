"""Mischtechnik bidirektional (FEED-INT-035).

Export: deterministisches Maschinen-Dokument aus der unveraenderlichen
Planversion (Referenz = plan_version_id); veraltete Plaene sind nicht
exportierbar. Rueckmeldung: tatsaechlich geladene Mengen landen idempotent
(client_ref) auf der Planversion mit Soll/Ist-Abgleich je Instruktion;
Rueckmeldungen auf veraltete Planversionen gehen nicht verloren, sondern
werden als Konflikt in die Import-Quarantaene (FEED-INT-034) gestellt.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.services.feeding_import_monitor_service import FeedingImportMonitorService
from app.services.feeding_plan_service import FeedingPlanService

EXPORT_FORMAT = "agrirouter-feeding-plan-v1"


class StalePlanVersionError(RuntimeError):
    """Veraltete Planversion: Export verweigert bzw. Rueckmeldung in Quarantaene."""


class UnknownFeedbackFeedError(ValueError):
    """Rueckgemeldetes Futter gehoert nicht zur Planversion."""


class FeedingMixerService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor
        self._plans = FeedingPlanService(db, tenant_id, actor)

    # ── Export ──────────────────────────────────────────────────────────────

    def build_export(self, plan_version_id: str) -> dict[str, Any]:
        version = self._plans.get_version(plan_version_id)
        if version["plan_status"] == "stale":
            raise StalePlanVersionError(
                "Planversion ist veraltet — bitte die aktuelle Version exportieren.")
        return {
            "format": EXPORT_FORMAT,
            "reference": version["id"],
            "plan_id": version["plan_id"],
            "version_no": version["version_no"],
            "group_id": version["group_id"],
            "group_name": version["group_name"],
            "animal_count": version["animal_count"],
            "valid_from": str(version["valid_from"]),
            "valid_until": str(version["valid_until"]) if version["valid_until"] else None,
            "loads": [{
                "sequence": item["sequence"],
                "feed_id": item["feed_id"],
                "feed_name": item["feed_name"],
                "kg_fm_per_animal": float(item["kg_fm_per_animal"]) if item["kg_fm_per_animal"] is not None else None,
                "target_batch_kg": float(item["target_batch_kg"]) if item["target_batch_kg"] is not None else None,
            } for item in version["instructions"]],
        }

    # ── Rueckmeldung ────────────────────────────────────────────────────────

    def record_feedback(self, *, plan_version_id: str, client_ref: str,
                        loaded: list[dict[str, Any]],
                        residual_kg: float | None = None) -> dict[str, Any]:
        version = self._plans.get_version(plan_version_id)

        if version["plan_status"] == "stale":
            # Konflikt sichtbar machen statt Datenverlust: Quarantaene-Job im Monitor.
            monitor = FeedingImportMonitorService(self.db, self.tenant_id, self.actor)
            job = monitor.quarantine_external(
                adapter="mixer-feedback",
                payload={"plan_version_id": plan_version_id, "client_ref": client_ref,
                         "loaded": loaded, "residual_kg": residual_kg},
                findings=[{"severity": "high",
                           "message": (f"Rueckmeldung bezieht sich auf die veraltete Planversion "
                                       f"{version['version_no']} — aktuelle Version pruefen und "
                                       "Rueckmeldung manuell zuordnen.")}],
            )
            return {"quarantined": True, "import_job_id": job["id"]}

        instructions = {item["feed_id"]: item for item in version["instructions"]}
        lines: list[dict[str, Any]] = []
        total_target = 0.0
        total_abs_delta = 0.0
        for entry in loaded:
            feed_id = str(entry["feed_id"])
            instruction = instructions.get(feed_id)
            if instruction is None:
                raise UnknownFeedbackFeedError(
                    f"Futtermittel {feed_id} ist nicht Teil dieser Planversion.")
            target = float(instruction["target_batch_kg"]) if instruction["target_batch_kg"] is not None else None
            kg_loaded = float(entry["kg_loaded"])
            delta = (kg_loaded - target) if target is not None else None
            lines.append({"feed_id": feed_id, "feed_name": instruction["feed_name"],
                          "kg_loaded": kg_loaded, "target_batch_kg": target, "delta_kg": delta})
            if target is not None and delta is not None:
                total_target += target
                total_abs_delta += abs(delta)
        accuracy_pct = (max(0.0, 100.0 * (1 - total_abs_delta / total_target))
                        if total_target > 0 else None)

        existing = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_mixer_feedback
          WHERE tenant_id=:tenant_id AND plan_version_id=:version_id AND client_ref=:client_ref
        """), {"tenant_id": self.tenant_id, "version_id": plan_version_id,
               "client_ref": client_ref}).mappings().first()
        if existing:
            result = dict(existing)
            result["duplicate"] = True
            result["quarantined"] = False
            return result

        row = self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_mixer_feedback
            (id,tenant_id,plan_version_id,client_ref,lines,residual_kg,accuracy_pct,created_by)
          VALUES (:id,:tenant_id,:version_id,:client_ref,CAST(:lines AS jsonb),
                  :residual_kg,:accuracy_pct,:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id,
               "version_id": plan_version_id, "client_ref": client_ref,
               "lines": json.dumps(lines, ensure_ascii=False),
               "residual_kg": residual_kg, "accuracy_pct": accuracy_pct,
               "actor": self.actor}).mappings().one()
        self.db.commit()
        result = dict(row)
        result["duplicate"] = False
        result["quarantined"] = False
        return result
