"""Feeding businesses, farm sites, herds and business grants (FEED-CORE-015).

Traegt die Betriebsakte-Hierarchie Betrieb -> Standort -> Herde -> Tiergruppe
und die zweite Rechtestufe (Betriebs-Grants) gemaess Zielarchitektur
docs/specs/feeding/target-architecture.md (Abschnitte 2 und 5).
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

DEFAULT_BUSINESS_NAME = "Eigener Betrieb"


class FeedingBusinessNotFound(LookupError):
    pass


class FeedingBusinessConflict(ValueError):
    pass


class FeedingBusinessService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor

    # ── Betriebe ────────────────────────────────────────────────────────────

    def _reject_foreign_business_id(self, business_id: str | None) -> None:
        if not business_id:
            return
        foreign = self.db.execute(text("""
          SELECT 1 FROM domain_agrar.feeding_businesses
          WHERE id=:id AND tenant_id != :tenant_id
        """), {"id": business_id, "tenant_id": self.tenant_id}).first()
        if foreign:
            raise FeedingBusinessConflict("Die Betriebs-ID ist nicht verfuegbar.")

    def _require_site(self, business_id: str, site_id: str) -> None:
        site = self.db.execute(text("""
          SELECT id FROM domain_agrar.farm_sites
          WHERE id=:site_id AND tenant_id=:tenant_id AND business_id=:business_id
        """), {"site_id": site_id, "tenant_id": self.tenant_id,
               "business_id": business_id}).mappings().first()
        if not site:
            raise FeedingBusinessNotFound("Betriebsstaette nicht gefunden.")

    def _require_herd(self, business_id: str, herd_id: str) -> None:
        herd = self.db.execute(text("""
          SELECT id FROM domain_agrar.herds
          WHERE id=:herd_id AND tenant_id=:tenant_id AND business_id=:business_id
        """), {"herd_id": herd_id, "tenant_id": self.tenant_id,
               "business_id": business_id}).mappings().first()
        if not herd:
            raise FeedingBusinessNotFound("Herde nicht gefunden.")

    def upsert_business(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._reject_foreign_business_id(payload.get("id"))
        params = {
            "id": payload.get("id") or str(uuid7()),
            "tenant_id": self.tenant_id,
            "business_partner_id": payload.get("business_partner_id"),
            "name": payload["name"],
            "production_type": payload.get("production_type"),
            "husbandry_form": payload.get("husbandry_form"),
            "feeding_system": payload.get("feeding_system"),
            "milking_system": payload.get("milking_system"),
            "advisory_status": payload.get("advisory_status") or "none",
            "preferences": json.dumps(payload.get("preferences") or {}, ensure_ascii=False),
            "active": payload.get("active", True),
            "actor": self.actor,
        }
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_businesses
            (id,tenant_id,business_partner_id,name,production_type,husbandry_form,
             feeding_system,milking_system,advisory_status,preferences,active,
             created_by,updated_by)
          VALUES (:id,:tenant_id,:business_partner_id,:name,:production_type,:husbandry_form,
             :feeding_system,:milking_system,:advisory_status,CAST(:preferences AS jsonb),:active,
             :actor,:actor)
          ON CONFLICT (id) DO UPDATE SET
             business_partner_id=EXCLUDED.business_partner_id, name=EXCLUDED.name,
             production_type=EXCLUDED.production_type, husbandry_form=EXCLUDED.husbandry_form,
             feeding_system=EXCLUDED.feeding_system, milking_system=EXCLUDED.milking_system,
             advisory_status=EXCLUDED.advisory_status, preferences=EXCLUDED.preferences,
             active=EXCLUDED.active, updated_by=EXCLUDED.updated_by, updated_at=now()
          RETURNING *
        """), params).mappings().one()
        self.db.commit()
        return dict(row)

    def activate_from_partner(self, business_partner_id: str, name: str) -> dict[str, Any]:
        """CRM-Partner ohne Doppelerfassung als Fuetterungsbetrieb aktivieren (FEED-BUS-001)."""
        existing = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_businesses
          WHERE tenant_id=:tenant_id AND business_partner_id=:partner_id
        """), {"tenant_id": self.tenant_id, "partner_id": business_partner_id}).mappings().first()
        if existing:
            return dict(existing)
        return self.upsert_business({"business_partner_id": business_partner_id, "name": name})

    def list_businesses(self, *, include_inactive: bool = False,
                        subject: str | None = None, unrestricted: bool = False) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT b.*,
                 (SELECT count(*) FROM domain_agrar.herds h
                   WHERE h.tenant_id=b.tenant_id AND h.business_id=b.id AND h.active) AS herd_count,
                 (SELECT count(*) FROM domain_agrar.feeding_groups g
                   WHERE g.tenant_id=b.tenant_id AND g.business_id=b.id AND g.active) AS group_count
          FROM domain_agrar.feeding_businesses b
          WHERE b.tenant_id=:tenant_id AND (:all OR b.active)
            AND (:unrestricted OR b.created_by=:subject OR EXISTS (
              SELECT 1 FROM domain_agrar.feeding_business_grants grant_row
              WHERE grant_row.tenant_id=b.tenant_id AND grant_row.business_id=b.id
                AND grant_row.subject=:subject AND grant_row.revoked_at IS NULL
                AND grant_row.valid_from <= now()
                AND (grant_row.valid_until IS NULL OR grant_row.valid_until > now())
            ))
          ORDER BY b.name
        """), {"tenant_id": self.tenant_id, "all": include_inactive,
               "subject": subject or "", "unrestricted": unrestricted}).mappings().all()
        return [dict(row) for row in rows]

    def get_business(self, business_id: str) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_businesses WHERE tenant_id=:tenant_id AND id=:id
        """), {"tenant_id": self.tenant_id, "id": business_id}).mappings().first()
        if not row:
            raise FeedingBusinessNotFound("Fuetterungsbetrieb nicht gefunden.")
        return dict(row)

    # ── Standorte und Herden ────────────────────────────────────────────────

    def upsert_site(self, business_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.get_business(business_id)
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.farm_sites (id,tenant_id,business_id,name,address,active)
          VALUES (:id,:tenant_id,:business_id,:name,:address,:active)
          ON CONFLICT (tenant_id,business_id,name) DO UPDATE SET
            address=EXCLUDED.address, active=EXCLUDED.active, updated_at=now()
          RETURNING *
        """), {"id": payload.get("id") or str(uuid7()), "tenant_id": self.tenant_id,
               "business_id": business_id, "name": payload["name"],
               "address": payload.get("address"), "active": payload.get("active", True)}).mappings().one()
        self.db.commit()
        return dict(row)

    def upsert_herd(self, business_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.get_business(business_id)
        if payload.get("site_id"):
            self._require_site(business_id, payload["site_id"])
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.herds (id,tenant_id,business_id,site_id,name,animal_type,active)
          VALUES (:id,:tenant_id,:business_id,:site_id,:name,:animal_type,:active)
          ON CONFLICT (tenant_id,business_id,name) DO UPDATE SET
            site_id=EXCLUDED.site_id, animal_type=EXCLUDED.animal_type,
            active=EXCLUDED.active, updated_at=now()
          RETURNING *
        """), {"id": payload.get("id") or str(uuid7()), "tenant_id": self.tenant_id,
               "business_id": business_id, "site_id": payload.get("site_id"),
               "name": payload["name"], "animal_type": payload.get("animal_type") or "dairy_cow",
               "active": payload.get("active", True)}).mappings().one()
        self.db.commit()
        return dict(row)

    def list_structure(self, business_id: str) -> dict[str, Any]:
        business = self.get_business(business_id)
        sites = self.db.execute(text("""
          SELECT * FROM domain_agrar.farm_sites
          WHERE tenant_id=:tenant_id AND business_id=:business_id ORDER BY name
        """), {"tenant_id": self.tenant_id, "business_id": business_id}).mappings().all()
        herds = self.db.execute(text("""
          SELECT * FROM domain_agrar.herds
          WHERE tenant_id=:tenant_id AND business_id=:business_id ORDER BY name
        """), {"tenant_id": self.tenant_id, "business_id": business_id}).mappings().all()
        groups = self.db.execute(text("""
          SELECT id,name,animal_count,herd_id FROM domain_agrar.feeding_groups
          WHERE tenant_id=:tenant_id AND business_id=:business_id AND active ORDER BY name
        """), {"tenant_id": self.tenant_id, "business_id": business_id}).mappings().all()
        return {"business": business, "sites": [dict(s) for s in sites],
                "herds": [dict(h) for h in herds], "groups": [dict(g) for g in groups]}

    def assign_group(self, business_id: str, group_id: str, herd_id: str | None = None) -> dict[str, Any]:
        self.get_business(business_id)
        if herd_id:
            self._require_herd(business_id, herd_id)
        row = self.db.execute(text("""
          UPDATE domain_agrar.feeding_groups
          SET business_id=:business_id, herd_id=:herd_id, updated_by=:actor, updated_at=now()
          WHERE tenant_id=:tenant_id AND id=:group_id
          RETURNING id,name,business_id,herd_id
        """), {"tenant_id": self.tenant_id, "business_id": business_id,
               "herd_id": herd_id, "group_id": group_id, "actor": self.actor}).mappings().first()
        if not row:
            raise FeedingBusinessNotFound("Fuetterungsgruppe nicht gefunden.")
        self.db.commit()
        return dict(row)

    # ── Backfill ────────────────────────────────────────────────────────────

    def backfill_default_business(self) -> dict[str, Any]:
        """Bestehende Tiergruppen ohne Betrieb dem Default-Betrieb des Tenants zuordnen."""
        business = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_businesses
          WHERE tenant_id=:tenant_id AND business_partner_id IS NULL AND name=:name
        """), {"tenant_id": self.tenant_id, "name": DEFAULT_BUSINESS_NAME}).mappings().first()
        if business:
            business = dict(business)
        else:
            business = self.upsert_business({"name": DEFAULT_BUSINESS_NAME})
        assigned = self.db.execute(text("""
          UPDATE domain_agrar.feeding_groups
          SET business_id=:business_id, updated_by=:actor, updated_at=now()
          WHERE tenant_id=:tenant_id AND business_id IS NULL
          RETURNING id
        """), {"tenant_id": self.tenant_id, "business_id": business["id"], "actor": self.actor}).fetchall()
        self.db.commit()
        return {"business_id": business["id"], "assigned_groups": len(assigned)}

    # ── Grants (zweite Rechtestufe) ─────────────────────────────────────────

    def grant_access(self, business_id: str, subject: str, scope: str,
                     valid_until: Any | None = None) -> dict[str, Any]:
        self.get_business(business_id)
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_business_grants
            (id,tenant_id,business_id,subject,scope,valid_until,granted_by)
          VALUES (:id,:tenant_id,:business_id,:subject,:scope,:valid_until,:actor)
          ON CONFLICT (tenant_id,business_id,subject,scope) WHERE revoked_at IS NULL
          DO UPDATE SET valid_until=EXCLUDED.valid_until, granted_by=EXCLUDED.granted_by
          RETURNING *
        """), {"id": str(uuid7()), "tenant_id": self.tenant_id, "business_id": business_id,
               "subject": subject, "scope": scope, "valid_until": valid_until,
               "actor": self.actor}).mappings().one()
        self.db.commit()
        return dict(row)

    def revoke_access(self, business_id: str, subject: str, scope: str,
                      reason: str | None = None) -> int:
        result = self.db.execute(text("""
          UPDATE domain_agrar.feeding_business_grants
          SET revoked_by=:actor, revoked_at=now(), revoke_reason=:reason
          WHERE tenant_id=:tenant_id AND business_id=:business_id
            AND subject=:subject AND scope=:scope AND revoked_at IS NULL
        """), {"tenant_id": self.tenant_id, "business_id": business_id,
               "subject": subject, "scope": scope, "actor": self.actor,
               "reason": reason})
        self.db.commit()
        return result.rowcount or 0

    def list_grants(self, business_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_business_grants
          WHERE tenant_id=:tenant_id AND business_id=:business_id
          ORDER BY subject, scope
        """), {"tenant_id": self.tenant_id, "business_id": business_id}).mappings().all()
        return [dict(row) for row in rows]

    def has_business_access(self, business_id: str, subject: str, scope: str) -> bool:
        """Gueltiger Grant fuer subject+scope (write schliesst read ein, admin alles)."""
        creator = self.db.execute(text("""
          SELECT 1 FROM domain_agrar.feeding_businesses
          WHERE tenant_id=:tenant_id AND id=:business_id AND created_by=:subject
          LIMIT 1
        """), {"tenant_id": self.tenant_id, "business_id": business_id,
               "subject": subject}).first()
        if creator:
            return True
        scopes = {"read": ["read", "write", "approve", "admin"],
                  "write": ["write", "approve", "admin"],
                  "approve": ["approve", "admin"],
                  "admin": ["admin"]}[scope]
        row = self.db.execute(text("""
          SELECT 1 FROM domain_agrar.feeding_business_grants
          WHERE tenant_id=:tenant_id AND business_id=:business_id AND subject=:subject
            AND scope = ANY(:scopes)
            AND valid_from <= now() AND (valid_until IS NULL OR valid_until > now())
            AND revoked_at IS NULL
          LIMIT 1
        """), {"tenant_id": self.tenant_id, "business_id": business_id,
               "subject": subject, "scopes": scopes}).first()
        return row is not None
