"""Revisionssichere Berichte (FEED-REP-039).

Erzeugung ist idempotent: gleiche unveraenderliche Quellversion + Profil
liefert denselben Inhalt (content_hash) und denselben bestehenden Datensatz
statt einer Dublette. Berichte sind append-only; PDF-Rendering und
DMS-Zustellung folgen als eigene Slices (dms_document_ref ist vorbereitet).
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.report_profiles import (
    build_consulting_report,
    build_feeding_plan_report,
    build_target_actual_report,
    build_trend_report,
    content_hash,
    feeding_plan_csv,
    target_actual_csv,
    trend_csv,
)
from app.core.uuid7 import uuid7
from app.services.feeding_plan_service import FeedingPlanService


class FeedingReportsService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    def _build_content(self, report_type: str, profile: str, source_ref: str) -> dict[str, Any]:
        if report_type == "feeding_plan":
            plan_version = FeedingPlanService(self.db, self.tenant_id, self.actor).get_version(source_ref)
            return build_feeding_plan_report(plan_version, profile)
        if report_type == "consulting":
            return build_consulting_report(self._consulting_draft(source_ref), profile)
        if report_type == "target_actual":
            plan_version = FeedingPlanService(self.db, self.tenant_id, self.actor).get_version(source_ref)
            return build_target_actual_report(
                plan_version, self._target_actual_aggregation(source_ref), profile)
        if report_type == "trend":
            return build_trend_report(
                self._group(source_ref), self._trend_days(source_ref), profile)
        raise ValueError(f"Unbekannter Berichtstyp: {report_type}")

    def _consulting_draft(self, draft_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT id,case_id,version,content,content_hash
          FROM domain_agrar.consulting_report_drafts
          WHERE tenant_id=:tenant_id AND id=:draft_id
        """), {"tenant_id": self.tenant_id, "draft_id": draft_id}).mappings().first()
        if not row:
            raise LookupError("Berichtsentwurf nicht gefunden.")
        return dict(row)

    def _target_actual_aggregation(self, plan_version_id: str) -> dict[str, Any]:
        components = self.db.execute(text("""
          SELECT c.feed_id, MAX(c.feed_name) AS feed_name, COUNT(*) AS n,
                 SUM(c.target_kg) AS target_kg_sum, SUM(c.actual_kg) AS actual_kg_sum,
                 SUM(c.delta_kg) AS delta_kg_sum
          FROM domain_agrar.feeding_actual_components c
          JOIN domain_agrar.feeding_actual_records r
            ON r.id=c.actual_record_id AND r.tenant_id=c.tenant_id
          WHERE c.tenant_id=:tenant_id AND r.plan_version_id=:plan_version_id
          GROUP BY c.feed_id ORDER BY c.feed_id
        """), {"tenant_id": self.tenant_id, "plan_version_id": plan_version_id}).mappings().all()
        causes = self.db.execute(text("""
          SELECT cause_class, COUNT(*) AS n FROM domain_agrar.feeding_actual_records
          WHERE tenant_id=:tenant_id AND plan_version_id=:plan_version_id
          GROUP BY cause_class ORDER BY cause_class
        """), {"tenant_id": self.tenant_id, "plan_version_id": plan_version_id}).mappings().all()
        return {
            "record_count": sum(int(row["n"]) for row in causes),
            "components": [{
                "feed_id": row["feed_id"],
                "feed_name": row["feed_name"],
                "n": int(row["n"]),
                "target_kg_sum": round(float(row["target_kg_sum"]), 3),
                "actual_kg_sum": round(float(row["actual_kg_sum"]), 3),
                "delta_kg_sum": round(float(row["delta_kg_sum"]), 3),
            } for row in components],
            "cause_breakdown": {row["cause_class"]: int(row["n"]) for row in causes},
        }

    def _group(self, group_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT id,name FROM domain_agrar.feeding_groups
          WHERE tenant_id=:tenant_id AND id=:group_id
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().first()
        if not row:
            raise LookupError("Fuetterungsgruppe nicht gefunden.")
        return dict(row)

    _TREND_NUMERIC_FIELDS = ("actual_milk_kg_cow", "actual_dmi_kg_cow",
                             "actual_fat_pct", "actual_protein_pct")

    def _trend_days(self, group_id: str) -> list[dict[str, Any]]:
        # Bewusst ohne today()-Fenster: gleicher Datenstand => gleicher Inhalt.
        rows = self.db.execute(text("""
          SELECT c.observation_date, c.cow_count, c.actual_milk_kg_cow,
                 c.actual_dmi_kg_cow, c.actual_fat_pct, c.actual_protein_pct,
                 c.source, r.version_no AS ration_version_no,
                 pv.version_no AS plan_version_no
          FROM domain_agrar.feeding_controlling_daily c
          LEFT JOIN domain_agrar.ration_versions r
            ON r.id=c.ration_version_id AND r.tenant_id=c.tenant_id
          LEFT JOIN domain_agrar.feeding_plan_versions pv
            ON pv.id=c.feeding_plan_version_id AND pv.tenant_id=c.tenant_id
          WHERE c.tenant_id=:tenant_id AND c.group_id=:group_id
          ORDER BY c.observation_date, c.recorded_at, c.id
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().all()
        days: list[dict[str, Any]] = []
        for row in rows:
            day = dict(row)
            day["observation_date"] = str(day["observation_date"])
            for key in self._TREND_NUMERIC_FIELDS:
                if day.get(key) is not None:
                    day[key] = float(day[key])
            days.append(day)
        return days

    def create_report(self, *, report_type: str, profile: str, source_ref: str) -> dict[str, Any]:
        content = self._build_content(report_type, profile, source_ref)
        digest = content_hash(content)

        existing = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_reports
          WHERE tenant_id=:tenant_id AND report_type=:report_type
            AND source_ref=:source_ref AND profile=:profile AND content_hash=:hash
        """), {"tenant_id": self.tenant_id, "report_type": report_type,
               "source_ref": source_ref, "profile": profile, "hash": digest}).mappings().first()
        if existing:
            result = dict(existing)
            result["duplicate"] = True
            return result

        row = self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_reports
            (id,tenant_id,report_type,profile,source_ref,content,content_hash,created_by)
          VALUES (:id,:tenant_id,:report_type,:profile,:source_ref,
                  CAST(:content AS jsonb),:hash,:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id,
               "report_type": report_type, "profile": profile, "source_ref": source_ref,
               "content": json.dumps(content, ensure_ascii=False, sort_keys=True),
               "hash": digest, "actor": self.actor}).mappings().one()
        self.db.commit()
        result = dict(row)
        result["duplicate"] = False
        return result

    def list_reports(self, *, source_ref: str | None = None) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT id,tenant_id,report_type,profile,source_ref,content_hash,
                 dms_document_ref,created_by,created_at
          FROM domain_agrar.feeding_reports
          WHERE tenant_id=:tenant_id AND (:source_ref IS NULL OR source_ref=:source_ref)
          ORDER BY created_at DESC
        """), {"tenant_id": self.tenant_id, "source_ref": source_ref}).mappings().all()
        return [dict(row) for row in rows]

    def get_report(self, report_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_reports
          WHERE tenant_id=:tenant_id AND id=:report_id
        """), {"tenant_id": self.tenant_id, "report_id": report_id}).mappings().first()
        if not row:
            raise LookupError("Bericht nicht gefunden.")
        return dict(row)

    def report_csv(self, report_id: str) -> str:
        report = self.get_report(report_id)
        if report["report_type"] == "feeding_plan":
            return feeding_plan_csv(report["content"])
        if report["report_type"] == "target_actual":
            return target_actual_csv(report["content"])
        if report["report_type"] == "trend":
            return trend_csv(report["content"])
        raise ValueError(
            f"CSV-Export fuer Berichtstyp {report['report_type']} nicht definiert "
            "(narrative Berichte werden nicht als CSV ausgegeben)."
        )
