import json

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
