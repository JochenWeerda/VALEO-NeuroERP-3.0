"""UIX-073: E-Mail-Termine werden als Kalender-Vorschlaege projiziert."""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from app.services.calendar_projection_service import CalendarProjectionService

pytestmark = pytest.mark.unit

NOW = datetime(2026, 7, 8, 9, tzinfo=UTC)


class _Result:
    def __init__(self, rows: list[dict[str, Any]] | None = None):
        self.rows = rows or []

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self.rows

    def first(self) -> dict[str, Any] | None:
        return self.rows[0] if self.rows else None


class _CalendarDb:
    def __init__(self) -> None:
        self.items: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.commits = 0

    def execute(self, statement: Any, params: dict[str, Any] | None = None) -> _Result:
        sql = str(statement)
        params = params or {}
        if "SELECT id, title, starts_at, ends_at, object_type, object_id, payload" in sql:
            rows = [
                row for row in self.items.values()
                if row["tenant_id"] == params["tenant_id"]
                and row["layer"] == "logistik"
                and row["status"] in {"projected", "proposed", "confirmed"}
                and not (row["source"] == "email_capture" and row["source_key"] == params["source_key"])
                and row["starts_at"] <= params["window_end"]
                and (row.get("ends_at") or row["starts_at"]) >= params["window_start"]
            ]
            return _Result(rows)
        if "INSERT INTO domain_shared.calendar_items" in sql:
            key = (params["tenant_id"], params["source"], params["source_key"])
            existing = self.items.get(key)
            if not existing or existing["status"] == "projected":
                self.items[key] = {
                    "id": existing["id"] if existing else params["id"],
                    **params,
                    "payload": json.loads(params["payload"]),
                    "created_at": NOW,
                    "updated_at": NOW,
                }
            return _Result([])
        if "UPDATE domain_shared.calendar_items" in sql and "status = 'proposed'" in sql:
            for item in self.items.values():
                if (
                    item["tenant_id"] == params["tenant_id"]
                    and item["id"] == params["id"]
                    and item["status"] == "proposed"
                ):
                    item["status"] = params["status"]
                    return _Result([item])
            return _Result([])
        return _Result([])

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        pass


def test_email_terms_are_written_as_proposed_calendar_items_idempotently() -> None:
    db = _CalendarDb()
    service = CalendarProjectionService(db)

    result = service.propose_email_terms(
        "tenant-uix073",
        mail_id="mail-7712",
        subject="Anlieferung Bestellung 7712",
        body="Wir liefern am 12.07. um 14 Uhr an.",
        received_at=NOW,
        sender_domain="spedition-meyer.de",
    )
    service.propose_email_terms(
        "tenant-uix073",
        mail_id="mail-7712",
        subject="Anlieferung Bestellung 7712",
        body="Wir liefern am 12.07. um 14 Uhr an.",
        received_at=NOW,
        sender_domain="spedition-meyer.de",
    )

    assert result["sourceKeys"] == ["mail-7712:0"]
    assert len(db.items) == 1
    item = db.items[("tenant-uix073", "email_capture", "mail-7712:0")]
    assert item["status"] == "proposed"
    assert item["layer"] == "logistik"
    assert item["payload"]["mail_id"] == "mail-7712"
    assert item["payload"]["matched_object"]["type"] == "purchase_order"
    assert item["object_screen_id"] == "einkauf/purchase-order"
    assert db.commits == 2


def test_email_terms_include_conflicts_for_same_resource_in_two_hour_window() -> None:
    db = _CalendarDb()
    db.items[("tenant-uix073", "manual", "avis-1")] = {
        "id": "avis-1",
        "tenant_id": "tenant-uix073",
        "source": "manual",
        "source_key": "avis-1",
        "layer": "logistik",
        "item_type": "termin",
        "title": "Bestehendes Avis",
        "starts_at": datetime(2026, 7, 12, 13, tzinfo=UTC),
        "ends_at": datetime(2026, 7, 12, 14, tzinfo=UTC),
        "all_day": False,
        "status": "confirmed",
        "object_type": "supplier",
        "object_id": "spedition-meyer.de",
        "payload": {"matched_object": {"type": "supplier", "id": "spedition-meyer.de"}},
    }

    CalendarProjectionService(db).propose_email_terms(
        "tenant-uix073",
        mail_id="mail-2",
        subject="Anlieferung",
        body="Wir kommen am 12.07. um 14 Uhr.",
        received_at=NOW,
        sender_domain="spedition-meyer.de",
    )

    item = db.items[("tenant-uix073", "email_capture", "mail-2:0")]
    assert item["payload"]["matched_object"]["type"] == "supplier"
    assert item["payload"]["conflicts"] == [
        {
            "item_id": "avis-1",
            "reason": "Slot ueberschneidet bestehenden Logistik-Termin",
            "title": "Bestehendes Avis",
            "starts_at": "2026-07-12T13:00:00+00:00",
        }
    ]


def test_email_terms_without_date_do_not_create_calendar_items() -> None:
    db = _CalendarDb()

    result = CalendarProjectionService(db).propose_email_terms(
        "tenant-uix073",
        mail_id="mail-empty",
        subject="Preisfrage",
        body="Koennen Sie ein Angebot fuer Weizen senden?",
        received_at=NOW + timedelta(hours=1),
        sender_domain="lieferant.test",
    )

    assert result["candidates"] == 0
    assert db.items == {}


def test_mail_to_calendar_proposal_can_be_confirmed_without_autoconfirm() -> None:
    db = _CalendarDb()
    service = CalendarProjectionService(db)

    service.propose_email_terms(
        "tenant-uix073",
        mail_id="mail-confirm",
        subject="Anlieferung Bestellung 8811",
        body="Bitte avisieren: Lieferung am 12.07. um 14 Uhr.",
        received_at=NOW,
        sender_domain="spedition-meyer.de",
    )
    item = db.items[("tenant-uix073", "email_capture", "mail-confirm:0")]

    assert item["status"] == "proposed"

    confirmed = service.transition_proposed("tenant-uix073", item["id"], "confirmed")

    assert confirmed is not None
    assert confirmed["status"] == "confirmed"
    assert db.items[("tenant-uix073", "email_capture", "mail-confirm:0")]["status"] == "confirmed"
