"""Deterministische Assistenz (FEED-AI-046).

Orchestriert versionierte Rechendienste zu auditierten Proposals
(append-only `feeding_assist_proposals`, FEED-AI-010). Kein Modellaufruf.
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.assist import (
    build_explain_proposal,
    build_measure_proposal,
    build_substitute_candidates,
)
from app.services.feeding_ration_editor_service import FeedingRationEditorService


class FeedingAssistService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    def _persist(self, proposal: dict[str, Any], *, group_id: str | None) -> dict[str, Any]:
        self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_assist_proposals
            (id,tenant_id,agent,objective,group_id,content,created_by)
          VALUES (:id,:tenant_id,:agent,:objective,:group_id,CAST(:content AS jsonb),:actor)
        """), {"id": proposal["proposal_id"], "tenant_id": self.tenant_id,
               "agent": proposal["agent"], "objective": proposal["objective"],
               "group_id": group_id,
               "content": json.dumps(proposal, ensure_ascii=False, sort_keys=True),
               "actor": self.actor})
        self.db.commit()
        return proposal

    def explain_findings(self, *, group_id: str,
                         components: list[dict[str, Any]]) -> dict[str, Any]:
        editor = FeedingRationEditorService(self.db, self.tenant_id, self.actor)
        evaluation = editor.evaluate(group_id=group_id,
                                     requirement_profile_id=None,
                                     components=components)
        history_n = int(self.db.execute(text("""
          SELECT COUNT(*) FROM domain_agrar.feeding_controlling_daily
          WHERE tenant_id=:tenant_id AND group_id=:group_id
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).scalar_one())
        proposal = build_explain_proposal(group_id=group_id, evaluation=evaluation,
                                          history_n=history_n)
        return self._persist(proposal, group_id=group_id)

    def propose_measures(self, *, findings: list[dict[str, Any]]) -> dict[str, Any]:
        existing = {str(row[0]) for row in self.db.execute(text("""
          SELECT actual_component_id FROM domain_agrar.feeding_actual_measures
          WHERE tenant_id=:tenant_id
        """), {"tenant_id": self.tenant_id}).all()}
        proposal = build_measure_proposal(findings=findings,
                                          existing_component_ids=existing,
                                          owner_subject=self.actor)
        return self._persist(proposal, group_id=None)

    def substitutes(self, *, feed_id: str) -> dict[str, Any]:
        source = self.db.execute(text("""
          SELECT id, name, feed_kind FROM domain_shared.futtermittel_einzelfutter
          WHERE tenant_id=:tenant_id AND id=:feed_id
        """), {"tenant_id": self.tenant_id, "feed_id": feed_id}).mappings().first()
        if not source:
            raise LookupError("Futtermittel nicht gefunden.")
        rows = self.db.execute(text("""
          SELECT f.id, f.name, f.feed_kind,
                 f.preis_pro_t AS price_eur_t,
                 EXISTS (SELECT 1 FROM domain_agrar.feeding_feed_reference_values rv
                         WHERE rv.tenant_id=f.tenant_id AND rv.feed_id=f.id
                           AND rv.nutrient_code='metabolizable_energy') AS has_energy_analysis
          FROM domain_shared.futtermittel_einzelfutter f
          WHERE f.tenant_id=:tenant_id AND f.id<>:feed_id
            AND f.feed_kind=:feed_kind AND f.approval_status='approved'
          ORDER BY f.name
        """), {"tenant_id": self.tenant_id, "feed_id": feed_id,
               "feed_kind": source["feed_kind"]}).mappings().all()
        return build_substitute_candidates(source=dict(source),
                                           candidates=[dict(row) for row in rows])

    def list_proposals(self, *, group_id: str | None = None) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT id, agent, objective, group_id, content, created_by, created_at
          FROM domain_agrar.feeding_assist_proposals
          WHERE tenant_id=:tenant_id AND (:group_id IS NULL OR group_id=:group_id)
          ORDER BY created_at DESC LIMIT 200
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().all()
        return [dict(row) for row in rows]
