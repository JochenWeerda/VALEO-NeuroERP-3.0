"""Versioned deviation policies, findings and human-created measures."""

from __future__ import annotations

from datetime import date
import hashlib
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.actual_measures import evaluate_deviation, validate_thresholds
from app.core.uuid7 import uuid7


class ActualMeasureNotFound(LookupError):
    pass


class ActualMeasureConflict(RuntimeError):
    pass


class FeedingActualMeasureService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor or "unknown"

    def create_policy(self, payload: dict[str, Any]) -> dict[str, Any]:
        validate_thresholds(payload["warning_pct"], payload["critical_pct"])
        self.db.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
            {"key": f"feeding-policy:{self.tenant_id}:{payload['feed_class']}"},
        )
        latest = int(
            self.db.execute(
                text("""SELECT COALESCE(MAX(version),0)
          FROM domain_agrar.feeding_deviation_policies
          WHERE tenant_id=:tenant_id AND feed_class=:feed_class"""),
                {"tenant_id": self.tenant_id, "feed_class": payload["feed_class"]},
            ).scalar_one()
        )
        row = (
            self.db.execute(
                text("""INSERT INTO domain_agrar.feeding_deviation_policies
          (id,tenant_id,feed_class,version,warning_pct,critical_pct,valid_from,reason,created_by)
          VALUES (:id,:tenant_id,:feed_class,:version,:warning_pct,:critical_pct,:valid_from,:reason,:actor)
          RETURNING *"""),
                {
                    **payload,
                    "id": str(uuid7()),
                    "tenant_id": self.tenant_id,
                    "version": latest + 1,
                    "actor": self.actor,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return dict(row)

    def list_policies(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.execute(
                text("""SELECT * FROM
          domain_agrar.feeding_deviation_policies WHERE tenant_id=:tenant_id
          ORDER BY feed_class,version DESC"""),
                {"tenant_id": self.tenant_id},
            )
            .mappings()
            .all()
        ]

    def findings(self, *, group_ids: list[str]) -> list[dict[str, Any]]:
        if not group_ids:
            return []
        rows = (
            self.db.execute(
                text("""SELECT c.*,r.plan_version_id,r.group_id,r.feeding_at,
          ef.feed_kind,policy.id AS policy_id,policy.version AS policy_version,
          policy.warning_pct,policy.critical_pct
          FROM domain_agrar.feeding_actual_components c
          JOIN domain_agrar.feeding_actual_records r ON r.tenant_id=c.tenant_id AND r.id=c.actual_record_id
          LEFT JOIN domain_shared.futtermittel_einzelfutter ef ON ef.tenant_id=c.tenant_id
            AND c.feed_id IN (ef.id,ef.artikel_nummer,COALESCE(ef.inventory_article_id,''))
          LEFT JOIN LATERAL (SELECT p.* FROM domain_agrar.feeding_deviation_policies p
            WHERE p.tenant_id=c.tenant_id AND p.feed_class=COALESCE(ef.feed_kind,'other')
              AND p.valid_from<=CAST(r.feeding_at AS date)
            ORDER BY p.valid_from DESC,p.version DESC LIMIT 1) policy ON TRUE
          WHERE c.tenant_id=:tenant_id AND r.group_id=ANY(:group_ids)
          ORDER BY r.feeding_at DESC"""),
                {"tenant_id": self.tenant_id, "group_ids": group_ids},
            )
            .mappings()
            .all()
        )
        result = []
        for raw in rows:
            row = dict(raw)
            if row["policy_id"] is None:
                result.append(
                    {
                        "actual_component_id": row["id"],
                        "actual_record_id": row["actual_record_id"],
                        "plan_version_id": row["plan_version_id"],
                        "group_id": row["group_id"],
                        "feed_id": row["feed_id"],
                        "feed_name": row["feed_name"],
                        "severity": "unconfigured",
                        "message": "Keine explizite Schwelle fuer diese Komponentenklasse konfiguriert.",
                        "feed_class": row["feed_kind"] or "other",
                        "policy_id": None,
                    }
                )
                continue
            finding = evaluate_deviation(
                target_kg=row["target_kg"],
                actual_kg=row["actual_kg"],
                warning_pct=row["warning_pct"],
                critical_pct=row["critical_pct"],
                feed_class=row["feed_kind"] or "other",
                policy_version=row["policy_version"],
            )
            if finding:
                result.append(
                    {
                        "actual_component_id": row["id"],
                        "actual_record_id": row["actual_record_id"],
                        "plan_version_id": row["plan_version_id"],
                        "group_id": row["group_id"],
                        "feed_id": row["feed_id"],
                        "feed_name": row["feed_name"],
                        "policy_id": row["policy_id"],
                        **finding,
                        "message": f"{row['feed_name'] or row['feed_id']}: {finding['delta_pct']} % Abweichung.",
                    }
                )
        return result

    def create_measure(
        self, payload: dict[str, Any], *, group_ids: list[str]
    ) -> dict[str, Any]:
        finding = next(
            (
                item
                for item in self.findings(group_ids=group_ids)
                if item["actual_component_id"] == payload["actual_component_id"]
            ),
            None,
        )
        if not finding or finding["severity"] not in {"warning", "critical"}:
            raise ActualMeasureConflict(
                "Kein massnahmenfaehiger Abweichungsbefund vorhanden."
            )
        if payload["due_date"] < date.today():
            raise ActualMeasureConflict(
                "Faelligkeit darf nicht in der Vergangenheit liegen."
            )
        request = {key: str(value) for key, value in payload.items()}
        digest = hashlib.sha256(
            json.dumps(request, sort_keys=True).encode()
        ).hexdigest()
        self.db.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
            {"key": f"feeding-measure:{self.tenant_id}:{payload['idempotency_key']}"},
        )
        prior = (
            self.db.execute(
                text("""SELECT * FROM domain_agrar.feeding_actual_measures
          WHERE tenant_id=:tenant_id AND idempotency_key=:key"""),
                {"tenant_id": self.tenant_id, "key": payload["idempotency_key"]},
            )
            .mappings()
            .first()
        )
        if prior:
            if prior["request_hash"] != digest:
                raise ActualMeasureConflict(
                    "Idempotency-Key wurde mit anderem Inhalt verwendet."
                )
            return dict(prior)
        row = (
            self.db.execute(
                text("""INSERT INTO domain_agrar.feeding_actual_measures
          (id,tenant_id,actual_record_id,actual_component_id,group_id,finding,title,
           owner_subject,due_date,reason,idempotency_key,request_hash,created_by)
          VALUES (:id,:tenant_id,:record_id,:component_id,:group_id,CAST(:finding AS jsonb),
           :title,:owner_subject,:due_date,:reason,:idempotency_key,:hash,:actor) RETURNING *"""),
                {
                    **payload,
                    "id": str(uuid7()),
                    "tenant_id": self.tenant_id,
                    "record_id": finding["actual_record_id"],
                    "component_id": finding["actual_component_id"],
                    "group_id": finding["group_id"],
                    "finding": json.dumps(finding, default=str),
                    "hash": digest,
                    "actor": self.actor,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return dict(row)

    def list_measures(self, *, group_ids: list[str]) -> list[dict[str, Any]]:
        if not group_ids:
            return []
        return [
            dict(row)
            for row in self.db.execute(
                text("""SELECT * FROM
          domain_agrar.feeding_actual_measures WHERE tenant_id=:tenant_id
          AND group_id=ANY(:group_ids) ORDER BY due_date,created_at"""),
                {"tenant_id": self.tenant_id, "group_ids": group_ids},
            )
            .mappings()
            .all()
        ]
