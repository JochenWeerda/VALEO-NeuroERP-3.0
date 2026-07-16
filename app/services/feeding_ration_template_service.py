"""Commands for immutable ration templates and read model for the feeding business file."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.agrar.rations.ration_templates import normalize_template_name, validate_copy_reason
from app.core.uuid7 import uuid7
from app.services.rations_lifecycle_service import RationLifecycleNotFound, RationLifecycleService


class RationTemplateNotFound(LookupError):
    pass


class RationTemplateConflict(RuntimeError):
    pass


class FeedingRationTemplateService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db = db
        self.tenant_id = tenant_id
        self.actor = actor or "unknown"

    def create(self, *, name: str, description: str | None, source_version_id: str) -> dict[str, Any]:
        source = self.db.execute(text("""
          SELECT rv.id AS source_ration_version_id,r.group_id,g.business_id,r.name AS source_ration_name,
                 rv.version_no AS source_version_no,rv.snapshot_checksum
          FROM domain_agrar.ration_versions rv
          JOIN domain_agrar.rations r ON r.tenant_id=rv.tenant_id AND r.id=rv.ration_id
          JOIN domain_agrar.feeding_groups g ON g.tenant_id=r.tenant_id AND g.id=r.group_id
          WHERE rv.tenant_id=:tenant_id AND rv.id=:version_id AND g.business_id IS NOT NULL
        """), {"tenant_id": self.tenant_id, "version_id": source_version_id}).mappings().first()
        if not source:
            raise RationTemplateNotFound("Quellversion mit Fuetterungsbetrieb nicht gefunden.")
        try:
            row = self.db.execute(text("""
              INSERT INTO domain_agrar.ration_templates
                (id,tenant_id,business_id,group_id,name,description,source_ration_version_id,created_by)
              VALUES (:id,:tenant_id,:business_id,:group_id,:name,:description,:source_version_id,:actor)
              RETURNING *
            """), {
                "id": str(uuid7()), "tenant_id": self.tenant_id,
                "business_id": source["business_id"], "group_id": source["group_id"],
                "name": normalize_template_name(name), "description": description,
                "source_version_id": source_version_id, "actor": self.actor,
            }).mappings().one()
            self.db.commit()
            return {**dict(row), **{key: source[key] for key in ("source_ration_name", "source_version_no", "snapshot_checksum")}}
        except IntegrityError as exc:
            self.db.rollback()
            raise RationTemplateConflict("Eine Vorlage mit diesem Namen existiert im Betrieb bereits.") from exc

    def get(self, template_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT t.*,r.name AS source_ration_name,rv.version_no AS source_version_no,rv.snapshot_checksum
          FROM domain_agrar.ration_templates t
          JOIN domain_agrar.ration_versions rv ON rv.tenant_id=t.tenant_id AND rv.id=t.source_ration_version_id
          JOIN domain_agrar.rations r ON r.tenant_id=rv.tenant_id AND r.id=rv.ration_id
          WHERE t.tenant_id=:tenant_id AND t.id=:template_id
        """), {"tenant_id": self.tenant_id, "template_id": template_id}).mappings().first()
        if not row:
            raise RationTemplateNotFound("Rationsvorlage nicht gefunden.")
        return dict(row)

    def list_for_business(self, business_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT t.*,r.name AS source_ration_name,rv.version_no AS source_version_no,rv.snapshot_checksum
          FROM domain_agrar.ration_templates t
          JOIN domain_agrar.ration_versions rv ON rv.tenant_id=t.tenant_id AND rv.id=t.source_ration_version_id
          JOIN domain_agrar.rations r ON r.tenant_id=rv.tenant_id AND r.id=rv.ration_id
          WHERE t.tenant_id=:tenant_id AND t.business_id=:business_id
          ORDER BY t.created_at DESC
        """), {"tenant_id": self.tenant_id, "business_id": business_id}).mappings().all()
        return [dict(row) for row in rows]
    def apply(self, *, template_id: str, target_ration_id: str,
              expected_latest_version_no: int, reason: str) -> dict[str, Any]:
        template = self.db.execute(text("""
          SELECT t.*,rv.snapshot
          FROM domain_agrar.ration_templates t
          JOIN domain_agrar.ration_versions rv ON rv.tenant_id=t.tenant_id AND rv.id=t.source_ration_version_id
          WHERE t.tenant_id=:tenant_id AND t.id=:template_id
        """), {"tenant_id": self.tenant_id, "template_id": template_id}).mappings().first()
        if not template:
            raise RationTemplateNotFound("Rationsvorlage nicht gefunden.")
        target = self.db.execute(text("""
          SELECT r.id,r.group_id FROM domain_agrar.rations r
          WHERE r.tenant_id=:tenant_id AND r.id=:ration_id
        """), {"tenant_id": self.tenant_id, "ration_id": target_ration_id}).mappings().first()
        if not target:
            raise RationLifecycleNotFound("Zielration nicht gefunden.")
        if target["group_id"] != template["group_id"]:
            raise RationTemplateConflict("Vorlagen duerfen nur innerhalb derselben Fuetterungsgruppe kopiert werden.")
        return RationLifecycleService(self.db, self.tenant_id, self.actor).create_version(
            ration_id=target_ration_id, snapshot=dict(template["snapshot"]), source="template",
            comment=validate_copy_reason(reason), based_on_version_id=template["source_ration_version_id"],
            expected_latest_version_no=expected_latest_version_no,
        )

    def business_overview(self, business_id: str) -> dict[str, Any]:
        business = self.db.execute(text("""
          SELECT b.*,
            (SELECT count(*)::int FROM domain_agrar.feeding_groups g WHERE g.tenant_id=b.tenant_id AND g.business_id=b.id) AS group_count,
            (SELECT count(*)::int FROM domain_agrar.rations r JOIN domain_agrar.feeding_groups g ON g.tenant_id=r.tenant_id AND g.id=r.group_id WHERE r.tenant_id=b.tenant_id AND g.business_id=b.id) AS ration_count,
            (SELECT count(*)::int FROM domain_agrar.ration_templates t WHERE t.tenant_id=b.tenant_id AND t.business_id=b.id) AS template_count
          FROM domain_agrar.feeding_businesses b
          WHERE b.tenant_id=:tenant_id AND b.id=:business_id
        """), {"tenant_id": self.tenant_id, "business_id": business_id}).mappings().first()
        if not business:
            raise RationTemplateNotFound("Fuetterungsbetrieb nicht gefunden.")
        rations = self.list_business_rations(business_id)
        result = dict(business)
        result["active_ration_count"] = sum(item["status"] == "active" for item in rations)
        result["readiness_unknown_count"] = sum(item["readiness_status"] == "not_checked" for item in rations)
        result["readiness_blocked_count"] = sum(item["readiness_blockers"] > 0 for item in rations)
        result["data_status"] = "empty" if not rations else ("incomplete" if result["readiness_unknown_count"] else "available")
        return result

    def list_business_groups(self, business_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT g.id,g.name,g.animal_count,g.profile_code,g.risk_level,g.active,g.updated_at,
                 count(DISTINCT r.id)::int AS ration_count
          FROM domain_agrar.feeding_groups g
          LEFT JOIN domain_agrar.rations r ON r.tenant_id=g.tenant_id AND r.group_id=g.id
          WHERE g.tenant_id=:tenant_id AND g.business_id=:business_id
          GROUP BY g.id ORDER BY g.active DESC,g.name
        """), {"tenant_id": self.tenant_id, "business_id": business_id}).mappings().all()
        return [dict(row) for row in rows]

    def list_business_rations(self, business_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT r.id,r.name,r.group_id,g.name AS group_name,rv.id AS version_id,rv.version_no,
                 lc.status,r.updated_at,
                 COALESCE(rv.snapshot->'readiness'->>'status','not_checked') AS readiness_status,
                 COALESCE((rv.snapshot->'readiness'->>'blocker_count')::int,0) AS readiness_blockers,
                 COALESCE((rv.snapshot->'readiness'->>'warning_count')::int,0) AS readiness_warnings
          FROM domain_agrar.rations r
          JOIN domain_agrar.feeding_groups g ON g.tenant_id=r.tenant_id AND g.id=r.group_id
          JOIN LATERAL (SELECT * FROM domain_agrar.ration_versions x WHERE x.tenant_id=r.tenant_id AND x.ration_id=r.id ORDER BY x.version_no DESC LIMIT 1) rv ON TRUE
          JOIN domain_agrar.ration_version_lifecycle lc ON lc.tenant_id=rv.tenant_id AND lc.version_id=rv.id
          WHERE r.tenant_id=:tenant_id AND g.business_id=:business_id ORDER BY (lc.status='active') DESC,r.updated_at DESC
        """), {"tenant_id": self.tenant_id, "business_id": business_id}).mappings().all()
        return [dict(row) for row in rows]

    def list_business_findings(self, business_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT e.id AS evaluation_id,r.id AS ration_id,r.name AS ration_name,g.name AS group_name,
                 finding->>'code' AS code,finding->>'severity' AS severity,finding->>'message' AS message,
                 e.evaluated_at
          FROM domain_agrar.ration_evaluations e
          JOIN domain_agrar.rations r ON r.tenant_id=e.tenant_id AND r.id=e.ration_id
          JOIN domain_agrar.feeding_groups g ON g.tenant_id=r.tenant_id AND g.id=r.group_id
          CROSS JOIN LATERAL jsonb_array_elements(e.findings) finding
          WHERE e.tenant_id=:tenant_id AND g.business_id=:business_id
            AND e.evaluated_at=(SELECT max(e2.evaluated_at) FROM domain_agrar.ration_evaluations e2 WHERE e2.tenant_id=e.tenant_id AND e2.ration_version_id=e.ration_version_id)
          ORDER BY CASE finding->>'severity' WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,e.evaluated_at DESC
        """), {"tenant_id": self.tenant_id, "business_id": business_id}).mappings().all()
        return [dict(row) for row in rows]
