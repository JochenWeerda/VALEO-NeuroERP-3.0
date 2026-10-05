"""SPEC-P1-06 Welle 2: getypte response_model fuer Mock-Harness, Futtermittel-QS
und POS-Fiskalisierung.

Wie in Welle 1 gilt: FastAPI filtert die Antwort gegen das response_model,
darum wird jedes Schema gegen die tatsaechliche Rueckgabeform geprueft.

Fuer die Mock-Harness laufen die Proben gegen den echten Service. Fuer
Futtermittel-QS und Fiskalisierung wird gegen DDL- bzw. servicegetreue
Beispielzeilen geprueft, weil beide eine laufende Datenbank braeuchten.
"""

from datetime import date, datetime

import pytest

from app.api.v1.endpoints import external_mock_harness as mock_module
from app.api.v1.endpoints import futtermittel_qs as qs_module
from app.api.v1.endpoints import pos_fiscalization as fiscal_module
from app.api.v1.schemas import futtermittel_qs_schemas as qs_schemas
from app.api.v1.schemas import pos_fiscalization_schemas as fiscal_schemas
from app.services.external_mock_harness_service import external_mock_harness_service as mock_service

pytestmark = pytest.mark.unit


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in route.methods:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = route.response_model
    return out


@pytest.mark.parametrize(
    "module",
    [mock_module, qs_module, fiscal_module],
    ids=["external_mock_harness", "futtermittel_qs", "pos_fiscalization"],
)
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    """Kein ``dict``/``list[dict]``/``Any`` mehr als response_model."""
    schwach = []
    for (path, method), model in _response_models(module).items():
        # Achtung: list[EchtesSchema].__name__ ist ebenfalls "list" — nur die
        # Textform unterscheidet den generischen Container vom nackten Typ.
        text = str(model)
        if (
            model is None
            or model in (dict, list)
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


# ── Mock-Harness: Proben gegen den echten Service ────────────────────────────

MOCK_CASES = [
    ("SystemsOverviewOut", lambda: mock_service.systems_overview()),
    ("DatevExportStartOut", lambda: mock_service.datev_export_start("M1", "2026-01-01", "2026-01-31")),
    ("DatevExportStatusOut", lambda: mock_service.datev_export_status("J1")),
    ("TseSignOut", lambda: mock_service.tse_sign_transaction("K1", "B1", 1999)),
    ("DsfinvkExportOut", lambda: mock_service.dsfinvk_export("K1", "2026-08-22")),
    ("ElsterSubmitOut", lambda: mock_service.elster_submit("123", "UStVA", "2026-07", {"a": 1})),
    ("ElsterStatusOut", lambda: mock_service.elster_status("T1")),
    ("DmsUploadOut", lambda: mock_service.dms_upload("Titel", "rechnung", "abc")),
    ("DmsSearchOut", lambda: mock_service.dms_search("weizen")),
    ("BankCamtImportOut", lambda: mock_service.bank_camt_import("DE99", 3)),
]


@pytest.mark.parametrize(("schema_name", "call"), MOCK_CASES, ids=[c[0] for c in MOCK_CASES])
def test_mock_harness_schema_behaelt_alle_felder(schema_name, call):
    from app.api.v1.schemas import external_mock_harness_schemas as schemas

    model = getattr(schemas, schema_name)
    data = call()
    dumped = _assert_kein_feldverlust(model, data, schema_name)
    # 'simulated: true' ist der Vertrag der Harness und darf nie wegfallen.
    assert dumped["simulated"] is True
    # Verschachtelte Listen ebenfalls vollstaendig.
    for key, value in data.items():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            for index, item in enumerate(value):
                fehlend = [k for k in item if k not in dumped[key][index]]
                assert not fehlend, f"{schema_name}.{key}[{index}] verliert {fehlend}"


# ── Futtermittel-QS: DDL-getreue Zeilen ──────────────────────────────────────


def test_haccp_plan_schema_deckt_das_ddl_ab():
    row = {
        "id": "1",
        "tenant_id": "t",
        "bezeichnung": "Plan",
        "gueltigkeit_von": date(2026, 1, 1),
        "gueltigkeit_bis": None,
        "gefahrenanalyse": [],
        "ccp_liste": [{"nr": 1}],
        "ueberwachung": [],
        "korrekturen": [],
        "verifizierung": {"turnus": "jaehrlich"},
        "aktiv": True,
        "erstellt_am": datetime(2026, 1, 1),
        "geaendert_am": datetime(2026, 1, 2),
    }
    dumped = _assert_kein_feldverlust(qs_schemas.HaccpPlanOut, row)
    assert dumped["ccp_liste"] == [{"nr": 1}]
    assert dumped["verifizierung"] == {"turnus": "jaehrlich"}


def test_vlog_meldung_schema_deckt_das_ddl_ab():
    row = {
        "id": "1",
        "tenant_id": "t",
        "rezeptur_id": "r",
        "meldedatum": date(2026, 8, 1),
        "menge_kg": 12.5,
        "rohstoff_liste": [{"artikel": "Weizen"}],
        "gvo_frei": True,
        "zertifikat_nr": "Z-1",
        "status": "erstellt",
        "notiz": None,
        "erstellt_am": datetime(2026, 8, 1),
        "geaendert_am": datetime(2026, 8, 1),
    }
    dumped = _assert_kein_feldverlust(qs_schemas.VlogMeldungOut, row)
    assert dumped["rohstoff_liste"] == [{"artikel": "Weizen"}]


def test_pruefpunkt_schema_deckt_das_ddl_ab():
    row = {
        "id": "1",
        "tenant_id": "t",
        "periode": "2026-08",
        "kategorie": "allgemein",
        "punkt_nr": "1.1",
        "bezeichnung": "B",
        "anforderung": "A",
        "bestaetigt": False,
        "abweichung": None,
        "massnahme": None,
        "bestaetigt_am": None,
        "bestaetigt_von": None,
        "erstellt_am": datetime(2026, 8, 1),
    }
    _assert_kein_feldverlust(qs_schemas.QsPruefpunktOut, row)


def test_qs_schreibantworten():
    assert qs_schemas.QsAnlageOut.model_validate({"id": "1", "ok": True}).model_dump() == {
        "id": "1",
        "ok": True,
    }
    assert qs_schemas.VlogStatusOut.model_validate(
        {"id": "1", "status": "gesendet"}
    ).model_dump() == {"id": "1", "status": "gesendet"}
    assert qs_schemas.PruefpunktBestaetigtOut.model_validate(
        {"id": "1", "bestaetigt": True}
    ).model_dump() == {"id": "1", "bestaetigt": True}


# ── POS-Fiskalisierung ───────────────────────────────────────────────────────


def test_fiskal_config_traegt_beide_zweige():
    """``get_config`` liefert ohne Datensatz einen Defaultblock ohne ``updated_at``."""
    unkonfiguriert = {
        "provider": "simulation",
        "dsfinvk_provider": "simulation",
        "cash_register_id": None,
        "client_id": None,
        "simulation_allowed": False,
        "settings": {},
        "configured": False,
    }
    dumped = _assert_kein_feldverlust(fiscal_schemas.FiscalConfigOut, unkonfiguriert)
    assert dumped["configured"] is False

    konfiguriert = {
        **unkonfiguriert,
        "provider": "fiskaly",
        "dsfinvk_provider": "fiskaly",
        "cash_register_id": "K1",
        "client_id": "C1",
        "settings": {"endpoint": "https://example.invalid"},
        "updated_at": datetime(2026, 8, 1),
        "configured": True,
    }
    dumped = _assert_kein_feldverlust(fiscal_schemas.FiscalConfigOut, konfiguriert)
    assert dumped["settings"] == {"endpoint": "https://example.invalid"}


def test_fiskal_readiness_behaelt_verschachtelte_providerfelder():
    provider = {
        "provider": "fiskaly",
        "ready": False,
        "live": False,
        "blockers": ["Kassen-/TSS-ID fehlt"],
        "capabilities": ["sign"],
        "details": {"env": "test"},
    }
    produkt = {
        "product": "submit_de",
        "label": "Submit DE",
        "ready": True,
        "blockers": [],
        "details": {},
    }
    daten = {
        "configured": True,
        "config_blockers": ["Client-ID fehlt"],
        "sign": provider,
        "dsfinvk": provider,
        "products": [produkt],
        "ready": False,
    }
    dumped = _assert_kein_feldverlust(fiscal_schemas.FiscalReadinessOut, daten)
    for feld in provider:
        assert feld in dumped["sign"], f"sign.{feld} verloren"
    for feld in produkt:
        assert feld in dumped["products"][0], f"products[0].{feld} verloren"
    assert dumped["sign"]["blockers"] == ["Kassen-/TSS-ID fehlt"]


def test_fiskal_tageswerte():
    daten = {
        "transaction_count": 5,
        "gross_total": 100.0,
        "cash_total": 40.0,
        "card_total": 60.0,
        "incomplete_count": 1,
    }
    _assert_kein_feldverlust(fiscal_schemas.FiscalDailySummaryOut, daten)


def test_fiskal_transaktionen_nutzen_den_vorhandenen_vertrag():
    """start/finish und die Exporte haben bereits Pydantic-Vertraege — die
    Endpunkte sollen genau diese deklarieren statt eigener Kopien."""
    from app.services.fiscalization.contracts import FiscalTransactionResult, ProviderResult

    modelle = _response_models(fiscal_module)
    assert modelle[("/pos/fiscalization/transactions/start", "POST")] is FiscalTransactionResult
    assert modelle[("/pos/fiscalization/transactions/finish", "POST")] is FiscalTransactionResult
    assert modelle[("/pos/fiscalization/cash-point-closings", "POST")] is ProviderResult
    assert modelle[("/pos/fiscalization/exports", "POST")] is ProviderResult
    assert modelle[("/pos/fiscalization/exports/{export_type}", "POST")] is ProviderResult
