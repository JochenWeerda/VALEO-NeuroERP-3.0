"""Transactional persistence service for feeding groups and ration versions."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.agrar.rations.lifecycle import RationStatus, TransitionError, snapshot_checksum, validate_transition
from app.agrar.rations.groups import validate_group_parameters
from app.core.uuid7 import uuid7


class RationLifecycleNotFound(LookupError):
    pass


class RationLifecycleConflict(RuntimeError):
    pass


def _dict(row: Any) -> dict[str, Any]:
    return dict(row) if row is not None else {}


class RationLifecycleService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db = db
        self.tenant_id = tenant_id
        self.actor = actor or "unknown"

    def create_group(self, payload: dict[str, Any]) -> dict[str, Any]:
        group_id = str(uuid7())
        self._validate_group_parent(payload.get("business_id"), payload.get("herd_id"))
        validate_group_parameters(
            profile=payload["profile_code"], pregnancy_status=payload["pregnancy_status"],
            gestation_day=payload.get("gestation_day"), milk_fat_pct=payload.get("milk_fat_pct"),
            milk_protein_pct=payload.get("milk_protein_pct"), valid_from=payload["valid_from"],
            valid_until=payload.get("valid_until"),
        )
        try:
            row = self.db.execute(text("""
              INSERT INTO domain_agrar.feeding_groups
                (id,tenant_id,external_ref,name,animal_type,animal_count,body_mass_kg,
                 days_in_milk,lactation_number,target_milk_kg,feeding_system,location,
                 business_id,herd_id,profile_code,pregnancy_status,gestation_day,
                 milk_fat_pct,milk_protein_pct,milk_urea_mg_dl,risk_level,
                 valid_from,valid_until,active,created_by,updated_by)
              VALUES
                (:id,:tenant_id,:external_ref,:name,:animal_type,:animal_count,:body_mass_kg,
                 :days_in_milk,:lactation_number,:target_milk_kg,:feeding_system,:location,
                 :business_id,:herd_id,:profile_code,:pregnancy_status,:gestation_day,
                 :milk_fat_pct,:milk_protein_pct,:milk_urea_mg_dl,:risk_level,
                 :valid_from,:valid_until,:active,:actor,:actor)
              RETURNING *
            """), {"id": group_id, "tenant_id": self.tenant_id, "actor": self.actor, **payload}).mappings().one()
            self._record_group_revision(_dict(row), "Anlage")
            self.db.commit()
            return _dict(row)
        except IntegrityError as exc:
            self.db.rollback()
            raise RationLifecycleConflict("Eine Fuetterungsgruppe mit dieser externen Referenz existiert bereits.") from exc

    def list_groups(self, *, active_only: bool = True, subject: str = "",
                    unrestricted: bool = False) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT g.*,
            COUNT(DISTINCT r.id)::int AS ration_count,
            COUNT(DISTINCT lc.version_id) FILTER (WHERE lc.status='active')::int AS active_ration_count
          FROM domain_agrar.feeding_groups g
          LEFT JOIN domain_agrar.feeding_businesses b
            ON b.tenant_id=g.tenant_id AND b.id=g.business_id
          LEFT JOIN domain_agrar.rations r ON r.tenant_id=g.tenant_id AND r.group_id=g.id
          LEFT JOIN domain_agrar.ration_version_lifecycle lc ON lc.tenant_id=g.tenant_id AND lc.group_id=g.id
          WHERE g.tenant_id=:tenant_id AND (:active_only=FALSE OR g.active=TRUE)
            AND (:unrestricted OR g.created_by=:subject OR b.created_by=:subject OR EXISTS (
              SELECT 1 FROM domain_agrar.feeding_business_grants grant_row
              WHERE grant_row.tenant_id=g.tenant_id AND grant_row.business_id=g.business_id
                AND grant_row.subject=:subject AND grant_row.revoked_at IS NULL
                AND grant_row.valid_from <= now()
                AND (grant_row.valid_until IS NULL OR grant_row.valid_until > now())
                AND grant_row.scope IN ('read','write','approve','admin')
            ))
          GROUP BY g.id ORDER BY g.active DESC,g.name
        """), {"tenant_id": self.tenant_id, "active_only": active_only,
                 "subject": subject, "unrestricted": unrestricted}).mappings().all()
        return [_dict(row) for row in rows]

    def has_business_access(self, business_id: str, subject: str, scope: str) -> bool:
        scopes = {"read": ["read", "write", "approve", "admin"],
                  "write": ["write", "approve", "admin"]}[scope]
        row = self.db.execute(text("""
          SELECT 1 FROM domain_agrar.feeding_businesses b
          WHERE b.tenant_id=:tenant_id AND b.id=:business_id
            AND (b.created_by=:subject OR EXISTS (
              SELECT 1 FROM domain_agrar.feeding_business_grants grant_row
              WHERE grant_row.tenant_id=b.tenant_id AND grant_row.business_id=b.id
                AND grant_row.subject=:subject AND grant_row.scope = ANY(:scopes)
                AND grant_row.revoked_at IS NULL AND grant_row.valid_from <= now()
                AND (grant_row.valid_until IS NULL OR grant_row.valid_until > now())
            )) LIMIT 1
        """), {"tenant_id": self.tenant_id, "business_id": business_id,
                 "subject": subject, "scopes": scopes}).first()
        return row is not None

    def has_group_access(self, group_id: str, subject: str, scope: str) -> bool:
        scopes = {"read": ["read", "write", "approve", "admin"],
                  "write": ["write", "approve", "admin"]}[scope]
        row = self.db.execute(text("""
          SELECT 1 FROM domain_agrar.feeding_groups g
          LEFT JOIN domain_agrar.feeding_businesses b
            ON b.tenant_id=g.tenant_id AND b.id=g.business_id
          WHERE g.tenant_id=:tenant_id AND g.id=:group_id
            AND (g.created_by=:subject OR b.created_by=:subject OR EXISTS (
              SELECT 1 FROM domain_agrar.feeding_business_grants grant_row
              WHERE grant_row.tenant_id=g.tenant_id AND grant_row.business_id=g.business_id
                AND grant_row.subject=:subject AND grant_row.scope = ANY(:scopes)
                AND grant_row.revoked_at IS NULL AND grant_row.valid_from <= now()
                AND (grant_row.valid_until IS NULL OR grant_row.valid_until > now())
            )) LIMIT 1
        """), {"tenant_id": self.tenant_id, "group_id": group_id,
                 "subject": subject, "scopes": scopes}).first()
        return row is not None

    def _validate_group_parent(self, business_id: str | None, herd_id: str | None) -> None:
        if herd_id and not business_id:
            raise RationLifecycleConflict("Eine Herde erfordert einen Fuetterungsbetrieb.")
        if business_id:
            business = self.db.execute(text("""
              SELECT id FROM domain_agrar.feeding_businesses
              WHERE tenant_id=:tenant_id AND id=:business_id AND active=TRUE
            """), {"tenant_id": self.tenant_id, "business_id": business_id}).first()
            if not business:
                raise RationLifecycleNotFound("Aktiver Fuetterungsbetrieb nicht gefunden.")
        if herd_id:
            herd = self.db.execute(text("""
              SELECT id FROM domain_agrar.herds
              WHERE tenant_id=:tenant_id AND business_id=:business_id AND id=:herd_id AND active=TRUE
            """), {"tenant_id": self.tenant_id, "business_id": business_id, "herd_id": herd_id}).first()
            if not herd:
                raise RationLifecycleNotFound("Aktive Herde im Fuetterungsbetrieb nicht gefunden.")

    def get_group(self, group_id: str, *, for_update: bool = False) -> dict[str, Any]:
        lock = " FOR UPDATE" if for_update else ""
        row = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_groups
          WHERE tenant_id=:tenant_id AND id=:group_id
        """ + lock), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().first()
        if not row:
            raise RationLifecycleNotFound("Fuetterungsgruppe nicht gefunden.")
        return _dict(row)

    def update_group(self, group_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        expected_revision = int(patch.pop("expected_revision"))
        reason = str(patch.pop("reason"))
        current = self.get_group(group_id, for_update=True)
        if int(current["revision"]) != expected_revision:
            raise RationLifecycleConflict(
                f"Die Fuetterungsgruppe wurde zwischenzeitlich geaendert (erwartet Revision {expected_revision}, aktuell {current['revision']})."
            )
        mutable = {
            "external_ref", "name", "animal_type", "animal_count", "body_mass_kg",
            "days_in_milk", "lactation_number", "target_milk_kg", "feeding_system",
            "location", "herd_id", "profile_code", "pregnancy_status", "gestation_day",
            "milk_fat_pct", "milk_protein_pct", "milk_urea_mg_dl", "risk_level",
            "valid_from", "valid_until", "active",
        }
        unknown = set(patch) - mutable
        if unknown:
            raise RationLifecycleConflict(f"Unbekannte Gruppenfelder: {', '.join(sorted(unknown))}")
        values = {key: patch.get(key, current.get(key)) for key in mutable}
        self._validate_group_parent(current.get("business_id"), values.get("herd_id"))
        validate_group_parameters(
            profile=values["profile_code"], pregnancy_status=values["pregnancy_status"],
            gestation_day=values.get("gestation_day"), milk_fat_pct=values.get("milk_fat_pct"),
            milk_protein_pct=values.get("milk_protein_pct"), valid_from=values["valid_from"],
            valid_until=values.get("valid_until"),
        )
        row = self.db.execute(text("""
          UPDATE domain_agrar.feeding_groups SET
            external_ref=:external_ref,name=:name,animal_type=:animal_type,
            animal_count=:animal_count,body_mass_kg=:body_mass_kg,days_in_milk=:days_in_milk,
            lactation_number=:lactation_number,target_milk_kg=:target_milk_kg,
            feeding_system=:feeding_system,location=:location,herd_id=:herd_id,
            profile_code=:profile_code,pregnancy_status=:pregnancy_status,
            gestation_day=:gestation_day,milk_fat_pct=:milk_fat_pct,
            milk_protein_pct=:milk_protein_pct,milk_urea_mg_dl=:milk_urea_mg_dl,
            risk_level=:risk_level,valid_from=:valid_from,valid_until=:valid_until,
            active=:active,revision=revision+1,updated_by=:actor,updated_at=now()
          WHERE tenant_id=:tenant_id AND id=:group_id AND revision=:expected_revision
          RETURNING *
        """), {**values, "tenant_id": self.tenant_id, "group_id": group_id,
                 "expected_revision": expected_revision, "actor": self.actor}).mappings().first()
        if not row:
            raise RationLifecycleConflict("Revision der Fuetterungsgruppe ist nicht mehr aktuell.")
        result = _dict(row)
        self._record_group_revision(result, reason)
        self.db.commit()
        return result

    def _record_group_revision(self, group: dict[str, Any], reason: str) -> None:
        self.db.execute(text("""
          INSERT INTO domain_agrar.feeding_group_revisions
            (id,tenant_id,group_id,revision,snapshot,reason,changed_by)
          VALUES (:id,:tenant_id,:group_id,:revision,CAST(:snapshot AS jsonb),:reason,:actor)
        """), {
            "id": str(uuid7()), "tenant_id": self.tenant_id, "group_id": group["id"],
            "revision": group.get("revision", 1),
            "snapshot": json.dumps(group, ensure_ascii=False, default=str),
            "reason": reason, "actor": self.actor,
        })

    def list_group_history(self, group_id: str) -> list[dict[str, Any]]:
        self.get_group(group_id)
        rows = self.db.execute(text("""
          SELECT * FROM domain_agrar.feeding_group_revisions
          WHERE tenant_id=:tenant_id AND group_id=:group_id ORDER BY revision DESC
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).mappings().all()
        return [_dict(row) for row in rows]

    def create_ration(
        self,
        *,
        group_id: str,
        name: str,
        description: str | None,
        snapshot: dict[str, Any],
        source: str,
        comment: str | None,
    ) -> dict[str, Any]:
        group = self.db.execute(text("""
          SELECT id FROM domain_agrar.feeding_groups
          WHERE tenant_id=:tenant_id AND id=:group_id AND active=TRUE
        """), {"tenant_id": self.tenant_id, "group_id": group_id}).first()
        if not group:
            raise RationLifecycleNotFound("Aktive Fuetterungsgruppe nicht gefunden.")
        ration_id = str(uuid7())
        self.db.execute(text("""
          INSERT INTO domain_agrar.rations (id,tenant_id,group_id,name,description,created_by)
          VALUES (:id,:tenant_id,:group_id,:name,:description,:actor)
        """), {
            "id": ration_id, "tenant_id": self.tenant_id, "group_id": group_id,
            "name": name, "description": description, "actor": self.actor,
        })
        version = self._create_version_locked(
            ration_id=ration_id,
            snapshot=snapshot,
            source=source,
            comment=comment,
            based_on_version_id=None,
            expected_latest_version_no=0,
        )
        self.db.commit()
        return self.get_ration(ration_id, include_audit=True, known_version=version)

    def create_version(
        self,
        *,
        ration_id: str,
        snapshot: dict[str, Any],
        source: str,
        comment: str | None,
        based_on_version_id: str | None,
        expected_latest_version_no: int,
    ) -> dict[str, Any]:
        try:
            version = self._create_version_locked(
                ration_id=ration_id,
                snapshot=snapshot,
                source=source,
                comment=comment,
                based_on_version_id=based_on_version_id,
                expected_latest_version_no=expected_latest_version_no,
            )
            self.db.commit()
            return version
        except IntegrityError as exc:
            self.db.rollback()
            raise RationLifecycleConflict("Dieser Rationsinhalt ist bereits als Version gespeichert.") from exc

    def _create_version_locked(
        self,
        *,
        ration_id: str,
        snapshot: dict[str, Any],
        source: str,
        comment: str | None,
        based_on_version_id: str | None,
        expected_latest_version_no: int,
    ) -> dict[str, Any]:
        ration = self.db.execute(text("""
          SELECT id,group_id FROM domain_agrar.rations
          WHERE tenant_id=:tenant_id AND id=:ration_id FOR UPDATE
        """), {"tenant_id": self.tenant_id, "ration_id": ration_id}).mappings().first()
        if not ration:
            raise RationLifecycleNotFound("Ration nicht gefunden.")
        latest = int(self.db.execute(text("""
          SELECT COALESCE(MAX(version_no),0) FROM domain_agrar.ration_versions
          WHERE tenant_id=:tenant_id AND ration_id=:ration_id
        """), {"tenant_id": self.tenant_id, "ration_id": ration_id}).scalar_one())
        if latest != expected_latest_version_no:
            raise RationLifecycleConflict(
                f"Die Ration wurde zwischenzeitlich geaendert (erwartet v{expected_latest_version_no}, aktuell v{latest})."
            )
        if based_on_version_id:
            base_exists = self.db.execute(text("""
              SELECT 1 FROM domain_agrar.ration_versions
              WHERE tenant_id=:tenant_id AND ration_id=:ration_id AND id=:version_id
            """), {
                "tenant_id": self.tenant_id, "ration_id": ration_id, "version_id": based_on_version_id,
            }).first()
            if not base_exists:
                raise RationLifecycleNotFound("Basisversion nicht gefunden.")
        version_id = str(uuid7())
        checksum = snapshot_checksum(snapshot)
        version_no = latest + 1
        row = self.db.execute(text("""
          INSERT INTO domain_agrar.ration_versions
            (id,tenant_id,ration_id,version_no,source,comment,snapshot,snapshot_checksum,based_on_version_id,created_by)
          VALUES
            (:id,:tenant_id,:ration_id,:version_no,:source,:comment,CAST(:snapshot AS jsonb),:checksum,:based_on,:actor)
          RETURNING *
        """), {
            "id": version_id, "tenant_id": self.tenant_id, "ration_id": ration_id,
            "version_no": version_no, "source": source, "comment": comment,
            "snapshot": json.dumps(snapshot, ensure_ascii=False, allow_nan=False),
            "checksum": checksum, "based_on": based_on_version_id, "actor": self.actor,
        }).mappings().one()
        self.db.execute(text("""
          INSERT INTO domain_agrar.ration_version_lifecycle
            (version_id,tenant_id,ration_id,group_id,status)
          VALUES (:version_id,:tenant_id,:ration_id,:group_id,'draft')
        """), {
            "version_id": version_id, "tenant_id": self.tenant_id,
            "ration_id": ration_id, "group_id": ration["group_id"],
        })
        self._audit(
            ration_id=ration_id,
            version_id=version_id,
            event_type="version_created",
            from_status=None,
            to_status=RationStatus.DRAFT.value,
            reason=comment,
            delta={"version_no": version_no, "source": source, "snapshot_checksum": checksum},
        )
        self.db.execute(text("UPDATE domain_agrar.rations SET updated_at=now() WHERE id=:id"), {"id": ration_id})
        result = _dict(row)
        result["status"] = RationStatus.DRAFT.value
        return result

    def list_rations(
        self,
        *,
        group_id: str | None = None,
        status: RationStatus | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT r.id,r.group_id,r.name,r.description,r.created_by,r.created_at,r.updated_at,
                 g.name AS group_name,g.animal_count,g.feeding_system,
                 latest.version_id,latest.version_no,latest.status,latest.feeding_start,
                 latest.snapshot_checksum,latest.created_at AS version_created_at
          FROM domain_agrar.rations r
          JOIN domain_agrar.feeding_groups g ON g.tenant_id=r.tenant_id AND g.id=r.group_id
          JOIN LATERAL (
            SELECT rv.id AS version_id,rv.version_no,rv.snapshot_checksum,rv.created_at,
                   lc.status,lc.feeding_start
            FROM domain_agrar.ration_versions rv
            JOIN domain_agrar.ration_version_lifecycle lc ON lc.version_id=rv.id AND lc.tenant_id=rv.tenant_id
            WHERE rv.tenant_id=r.tenant_id AND rv.ration_id=r.id
            ORDER BY rv.version_no DESC LIMIT 1
          ) latest ON TRUE
          WHERE r.tenant_id=:tenant_id
            AND (:group_id IS NULL OR r.group_id=:group_id)
            AND (:status IS NULL OR latest.status=:status)
          ORDER BY (latest.status='active') DESC,r.updated_at DESC LIMIT :limit
        """), {
            "tenant_id": self.tenant_id, "group_id": group_id,
            "status": status.value if status else None, "limit": limit,
        }).mappings().all()
        return [_dict(row) for row in rows]

    def list_active_rations(self) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT r.id AS ration_id,r.name,r.group_id,g.name AS group_name,g.animal_count,
                 rv.id AS version_id,rv.version_no,rv.snapshot,rv.snapshot_checksum,
                 lc.feeding_start,lc.activated_at
          FROM domain_agrar.ration_version_lifecycle lc
          JOIN domain_agrar.ration_versions rv ON rv.tenant_id=lc.tenant_id AND rv.id=lc.version_id
          JOIN domain_agrar.rations r ON r.tenant_id=lc.tenant_id AND r.id=lc.ration_id
          JOIN domain_agrar.feeding_groups g ON g.tenant_id=lc.tenant_id AND g.id=lc.group_id
          WHERE lc.tenant_id=:tenant_id AND lc.status='active'
          ORDER BY g.name
        """), {"tenant_id": self.tenant_id}).mappings().all()
        return [_dict(row) for row in rows]

    def get_ration(
        self,
        ration_id: str,
        *,
        include_audit: bool = True,
        known_version: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        header = self.db.execute(text("""
          SELECT r.*,g.name AS group_name,g.animal_count,g.feeding_system,g.location
          FROM domain_agrar.rations r
          JOIN domain_agrar.feeding_groups g ON g.tenant_id=r.tenant_id AND g.id=r.group_id
          WHERE r.tenant_id=:tenant_id AND r.id=:ration_id
        """), {"tenant_id": self.tenant_id, "ration_id": ration_id}).mappings().first()
        if not header:
            raise RationLifecycleNotFound("Ration nicht gefunden.")
        versions = self.db.execute(text("""
          SELECT rv.*,lc.status,lc.feeding_start,lc.reviewed_by,lc.reviewed_at,
                 lc.approved_by,lc.approved_at,lc.activated_by,lc.activated_at,
                 lc.retired_by,lc.retired_at,lc.archived_by,lc.archived_at
          FROM domain_agrar.ration_versions rv
          JOIN domain_agrar.ration_version_lifecycle lc ON lc.version_id=rv.id AND lc.tenant_id=rv.tenant_id
          WHERE rv.tenant_id=:tenant_id AND rv.ration_id=:ration_id
          ORDER BY rv.version_no DESC
        """), {"tenant_id": self.tenant_id, "ration_id": ration_id}).mappings().all()
        result = _dict(header)
        result["versions"] = [_dict(row) for row in versions]
        if known_version and not result["versions"]:
            result["versions"] = [known_version]
        if include_audit:
            result["audit"] = self.list_audit(ration_id)
        if result["versions"]:
            latest = result["versions"][0]
            result["latest_version_id"] = latest["id"]
            result["latest_version_no"] = latest["version_no"]
            result["latest_status"] = latest["status"]
            result["latest_feeding_start"] = latest["feeding_start"]
            readiness = latest.get("snapshot", {}).get("readiness", {}) if isinstance(latest.get("snapshot"), dict) else {}
            result["latest_readiness_status"] = readiness.get("status", "not_checked")
            result["latest_readiness_blockers"] = int(readiness.get("blocker_count", 0) or 0)
            result["latest_readiness_warnings"] = int(readiness.get("warning_count", 0) or 0)
        return result

    def list_versions(self, ration_id: str) -> list[dict[str, Any]]:
        detail = self.get_ration(ration_id, include_audit=False)
        return detail["versions"]

    def transition(
        self,
        *,
        version_id: str,
        target: RationStatus,
        expected_status: RationStatus,
        reason: str | None,
        feeding_start: datetime | None,
    ) -> dict[str, Any]:
        row = self.db.execute(text("""
          SELECT rv.id AS version_id,rv.ration_id,rv.version_no,rv.snapshot_checksum,rv.snapshot,
                 lc.group_id,lc.status,lc.feeding_start
          FROM domain_agrar.ration_versions rv
          JOIN domain_agrar.ration_version_lifecycle lc ON lc.version_id=rv.id AND lc.tenant_id=rv.tenant_id
          WHERE rv.tenant_id=:tenant_id AND rv.id=:version_id FOR UPDATE OF lc
        """), {"tenant_id": self.tenant_id, "version_id": version_id}).mappings().first()
        if not row:
            raise RationLifecycleNotFound("Rationsversion nicht gefunden.")
        if row["status"] != expected_status.value:
            raise RationLifecycleConflict(
                f"Statuskonflikt: erwartet {expected_status.value}, aktuell {row['status']}."
            )
        effective_start = feeding_start or row["feeding_start"]
        validate_transition(row["status"], target, reason=reason, feeding_start=effective_start)
        readiness = row["snapshot"].get("readiness", {}) if isinstance(row["snapshot"], dict) else {}
        blockers = int(readiness.get("blocker_count", 0) or 0)
        if target in {RationStatus.APPROVED, RationStatus.ACTIVE} and blockers > 0 and not (reason or "").startswith("OVERRIDE:"):
            raise RationLifecycleConflict(
                f"Readiness blockiert diesen Schritt ({blockers} Befund(e)). Begruendete Ausnahme mit 'OVERRIDE:' erforderlich."
            )
        superseded: list[dict[str, Any]] = []
        if target is RationStatus.ACTIVE:
            if effective_start is None:
                effective_start = datetime.now(timezone.utc)
            superseded = [
                _dict(item)
                for item in self.db.execute(text("""
                  SELECT version_id,ration_id,status FROM domain_agrar.ration_version_lifecycle
                  WHERE tenant_id=:tenant_id AND group_id=:group_id AND status='active'
                    AND version_id<>:version_id FOR UPDATE
                """), {
                    "tenant_id": self.tenant_id, "group_id": row["group_id"], "version_id": version_id,
                }).mappings().all()
            ]
            for old in superseded:
                self.db.execute(text("""
                  UPDATE domain_agrar.ration_version_lifecycle
                  SET status='retired',retired_by=:actor,retired_at=now(),updated_at=now()
                  WHERE tenant_id=:tenant_id AND version_id=:version_id
                """), {"actor": self.actor, "tenant_id": self.tenant_id, "version_id": old["version_id"]})
                self._audit(
                    ration_id=old["ration_id"], version_id=old["version_id"],
                    event_type="superseded", from_status="active", to_status="retired",
                    reason=f"Durch Version {version_id} ersetzt.", delta={"replacement_version_id": version_id},
                )
        updated = self.db.execute(text("""
          UPDATE domain_agrar.ration_version_lifecycle SET
            status=:target,
            feeding_start=CASE
              WHEN :target='scheduled' THEN :feeding_start
              WHEN :target='active' THEN :feeding_start
              WHEN :target='approved' AND status='scheduled' THEN NULL
              ELSE feeding_start END,
            reviewed_by=CASE WHEN :target='in_review' THEN :actor ELSE reviewed_by END,
            reviewed_at=CASE WHEN :target='in_review' THEN now() ELSE reviewed_at END,
            approved_by=CASE WHEN :target='approved' THEN :actor ELSE approved_by END,
            approved_at=CASE WHEN :target='approved' THEN now() ELSE approved_at END,
            activated_by=CASE WHEN :target='active' THEN :actor ELSE activated_by END,
            activated_at=CASE WHEN :target='active' THEN now() ELSE activated_at END,
            retired_by=CASE WHEN :target='retired' THEN :actor ELSE retired_by END,
            retired_at=CASE WHEN :target='retired' THEN now() ELSE retired_at END,
            archived_by=CASE WHEN :target='archived' THEN :actor ELSE archived_by END,
            archived_at=CASE WHEN :target='archived' THEN now() ELSE archived_at END,
            updated_at=now()
          WHERE tenant_id=:tenant_id AND version_id=:version_id
          RETURNING *
        """), {
            "target": target.value, "feeding_start": effective_start,
            "actor": self.actor, "tenant_id": self.tenant_id, "version_id": version_id,
        }).mappings().one()
        self._audit(
            ration_id=row["ration_id"], version_id=version_id,
            event_type="status_transition", from_status=row["status"], to_status=target.value,
            reason=reason,
            delta={
                "version_no": row["version_no"],
                "feeding_start": effective_start.isoformat() if effective_start else None,
                "superseded_version_ids": [item["version_id"] for item in superseded],
            },
        )
        self.db.execute(text("UPDATE domain_agrar.rations SET updated_at=now() WHERE id=:id"), {"id": row["ration_id"]})
        self.db.commit()
        result = _dict(updated)
        result["version_no"] = row["version_no"]
        result["snapshot_checksum"] = row["snapshot_checksum"]
        result["superseded_version_ids"] = [item["version_id"] for item in superseded]
        return result

    def list_audit(self, ration_id: str) -> list[dict[str, Any]]:
        rows = self.db.execute(text("""
          SELECT * FROM domain_agrar.ration_audit_events
          WHERE tenant_id=:tenant_id AND ration_id=:ration_id
          ORDER BY occurred_at DESC,id DESC
        """), {"tenant_id": self.tenant_id, "ration_id": ration_id}).mappings().all()
        return [_dict(row) for row in rows]

    def _audit(
        self,
        *,
        ration_id: str,
        version_id: str | None,
        event_type: str,
        from_status: str | None,
        to_status: str | None,
        reason: str | None,
        delta: dict[str, Any],
    ) -> None:
        self.db.execute(text("""
          INSERT INTO domain_agrar.ration_audit_events
            (id,tenant_id,ration_id,version_id,event_type,from_status,to_status,actor,reason,delta)
          VALUES
            (:id,:tenant_id,:ration_id,:version_id,:event_type,:from_status,:to_status,:actor,:reason,CAST(:delta AS jsonb))
        """), {
            "id": str(uuid7()), "tenant_id": self.tenant_id, "ration_id": ration_id,
            "version_id": version_id, "event_type": event_type,
            "from_status": from_status, "to_status": to_status,
            "actor": self.actor, "reason": reason,
            "delta": json.dumps(delta, ensure_ascii=False),
        })


__all__ = [
    "RationLifecycleService",
    "RationLifecycleNotFound",
    "RationLifecycleConflict",
    "TransitionError",
]
