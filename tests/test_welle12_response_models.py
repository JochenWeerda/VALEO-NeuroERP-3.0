"""SPEC-P1-06 Welle 12: Controlling, Periodenabschluss, Bank-Import."""

import pytest

from app.api.v1.endpoints import bank_import as bank_module
from app.api.v1.endpoints import controlling_actions as ctrl_module
from app.api.v1.endpoints import finance_period as period_module
from app.api.v1.schemas import finance_controlling_bundle_schemas as fin

pytestmark = pytest.mark.unit

WELLE12_MODULE = [ctrl_module, period_module, bank_module]


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in getattr(route, "methods", []) or []:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = getattr(route, "response_model", None)
    return out


@pytest.mark.parametrize("module", WELLE12_MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        if model is None:
            continue
        text = str(model)
        if (
            model in (dict, list)
            or "dict[str, Any]" in text
            or "list[dict" in text
        ):
            schwach.append(f"{method} {path}")
    assert not schwach, f"noch schwach typisiert: {schwach}"


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


def test_controlling_and_period_shapes():
    _assert_kein_feldverlust(
        fin.ControllingBudgetCreatedOut,
        {
            "id": "b1",
            "kostenstelle_id": "KST1",
            "periode": "2026-09",
            "plan_eur": 1000.0,
            "bezeichnung": "Plan",
            "status": "ENTWURF",
        },
    )
    _assert_kein_feldverlust(
        fin.ControllingBudgetTransitionOut,
        {
            "id": "b1",
            "tenant_id": "t1",
            "kostenstelle_id": "KST1",
            "periode": "2026-09",
            "plan_eur": 1000.0,
            "bezeichnung": "Plan",
            "status": "FREIGEGEBEN",
            "previous_status": "ENTWURF",
            "idempotent": False,
            "freigabe_operator": "u1",
            "extra_db_col": "kept",
        },
    )
    _assert_kein_feldverlust(
        fin.ControllingAbweichungOut,
        {
            "kostenstelle_id": "KST1",
            "periode": "2026-09",
            "plan_eur": 100.0,
            "ist_eur": 110.0,
            "abweichung_eur": 10.0,
            "abweichung_pct": 10.0,
            "ampel": "GELB",
        },
    )
    _assert_kein_feldverlust(
        fin.ControllingIstWertOut,
        {
            "id": "i1",
            "kostenstelle_id": "KST1",
            "periode": "2026-09",
            "ist_eur": 50.0,
            "buchungsref": "B-1",
        },
    )
    _assert_kein_feldverlust(
        fin.ControllingKstAbschlussOut,
        {
            "id": "a1",
            "kostenstelle_id": "KST1",
            "periode": "2026-09",
            "status": "ABGESCHLOSSEN",
            "previous_status": "IN_BEARBEITUNG",
            "idempotent": False,
        },
    )
    _assert_kein_feldverlust(
        fin.FinancePeriodListOut,
        {
            "items": [
                {
                    "period": "2026-09",
                    "start": "2026-09-01",
                    "end": "2026-09-30",
                    "status": "offen",
                    "closed_at": None,
                    "closed_by": None,
                    "offen_count": 2,
                    "storno_inkonsistent": 0,
                    "abschlussreif": False,
                }
            ]
        },
    )
    _assert_kein_feldverlust(
        fin.FinancePeriodReadinessOut,
        {
            "period": "2026-09",
            "offen_count": 0,
            "storno_inkonsistent": 0,
            "ready": True,
            "blocker": [],
        },
    )
    _assert_kein_feldverlust(
        fin.FinancePeriodActionOut,
        {"ok": True, "period": "2026-09", "status": "closed", "erzwungen": False},
    )


def test_bank_import_shapes():
    _assert_kein_feldverlust(
        fin.BankStatementImportOut,
        {
            "statement_id": "s1",
            "lines": 3,
            "iban": "DE00",
            "format": "MT940",
        },
    )
    _assert_kein_feldverlust(
        fin.BankMatchOut,
        {
            "statement_id": "s1",
            "matched": 1,
            "unmatched": 2,
            "info": "Keine offenen Buchungen",
        },
    )
    _assert_kein_feldverlust(
        fin.BankStatementListOut,
        {
            "items": [
                {
                    "id": "s1",
                    "iban": "DE00",
                    "format": "MT940",
                    "filename": "a.sta",
                    "line_count": 3,
                    "imported_at": "2026-09-01T10:00:00",
                }
            ],
            "count": 1,
        },
    )
