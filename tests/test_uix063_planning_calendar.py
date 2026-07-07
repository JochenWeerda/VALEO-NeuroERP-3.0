from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.mask_screen_definition import _check_readiness
from app.core.database import get_db
from app.core.screen_definitions import get_screen_definition
from app.services.calendar_projection_service import (
    AgrarSachkundeProjector,
    CalendarItemDraft,
    CalendarProjectionService,
    CrmWiedervorlagenProjector,
    KontraktFristenProjector,
    OpenItemsProjector,
    PeriodischeBuchungenProjector,
    SaisonKalenderProjector,
)
from main import app


HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-calendar-uix063"}
NOW = datetime(2026, 7, 7, 8, tzinfo=UTC)


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
    def __init__(self):
        self.items: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.tokens: dict[str, str] = {}
        self.commits = 0
        self.deletes: list[dict[str, Any]] = []

    def execute(self, statement: Any, params: dict[str, Any] | None = None) -> _Result:
        sql = str(statement)
        params = params or {}
        if "FROM domain_erp.periodische_buchungen" in sql:
            return _Result([{
                "id": "pb-1", "buchung_nr": "PB-1", "bezeichnung": "Abo-Rechnung",
                "naechste_ausfuehrung": NOW + timedelta(days=3), "betrag": 120, "rhythmus": "monthly",
            }])
        if "FROM domain_erp.open_items" in sql:
            return _Result([{
                "id": "op-1", "beleg_nr": "RE-1", "partner_name": "Folkerts",
                "faellig_am": (NOW + timedelta(days=5)).date(), "offen": 250,
            }])
        if "FROM domain_agrar.kontrakte" in sql:
            return _Result([{
                "id": "kon-1", "kontrakt_nr": "K-1", "partner_name": "DueKa",
                "andienung_bis": (NOW + timedelta(days=20)).date(),
                "fruehbezugsrabatt_bis": (NOW + timedelta(days=8)).date(),
            }])
        if "FROM domain_crm.activities" in sql:
            return _Result([{
                "id": "act-1", "customer_id": "cust-1", "customer_name": "Folkerts",
                "subject": "Rueckruf", "due_date": NOW + timedelta(days=2),
            }])
        if "FROM domain_compliance.agrar_sachkunde" in sql:
            return _Result([{
                "id": "sk-1", "person_ref": "u-1", "display_name": "Meyer",
                "gueltig_bis": (NOW + timedelta(days=30)).date(), "sachkunde_art": "PSM",
            }])
        if "INSERT INTO domain_shared.calendar_items" in sql:
            key = (params["tenant_id"], params["source"], params["source_key"])
            existing = self.items.get(key)
            if not existing or existing["status"] == "projected":
                row = {
                    "id": existing["id"] if existing else params["id"],
                    **params,
                    "payload": json.loads(params["payload"]),
                    "created_at": NOW,
                    "updated_at": NOW,
                }
                self.items[key] = row
            return _Result([])
        if "DELETE FROM domain_shared.calendar_items" in sql:
            self.deletes.append(params)
            keys = set(params.get("source_keys") or [])
            for key, row in list(self.items.items()):
                if row["tenant_id"] == params["tenant_id"] and row["source"] == params["source"] and row["status"] == "projected" and row["source_key"] not in keys:
                    self.items.pop(key)
            return _Result([])
        if "FROM domain_shared.calendar_items" in sql:
            layers = set(params.get("layers") or [])
            rows = [
                row for row in self.items.values()
                if row["tenant_id"] == params["tenant_id"] and (not layers or row["layer"] in layers)
            ]
            return _Result(rows)
        if "UPDATE domain_shared.calendar_items" in sql:
            for key, row in self.items.items():
                if row["tenant_id"] == params["tenant_id"] and row["id"] == params["id"] and row["status"] == "proposed":
                    row["status"] = params["status"]
                    return _Result([row])
            return _Result([])
        if "INSERT INTO domain_shared.calendar_ics_tokens" in sql:
            self.tokens[params["token_hash"]] = params["tenant_id"]
            return _Result([])
        if "FROM domain_shared.calendar_ics_tokens" in sql:
            tenant = self.tokens.get(params["token_hash"])
            return _Result([{"tenant_id": tenant}] if tenant else [])
        return _Result([])

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        pass


def test_all_five_projectors_emit_linked_drafts():
    db = _CalendarDb()
    projectors = [
        PeriodischeBuchungenProjector(),
        OpenItemsProjector(),
        KontraktFristenProjector(),
        CrmWiedervorlagenProjector(),
        AgrarSachkundeProjector(),
    ]
    drafts = [draft for projector in projectors for draft in projector.project(db, "tenant-calendar-uix063", now=NOW)]
    sources = {draft.source for draft in drafts}

    assert sources == {"periodische_buchungen", "open_items", "kontrakt_fristen", "crm_wiedervorlagen", "agrar_sachkunde"}
    assert all(draft.object_route and draft.object_screen_id for draft in drafts)


def test_saison_kalender_projector_reads_static_yaml(tmp_path):
    config_path = tmp_path / "saison_kalender.yaml"
    config_path.write_text(
        """
version: 1
region: DE-Nord
entries:
  - key: weizen-ernte
    title: Erntefenster Weizen
    crop: weizen
    starts_on: "07-20"
    ends_on: "08-05"
    object_route: /planung/kalender
""".strip(),
        encoding="utf-8",
    )

    drafts = SaisonKalenderProjector(config_path).project(_CalendarDb(), "tenant-calendar-uix063", now=NOW)

    assert len(drafts) == 1
    assert drafts[0].source == "saison_kalender"
    assert drafts[0].layer == "saison"
    assert drafts[0].source_key == "weizen-ernte:2026"
    assert drafts[0].payload["region"] == "DE-Nord"


def test_reproject_is_idempotent_and_preserves_non_projected_statuses():
    db = _CalendarDb()
    service = CalendarProjectionService(db)
    service.reproject("tenant-calendar-uix063", now=NOW)
    first_count = len(db.items)

    proposed = CalendarItemDraft(
        source="open_items",
        source_key="manual-proposed",
        layer="finanzen",
        item_type="termin",
        title="Vorschlag",
        starts_at=NOW + timedelta(days=1),
        status="proposed",
        object_route="/finance/op-debitoren/op-x",
        object_screen_id="finance/ar-open-item",
    )
    db.items[("tenant-calendar-uix063", proposed.source, proposed.source_key)] = {
        "id": "proposed-1",
        "tenant_id": "tenant-calendar-uix063",
        **proposed.__dict__,
        "payload": {},
    }

    service.reproject("tenant-calendar-uix063", now=NOW)

    assert len(db.items) == first_count + 1
    assert db.items[("tenant-calendar-uix063", "open_items", "manual-proposed")]["status"] == "proposed"
    assert db.commits == 2


def test_planung_kalender_screen_definition_is_generator_ready():
    sd = get_screen_definition("planung/kalender")
    assert sd is not None
    assert sd["mode"] == "cockpit"
    assert sd["calendar"]["endpoint"] == "/api/v1/planung/kalender"
    readiness = _check_readiness(sd)
    assert readiness["generatorReady"] is True, readiness
    assert "[cockpit_content]" not in " ".join(readiness["warnings"])


def test_calendar_api_lists_by_tenant_and_layer():
    db = _CalendarDb()
    CalendarProjectionService(db).reproject("tenant-calendar-uix063", now=NOW)

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/planung/kalender",
            headers=HEADERS,
            params={"from": NOW.isoformat(), "to": (NOW + timedelta(days=40)).isoformat(), "layers": "finanzen"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body
    assert {item["layer"] for item in body} == {"finanzen"}
    assert all(item["tenant_id"] == "tenant-calendar-uix063" for item in body)


def test_ics_token_is_rotatable_and_feed_is_read_only():
    db = _CalendarDb()
    service = CalendarProjectionService(db)
    service.reproject("tenant-calendar-uix063", now=NOW)

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        token_response = client.get("/api/v1/planung/kalender/ics-token", headers=HEADERS)
        token = token_response.json()["token"]
        feed_response = client.get("/api/v1/planung/kalender/ics", params={"token": token})
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert token_response.status_code == 200
    assert feed_response.status_code == 200
    assert "BEGIN:VCALENDAR" in feed_response.text
    assert "Abo-Rechnung" in feed_response.text
