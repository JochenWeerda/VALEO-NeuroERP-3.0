"""Transactional lifecycle, overdue notification and history for feeding measures."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.events import emit_feeding_event
from app.agrar.rations.measure_lifecycle import (
    MeasureLifecycleError,
    overdue_notification_key,
    transition_measure,
)
from app.core.uuid7 import uuid7


class FeedingMeasureNotFound(LookupError):
    pass


class FeedingMeasureConflict(RuntimeError):
    pass


class FeedingMeasureLifecycleService:
    def __init__(self, db: Session, tenant_id: str, actor: str):
        self.db, self.tenant_id, self.actor = db, tenant_id, actor or "unknown"

    def _latest(
        self, measure_id: str, *, group_ids: list[str], lock: bool = False
    ) -> dict[str, Any]:
        lock_sql = " FOR UPDATE OF v" if lock else ""
        row = (
            self.db.execute(
                text(
                    """SELECT v.*,m.group_id,m.title
          FROM domain_agrar.feeding_measure_versions v
          JOIN domain_agrar.feeding_actual_measures m
            ON m.tenant_id=v.tenant_id AND m.id=v.measure_id
          WHERE v.tenant_id=:tenant_id AND v.measure_id=:measure_id
            AND m.group_id=ANY(:group_ids)
          ORDER BY v.version DESC LIMIT 1"""
                    + lock_sql
                ),
                {
                    "tenant_id": self.tenant_id,
                    "measure_id": measure_id,
                    "group_ids": group_ids,
                },
            )
            .mappings()
            .first()
        )
        if not row:
            raise FeedingMeasureNotFound("Massnahme nicht gefunden.")
        return dict(row)

    def transition(
        self, measure_id: str, payload: dict[str, Any], *, group_ids: list[str]
    ) -> dict[str, Any]:
        current = self._latest(measure_id, group_ids=group_ids, lock=True)
        if current["version"] != payload["expected_version"]:
            raise FeedingMeasureConflict(
                f"Versionskonflikt: erwartet {payload['expected_version']}, aktuell {current['version']}."
            )
        try:
            target = transition_measure(
                current_status=current["status"],
                target_status=payload["target_status"],
                reason=payload["reason"],
                effectiveness=payload.get("effectiveness"),
                effectiveness_result=payload.get("effectiveness_result"),
            )
        except MeasureLifecycleError as exc:
            raise FeedingMeasureConflict(str(exc)) from exc
        values = {
            "owner_subject": payload.get("owner_subject") or current["owner_subject"],
            "due_date": payload.get("due_date") or current["due_date"],
            "reminder_date": payload.get("reminder_date", current["reminder_date"]),
            "escalation_status": payload.get("escalation_status")
            or current["escalation_status"],
        }
        row = (
            self.db.execute(
                text("""INSERT INTO domain_agrar.feeding_measure_versions
          (id,tenant_id,measure_id,version,status,owner_subject,due_date,reminder_date,
           escalation_status,effectiveness,effectiveness_result,reason,changed_by)
          VALUES (:id,:tenant_id,:measure_id,:version,:status,:owner_subject,:due_date,
           :reminder_date,:escalation_status,:effectiveness,:effectiveness_result,:reason,:actor)
          RETURNING *"""),
                {
                    **payload,
                    **values,
                    "id": str(uuid7()),
                    "tenant_id": self.tenant_id,
                    "measure_id": measure_id,
                    "version": current["version"] + 1,
                    "status": target,
                    "actor": self.actor,
                },
            )
            .mappings()
            .one()
        )
        if target == "completed":
            emit_feeding_event(
                self.db,
                tenant_id=self.tenant_id,
                event_type="feeding.measure.completed",
                aggregate_id=measure_id,
                payload={
                    "measure_id": measure_id,
                    "version": row["version"],
                    "group_id": current["group_id"],
                    "effectiveness": row["effectiveness"],
                },
            )
        self.db.commit()
        return dict(row)

    def history(self, measure_id: str, *, group_ids: list[str]) -> list[dict[str, Any]]:
        self._latest(measure_id, group_ids=group_ids)
        return [
            dict(row)
            for row in self.db.execute(
                text("""SELECT *
          FROM domain_agrar.feeding_measure_versions
          WHERE tenant_id=:tenant_id AND measure_id=:measure_id ORDER BY version DESC"""),
                {"tenant_id": self.tenant_id, "measure_id": measure_id},
            )
            .mappings()
            .all()
        ]

    def process_overdue(self, *, as_of: date, group_ids: list[str]) -> dict[str, int]:
        if not group_ids:
            return {"examined": 0, "created": 0}
        rows = (
            self.db.execute(
                text("""SELECT DISTINCT ON (v.measure_id)
          v.*,m.group_id,m.title FROM domain_agrar.feeding_measure_versions v
          JOIN domain_agrar.feeding_actual_measures m
            ON m.tenant_id=v.tenant_id AND m.id=v.measure_id
          WHERE v.tenant_id=:tenant_id AND m.group_id=ANY(:group_ids)
          ORDER BY v.measure_id,v.version DESC"""),
                {
                    "tenant_id": self.tenant_id,
                    "group_ids": group_ids,
                },
            )
            .mappings()
            .all()
        )
        due = [
            dict(row)
            for row in rows
            if row["status"] not in {"completed", "cancelled"}
            and row["due_date"] < as_of
        ]
        created = 0
        for item in due:
            key = overdue_notification_key(
                item["measure_id"], item["version"], item["due_date"]
            )
            notification = self.db.execute(
                text("""INSERT INTO domain_agrar.feeding_notifications
              (id,tenant_id,recipient_subject,event_type,aggregate_id,title,body,deep_link,dedupe_key)
              VALUES (:id,:tenant_id,:recipient,'feeding.measure.overdue',:measure_id,:title,:body,:link,:key)
              ON CONFLICT (tenant_id,dedupe_key) DO NOTHING RETURNING id"""),
                {
                    "id": str(uuid7()),
                    "tenant_id": self.tenant_id,
                    "recipient": item["owner_subject"],
                    "measure_id": item["measure_id"],
                    "title": f"Massnahme ueberfaellig: {item['title']}",
                    "body": f"Faellig seit {item['due_date']}",
                    "link": f"/futtermittel/beratung?measure_id={item['measure_id']}",
                    "key": key,
                },
            ).first()
            if notification:
                emit_feeding_event(
                    self.db,
                    tenant_id=self.tenant_id,
                    event_type="feeding.measure.overdue",
                    aggregate_id=item["measure_id"],
                    payload={
                        "measure_id": item["measure_id"],
                        "version": item["version"],
                        "group_id": item["group_id"],
                        "owner_subject": item["owner_subject"],
                        "due_date": str(item["due_date"]),
                        "notification_id": notification[0],
                    },
                )
                created += 1
        self.db.commit()
        return {"examined": len(due), "created": created}

    def notifications(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.execute(
                text("""SELECT *
          FROM domain_agrar.feeding_notifications
          WHERE tenant_id=:tenant_id AND recipient_subject=:actor
          ORDER BY created_at DESC"""),
                {
                    "tenant_id": self.tenant_id,
                    "actor": self.actor,
                },
            )
            .mappings()
            .all()
        ]
