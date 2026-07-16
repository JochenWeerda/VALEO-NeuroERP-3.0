"""Append-only component actual-feeding command and variance projection."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
from io import StringIO
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.actual_feeding import (
    ActualFeedingValidationError,
    calculate_component_actual,
    calculate_value_consequences,
    validate_components,
)
from app.core.uuid7 import uuid7
from app.services.feeding_plan_service import FeedingPlanNotFound, FeedingPlanService


class FeedingActualNotFound(LookupError):
    pass


class FeedingActualConflict(RuntimeError):
    pass


class FeedingActualService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor or "unknown"

    def _plan(self, version_id: str) -> dict[str, Any]:
        try:
            plan = FeedingPlanService(self.db, self.tenant_id, self.actor).get_version(version_id)
        except FeedingPlanNotFound as exc:
            raise FeedingActualNotFound(str(exc)) from exc
        if plan["plan_status"] != "current":
            raise FeedingActualConflict("Ist-Fuetterung kann nur gegen eine aktuelle Planversion erfasst werden.")
        return plan

    def _feed_context(self, feed_id: str, feeding_at: datetime) -> dict[str, Any]:
        material = self.db.execute(text("""SELECT ef.id,
          (SELECT p.price_eur_t+p.freight_eur_t FROM domain_agrar.feeding_feed_products p
           WHERE p.tenant_id=ef.tenant_id AND p.feed_id=ef.id AND p.active=TRUE
             AND p.valid_from<=CAST(:day AS date) AND (p.valid_until IS NULL OR p.valid_until>=CAST(:day AS date))
           ORDER BY p.updated_at DESC LIMIT 1) AS price_eur_t
          FROM domain_shared.futtermittel_einzelfutter ef
          WHERE ef.tenant_id=:tenant_id AND :feed_id IN
            (ef.id,ef.artikel_nummer,COALESCE(ef.inventory_article_id,'')) LIMIT 1"""),
          {"tenant_id": self.tenant_id, "feed_id": feed_id, "day": feeding_at}).mappings().first()
        if not material:
            return {"price_eur_t": None, "nutrients": []}
        nutrients = self.db.execute(text("""SELECT DISTINCT ON (nutrient_code)
          nutrient_code AS code,value,unit_code AS unit,basis,id,revision,source_type,source_ref
          FROM domain_agrar.feeding_feed_reference_values
          WHERE tenant_id=:tenant_id AND feed_id=:feed_id
            AND valid_from<=CAST(:day AS date) AND (valid_until IS NULL OR valid_until>=CAST(:day AS date))
          ORDER BY nutrient_code,priority DESC,valid_from DESC,revision DESC"""),
          {"tenant_id": self.tenant_id, "feed_id": material["id"], "day": feeding_at}).mappings().all()
        return {"price_eur_t": material["price_eur_t"],
                "nutrients": [dict(row) for row in nutrients]}

    def record(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = self._plan(payload["plan_version_id"])
        instructions = {str(row["feed_id"]): row for row in plan["instructions"]}
        validate_components(payload["components"], set(instructions))
        if payload["cause_class"] == "other" and len((payload.get("comment") or "").strip()) < 10:
            raise ActualFeedingValidationError("Ursache 'other' erfordert einen Kommentar mit mindestens 10 Zeichen.")
        feeding_at = payload["feeding_at"]
        if feeding_at.tzinfo is None:
            feeding_at = feeding_at.replace(tzinfo=timezone.utc)
        canonical = {**payload, "feeding_at": feeding_at.isoformat(),
                     "components": sorted(payload["components"], key=lambda row: row["feed_id"])}
        request_hash = hashlib.sha256(json.dumps(canonical, sort_keys=True, default=str).encode()).hexdigest()
        self.db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
                        {"key": f"feeding-actual:{self.tenant_id}:{payload['idempotency_key']}"})
        prior = self.db.execute(text("""SELECT id,request_hash FROM domain_agrar.feeding_actual_records
          WHERE tenant_id=:tenant_id AND idempotency_key=:key"""),
          {"tenant_id": self.tenant_id, "key": payload["idempotency_key"]}).mappings().first()
        if prior:
            if prior["request_hash"] != request_hash:
                raise FeedingActualConflict("Idempotency-Key wurde mit anderem Inhalt verwendet.")
            return self.get(prior["id"])
        if payload.get("supersedes_id"):
            predecessor = self.get(payload["supersedes_id"])
            if predecessor["plan_version_id"] != plan["id"]:
                raise FeedingActualConflict("Korrektur und Vorgaenger muessen dieselbe Planversion referenzieren.")

        record_id, event_id = str(uuid7()), str(uuid7())
        self.db.execute(text("""INSERT INTO domain_agrar.feeding_actual_records
          (id,tenant_id,plan_version_id,group_id,feeding_at,source,source_ref,cause_class,
           comment,context,supersedes_id,idempotency_key,request_hash,recorded_by)
          VALUES (:id,:tenant_id,:plan_version_id,:group_id,:feeding_at,:source,:source_ref,
           :cause_class,:comment,CAST(:context_json AS jsonb),:supersedes_id,:idempotency_key,:request_hash,:actor)"""),
          {**payload, "id": record_id, "tenant_id": self.tenant_id,
           "group_id": plan["group_id"], "feeding_at": feeding_at,
           "context_json": json.dumps(payload.get("context") or {}, default=str, ensure_ascii=False),
           "request_hash": request_hash, "actor": self.actor})
        for component in payload["components"]:
            instruction = instructions[str(component["feed_id"])]
            if instruction["target_batch_kg"] is None:
                raise FeedingActualConflict(f"Planmenge fuer {component['feed_id']} ist unbekannt.")
            variance = calculate_component_actual(
                target_kg=instruction["target_batch_kg"], actual_kg=component["actual_kg"],
            )
            context = self._feed_context(str(component["feed_id"]), feeding_at)
            consequence = calculate_value_consequences(
                target_kg=variance.target_kg, actual_kg=variance.actual_kg,
                price_eur_t=context["price_eur_t"], nutrient_values=context["nutrients"],
            )
            consequence["source_values"] = context["nutrients"]
            self.db.execute(text("""INSERT INTO domain_agrar.feeding_actual_components
              (id,tenant_id,actual_record_id,instruction_id,feed_id,feed_name,target_kg,
               actual_kg,delta_kg,delta_pct,value_consequences)
              VALUES (:id,:tenant_id,:record_id,:instruction_id,:feed_id,:feed_name,:target,
               :actual,:delta,:pct,CAST(:consequence AS jsonb))"""), {
                "id": str(uuid7()), "tenant_id": self.tenant_id, "record_id": record_id,
                "instruction_id": instruction["id"], "feed_id": component["feed_id"],
                "feed_name": instruction.get("feed_name"), "target": variance.target_kg,
                "actual": variance.actual_kg, "delta": variance.delta_kg,
                "pct": variance.delta_pct,
                "consequence": json.dumps(consequence, default=str, ensure_ascii=False),
            })
        event = {"schema_version": "1.0", "event_id": event_id,
                 "event_type": "feeding.actual.recorded", "aggregate_id": record_id,
                 "timestamp": datetime.now(timezone.utc).isoformat(),
                 "payload": {"actual_record_id": record_id, "plan_version_id": plan["id"],
                 "group_id": plan["group_id"], "feeding_at": feeding_at.isoformat()}}
        self.db.execute(text("""INSERT INTO public.outbox_events
          (id,event_type,aggregate_id,payload,"timestamp",published,retry_count,tenant_id)
          VALUES (:id,'feeding.actual.recorded',:aggregate_id,:payload,:timestamp,FALSE,0,:tenant_id)"""),
          {"id": event_id, "aggregate_id": record_id, "payload": json.dumps(event),
           "timestamp": datetime.now(timezone.utc), "tenant_id": self.tenant_id})
        self.db.commit()
        return self.get(record_id)

    def get(self, record_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""SELECT r.*,g.name AS group_name,pv.version_no AS plan_version_no
          FROM domain_agrar.feeding_actual_records r
          JOIN domain_agrar.feeding_groups g ON g.tenant_id=r.tenant_id AND g.id=r.group_id
          JOIN domain_agrar.feeding_plan_versions pv ON pv.tenant_id=r.tenant_id AND pv.id=r.plan_version_id
          WHERE r.tenant_id=:tenant_id AND r.id=:id"""),
          {"tenant_id": self.tenant_id, "id": record_id}).mappings().first()
        if not row:
            raise FeedingActualNotFound("Ist-Fuetterung nicht gefunden.")
        result = dict(row)
        result["components"] = [dict(item) for item in self.db.execute(text("""SELECT *
          FROM domain_agrar.feeding_actual_components WHERE tenant_id=:tenant_id
          AND actual_record_id=:id ORDER BY feed_name,feed_id"""),
          {"tenant_id": self.tenant_id, "id": record_id}).mappings().all()]
        return result

    def list(self, *, group_ids: list[str]) -> list[dict[str, Any]]:
        if not group_ids:
            return []
        ids = self.db.execute(text("""SELECT id FROM domain_agrar.feeding_actual_records
          WHERE tenant_id=:tenant_id AND group_id=ANY(:group_ids) ORDER BY feeding_at DESC"""),
          {"tenant_id": self.tenant_id, "group_ids": group_ids}).scalars().all()
        return [self.get(record_id) for record_id in ids]

    def list_components(self, *, group_ids: list[str]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for record in self.list(group_ids=group_ids):
            for component in record["components"]:
                consequence = component.get("value_consequences") or {}
                nutrients = consequence.get("nutrients") or []
                result.append({
                    "id": component["id"], "actual_record_id": record["id"],
                    "plan_version_id": record["plan_version_id"],
                    "plan_version_no": record["plan_version_no"],
                    "group_id": record["group_id"], "group_name": record["group_name"],
                    "feeding_at": record["feeding_at"], "cause_class": record["cause_class"],
                    "comment": record["comment"], "source": record["source"],
                    "feed_id": component["feed_id"], "feed_name": component["feed_name"],
                    "target_kg": component["target_kg"], "actual_kg": component["actual_kg"],
                    "delta_kg": component["delta_kg"], "delta_pct": component["delta_pct"],
                    "cost_delta_eur": (consequence.get("cost") or {}).get("delta_eur"),
                    "nutrient_delta_summary": ", ".join(
                        f"{item['code']}: {item['delta']} {item['result_unit']}" for item in nutrients
                    ) or None,
                    "missing_value_summary": ", ".join(consequence.get("missing") or []) or None,
                })
        return result

    @staticmethod
    def to_csv(records: list[dict[str, Any]]) -> str:
        output = StringIO(newline="")
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["actual_record_id", "plan_version_id", "feeding_at", "group_id",
                         "feed_id", "feed_name", "target_kg", "actual_kg", "delta_kg",
                         "delta_pct", "cause_class", "comment", "cost_delta_eur", "missing_values"])
        for record in records:
            for component in record["components"]:
                consequence = component["value_consequences"] or {}
                writer.writerow([record["id"], record["plan_version_id"], record["feeding_at"],
                    record["group_id"], component["feed_id"], component["feed_name"],
                    component["target_kg"], component["actual_kg"], component["delta_kg"],
                    component["delta_pct"], record["cause_class"], record["comment"],
                    (consequence.get("cost") or {}).get("delta_eur"),
                    ",".join(consequence.get("missing") or [])])
        return output.getvalue()
