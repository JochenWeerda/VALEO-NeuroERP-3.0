"""Reproducible report-draft projection for consulting cases."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


class ConsultingReportConflict(RuntimeError):
    pass


class FeedingConsultingReportService:
    def __init__(
        self, db: Session, tenant_id: str, actor: str, *, unrestricted: bool = False
    ):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor or "unknown"
        self.unrestricted = unrestricted

    def _case(self, case_id: str, *, scope: str = "read") -> dict[str, Any]:
        scopes = (
            ["read", "write", "approve", "admin"]
            if scope == "read"
            else ["write", "approve", "admin"]
        )
        row = (
            self.db.execute(
                text("""SELECT c.* FROM domain_agrar.consulting_cases c
          LEFT JOIN domain_agrar.feeding_groups g
            ON g.tenant_id=c.tenant_id AND g.id=c.group_id
          WHERE c.tenant_id=:tenant_id AND c.id=:case_id AND (
            :unrestricted OR c.created_by=:actor OR g.created_by=:actor OR EXISTS (
              SELECT 1 FROM domain_agrar.feeding_business_grants grant_row
              WHERE grant_row.tenant_id=c.tenant_id
                AND grant_row.business_id=COALESCE(c.business_id,g.business_id)
                AND grant_row.subject=:actor AND grant_row.scope=ANY(:scopes)
                AND grant_row.revoked_at IS NULL AND grant_row.valid_from<=now()
                AND (grant_row.valid_until IS NULL OR grant_row.valid_until>now())
            ))"""),
                {
                    "tenant_id": self.tenant_id,
                    "case_id": case_id,
                    "actor": self.actor,
                    "scopes": scopes,
                    "unrestricted": self.unrestricted,
                },
            )
            .mappings()
            .first()
        )
        if not row:
            raise LookupError("Beratungsfall nicht gefunden.")
        return dict(row)

    def link_measure(self, case_id: str, measure_id: str) -> dict[str, Any]:
        case = self._case(case_id, scope="write")
        measure = (
            self.db.execute(
                text("""SELECT m.id,m.group_id,g.business_id
          FROM domain_agrar.feeding_actual_measures m
          JOIN domain_agrar.feeding_groups g
            ON g.tenant_id=m.tenant_id AND g.id=m.group_id
          LEFT JOIN domain_agrar.feeding_businesses b
            ON b.tenant_id=g.tenant_id AND b.id=g.business_id
          WHERE m.tenant_id=:tenant_id AND m.id=:measure_id AND (
            :unrestricted OR g.created_by=:actor OR b.created_by=:actor OR EXISTS (
              SELECT 1 FROM domain_agrar.feeding_business_grants grant_row
              WHERE grant_row.tenant_id=m.tenant_id
                AND grant_row.business_id=g.business_id
                AND grant_row.subject=:actor
                AND grant_row.scope=ANY(:scopes)
                AND grant_row.revoked_at IS NULL AND grant_row.valid_from<=now()
                AND (grant_row.valid_until IS NULL OR grant_row.valid_until>now())
            ))"""),
                {
                    "tenant_id": self.tenant_id,
                    "measure_id": measure_id,
                    "actor": self.actor,
                    "scopes": ["write", "approve", "admin"],
                    "unrestricted": self.unrestricted,
                },
            )
            .mappings()
            .first()
        )
        if not measure:
            raise LookupError("Massnahme nicht gefunden.")
        if case.get("group_id") and case["group_id"] != measure["group_id"]:
            raise ConsultingReportConflict(
                "Fall und Massnahme muessen dieselbe Fuetterungsgruppe besitzen."
            )
        if case.get("business_id") and case["business_id"] != measure["business_id"]:
            raise ConsultingReportConflict(
                "Fall und Massnahme muessen demselben Betrieb zugeordnet sein."
            )
        self.db.execute(
            text("""INSERT INTO domain_agrar.consulting_case_measures
          (id,tenant_id,case_id,measure_id,linked_by)
          VALUES (:id,:tenant_id,:case_id,:measure_id,:actor)
          ON CONFLICT (tenant_id,case_id,measure_id) DO NOTHING"""),
            {
                "id": str(uuid7()),
                "tenant_id": self.tenant_id,
                "case_id": case_id,
                "measure_id": measure_id,
                "actor": self.actor,
            },
        )
        row = (
            self.db.execute(
                text("""SELECT * FROM domain_agrar.consulting_case_measures
          WHERE tenant_id=:tenant_id AND case_id=:case_id AND measure_id=:measure_id"""),
                {
                    "tenant_id": self.tenant_id,
                    "case_id": case_id,
                    "measure_id": measure_id,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return dict(row)

    def _content(self, case_id: str) -> dict[str, Any]:
        case = self._case(case_id)
        observations = [
            dict(row)
            for row in self.db.execute(
                text("""SELECT id,category,text,
          photo_document_refs,ration_id,analysis_ref,observation_date,created_by,created_at
          FROM domain_agrar.consulting_observations WHERE tenant_id=:tenant_id AND case_id=:case_id
          ORDER BY created_at,id"""),
                {
                    "tenant_id": self.tenant_id,
                    "case_id": case_id,
                },
            )
            .mappings()
            .all()
        ]
        measures = [
            dict(row)
            for row in self.db.execute(
                text("""SELECT
          link.measure_id,m.title,v.version,v.status,v.owner_subject,v.due_date,
          v.reminder_date,v.escalation_status,v.effectiveness,v.effectiveness_result
          FROM domain_agrar.consulting_case_measures link
          JOIN domain_agrar.feeding_actual_measures m
            ON m.tenant_id=link.tenant_id AND m.id=link.measure_id
          JOIN LATERAL (SELECT mv.* FROM domain_agrar.feeding_measure_versions mv
            WHERE mv.tenant_id=link.tenant_id AND mv.measure_id=link.measure_id
            ORDER BY mv.version DESC LIMIT 1) v ON TRUE
          WHERE link.tenant_id=:tenant_id AND link.case_id=:case_id
          ORDER BY m.title,link.measure_id"""),
                {
                    "tenant_id": self.tenant_id,
                    "case_id": case_id,
                },
            )
            .mappings()
            .all()
        ]
        return {
            "schema_version": "1.0",
            "case": {
                key: case.get(key)
                for key in (
                    "id",
                    "business_id",
                    "group_id",
                    "case_type",
                    "title",
                    "initial_situation",
                    "status",
                    "closing_summary",
                    "created_by",
                    "created_at",
                    "closed_by",
                    "closed_at",
                )
            },
            "observations": observations,
            "measures": measures,
        }

    def list_measures(self, case_id: str) -> list[dict[str, Any]]:
        self._case(case_id)
        return [
            dict(row)
            for row in self.db.execute(
                text("""SELECT link.measure_id,m.title,v.version,v.status,
          v.owner_subject,v.due_date,v.reminder_date,v.escalation_status,
          v.effectiveness,v.effectiveness_result
          FROM domain_agrar.consulting_case_measures link
          JOIN domain_agrar.feeding_actual_measures m
            ON m.tenant_id=link.tenant_id AND m.id=link.measure_id
          JOIN LATERAL (SELECT mv.* FROM domain_agrar.feeding_measure_versions mv
            WHERE mv.tenant_id=link.tenant_id AND mv.measure_id=link.measure_id
            ORDER BY mv.version DESC LIMIT 1) v ON TRUE
          WHERE link.tenant_id=:tenant_id AND link.case_id=:case_id
          ORDER BY v.due_date,m.title"""),
                {"tenant_id": self.tenant_id, "case_id": case_id},
            )
            .mappings()
            .all()
        ]

    def create_draft(self, case_id: str, reason: str) -> dict[str, Any]:
        self._case(case_id, scope="write")
        self.db.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
            {"key": f"consulting-report:{self.tenant_id}:{case_id}"},
        )
        content = self._content(case_id)
        serialized = json.dumps(
            content, sort_keys=True, default=str, ensure_ascii=False
        )
        digest = hashlib.sha256(serialized.encode()).hexdigest()
        prior = (
            self.db.execute(
                text("""SELECT * FROM domain_agrar.consulting_report_drafts
          WHERE tenant_id=:tenant_id AND case_id=:case_id AND content_hash=:hash"""),
                {
                    "tenant_id": self.tenant_id,
                    "case_id": case_id,
                    "hash": digest,
                },
            )
            .mappings()
            .first()
        )
        if prior:
            return dict(prior)
        version = (
            int(
                self.db.execute(
                    text("""SELECT COALESCE(MAX(version),0)
          FROM domain_agrar.consulting_report_drafts
          WHERE tenant_id=:tenant_id AND case_id=:case_id"""),
                    {
                        "tenant_id": self.tenant_id,
                        "case_id": case_id,
                    },
                ).scalar_one()
            )
            + 1
        )
        row = (
            self.db.execute(
                text("""INSERT INTO domain_agrar.consulting_report_drafts
          (id,tenant_id,case_id,version,content,content_hash,reason,created_by)
          VALUES (:id,:tenant_id,:case_id,:version,CAST(:content AS jsonb),:hash,:reason,:actor)
          RETURNING *"""),
                {
                    "id": str(uuid7()),
                    "tenant_id": self.tenant_id,
                    "case_id": case_id,
                    "version": version,
                    "content": serialized,
                    "hash": digest,
                    "reason": reason,
                    "actor": self.actor,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return dict(row)

    def list_drafts(self, case_id: str) -> list[dict[str, Any]]:
        self._case(case_id)
        return [
            dict(row)
            for row in self.db.execute(
                text("""SELECT *
          FROM domain_agrar.consulting_report_drafts
          WHERE tenant_id=:tenant_id AND case_id=:case_id ORDER BY version DESC"""),
                {
                    "tenant_id": self.tenant_id,
                    "case_id": case_id,
                },
            )
            .mappings()
            .all()
        ]
