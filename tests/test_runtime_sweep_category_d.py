import json

import httpx
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.endpoints import activities, cases, einkauf_bestellvorschlag, journal_entries, opportunities
from app.domains.inventory.application.services.replenishment_service import ReplenishmentService
from app.finance.gobd import BelegnummernLuecke, _count_missing_belegnummern
from app.infrastructure.models import NawaroPrintNotification


class _Query:
    def __init__(self, rows):
        self._rows = rows

    def filter(self, *_args, **_kwargs):
        return self

    def all(self):
        return self._rows


class _Db:
    def __init__(self, rows):
        self._rows = rows

    def query(self, *_args, **_kwargs):
        return _Query(self._rows)


class _FailingDb:
    rolled_back = False

    def query(self, *_args, **_kwargs):
        raise SQLAlchemyError("table missing")

    def rollback(self):
        self.rolled_back = True


class _Request:
    query_params: dict[str, str] = {}


def test_belegnummern_luecken_count_missing_range():
    luecken = [
        BelegnummernLuecke(von_nummer="3", bis_nummer="5"),
        BelegnummernLuecke(von_nummer="9", bis_nummer="9"),
    ]

    assert _count_missing_belegnummern(luecken) == 4


def test_inventory_turnover_report_is_strict_json_when_no_cogs():
    report = ReplenishmentService(_Db(rows=[])).get_inventory_turnover_report(
        "tenant-1",
        period_days=30,
    )

    assert report["turnover_ratio"] == 0.0
    assert report["turnover_days"] is None
    json.dumps(report, allow_nan=False)


def test_nawaro_print_notification_model_matches_router_contract():
    for column_name in [
        "tenant_id",
        "debtor_from",
        "debtor_to",
        "delivery_option",
        "form_code",
        "copies",
        "printer_name",
        "created_at",
        "updated_at",
    ]:
        assert hasattr(NawaroPrintNotification, column_name)


@pytest.mark.asyncio
async def test_crm_activity_list_degrades_when_downstream_unreachable(monkeypatch):
    async def _raise_downstream(**_kwargs):
        raise httpx.ConnectError("crm-core unavailable")

    monkeypatch.setattr(activities.crm_core_client, "list_activities", _raise_downstream)

    response = await activities.list_activities(skip=0, limit=50)

    assert response.total == 0
    assert response.items == []


@pytest.mark.asyncio
async def test_crm_case_list_degrades_when_downstream_unreachable(monkeypatch):
    async def _raise_downstream(**_kwargs):
        raise httpx.ConnectError("crm-service unavailable")

    monkeypatch.setattr(cases, "crm_list_cases", _raise_downstream)

    response = await cases.list_cases(skip=0, limit=50)

    assert response.total == 0
    assert response.items == []


@pytest.mark.asyncio
async def test_crm_opportunity_list_degrades_when_downstream_unreachable(monkeypatch):
    async def _raise_downstream(**_kwargs):
        raise httpx.ConnectError("crm-sales unavailable")

    monkeypatch.setattr(opportunities, "crm_list_opportunities", _raise_downstream)

    response = await opportunities.list_opportunities(skip=0, limit=50)

    assert response.total == 0
    assert response.items == []


@pytest.mark.asyncio
async def test_journal_entry_list_raises_503_on_sqlalchemy_error():
    # SPEC-P0-03 harte Regel: FIBU-Journal ist KEIN Kategorie-D-Endpoint —
    # bei DB-Fehler RFC-7807 503 statt stiller leerer Liste (Datenintegritaet).
    from fastapi import HTTPException

    db = _FailingDb()

    with pytest.raises(HTTPException) as exc_info:
        await journal_entries.list_journal_entries(
            request=_Request(),
            tenant_id="tenant-1",
            skip=0,
            limit=50,
            db=db,
        )

    assert db.rolled_back is True
    assert exc_info.value.status_code == 503
    assert "nicht verfuegbar" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_rohware_vorschlag_degrades_on_sqlalchemy_error(monkeypatch):
    class _Service:
        def compute_vorschlag_rohware(self, *_args, **_kwargs):
            raise SQLAlchemyError("transaction failed")

    db = _FailingDb()
    monkeypatch.setattr(einkauf_bestellvorschlag, "_svc", lambda *_args, **_kwargs: _Service())

    response = await einkauf_bestellvorschlag.vorschlag_rohware(
        db=db,
        tenant_id="tenant-1",
    )

    assert db.rolled_back is True
    assert response == []
