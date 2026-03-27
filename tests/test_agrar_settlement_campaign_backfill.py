from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

from app.api.v1.endpoints import agrar_settlements as module
from app.api.v1.endpoints.agrar_settlements import (
    SettlementCampaignBackfillRequest,
    backfill_settlement_campaign_reference,
)
from app.infrastructure.models import AgrarSettlement


class _FakeSettlementQuery:
    def __init__(self, settlements: list["_SettlementStub"]):
        self.settlements = settlements

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self.settlements


class _FakeDb:
    def __init__(self, settlements: list["_SettlementStub"]):
        self.settlements = settlements
        self.commits = 0

    def query(self, model):
        if model is AgrarSettlement:
            return _FakeSettlementQuery(self.settlements)
        raise AssertionError(f"unexpected model {model}")

    def commit(self):
        self.commits += 1

    def rollback(self):
        return None


@dataclass
class _SettlementStub:
    id: str
    created_at: datetime | None
    campaign_id: str | None = None


def test_backfill_assigns_campaign_id_for_unambiguous_legacy_settlements(monkeypatch):
    db = _FakeDb(
        [
            _SettlementStub(id="set-1", created_at=datetime(2026, 7, 10, tzinfo=timezone.utc)),
            _SettlementStub(id="set-2", created_at=datetime(2026, 8, 5, tzinfo=timezone.utc)),
        ]
    )
    monkeypatch.setattr(
        module,
        "_load_tenant_settings",
        lambda _db, _tenant_id: {
            "erntefenster_campaigns": [
                {"id": "camp-1", "start_date": "2026-07-01", "end_date": "2026-07-31"},
                {"id": "camp-2", "start_date": "2026-08-01", "end_date": "2026-08-31"},
            ]
        },
    )

    result = asyncio.run(
        backfill_settlement_campaign_reference(
            SettlementCampaignBackfillRequest(campaign_id="camp-1"),
            tenant_id="tenant-1",
            db=db,
        )
    )

    assert result.updated_count == 1
    assert result.ambiguous_count == 0
    assert result.updated_settlement_ids == ["set-1"]
    assert db.settlements[0].campaign_id == "camp-1"
    assert db.settlements[1].campaign_id is None
    assert db.commits == 1


def test_backfill_leaves_ambiguous_legacy_settlements_unassigned(monkeypatch):
    db = _FakeDb(
        [
            _SettlementStub(id="set-ambiguous", created_at=datetime(2026, 7, 20, tzinfo=timezone.utc)),
        ]
    )
    monkeypatch.setattr(
        module,
        "_load_tenant_settings",
        lambda _db, _tenant_id: {
            "erntefenster_campaigns": [
                {"id": "camp-1", "start_date": "2026-07-01", "end_date": "2026-07-31"},
                {"id": "camp-2", "start_date": "2026-07-15", "end_date": "2026-08-15"},
            ]
        },
    )

    result = asyncio.run(
        backfill_settlement_campaign_reference(
            SettlementCampaignBackfillRequest(campaign_id="camp-1"),
            tenant_id="tenant-1",
            db=db,
        )
    )

    assert result.updated_count == 0
    assert result.ambiguous_count == 1
    assert result.ambiguous_settlement_ids == ["set-ambiguous"]
    assert db.settlements[0].campaign_id is None
    assert db.commits == 0
