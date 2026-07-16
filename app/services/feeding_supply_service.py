"""Plan-bound supply projection and controlled procurement handoff."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.supply import calculate_supply, trade_unit_to_kg
from app.core.uuid7 import uuid7
from app.services.feeding_plan_service import FeedingPlanService


class FeedingSupplyNotFound(LookupError):
    pass


class FeedingSupplyConflict(RuntimeError):
    pass


class FeedingSupplyService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor or "unknown"

    def _catalog(self) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT ef.id,ef.artikel_nummer,ef.inventory_article_id,ef.name,
                 (ef.verfuegbar_t*1000)::numeric AS stock_kg,
                 product.id AS product_id,product.sku,product.packaging_unit,
                 product.package_size,product.minimum_order_qty
          FROM domain_shared.futtermittel_einzelfutter ef
          LEFT JOIN LATERAL (
            SELECT p.* FROM domain_agrar.feeding_feed_products p
            WHERE p.tenant_id=ef.tenant_id AND p.feed_id=ef.id AND p.active=TRUE
              AND p.valid_from<=CURRENT_DATE AND (p.valid_until IS NULL OR p.valid_until>=CURRENT_DATE)
            ORDER BY p.updated_at DESC LIMIT 1
          ) product ON TRUE
          WHERE ef.tenant_id=:tenant_id AND ef.aktiv=TRUE
        """), {"tenant_id": self.tenant_id}).mappings().all()
        return [dict(row) for row in rows]

    @staticmethod
    def _match(feed_id: str, catalog: list[dict[str, Any]]) -> dict[str, Any] | None:
        return next((row for row in catalog if feed_id in {
            str(row["id"]), str(row["artikel_nummer"]), str(row["inventory_article_id"] or ""),
        }), None)

    def project(self, *, horizon_days: int, safety_pct: float,
                subject: str, unrestricted: bool) -> list[dict[str, Any]]:
        plans = FeedingPlanService(self.db, self.tenant_id, self.actor).list_current(
            subject=subject, unrestricted=unrestricted,
        )
        catalog = self._catalog()
        result: list[dict[str, Any]] = []
        for plan in plans:
            for instruction in plan["instructions"]:
                feed_id = str(instruction["feed_id"])
                material = self._match(feed_id, catalog)
                unit_kg = trade_unit_to_kg(
                    material.get("packaging_unit") if material else None,
                    material.get("package_size") if material else None,
                )
                projection = calculate_supply(
                    daily_demand_kg=instruction.get("target_batch_kg") or 0,
                    horizon_days=horizon_days, safety_pct=safety_pct,
                    stock_kg=material.get("stock_kg") if material else None,
                    trade_unit_kg=unit_kg,
                ).to_dict()
                result.append({
                    "plan_version_id": plan["id"], "plan_version_no": plan["version_no"],
                    "group_id": plan["group_id"], "group_name": plan["group_name"],
                    "feed_id": feed_id,
                    "feed_name": instruction.get("feed_name") or (material.get("name") if material else feed_id),
                    "product_id": material.get("product_id") if material else None,
                    "sku": material.get("sku") if material else None,
                    **projection,
                })
        return result

    def list_handoffs(self, *, subject: str, unrestricted: bool) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT handoff.* FROM domain_agrar.feeding_supply_handoffs handoff
          JOIN domain_agrar.feeding_groups g
            ON g.tenant_id=handoff.tenant_id AND g.id=handoff.group_id
          LEFT JOIN domain_agrar.feeding_businesses b
            ON b.tenant_id=g.tenant_id AND b.id=g.business_id
          WHERE handoff.tenant_id=:tenant_id AND (
            :unrestricted OR g.created_by=:subject OR b.created_by=:subject OR EXISTS (
              SELECT 1 FROM domain_agrar.feeding_business_grants grant_row
              WHERE grant_row.tenant_id=g.tenant_id
                AND grant_row.business_id=g.business_id
                AND grant_row.subject=:subject
                AND grant_row.revoked_at IS NULL
                AND grant_row.valid_from<=now()
                AND (grant_row.valid_until IS NULL OR grant_row.valid_until>now())
                AND grant_row.scope IN ('read','write','approve','admin')
            )
          ) ORDER BY handoff.created_at DESC
        """), {"tenant_id": self.tenant_id, "subject": subject,
                 "unrestricted": unrestricted}).mappings().all()
        return [dict(row) for row in rows]

    def create_handoff(self, *, plan_version_id: str, feed_id: str, horizon_days: int,
                       safety_pct: float, idempotency_key: str, reason: str,
                       subject: str, unrestricted: bool) -> dict[str, Any]:
        if len(reason.strip()) < 10:
            raise FeedingSupplyConflict("Uebergabegrund muss mindestens 10 Zeichen enthalten.")
        request = {"plan_version_id": plan_version_id, "feed_id": feed_id,
                   "horizon_days": horizon_days, "safety_pct": str(safety_pct), "reason": reason.strip()}
        request_hash = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        self.db.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
                        {"key": f"feeding-supply:{self.tenant_id}:{idempotency_key}"})
        prior = self.db.execute(text("""SELECT * FROM domain_agrar.feeding_supply_handoffs
          WHERE tenant_id=:tenant_id AND idempotency_key=:key"""),
          {"tenant_id": self.tenant_id, "key": idempotency_key}).mappings().first()
        if prior:
            if prior["request_hash"] != request_hash:
                raise FeedingSupplyConflict("Idempotency-Key wurde mit anderem Inhalt verwendet.")
            return dict(prior)
        projection = next((row for row in self.project(
            horizon_days=horizon_days, safety_pct=safety_pct,
            subject=subject, unrestricted=unrestricted,
        ) if row["plan_version_id"] == plan_version_id and row["feed_id"] == feed_id), None)
        if not projection:
            raise FeedingSupplyNotFound("Aktueller Planbedarf nicht gefunden.")
        if projection["shortage_kg"] is None:
            raise FeedingSupplyConflict("Bestand ist unbekannt; keine Einkaufsmenge ableitbar.")
        if projection["shortage_kg"] <= 0:
            raise FeedingSupplyConflict("Keine Unterdeckung fuer eine Einkaufsuebergabe vorhanden.")
        if projection["suggested_order_kg"] is None:
            raise FeedingSupplyConflict("Handelseinheit ist unbekannt; Einkaufsmenge muss fachlich geklaert werden.")
        handoff_id, event_id = str(uuid7()), str(uuid7())
        row = self.db.execute(text("""INSERT INTO domain_agrar.feeding_supply_handoffs
          (id,tenant_id,plan_version_id,group_id,feed_id,projection,idempotency_key,request_hash,reason,created_by)
          VALUES (:id,:tenant_id,:plan_version_id,:group_id,:feed_id,CAST(:projection AS jsonb),:key,:hash,:reason,:actor)
          RETURNING *"""), {"id": handoff_id, "tenant_id": self.tenant_id,
          "plan_version_id": plan_version_id, "group_id": projection["group_id"], "feed_id": feed_id,
          "projection": json.dumps(projection, default=str), "key": idempotency_key,
          "hash": request_hash, "reason": reason.strip(), "actor": self.actor}).mappings().one()
        timestamp = datetime.now(timezone.utc)
        event = {"schema_version": "1.0", "event_id": event_id,
                 "event_type": "feeding.supply.procurement_handoff.created",
                 "aggregate_id": handoff_id, "timestamp": timestamp.isoformat(),
                 "payload": {"handoff_id": handoff_id, "plan_version_id": plan_version_id,
                 "group_id": projection["group_id"], "feed_id": feed_id,
                 "suggested_order_kg": str(projection["suggested_order_kg"])}}
        self.db.execute(text("""INSERT INTO public.outbox_events
          (id,event_type,aggregate_id,payload,"timestamp",published,retry_count,tenant_id)
          VALUES (:id,'feeding.supply.procurement_handoff.created',:aggregate_id,:payload,:timestamp,FALSE,0,:tenant_id)"""),
          {"id": event_id, "aggregate_id": handoff_id, "payload": json.dumps(event),
           "timestamp": timestamp, "tenant_id": self.tenant_id})
        self.db.commit()
        return dict(row)
