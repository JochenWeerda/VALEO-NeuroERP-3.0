"""Idempotent daily feeding-control observations and variance read model."""
from __future__ import annotations
from datetime import date, timedelta
import json
from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.agrar.rations.controlling import deviation, energy_corrected_milk, nitrogen_efficiency
from app.core.uuid7 import uuid7

def _float(value: Any) -> float | None:
    return None if value is None else float(value)

class RationsControllingService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    def _active_target(self, group_id: str) -> tuple[str | None, dict[str, Any]]:
        row = self.db.execute(text("""
          SELECT rv.id,rv.snapshot FROM domain_agrar.ration_version_lifecycle lc
          JOIN domain_agrar.ration_versions rv ON rv.id=lc.version_id AND rv.tenant_id=lc.tenant_id
          WHERE lc.tenant_id=:tenant_id AND lc.group_id=:group_id AND lc.status='active'
          LIMIT 1
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().first()
        return (None, {}) if not row else (row["id"], row["snapshot"] or {})

    @staticmethod
    def _targets(snapshot: dict[str, Any]) -> dict[str, float | None]:
        wizard = snapshot.get("wizard") if isinstance(snapshot.get("wizard"), dict) else {}
        result = snapshot.get("optimization_result") if isinstance(snapshot.get("optimization_result"), dict) else {}
        env = result.get("environmental") if isinstance(result.get("environmental"), dict) else {}
        return {
            "target_dmi_kg_cow": _float(result.get("total_dm_kg") or result.get("dmi_kg_day")),
            "target_cost_eur_cow": _float(result.get("total_cost_eur_day")),
            "target_milk_kg_cow": _float(wizard.get("milkYield")),
            "target_methane_kg_cow": _float(env.get("methane_kg_cow_day") or result.get("methane_kg_cow_day")),
        }

    def record(self, payload: dict[str, Any]) -> dict[str, Any]:
        group = self.db.execute(text("SELECT id FROM domain_agrar.feeding_groups WHERE tenant_id=:tenant_id AND id=:group_id"),
            {"tenant_id": self.tenant_id, "group_id": payload["group_id"]}).first()
        if not group: raise LookupError("Fuetterungsgruppe nicht gefunden.")
        version_id, snapshot = self._active_target(payload["group_id"])
        targets = self._targets(snapshot)
        ecm = energy_corrected_milk(payload.get("actual_milk_kg_cow"), payload.get("actual_fat_pct"), payload.get("actual_protein_pct"))
        n_eff = nitrogen_efficiency(payload.get("actual_milk_kg_cow"), payload.get("actual_protein_pct"), payload.get("feed_n_kg_cow"))
        params = {**payload, **targets, "id": str(uuid7()), "tenant_id": self.tenant_id,
            "version_id": version_id, "actual_ecm": ecm, "n_eff": n_eff, "actor": self.actor,
            "payload_json": json.dumps(payload.get("payload") or {}, ensure_ascii=False)}
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_controlling_daily
            (id,tenant_id,group_id,ration_version_id,observation_date,source,source_ref,cow_count,
             target_dmi_kg_cow,actual_dmi_kg_cow,target_cost_eur_cow,actual_cost_eur_cow,
             target_milk_kg_cow,actual_milk_kg_cow,actual_fat_pct,actual_protein_pct,actual_ecm_kg_cow,
             feed_n_kg_cow,nitrogen_efficiency_pct,target_methane_kg_cow,actual_methane_kg_cow,
             methane_estimated,payload,recorded_by)
          VALUES (:id,:tenant_id,:group_id,:version_id,:observation_date,:source,:source_ref,:cow_count,
             :target_dmi_kg_cow,:actual_dmi_kg_cow,:target_cost_eur_cow,:actual_cost_eur_cow,
             :target_milk_kg_cow,:actual_milk_kg_cow,:actual_fat_pct,:actual_protein_pct,:actual_ecm,
             :feed_n_kg_cow,:n_eff,:target_methane_kg_cow,:actual_methane_kg_cow,
             :methane_estimated,CAST(:payload_json AS jsonb),:actor)
          ON CONFLICT (tenant_id,group_id,observation_date,source,source_ref) DO UPDATE SET
             cow_count=EXCLUDED.cow_count,ration_version_id=EXCLUDED.ration_version_id,
             target_dmi_kg_cow=EXCLUDED.target_dmi_kg_cow,actual_dmi_kg_cow=EXCLUDED.actual_dmi_kg_cow,
             target_cost_eur_cow=EXCLUDED.target_cost_eur_cow,actual_cost_eur_cow=EXCLUDED.actual_cost_eur_cow,
             target_milk_kg_cow=EXCLUDED.target_milk_kg_cow,actual_milk_kg_cow=EXCLUDED.actual_milk_kg_cow,
             actual_fat_pct=EXCLUDED.actual_fat_pct,actual_protein_pct=EXCLUDED.actual_protein_pct,
             actual_ecm_kg_cow=EXCLUDED.actual_ecm_kg_cow,feed_n_kg_cow=EXCLUDED.feed_n_kg_cow,
             nitrogen_efficiency_pct=EXCLUDED.nitrogen_efficiency_pct,
             target_methane_kg_cow=EXCLUDED.target_methane_kg_cow,actual_methane_kg_cow=EXCLUDED.actual_methane_kg_cow,
             methane_estimated=EXCLUDED.methane_estimated,payload=EXCLUDED.payload,
             recorded_by=EXCLUDED.recorded_by,recorded_at=now()
          RETURNING *
        """), params).mappings().one()
        self.db.commit()
        return self._decorate(dict(row))

    @staticmethod
    def _decorate(row: dict[str, Any]) -> dict[str, Any]:
        for key, value in list(row.items()):
            if hasattr(value, "as_tuple"): row[key] = float(value)
        row["dmi_deviation_kg"] = deviation(row.get("actual_dmi_kg_cow"), row.get("target_dmi_kg_cow"))
        row["cost_deviation_eur"] = deviation(row.get("actual_cost_eur_cow"), row.get("target_cost_eur_cow"))
        row["milk_deviation_kg"] = deviation(row.get("actual_milk_kg_cow"), row.get("target_milk_kg_cow"))
        return row

    def series(self, *, group_id: str | None = None, date_from: date | None = None, date_to: date | None = None) -> list[dict[str, Any]]:
        end, start = date_to or date.today(), date_from or ((date_to or date.today()) - timedelta(days=30))
        rows = self.db.execute(text("""
          SELECT c.*,g.name AS group_name,r.version_no
          FROM domain_agrar.feeding_controlling_daily c
          JOIN domain_agrar.feeding_groups g ON g.id=c.group_id AND g.tenant_id=c.tenant_id
          LEFT JOIN domain_agrar.ration_versions r ON r.id=c.ration_version_id AND r.tenant_id=c.tenant_id
          WHERE c.tenant_id=:tenant_id AND c.observation_date BETWEEN :date_from AND :date_to
            AND (:group_id IS NULL OR c.group_id=:group_id)
          ORDER BY c.observation_date DESC,g.name,c.recorded_at DESC
        """), {"tenant_id": self.tenant_id, "date_from": start, "date_to": end, "group_id": group_id}).mappings().all()
        return [self._decorate(dict(row)) for row in rows]
