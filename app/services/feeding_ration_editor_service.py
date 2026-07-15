"""Rationseditor: Draft-Bewertung gegen Katalog und Bedarfsprofil (FEED-EDITOR-021).

Reine Lese-/Rechenoperation: aufloesen der Komponenten ueber den kanonischen
Futtermittelkatalog (FEED-CORE-018), Bedarf aus dem persistierten
RequirementProfile (FEED-CORE-020), Bewertung ueber die deterministische
Draft-Funktion (Code-SSOT). Persistiert wird hier nichts — Speichern bleibt
der append-only Lifecycle-Pfad.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.ration_draft import evaluate_draft
from app.core.uuid7 import uuid7
from app.services.feeding_feed_catalog_service import FeedingFeedCatalogService


class EmptyRationVersionError(ValueError):
    """Version ohne Komponenten kann nicht fachlich bewertet werden."""


class FeedingRationEditorService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor
        self._catalog = FeedingFeedCatalogService(db, tenant_id, actor)

    def _requirements(self, group_id: str, requirement_profile_id: str | None) -> tuple[str, dict[str, Any]]:
        if requirement_profile_id:
            row = self.db.execute(text("""
              SELECT id, requirements FROM domain_agrar.requirement_profiles
              WHERE tenant_id=:tenant_id AND id=:profile_id AND group_id=:group_id
            """), {"tenant_id": self.tenant_id, "profile_id": requirement_profile_id,
                   "group_id": group_id}).mappings().first()
        else:
            row = self.db.execute(text("""
              SELECT id, requirements FROM domain_agrar.requirement_profiles
              WHERE tenant_id=:tenant_id AND group_id=:group_id
              ORDER BY created_at DESC LIMIT 1
            """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().first()
        if not row:
            raise LookupError("Kein Bedarfsprofil fuer diese Gruppe gefunden — bitte zuerst Bedarf berechnen.")
        return row["id"], dict(row["requirements"])

    def evaluate(self, *, group_id: str, requirement_profile_id: str | None,
                 components: list[dict[str, Any]]) -> dict[str, Any]:
        profile_id, requirements = self._requirements(group_id, requirement_profile_id)
        feeds: dict[str, dict[str, Any]] = {}
        for component in components:
            feed_id = str(component["feed_id"])
            if feed_id in feeds:
                continue
            detail = self._catalog.get_feed(feed_id)
            feeds[feed_id] = detail["solver_feed"]
        result = evaluate_draft(components, feeds, requirements)
        result["requirement_profile_id"] = profile_id
        result["group_id"] = group_id
        return result

    # ── Persistierte Versionsbewertung (FEED-EDITOR-022) ───────────────────

    def _version_components(self, version_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        version = self.db.execute(text("""
          SELECT v.id, v.ration_id, v.snapshot, r.group_id
          FROM domain_agrar.ration_versions v
          JOIN domain_agrar.rations r ON r.id=v.ration_id AND r.tenant_id=v.tenant_id
          WHERE v.tenant_id=:tenant_id AND v.id=:version_id
        """), {"tenant_id": self.tenant_id, "version_id": version_id}).mappings().first()
        if not version:
            raise LookupError("Rationsversion nicht gefunden.")
        snapshot = version["snapshot"] or {}
        raw = snapshot.get("components") if isinstance(snapshot, dict) else None
        components = [
            {"feed_id": str(item.get("feed_id")), "kg_fm": float(item.get("kg_fm") or 0)}
            for item in (raw or [])
            if isinstance(item, dict) and item.get("feed_id")
        ]
        if not components:
            raise EmptyRationVersionError(
                "Diese Version enthaelt keine bewertbaren Komponenten (leerer Snapshot).")
        return dict(version), components

    def evaluate_version(self, version_id: str) -> dict[str, Any]:
        """Bewertung serverseitig aus dem unveraenderlichen Snapshot ableiten
        und append-only persistieren — keine Client-Payload, keine zweite Wahrheit."""
        version, components = self._version_components(version_id)
        result = self.evaluate(group_id=version["group_id"],
                               requirement_profile_id=None, components=components)
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.ration_evaluations
            (id,tenant_id,ration_id,ration_version_id,requirement_profile_id,
             totals,deltas,findings,coverage,evaluated_by)
          VALUES (:id,:tenant_id,:ration_id,:version_id,:profile_id,
             CAST(:totals AS jsonb),CAST(:deltas AS jsonb),CAST(:findings AS jsonb),
             CAST(:coverage AS jsonb),:actor)
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id,
               "ration_id": version["ration_id"], "version_id": version_id,
               "profile_id": result["requirement_profile_id"],
               "totals": json.dumps(result["totals"], ensure_ascii=False),
               "deltas": json.dumps(result["deltas"], ensure_ascii=False),
               "findings": json.dumps(result["findings"], ensure_ascii=False),
               "coverage": json.dumps(result["coverage"], ensure_ascii=False),
               "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)

    def latest_evaluation(self, version_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT * FROM domain_agrar.ration_evaluations
          WHERE tenant_id=:tenant_id AND ration_version_id=:version_id
          ORDER BY evaluated_at DESC LIMIT 1
        """), {"tenant_id": self.tenant_id, "version_id": version_id}).mappings().first()
        if not row:
            raise LookupError("Fuer diese Version liegt noch keine Bewertung vor.")
        return dict(row)
