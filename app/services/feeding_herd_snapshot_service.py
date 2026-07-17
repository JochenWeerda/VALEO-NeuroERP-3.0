"""Gruppenhistorie aus Herd-Deltas (FEED-HERD-043).

Verdichtet `herd_data_observations` (kind group_kpi) zu taeglichen
`animal_group_snapshots` je Fuetterungsgruppe — idempotent: gleicher
Datenstand liefert dieselben Snapshots (Upsert je Tag; die juengste
Provider-Aktualisierung eines Tages gewinnt). Zusaetzlich Veraltet-Status
der Gruppenparameter (Alter der letzten Bestaetigung).
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

# Schwelle fuer die Veraltet-Warnung (6.2 SOLL): 30 Tage ohne Bestaetigung.
STALE_AFTER_DAYS = 30


class FeedingHerdSnapshotService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    def _group(self, group_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT id, name, external_ref, animal_count, updated_at, parameters_confirmed_at
          FROM domain_agrar.feeding_groups
          WHERE tenant_id=:tenant_id AND id=:group_id
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().first()
        if not row:
            raise LookupError("Fuetterungsgruppe nicht gefunden.")
        return dict(row)

    def condense(self, group_id: str) -> dict[str, Any]:
        """Taegliche Snapshots aus den group_kpi-Beobachtungen verdichten.

        Mapping: `feeding_groups.external_ref` = Provider-Gruppen-ID der
        Beobachtung. Je Tag gewinnt die juengste `provider_updated_at`-Zeile
        (Tageskorrekturen ersetzen den Datenstand, nie zwei Wahrheiten).
        """
        group = self._group(group_id)
        if not group.get("external_ref"):
            raise ValueError(
                "Gruppe hat keine externe Referenz (external_ref) — "
                "ohne Provider-Zuordnung ist keine Verdichtung moeglich.")
        rows = self.db.execute(text("""
          SELECT DISTINCT ON (CAST(effective_at AS date))
                 id, CAST(effective_at AS date) AS snapshot_date, payload
          FROM domain_agrar.herd_data_observations
          WHERE tenant_id=:tenant_id AND kind='group_kpi'
            AND group_id=:external_ref AND is_deleted=FALSE
          ORDER BY CAST(effective_at AS date), provider_updated_at DESC, imported_at DESC
        """), {"tenant_id": self.tenant_id,
               "external_ref": group["external_ref"]}).mappings().all()
        for row in rows:
            payload = row["payload"] or {}
            cow_count = payload.get("cow_count")
            self.db.execute(text("""
              INSERT INTO domain_agrar.animal_group_snapshots
                (id,tenant_id,group_id,snapshot_date,cow_count,kpis,source,source_observation_id)
              VALUES (:id,:tenant_id,:group_id,:snapshot_date,:cow_count,
                      CAST(:kpis AS jsonb),'herd_data',:observation_id)
              ON CONFLICT (tenant_id,group_id,snapshot_date) DO UPDATE SET
                cow_count=EXCLUDED.cow_count, kpis=EXCLUDED.kpis,
                source_observation_id=EXCLUDED.source_observation_id,
                condensed_at=now()
            """), {"id": str(uuid7()), "tenant_id": self.tenant_id, "group_id": group_id,
                   "snapshot_date": row["snapshot_date"],
                   "cow_count": int(cow_count) if cow_count is not None else None,
                   "kpis": json.dumps(payload.get("kpis") or {}, ensure_ascii=False),
                   "observation_id": row["id"]})
        self.db.commit()
        count = self.db.execute(text("""
          SELECT COUNT(*) FROM domain_agrar.animal_group_snapshots
          WHERE tenant_id=:tenant_id AND group_id=:group_id
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).scalar_one()
        return {"group_id": group_id, "condensed_days": len(rows),
                "snapshot_count": int(count)}

    def history(self, group_id: str) -> list[dict[str, Any]]:
        self._group(group_id)
        rows = self.db.execute(text("""
          SELECT id, group_id, snapshot_date, cow_count, kpis, source,
                 source_observation_id, condensed_at
          FROM domain_agrar.animal_group_snapshots
          WHERE tenant_id=:tenant_id AND group_id=:group_id
          ORDER BY snapshot_date DESC
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().all()
        return [{**dict(row), "snapshot_date": str(row["snapshot_date"])} for row in rows]

    def staleness(self, group_id: str) -> dict[str, Any]:
        """Alter der letzten Parameterbestaetigung; ohne explizite Bestaetigung
        zaehlt die letzte fachliche Aenderung (updated_at)."""
        group = self._group(group_id)
        row = self.db.execute(text("""
          SELECT GREATEST(0, EXTRACT(DAY FROM now() -
                   COALESCE(parameters_confirmed_at, updated_at)))::int AS days,
                 COALESCE(parameters_confirmed_at, updated_at) AS confirmed_at
          FROM domain_agrar.feeding_groups
          WHERE tenant_id=:tenant_id AND id=:group_id
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().one()
        latest_snapshot = self.db.execute(text("""
          SELECT MAX(snapshot_date) FROM domain_agrar.animal_group_snapshots
          WHERE tenant_id=:tenant_id AND group_id=:group_id
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).scalar()
        days = int(row["days"])
        return {
            "group_id": group_id,
            "group_name": group["name"],
            "last_confirmed_at": row["confirmed_at"],
            "days_since_confirmation": days,
            "stale": days > STALE_AFTER_DAYS,
            "stale_after_days": STALE_AFTER_DAYS,
            "latest_snapshot_date": str(latest_snapshot) if latest_snapshot else None,
        }

    def confirm_parameters(self, group_id: str) -> dict[str, Any]:
        self._group(group_id)
        self.db.execute(text("""
          UPDATE domain_agrar.feeding_groups
          SET parameters_confirmed_at=now(), updated_by=:actor
          WHERE tenant_id=:tenant_id AND id=:group_id
        """), {"tenant_id": self.tenant_id, "group_id": group_id, "actor": self.actor})
        self.db.commit()
        return self.staleness(group_id)
