"""Application service for tenant-safe, versioned feed analyses."""

from __future__ import annotations

import json
from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.feed_analysis import (
    AnalysisStatus,
    evaluate_analysis,
    normalize_analysis_value,
    transition_analysis,
)
from app.core.uuid7 import uuid7
from app.agrar.rations.events import emit_feeding_event


class FeedAnalysisNotFound(LookupError):
    pass


class FeedAnalysisConflict(ValueError):
    pass


class FeedingFeedAnalysisService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    def _head(self, analysis_id: str, *, lock: bool = False) -> dict[str, Any]:
        suffix = " FOR UPDATE" if lock else ""
        row = (
            self.db.execute(
                text(
                    """
          SELECT * FROM domain_shared.grundfutter_analysen
          WHERE tenant_id=:tenant_id AND id=:analysis_id
        """
                    + suffix
                ),
                {"tenant_id": self.tenant_id, "analysis_id": analysis_id},
            )
            .mappings()
            .first()
        )
        if not row:
            raise FeedAnalysisNotFound("Futteranalyse nicht gefunden.")
        return dict(row)

    def _assert_feed(self, feed_id: str | None) -> None:
        if feed_id is None:
            return
        exists = self.db.execute(
            text("""
          SELECT 1 FROM domain_shared.futtermittel_einzelfutter
          WHERE tenant_id=:tenant_id AND id=:feed_id
        """),
            {"tenant_id": self.tenant_id, "feed_id": feed_id},
        ).scalar()
        if not exists:
            raise FeedAnalysisConflict(
                "Zugeordnetes Futtermittel wurde nicht gefunden."
            )

    def list_analyses(
        self,
        *,
        status: str | None = None,
        feed_id: str | None = None,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = (
            self.db.execute(
                text("""
          SELECT id,tenant_id,feed_id,scope_code,bezeichnung,probe_nr,probenart,labor,analyse_datum,
                 status,is_active,valid_from,valid_until,revision,updated_at
          FROM domain_shared.grundfutter_analysen
          WHERE tenant_id=:tenant_id
            AND (:status IS NULL OR status=:status)
            AND (:feed_id IS NULL OR feed_id=:feed_id)
            AND (:search IS NULL OR bezeichnung ILIKE '%' || :search || '%'
                 OR probe_nr ILIKE '%' || :search || '%')
          ORDER BY is_active DESC, analyse_datum DESC NULLS LAST, created_at DESC
        """),
                {
                    "tenant_id": self.tenant_id,
                    "status": status,
                    "feed_id": feed_id,
                    "search": search,
                },
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def values(self, analysis_id: str) -> list[dict[str, Any]]:
        self._head(analysis_id)
        rows = (
            self.db.execute(
                text("""
          SELECT DISTINCT ON (nutrient_code) * FROM domain_shared.feeding_feed_analysis_values
          WHERE tenant_id=:tenant_id AND analysis_id=:analysis_id
          ORDER BY nutrient_code,revision DESC
        """),
                {"tenant_id": self.tenant_id, "analysis_id": analysis_id},
            )
            .mappings()
            .all()
        )
        result = [dict(row) for row in rows]
        for row in result:
            row["estimated"] = row["value_status"] == "estimated"
        return result

    def findings(self, analysis_id: str) -> list[dict[str, Any]]:
        self._head(analysis_id)
        rows = (
            self.db.execute(
                text("""
          SELECT * FROM domain_shared.feeding_feed_analysis_findings
          WHERE tenant_id=:tenant_id AND analysis_id=:analysis_id
          ORDER BY CASE severity WHEN 'blocker' THEN 0 WHEN 'warning' THEN 1 ELSE 2 END,code
        """),
                {"tenant_id": self.tenant_id, "analysis_id": analysis_id},
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def get_analysis(self, analysis_id: str) -> dict[str, Any]:
        head = self._head(analysis_id)
        head["values"] = self.values(analysis_id)
        head["findings"] = self.findings(analysis_id)
        return head

    def history(self, analysis_id: str) -> list[dict[str, Any]]:
        self._head(analysis_id)
        rows = (
            self.db.execute(
                text("""
          SELECT * FROM domain_shared.feeding_feed_analysis_revisions
          WHERE tenant_id=:tenant_id AND analysis_id=:analysis_id ORDER BY revision DESC
        """),
                {"tenant_id": self.tenant_id, "analysis_id": analysis_id},
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def create_analysis(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._assert_feed(payload.get("feed_id"))
        analysis_id = str(payload.get("id") or uuid7())
        status = AnalysisStatus(payload.get("status", AnalysisStatus.DRAFT))
        if status not in {
            AnalysisStatus.UPLOADED,
            AnalysisStatus.MAPPED,
            AnalysisStatus.DRAFT,
        }:
            raise FeedAnalysisConflict(
                "Neue Analysen duerfen nur uploaded, mapped oder draft sein."
            )
        valid_from = payload.get("valid_from") or date.today()
        if payload.get("valid_until") and payload["valid_until"] < valid_from:
            raise FeedAnalysisConflict("Gueltigkeitsende liegt vor dem Beginn.")
        try:
            self.db.execute(
                text("""
              INSERT INTO domain_shared.grundfutter_analysen
                (id,tenant_id,feed_id,scope_code,bezeichnung,probe_nr,probenart,labor,analyse_datum,
                 method,sampled_at,valid_from,valid_until,original_document_id,original_sha256,
                 quelle_datei,status,is_active,revision,changed_by,notizen)
              VALUES
                (:id,:tenant_id,:feed_id,:scope_code,:bezeichnung,:probe_nr,:probenart,:labor,:analyse_datum,
                 :method,:sampled_at,:valid_from,:valid_until,:original_document_id,:original_sha256,
                 :quelle_datei,:status,false,1,:actor,:notizen)
            """),
                {
                    "id": analysis_id,
                    "tenant_id": self.tenant_id,
                    "actor": self.actor,
                    "feed_id": payload.get("feed_id"),
                    "bezeichnung": payload["bezeichnung"],
                    "scope_code": payload.get("scope_code", "default"),
                    "probe_nr": payload.get("probe_nr"),
                    "probenart": payload.get("probenart"),
                    "labor": payload.get("labor"),
                    "analyse_datum": payload.get("analyse_datum"),
                    "method": payload.get("method"),
                    "sampled_at": payload.get("sampled_at"),
                    "valid_from": valid_from,
                    "valid_until": payload.get("valid_until"),
                    "original_document_id": payload.get("original_document_id"),
                    "original_sha256": payload.get("original_sha256"),
                    "quelle_datei": payload.get("quelle_datei"),
                    "status": status.value,
                    "notizen": payload.get("notizen"),
                },
            )
            for value in payload.get("values") or []:
                self._add_value(analysis_id, value)
            self._append_revision(analysis_id, 1, "Anlage")
            self.db.commit()
            return self.get_analysis(analysis_id)
        except Exception:
            self.db.rollback()
            raise

    def record_legacy_create(self, analysis_id: str) -> dict[str, Any]:
        """Attach the canonical audit contract to a head created by the legacy parser."""
        head = self._head(analysis_id, lock=True)
        existing = self.db.execute(
            text("""
          SELECT 1 FROM domain_shared.feeding_feed_analysis_revisions
          WHERE tenant_id=:tenant_id AND analysis_id=:analysis_id AND revision=:revision
        """),
            {
                "tenant_id": self.tenant_id,
                "analysis_id": analysis_id,
                "revision": int(head["revision"]),
            },
        ).scalar()
        if not existing:
            self._append_revision(
                analysis_id,
                int(head["revision"]),
                "Anlage ueber kompatible Grundfutteranalyse-API",
            )
        self.db.commit()
        return self.get_analysis(analysis_id)

    def record_legacy_update(
        self, analysis_id: str, *, verified: bool, reason: str
    ) -> dict[str, Any]:
        head = self._head(analysis_id, lock=True)
        if head["status"] in {
            AnalysisStatus.RELEASED.value,
            AnalysisStatus.SUPERSEDED.value,
            AnalysisStatus.REJECTED.value,
        }:
            raise FeedAnalysisConflict("Abgeschlossene Analysen sind unveraenderlich.")
        revision = int(head["revision"]) + 1
        target_status = AnalysisStatus.VALIDATED.value if verified else head["status"]
        self.db.execute(
            text("""
          UPDATE domain_shared.grundfutter_analysen
          SET status=:status,revision=:revision,updated_at=now(),changed_by=:actor
          WHERE tenant_id=:tenant_id AND id=:analysis_id
        """),
            {
                "status": target_status,
                "revision": revision,
                "actor": self.actor,
                "tenant_id": self.tenant_id,
                "analysis_id": analysis_id,
            },
        )
        self._append_revision(analysis_id, revision, reason)
        self.db.commit()
        return self.get_analysis(analysis_id)

    def add_value(self, analysis_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        head = self._head(analysis_id, lock=True)
        if head["status"] in {
            AnalysisStatus.RELEASED.value,
            AnalysisStatus.SUPERSEDED.value,
            AnalysisStatus.REJECTED.value,
        }:
            raise FeedAnalysisConflict("Abgeschlossene Analysen sind unveraenderlich.")
        try:
            row = self._add_value(analysis_id, payload)
            revision = int(head["revision"]) + 1
            self.db.execute(
                text("""
              UPDATE domain_shared.grundfutter_analysen SET revision=:revision,updated_at=now(),changed_by=:actor
              WHERE tenant_id=:tenant_id AND id=:analysis_id
            """),
                {
                    "revision": revision,
                    "actor": self.actor,
                    "tenant_id": self.tenant_id,
                    "analysis_id": analysis_id,
                },
            )
            self._append_revision(
                analysis_id, revision, f"Analysewert {row['nutrient_code']} erfasst"
            )
            self.db.commit()
            return row
        except Exception:
            self.db.rollback()
            raise

    def _add_value(self, analysis_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = normalize_analysis_value(
            payload["nutrient_code"],
            payload["original_value"],
            payload["original_unit_code"],
            payload["canonical_unit_code"],
            payload["basis"],
            payload.get("value_status", "measured"),
        )
        revision = int(
            self.db.execute(
                text("""
          SELECT COALESCE(MAX(revision),0)+1 FROM domain_shared.feeding_feed_analysis_values
          WHERE tenant_id=:tenant_id AND analysis_id=:analysis_id AND nutrient_code=:nutrient_code
        """),
                {
                    "tenant_id": self.tenant_id,
                    "analysis_id": analysis_id,
                    "nutrient_code": normalized.nutrient_code,
                },
            ).scalar_one()
        )
        value_id = str(payload.get("id") or uuid7())
        params = {
            "id": value_id,
            "tenant_id": self.tenant_id,
            "analysis_id": analysis_id,
            "nutrient_code": normalized.nutrient_code,
            "original_value": normalized.original_value,
            "original_unit_code": normalized.original_unit_code,
            "canonical_value": normalized.canonical_value,
            "canonical_unit_code": normalized.canonical_unit_code,
            "basis": normalized.basis,
            "value_status": normalized.value_status.value,
            "method": payload.get("method"),
            "detection_limit": payload.get("detection_limit"),
            "confidence": payload.get("confidence"),
            "source_ref": payload.get("source_ref"),
            "revision": revision,
            "actor": self.actor,
        }
        self.db.execute(
            text("""
          INSERT INTO domain_shared.feeding_feed_analysis_values
            (id,tenant_id,analysis_id,nutrient_code,original_value,original_unit_code,
             canonical_value,canonical_unit_code,basis,value_status,method,detection_limit,
             confidence,source_ref,revision,created_by)
          VALUES (:id,:tenant_id,:analysis_id,:nutrient_code,:original_value,:original_unit_code,
                  :canonical_value,:canonical_unit_code,:basis,:value_status,:method,:detection_limit,
                  :confidence,:source_ref,:revision,:actor)
        """),
            params,
        )
        return {**params, "estimated": normalized.estimated}

    def validate(self, analysis_id: str, expected_revision: int) -> dict[str, Any]:
        head = self._head(analysis_id, lock=True)
        if int(head["revision"]) != expected_revision:
            raise FeedAnalysisConflict(
                f"Versionskonflikt: erwartet {expected_revision}, aktuell {head['revision']}."
            )
        if head["status"] not in {
            AnalysisStatus.DRAFT.value,
            AnalysisStatus.VALIDATED.value,
        }:
            raise FeedAnalysisConflict("Nur Entwuerfe koennen validiert werden.")
        findings = evaluate_analysis(self.values(analysis_id))
        if head.get("quelle_datei") and not head.get("original_document_id"):
            findings.append(
                {
                    "code": "original-document-not-archived",
                    "severity": "blocker",
                    "message": "Importierter Originalbeleg ist noch nicht revisionssicher im DMS referenziert.",
                }
            )
        try:
            self.db.execute(
                text("""DELETE FROM domain_shared.feeding_feed_analysis_findings
              WHERE tenant_id=:tenant_id AND analysis_id=:analysis_id"""),
                {"tenant_id": self.tenant_id, "analysis_id": analysis_id},
            )
            for finding in findings:
                self.db.execute(
                    text("""
                  INSERT INTO domain_shared.feeding_feed_analysis_findings
                    (id,tenant_id,analysis_id,code,severity,message,nutrient_code,observed_value)
                  VALUES (:id,:tenant_id,:analysis_id,:code,:severity,:message,:nutrient_code,:observed_value)
                """),
                    {
                        "id": str(uuid7()),
                        "tenant_id": self.tenant_id,
                        "analysis_id": analysis_id,
                        "code": finding["code"],
                        "severity": finding["severity"],
                        "message": finding.get("message", finding["code"]),
                        "nutrient_code": finding.get("nutrient_code"),
                        "observed_value": finding.get("value"),
                    },
                )
            revision = expected_revision + 1
            self.db.execute(
                text("""UPDATE domain_shared.grundfutter_analysen
              SET status='validated',revision=:revision,updated_at=now(),changed_by=:actor
              WHERE tenant_id=:tenant_id AND id=:analysis_id"""),
                {
                    "revision": revision,
                    "actor": self.actor,
                    "tenant_id": self.tenant_id,
                    "analysis_id": analysis_id,
                },
            )
            self._append_revision(analysis_id, revision, "Plausibilitaet validiert")
            self.db.commit()
            return self.get_analysis(analysis_id)
        except Exception:
            self.db.rollback()
            raise

    def transition(
        self,
        analysis_id: str,
        target: AnalysisStatus | str,
        expected_revision: int,
        reason: str,
    ) -> dict[str, Any]:
        head = self._head(analysis_id, lock=True)
        if int(head["revision"]) != expected_revision:
            raise FeedAnalysisConflict(
                f"Versionskonflikt: erwartet {expected_revision}, aktuell {head['revision']}."
            )
        try:
            target_status = transition_analysis(
                head["status"], target, self.findings(analysis_id)
            )
        except ValueError as exc:
            raise FeedAnalysisConflict(str(exc)) from exc
        if target_status == AnalysisStatus.RELEASED and not head.get("feed_id"):
            raise FeedAnalysisConflict(
                "Freigabe erfordert die Zuordnung zu einem Futtermittel."
            )
        revision = expected_revision + 1
        try:
            if target_status == AnalysisStatus.RELEASED:
                replaced = (
                    self.db.execute(
                        text("""
                  SELECT id,revision FROM domain_shared.grundfutter_analysen
                  WHERE tenant_id=:tenant_id AND feed_id=:feed_id AND scope_code=:scope_code
                    AND status='released' AND is_active
                    AND id<>:analysis_id FOR UPDATE
                """),
                        {
                            "tenant_id": self.tenant_id,
                            "feed_id": head["feed_id"],
                            "scope_code": head["scope_code"],
                            "analysis_id": analysis_id,
                        },
                    )
                    .mappings()
                    .all()
                )
                self.db.execute(
                    text("""
                  UPDATE domain_shared.grundfutter_analysen
                  SET status='superseded',is_active=false,revision=revision+1,updated_at=now(),changed_by=:actor
                  WHERE tenant_id=:tenant_id AND feed_id=:feed_id AND scope_code=:scope_code
                    AND status='released' AND is_active AND id<>:analysis_id
                """),
                    {
                        "actor": self.actor,
                        "tenant_id": self.tenant_id,
                        "feed_id": head["feed_id"],
                        "scope_code": head["scope_code"],
                        "analysis_id": analysis_id,
                    },
                )
                for prior in replaced:
                    self._append_revision(
                        str(prior["id"]),
                        int(prior["revision"]) + 1,
                        f"Durch Analyse {analysis_id} ersetzt",
                    )
            self.db.execute(
                text("""
              UPDATE domain_shared.grundfutter_analysen
              SET status=:status,is_active=:active,revision=:revision,updated_at=now(),changed_by=:actor,
                  released_at=CASE WHEN :active THEN now() ELSE released_at END,
                  released_by=CASE WHEN :active THEN :actor ELSE released_by END,
                  verifiziert=CASE WHEN :active THEN true ELSE verifiziert END
              WHERE tenant_id=:tenant_id AND id=:analysis_id
            """),
                {
                    "status": target_status.value,
                    "active": target_status == AnalysisStatus.RELEASED,
                    "revision": revision,
                    "actor": self.actor,
                    "tenant_id": self.tenant_id,
                    "analysis_id": analysis_id,
                },
            )
            self._append_revision(analysis_id, revision, reason)
            if target_status == AnalysisStatus.RELEASED:
                emit_feeding_event(
                    self.db,
                    tenant_id=self.tenant_id,
                    event_type="feeding.analysis.released",
                    aggregate_id=analysis_id,
                    payload={
                        "analysis_id": analysis_id,
                        "feed_id": head["feed_id"],
                        "scope_code": head["scope_code"],
                        "revision": revision,
                        "superseded_analysis_ids": [
                            str(item["id"]) for item in replaced
                        ],
                        "actor": self.actor,
                    },
                )
            self.db.commit()
            return self.get_analysis(analysis_id)
        except Exception:
            self.db.rollback()
            raise

    def attach_document(
        self, analysis_id: str, document_id: str, sha256: str, expected_revision: int
    ) -> dict[str, Any]:
        head = self._head(analysis_id, lock=True)
        if int(head["revision"]) != expected_revision:
            raise FeedAnalysisConflict(
                f"Versionskonflikt: erwartet {expected_revision}, aktuell {head['revision']}."
            )
        digest = sha256.lower()
        if len(digest) != 64 or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise FeedAnalysisConflict("SHA-256 des Originalbelegs ist ungueltig.")
        revision = expected_revision + 1
        self.db.execute(
            text("""UPDATE domain_shared.grundfutter_analysen
          SET original_document_id=:document_id,original_sha256=:digest,revision=:revision,
              updated_at=now(),changed_by=:actor WHERE tenant_id=:tenant_id AND id=:analysis_id"""),
            {
                "document_id": document_id,
                "digest": digest,
                "revision": revision,
                "actor": self.actor,
                "tenant_id": self.tenant_id,
                "analysis_id": analysis_id,
            },
        )
        self._append_revision(analysis_id, revision, "Originalbeleg referenziert")
        self.db.commit()
        return self.get_analysis(analysis_id)

    def _append_revision(self, analysis_id: str, revision: int, reason: str) -> None:
        head = self._head(analysis_id)
        snapshot = {
            key: value
            for key, value in head.items()
            if key not in {"updated_at", "created_at"}
        }
        self.db.execute(
            text("""
          INSERT INTO domain_shared.feeding_feed_analysis_revisions
            (id,tenant_id,analysis_id,revision,snapshot,reason,changed_by)
          VALUES (:id,:tenant_id,:analysis_id,:revision,CAST(:snapshot AS jsonb),:reason,:actor)
        """),
            {
                "id": str(uuid7()),
                "tenant_id": self.tenant_id,
                "analysis_id": analysis_id,
                "revision": revision,
                "snapshot": json.dumps(snapshot, default=str, ensure_ascii=False),
                "reason": reason,
                "actor": self.actor,
            },
        )
