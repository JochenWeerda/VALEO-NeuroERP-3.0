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
    build_feeding_plan_report,
    content_hash,
    feeding_plan_csv,
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
        raise ValueError(f"Unbekannter Berichtstyp: {report_type}")

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
        raise ValueError(f"CSV-Export fuer Berichtstyp {report['report_type']} nicht definiert.")
