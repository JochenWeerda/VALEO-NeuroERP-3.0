"""Beratungsfaelle und Beobachtungen (FEED-CONS-031).

Faelle buendeln Beobachtungen, DMS-Fotoreferenzen und fachliche Verknuepfungen
chronologisch je Betrieb/Gruppe. Beobachtungen sind append-only; der mobile
Erfassungspfad ist ueber (tenant, case, client_ref) idempotent — doppelte
Einreichung liefert dieselbe Beobachtung statt einer Dublette.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


class ConsultingCaseClosedError(ValueError):
    """Geschlossene Faelle nehmen keine neuen Beobachtungen an."""


class FeedingConsultingService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    def _assert_ref(self, table: str, ref_id: str | None, message: str) -> None:
        if ref_id is None:
            return
        row = self.db.execute(text(
            f"SELECT 1 FROM domain_agrar.{table} WHERE tenant_id=:tenant_id AND id=:ref_id"
        ), {"tenant_id": self.tenant_id, "ref_id": ref_id}).first()
        if not row:
            raise LookupError(message)

    def create_case(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._assert_ref("feeding_businesses", payload.get("business_id"),
                         "Fuetterungsbetrieb nicht gefunden.")
        self._assert_ref("feeding_groups", payload.get("group_id"),
                         "Fuetterungsgruppe nicht gefunden.")
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.consulting_cases
            (id,tenant_id,business_id,group_id,case_type,title,initial_situation,created_by)
          VALUES (:id,:tenant_id,:business_id,:group_id,:case_type,:title,:initial_situation,:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id,
               "business_id": payload.get("business_id"), "group_id": payload.get("group_id"),
               "case_type": payload["case_type"], "title": payload["title"],
               "initial_situation": payload.get("initial_situation"),
               "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)

    def list_cases(self, *, status: str | None = None) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT c.*,
            (SELECT count(*) FROM domain_agrar.consulting_observations o
              WHERE o.tenant_id=c.tenant_id AND o.case_id=c.id)::int AS observation_count
          FROM domain_agrar.consulting_cases c
          WHERE c.tenant_id=:tenant_id AND (:status IS NULL OR c.status=:status)
          ORDER BY c.created_at DESC
        """), {"tenant_id": self.tenant_id, "status": status}).mappings().all()
        return [dict(row) for row in rows]

    def _case(self, case_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT * FROM domain_agrar.consulting_cases
          WHERE tenant_id=:tenant_id AND id=:case_id
        """), {"tenant_id": self.tenant_id, "case_id": case_id}).mappings().first()
        if not row:
            raise LookupError("Beratungsfall nicht gefunden.")
        return dict(row)

    def get_case(self, case_id: str) -> dict[str, Any]:
        case = self._case(case_id)
        observations = self.db.execute(text("""
          SELECT * FROM domain_agrar.consulting_observations
          WHERE tenant_id=:tenant_id AND case_id=:case_id
          ORDER BY created_at
        """), {"tenant_id": self.tenant_id, "case_id": case_id}).mappings().all()
        case["observations"] = [dict(observation) for observation in observations]
        return case

    def add_observation(self, case_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        case = self._case(case_id)
        if case["status"] != "open":
            raise ConsultingCaseClosedError(
                "Der Beratungsfall ist abgeschlossen — fuer neue Beobachtungen einen Folgefall anlegen.")
        self._assert_ref("rations", payload.get("ration_id"), "Ration nicht gefunden.")

        existing = self.db.execute(text("""
          SELECT * FROM domain_agrar.consulting_observations
          WHERE tenant_id=:tenant_id AND case_id=:case_id AND client_ref=:client_ref
        """), {"tenant_id": self.tenant_id, "case_id": case_id,
               "client_ref": payload["client_ref"]}).mappings().first()
        if existing:
            result = dict(existing)
            result["duplicate"] = True
            return result

        row = self.db.execute(text("""
          INSERT INTO domain_agrar.consulting_observations
            (id,tenant_id,case_id,category,text,photo_document_refs,ration_id,
             analysis_ref,observation_date,client_ref,created_by)
          VALUES (:id,:tenant_id,:case_id,:category,:text,CAST(:photos AS jsonb),:ration_id,
             :analysis_ref,:observation_date,:client_ref,:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id, "case_id": case_id,
               "category": payload["category"], "text": payload["text"],
               "photos": json.dumps(payload.get("photo_document_refs") or [], ensure_ascii=False),
               "ration_id": payload.get("ration_id"),
               "analysis_ref": payload.get("analysis_ref"),
               "observation_date": payload.get("observation_date"),
               "client_ref": payload["client_ref"], "actor": self.actor}).mappings().one()
        self.db.execute(text("""
          UPDATE domain_agrar.consulting_cases SET updated_at=now()
          WHERE tenant_id=:tenant_id AND id=:case_id
        """), {"tenant_id": self.tenant_id, "case_id": case_id})
        self.db.commit()
        result = dict(row)
        result["duplicate"] = False
        return result

    def close_case(self, case_id: str, summary: str) -> dict[str, Any]:
        case = self._case(case_id)
        if case["status"] == "closed":
            return case
        row = self.db.execute(text("""
          UPDATE domain_agrar.consulting_cases
          SET status='closed', closing_summary=:summary, closed_by=:actor,
              closed_at=now(), updated_at=now()
          WHERE tenant_id=:tenant_id AND id=:case_id
          RETURNING *
        """), {"tenant_id": self.tenant_id, "case_id": case_id,
               "summary": summary, "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)
