"""Transactional feeding-plan publication service."""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.feeding_plan import build_mixing_instructions
from app.core.uuid7 import uuid7


class FeedingPlanNotFound(LookupError):
    pass


class FeedingPlanConflict(RuntimeError):
    pass


class FeedingPlanService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor or "unknown"

    async def publish(self, *, source_ration_version_id: str, animal_count: int,
                      dosing_step_kg: Decimal, rounding_mode: str, valid_from: date,
                      valid_until: date | None, reason: str, idempotency_key: str) -> dict[str, Any]:
        if valid_until and valid_until < valid_from:
            raise FeedingPlanConflict("Gueltig-bis darf nicht vor Gueltig-ab liegen.")
        if len(reason.strip()) < 10:
            raise FeedingPlanConflict("Publikationsgrund muss mindestens 10 Zeichen enthalten.")
        request = {"source": source_ration_version_id, "animal_count": animal_count,
                   "dosing_step_kg": str(dosing_step_kg), "rounding_mode": rounding_mode,
                   "valid_from": str(valid_from), "valid_until": str(valid_until), "reason": reason.strip()}
        request_hash = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        # Serialize retries before checking the idempotency record. The lock lives
        # in this transaction and therefore covers plan, instructions and outbox.
        self.db.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:lock_key,0))"),
            {"lock_key": f"feeding-plan-publish:{self.tenant_id}:{idempotency_key}"},
        )
        prior = self.db.execute(text("SELECT id,request_hash FROM domain_agrar.feeding_plan_versions WHERE tenant_id=:tenant_id AND idempotency_key=:key"),
                                {"tenant_id": self.tenant_id, "key": idempotency_key}).mappings().first()
        if prior:
            if prior["request_hash"] != request_hash:
                raise FeedingPlanConflict("Idempotency-Key wurde mit anderem Inhalt verwendet.")
            return self.get_version(prior["id"])
        source = self.db.execute(text("""SELECT rv.id,rv.snapshot,rv.ration_id,r.group_id,r.name,lc.status
          FROM domain_agrar.ration_versions rv JOIN domain_agrar.rations r ON r.tenant_id=rv.tenant_id AND r.id=rv.ration_id
          JOIN domain_agrar.ration_version_lifecycle lc ON lc.tenant_id=rv.tenant_id AND lc.version_id=rv.id
          WHERE rv.tenant_id=:tenant_id AND rv.id=:id FOR UPDATE OF rv"""),
          {"tenant_id": self.tenant_id, "id": source_ration_version_id}).mappings().first()
        if not source:
            raise FeedingPlanNotFound("Rationsversion nicht gefunden.")
        if source["status"] not in {"approved", "active"}:
            raise FeedingPlanConflict("Nur approved oder active Rationsversionen duerfen publiziert werden.")
        self.db.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:lock_key,1))"),
            {"lock_key": f"feeding-plan-group:{self.tenant_id}:{source['group_id']}"},
        )
        instructions = build_mixing_instructions(dict(source["snapshot"]), animal_count=animal_count,
                                                  dosing_step_kg=dosing_step_kg, rounding_mode=rounding_mode)
        plan = self.db.execute(text("""INSERT INTO domain_agrar.feeding_plans (id,tenant_id,group_id,name,created_by)
          VALUES (:id,:tenant_id,:group_id,:name,:actor) ON CONFLICT (tenant_id,group_id) DO UPDATE SET name=domain_agrar.feeding_plans.name RETURNING id"""),
          {"id": str(uuid7()), "tenant_id": self.tenant_id, "group_id": source["group_id"], "name": source["name"], "actor": self.actor}).mappings().one()
        latest = int(self.db.execute(text("SELECT COALESCE(MAX(version_no),0) FROM domain_agrar.feeding_plan_versions WHERE tenant_id=:tenant_id AND plan_id=:plan_id"),
                                     {"tenant_id": self.tenant_id, "plan_id": plan["id"]}).scalar_one())
        version_id, event_id = str(uuid7()), str(uuid7())
        self.db.execute(text("""INSERT INTO domain_agrar.feeding_plan_versions
          (id,tenant_id,plan_id,version_no,source_ration_version_id,animal_count,dosing_step_kg,rounding_mode,valid_from,valid_until,reason,idempotency_key,request_hash,published_by)
          VALUES (:id,:tenant_id,:plan_id,:version_no,:source,:animal_count,:step,:mode,:valid_from,:valid_until,:reason,:key,:hash,:actor)"""),
          {"id": version_id, "tenant_id": self.tenant_id, "plan_id": plan["id"], "version_no": latest+1,
           "source": source_ration_version_id, "animal_count": animal_count, "step": dosing_step_kg,
           "mode": rounding_mode, "valid_from": valid_from, "valid_until": valid_until, "reason": reason.strip(),
           "key": idempotency_key, "hash": request_hash, "actor": self.actor})
        for item in instructions:
            self.db.execute(text("""INSERT INTO domain_agrar.feeding_mixing_instructions
              (id,tenant_id,plan_version_id,sequence,feed_id,feed_name,kg_fm_per_animal,raw_batch_kg,target_batch_kg,rounding_delta_kg)
              VALUES (:id,:tenant_id,:version_id,:sequence,:feed_id,:feed_name,:kg_fm,:raw,:target,:delta)"""),
              {"id": str(uuid7()), "tenant_id": self.tenant_id, "version_id": version_id, "sequence": item.sequence,
               "feed_id": item.feed_id, "feed_name": item.feed_name, "kg_fm": item.kg_fm_per_animal,
               "raw": item.raw_batch_kg, "target": item.target_batch_kg, "delta": item.rounding_delta_kg})
        payload = {"schema_version": "1.0", "event_id": event_id, "event_type": "feeding.plan.published", "aggregate_id": plan["id"],
                   "timestamp": datetime.now(timezone.utc).isoformat(), "payload": {"plan_id": plan["id"],
                   "plan_version_id": version_id, "source_ration_version_id": source_ration_version_id,
                   "group_id": source["group_id"], "version_no": latest+1, "valid_from": str(valid_from), "valid_until": str(valid_until)}}
        self.db.execute(text("""INSERT INTO public.outbox_events (id,event_type,aggregate_id,payload,"timestamp",published,retry_count,tenant_id)
          VALUES (:id,'feeding.plan.published',:aggregate_id,:payload,:timestamp,FALSE,0,:tenant_id)"""),
          {"id": event_id, "aggregate_id": plan["id"], "payload": json.dumps(payload), "timestamp": datetime.now(timezone.utc), "tenant_id": self.tenant_id})
        self.db.commit()
        return self.get_version(version_id)

    def get_version(self, version_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""SELECT pv.*,p.group_id,p.name FROM domain_agrar.feeding_plan_versions pv
          JOIN domain_agrar.feeding_plans p ON p.tenant_id=pv.tenant_id AND p.id=pv.plan_id
          WHERE pv.tenant_id=:tenant_id AND pv.id=:id"""), {"tenant_id": self.tenant_id, "id": version_id}).mappings().first()
        if not row:
            raise FeedingPlanNotFound("Planversion nicht gefunden.")
        result = dict(row)
        result["instructions"] = [dict(x) for x in self.db.execute(text("SELECT * FROM domain_agrar.feeding_mixing_instructions WHERE tenant_id=:tenant_id AND plan_version_id=:id ORDER BY sequence"), {"tenant_id": self.tenant_id, "id": version_id}).mappings().all()]
        return result

    def list_versions(self, group_id: str | None = None, *, subject: str = "",
                      unrestricted: bool = False) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""SELECT pv.*,p.group_id,p.name FROM domain_agrar.feeding_plan_versions pv
          JOIN domain_agrar.feeding_plans p ON p.tenant_id=pv.tenant_id AND p.id=pv.plan_id
          JOIN domain_agrar.feeding_groups g ON g.tenant_id=p.tenant_id AND g.id=p.group_id
          LEFT JOIN domain_agrar.feeding_businesses b ON b.tenant_id=g.tenant_id AND b.id=g.business_id
          WHERE pv.tenant_id=:tenant_id AND (:group_id IS NULL OR p.group_id=:group_id)
            AND (:unrestricted OR g.created_by=:subject OR b.created_by=:subject OR EXISTS (
              SELECT 1 FROM domain_agrar.feeding_business_grants grant_row
              WHERE grant_row.tenant_id=g.tenant_id AND grant_row.business_id=g.business_id
                AND grant_row.subject=:subject AND grant_row.scope IN ('read','write','approve','admin')
                AND grant_row.revoked_at IS NULL AND grant_row.valid_from<=now()
                AND (grant_row.valid_until IS NULL OR grant_row.valid_until>now())
            )) ORDER BY pv.published_at DESC"""),
          {"tenant_id": self.tenant_id, "group_id": group_id, "subject": subject,
           "unrestricted": unrestricted}).mappings().all()
        return [dict(row) for row in rows]
