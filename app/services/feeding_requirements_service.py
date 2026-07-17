"""Bewertungssysteme, Bedarfsprofile und Solverlauf-Dokumentation (FEED-CORE-020).

FEED-REQ-002: Normsystem-Auswahl und -Version als Daten; FEED-OPT-005:
reproduzierbar dokumentierte Solverlaeufe. Bedarfsformeln bleiben Code-SSOT
(GfE 2023, golden-getestet) — dieser Service persistiert Eingangsgroessen,
explizit gekennzeichnete Schaetzwerte, Systemversion und Ergebnis append-only.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.evaluation_systems import SEED_SYSTEMS
from app.agrar.rations.requirements import gfe_requirements
from app.core.uuid7 import uuid7

# Fachliche Defaults fuer fehlende Eingangsgroessen. Jede Anwendung eines
# Defaults wird als Schaetzwert gekennzeichnet — nie still ergaenzt (Lastenheft 6.5).
PROFILE_DEFAULTS: dict[str, Any] = {
    "breed": "Holstein",
    "body_weight_kg": 650,
    "milk_kg_day": 30,
    "milk_fat_pct": 4.0,
    "milk_protein_pct": 3.4,
    "lactation_stage_days": 100,
    "parity": 2,
    "feeding_type": "TMR",
}

REQUIREMENTS_SYSTEM_ID = "gfe2023"


class FeedingRequirementsService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    # ── Systemregistry ──────────────────────────────────────────────────────

    def seed_systems(self) -> dict[str, int]:
        created_systems = 0
        created_versions = 0
        for seed in SEED_SYSTEMS:
            result = self.db.execute(text("""
              INSERT INTO domain_agrar.evaluation_systems (id,name,description)
              VALUES (:id,:name,:description)
              ON CONFLICT (id) DO NOTHING
            """), {"id": seed.system_id, "name": seed.name, "description": seed.description})
            created_systems += result.rowcount or 0
            result = self.db.execute(text("""
              INSERT INTO domain_agrar.evaluation_system_versions
                (id,system_id,version_label,module_ref,is_current)
              VALUES (:id,:system_id,:version_label,:module_ref,TRUE)
              ON CONFLICT (system_id,version_label) DO NOTHING
            """), {"id": str(uuid7()), "system_id": seed.system_id,
                   "version_label": seed.version_label, "module_ref": seed.module_ref})
            created_versions += result.rowcount or 0
        self.db.commit()
        return {"created_systems": created_systems, "created_versions": created_versions}

    def list_systems(self) -> list[dict[str, Any]]:
        self.seed_systems()
        systems = self.db.execute(text("""
          SELECT id,name,description FROM domain_agrar.evaluation_systems ORDER BY id
        """)).mappings().all()
        versions = self.db.execute(text("""
          SELECT id,system_id,version_label,module_ref,is_current,valid_from
          FROM domain_agrar.evaluation_system_versions ORDER BY system_id,valid_from
        """)).mappings().all()
        by_system: dict[str, list[dict[str, Any]]] = {}
        for version in versions:
            by_system.setdefault(version["system_id"], []).append(dict(version))
        return [{**dict(system), "versions": by_system.get(system["id"], [])} for system in systems]

    def _current_version_id(self, system_id: str) -> str:
        row = self.db.execute(text("""
          SELECT id FROM domain_agrar.evaluation_system_versions
          WHERE system_id=:system_id AND is_current LIMIT 1
        """), {"system_id": system_id}).first()
        if not row:
            self.seed_systems()
            row = self.db.execute(text("""
              SELECT id FROM domain_agrar.evaluation_system_versions
              WHERE system_id=:system_id AND is_current LIMIT 1
            """), {"system_id": system_id}).first()
        if not row:
            raise LookupError(f"Bewertungssystem {system_id} ist nicht registriert.")
        return row[0]

    # ── Bedarfsprofile ──────────────────────────────────────────────────────

    def create_requirement_profile(self, group_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
        group = self.db.execute(text("""
          SELECT id FROM domain_agrar.feeding_groups
          WHERE tenant_id=:tenant_id AND id=:group_id
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).first()
        if not group:
            raise LookupError("Fuetterungsgruppe nicht gefunden.")

        profile_inputs = dict(PROFILE_DEFAULTS)
        estimated = sorted(key for key in PROFILE_DEFAULTS
                           if inputs.get(key) is None)
        for key, value in inputs.items():
            if value is not None:
                profile_inputs[key] = value

        # Golden-getestete GfE-2023-Bedarfslogik (Code-SSOT seit FEED-OPT-042
        # als eigenes Domaenenmodul — kein Monolith-Import mehr).
        requirements = gfe_requirements(profile_inputs).model_dump()

        system_version_id = self._current_version_id(REQUIREMENTS_SYSTEM_ID)
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.requirement_profiles
            (id,tenant_id,group_id,system_version_id,inputs,estimated_inputs,requirements,created_by)
          VALUES (:id,:tenant_id,:group_id,:system_version_id,
                  CAST(:inputs AS jsonb),CAST(:estimated AS jsonb),CAST(:requirements AS jsonb),:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id, "group_id": group_id,
               "system_version_id": system_version_id,
               "inputs": json.dumps(profile_inputs, ensure_ascii=False),
               "estimated": json.dumps(estimated, ensure_ascii=False),
               "requirements": json.dumps(requirements, ensure_ascii=False),
               "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)

    def list_requirement_profiles(self, group_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT * FROM domain_agrar.requirement_profiles
          WHERE tenant_id=:tenant_id AND group_id=:group_id
          ORDER BY created_at DESC
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().all()
        return [dict(row) for row in rows]

    # ── Solverlauf-Dokumentation ───────────────────────────────────────────

    def record_optimization_run(self, ration_version_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        version = self.db.execute(text("""
          SELECT id, ration_id FROM domain_agrar.ration_versions
          WHERE tenant_id=:tenant_id AND id=:version_id
        """), {"tenant_id": self.tenant_id, "version_id": ration_version_id}).mappings().first()
        if not version:
            raise LookupError("Rationsversion nicht gefunden.")
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.optimization_runs
            (id,tenant_id,ration_id,ration_version_id,solver_version,objective,status,
             duration_ms,parameters,created_by)
          VALUES (:id,:tenant_id,:ration_id,:version_id,:solver_version,:objective,:status,
                  :duration_ms,CAST(:parameters AS jsonb),:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id,
               "ration_id": version["ration_id"], "version_id": ration_version_id,
               "solver_version": payload["solver_version"], "objective": payload["objective"],
               "status": payload["status"], "duration_ms": payload.get("duration_ms"),
               "parameters": json.dumps(payload.get("parameters") or {}, ensure_ascii=False),
               "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)

    def list_optimization_runs(self, *, ration_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT * FROM domain_agrar.optimization_runs
          WHERE tenant_id=:tenant_id AND ration_id=:ration_id
          ORDER BY created_at DESC
        """), {"tenant_id": self.tenant_id, "ration_id": ration_id}).mappings().all()
        return [dict(row) for row in rows]
