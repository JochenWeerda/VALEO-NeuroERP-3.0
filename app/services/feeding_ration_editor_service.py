"""Rationseditor: Draft-Bewertung gegen Katalog und Bedarfsprofil (FEED-EDITOR-021).

Reine Lese-/Rechenoperation: aufloesen der Komponenten ueber den kanonischen
Futtermittelkatalog (FEED-CORE-018), Bedarf aus dem persistierten
RequirementProfile (FEED-CORE-020), Bewertung ueber die deterministische
Draft-Funktion (Code-SSOT). Persistiert wird hier nichts — Speichern bleibt
der append-only Lifecycle-Pfad.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.ration_draft import evaluate_draft
from app.services.feeding_feed_catalog_service import FeedingFeedCatalogService


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
