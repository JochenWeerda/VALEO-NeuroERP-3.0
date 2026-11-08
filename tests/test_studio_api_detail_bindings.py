"""Tenant-scoped detail reads backing Studio object pages."""

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import (
    fibu_geschaeftsjahre,
    fibu_stammdaten,
    fibu_zahlungsmeldungen,
    individualpreise,
    op_skonto_auszifferung,
    preis_rabattgruppen,
    produktion_rezepturgruppen,
    warengruppen,
)


class _Result:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row


class _Db:
    def __init__(self, row=None):
        self.row = row
        self.calls = []

    def execute(self, statement, params):
        self.calls.append((str(statement), params))
        return _Result(self.row)


@pytest.mark.parametrize(
    "read_detail",
    [
        warengruppen.get_warengruppe,
        individualpreise.get_individualpreis,
        preis_rabattgruppen.get_rabattgruppe,
        produktion_rezepturgruppen.get_rezepturgruppe,
        fibu_geschaeftsjahre.get_geschaeftsjahr,
        fibu_zahlungsmeldungen.get_zahlungsmeldung,
        op_skonto_auszifferung.get_auszifferung,
        fibu_stammdaten.get_zahlungsformular,
    ],
)
def test_studio_detail_reads_use_verified_tenant_and_hide_foreign_or_missing_rows(read_detail):
    db = _Db()
    for tenant in ("tenant-a", "tenant-b"):
        with pytest.raises(HTTPException) as exc:
            read_detail("object-1", db=db, tenant_id=tenant)
        assert exc.value.status_code == 404
        sql, params = db.calls[-1]
        assert "tenant_id" in sql
        assert params["tid"] == tenant
        assert "object-1" in params.values()


def test_studio_detail_routes_keep_typed_get_contracts():
    routes = {
        route.path: route
        for router in (
            warengruppen.router,
            individualpreise.router,
            preis_rabattgruppen.router,
            produktion_rezepturgruppen.router,
            fibu_geschaeftsjahre.router,
            fibu_zahlungsmeldungen.router,
            op_skonto_auszifferung.router,
            fibu_stammdaten.router,
        )
        for route in router.routes
        if "GET" in route.methods
    }
    for path in (
        "/stammdaten/warengruppen/{gruppe_nr}",
        "/preise/individualpreise/{preis_id}",
        "/preise/rabatte/gruppen/{gruppe_id}",
        "/produktion/mischfutter/rezepturgruppen/{gruppe_nr}",
        "/fibu/geschaeftsjahre/detail/{jahr_id}",
        "/fibu/zahlungsmeldungen/{meldung_id}",
        "/fibu/op-auszifferung/{auszifferung_id}",
        "/fibu/stammdaten/zahlungsformulare/{formular_id}",
    ):
        assert path in routes
        assert routes[path].response_model is not None
