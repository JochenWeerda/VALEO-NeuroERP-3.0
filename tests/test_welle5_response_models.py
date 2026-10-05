"""SPEC-P1-06 Welle 5: getypte response_model fuer Finanzaktionen, Abwesenheit,
Legacy-Adapter und Rations-Schnittstellen.
"""

from datetime import date, datetime

import pytest

from app.api.v1.endpoints import finance_actions as finance_module
from app.api.v1.endpoints import hrm_abwesenheit as hrm_module
from app.api.v1.endpoints import legacy_interface_adapters as adapter_module
from app.api.v1.endpoints import rations_integrations as rations_module
from app.api.v1.schemas import finance_actions_schemas as fa
from app.api.v1.schemas import hrm_abwesenheit_schemas as hrm
from app.api.v1.schemas import legacy_interface_adapters_schemas as la
from app.api.v1.schemas import rations_integrations_schemas as ri

pytestmark = pytest.mark.unit

# Die vier Aktions-Endpunkte dieser Welle. finance_actions enthaelt daneben
# viele weitere Routen, die schon vorher getypt waren.
WELLE5_PFADE = {
    "/finance/actions/sepa/mandate",
    "/finance/actions/sepa/mandate/{mandat_id}/widerruf",
    "/finance/actions/sepa/batches",
    "/finance/actions/ratenzahlung/plaene",
    "/finance/actions/ratenzahlung/raten/{rate_id}/buchen",
    "/finance/actions/mahnstufe/{rechnungsnr}/eskalieren",
    "/finance/actions/mahnstufe/{rechnungsnr}/trail",
}


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in route.methods:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = route.response_model
    return out


def _ist_schwach(model) -> bool:
    text = str(model)
    return (
        model is None
        or model in (dict, list)
        or "dict[str, Any]" in text
        or "list[dict" in text
    )


@pytest.mark.parametrize(
    "module",
    [finance_module, hrm_module, adapter_module, rations_module],
    ids=["finance_actions", "hrm_abwesenheit", "legacy_interface_adapters", "rations_integrations"],
)
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = [
        f"{method} {path}"
        for (path, method), model in _response_models(module).items()
        if _ist_schwach(model)
    ]
    assert not schwach, f"noch schwach typisiert: {schwach}"


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


# ── Finanzaktionen ──────────────────────────────────────────────────────────


def test_sepa_mandat_traegt_anlage_und_widerruf():
    """Der Widerruf spreizt die gespeicherte Zeile und ergaenzt idempotent."""
    anlage = {
        "id": "m1",
        "mandat_ref": "MND-001",
        "glaeubiger_id": "DE98ZZZ09999999999",
        "iban": "DE02120300000000202051",
        "bic": "BYLADEM1001",
        "typ": "CORE",
        "status": "AKTIV",
        "erteilung_am": date(2026, 8, 1),
    }
    _assert_kein_feldverlust(fa.SepaMandatOut, anlage, "Mandat(Anlage)")

    widerruf = {
        **anlage,
        "tenant_id": "t",
        "status": "WIDERRUFEN",
        "widerruf_am": date(2026, 8, 20),
        "created_at": datetime(2026, 8, 1),
        "idempotent": False,
    }
    dumped = _assert_kein_feldverlust(fa.SepaMandatOut, widerruf, "Mandat(Widerruf)")
    assert dumped["widerruf_am"] == date(2026, 8, 20)


def test_sepa_batch_behaelt_die_xml_nutzlast():
    dumped = _assert_kein_feldverlust(
        fa.SepaBatchOut,
        {
            "id": "b1",
            "faellig_am": "2026-09-01",
            "gesamt_eur": 1500.0,
            "anzahl_eintraege": 3,
            "status": "ERSTELLT",
            "xml_payload": "<Document>...</Document>",
        },
    )
    assert dumped["xml_payload"].startswith("<Document>")


def test_ratenzahlung_plan_und_rate():
    dumped = _assert_kein_feldverlust(
        fa.RatenzahlungsplanOut,
        {
            "id": "p1",
            "op_id": "OP-1",
            "gesamt_eur": 1200.0,
            "anzahl_raten": 12,
            "restbetrag_eur": 1200.0,
            "status": "AKTIV",
            "rate_ids": ["r1", "r2"],
            "idempotent": False,
        },
        "Plan(Neuanlage)",
    )
    assert dumped["rate_ids"] == ["r1", "r2"]

    # Idempotenzpfad: gespeicherte Zeile ohne rate_ids
    _assert_kein_feldverlust(
        fa.RatenzahlungsplanOut,
        {
            "id": "p1",
            "tenant_id": "t",
            "op_id": "OP-1",
            "gesamt_eur": 1200.0,
            "anzahl_raten": 12,
            "restbetrag_eur": 900.0,
            "status": "AKTIV",
            "created_at": datetime(2026, 8, 1),
            "idempotent": True,
        },
        "Plan(idempotent)",
    )

    dumped = _assert_kein_feldverlust(
        fa.RateOut,
        {
            "id": "r1",
            "plan_id": "p1",
            "tenant_id": "t",
            "rate_nr": 1,
            "betrag_eur": 100.0,
            "faellig_am": date(2026, 9, 1),
            "bezahlt_am": date(2026, 9, 1),
            "status": "BEZAHLT",
            "plan_restbetrag_eur": 1100.0,
            "plan_status": "AKTIV",
            "idempotent": False,
        },
    )
    assert dumped["plan_restbetrag_eur"] == 1100.0


def test_mahnstufe_und_trail():
    stufe = {
        "id": "a1",
        "rechnungsnr": "RE-2026-001",
        "stufe": "2",
        "vorherige_stufe": "1",
        "bearbeitungsgebuehr_eur": 5.0,
        "operator": "system",
    }
    _assert_kein_feldverlust(fa.MahnstufeOut, stufe)

    trail_zeile = {
        "id": "a1",
        "tenant_id": "t",
        "rechnungsnr": "RE-2026-001",
        "stufe": "2",
        "operator": "system",
        "bearbeitungsgebuehr_eur": 5.0,
        "created_at": datetime(2026, 8, 1),
    }
    dumped = _assert_kein_feldverlust(
        fa.MahnstufenTrailOut,
        {"rechnungsnr": "RE-2026-001", "trail": [trail_zeile], "count": 1},
    )
    assert dumped["trail"][0]["bearbeitungsgebuehr_eur"] == 5.0


# ── Abwesenheit ─────────────────────────────────────────────────────────────


def test_abwesenheitsantrag_behaelt_abgeleitete_kennzeichen():
    antrag = {
        "antrag_id": "a1",
        "tenant_id": "t",
        "mitarbeiter_nr": "MA-1",
        "typ": "KRANKHEIT",
        "von_datum": "2026-08-01",
        "bis_datum": "2026-08-05",
        "arbeitstage": 5.0,
        "status": "BEANTRAGT",
        "beantragt_von": "MA-1",
        "beantragt_am": "2026-07-30T08:00:00",
        "kommentar": None,
        "genehmigt_von": None,
        "genehmigt_am": None,
        "ablehnung_grund": None,
        "eau_nachweis_id": None,
        "vertretung_durch": "MA-2",
        "eau_pflicht": True,
        "abgeschlossen": False,
    }
    dumped = _assert_kein_feldverlust(hrm.AbwesenheitsantragOut, antrag)
    # eau_pflicht und abgeschlossen werden berechnet, nicht gespeichert —
    # sie duerfen nicht wegtypisiert werden.
    assert dumped["eau_pflicht"] is True
    assert dumped["abgeschlossen"] is False

    _assert_kein_feldverlust(
        hrm.AbwesenheitsantragListeOut, {"items": [antrag], "count": 1}
    )


def test_urlaubskonto():
    _assert_kein_feldverlust(
        hrm.UrlaubskontoOut,
        {
            "mitarbeiter_nr": "MA-1",
            "jahr": 2026,
            "anspruch_tage": 30.0,
            "verbraucht_tage": 12.0,
            "resturlaub_tage": 18.0,
            "genehmigte_antraege": 3,
        },
    )


# ── Legacy-Adapter ──────────────────────────────────────────────────────────


def test_adapter_antworten_behalten_execution_enabled():
    """``execution_enabled: false`` ist Teil des Vertrags — der Adapter ist
    repo-seitig fertig, die Ausfuehrung extern gegated."""
    profil = {
        "profile_key": "edifact_orders",
        "title": "EDIFACT ORDERS",
        "required_contract_fields": ["kunden_nr", "artikel_nr"],
        "execution_enabled": False,
        "status": "inactive",
    }
    _assert_kein_feldverlust(la.AdapterProfileOut, profil, "Profil(unkonfiguriert)")

    konfiguriert = {
        **profil,
        "status": "active",
        "format_version": "D96A",
        "mapping_version": "v2",
        "approved_by": "u1",
        "approved_at": datetime(2026, 8, 1),
        "updated_at": datetime(2026, 8, 2),
    }
    _assert_kein_feldverlust(la.AdapterProfileOut, konfiguriert, "Profil(konfiguriert)")

    liste = _assert_kein_feldverlust(
        la.AdapterProfileListOut,
        {"items": [konfiguriert], "total": 1, "execution_enabled": False},
    )
    assert liste["execution_enabled"] is False

    _assert_kein_feldverlust(
        la.AdapterConfigureOut,
        {"profile_key": "edifact_orders", "status": "active", "execution_enabled": False},
    )
    _assert_kein_feldverlust(
        la.AdapterIntakeOut,
        {"id": "b1", "status": "received", "duplicate": False, "payload_hash": "abc"},
    )


def test_adapter_stapelaktionen_und_monitor():
    batch = {
        "id": "b1",
        "profile_key": "edifact_orders",
        "external_id": "EXT-1",
        "payload_hash": "abc",
        "mapping_version": "v2",
        "status": "staged",
        "record_count": 10,
        "staged_count": 9,
        "mismatch_count": 1,
        "error_code": None,
        "error_message": None,
        "created_at": datetime(2026, 8, 1),
        "updated_at": datetime(2026, 8, 2),
    }
    _assert_kein_feldverlust(la.AdapterBatchOut, batch)
    _assert_kein_feldverlust(
        la.AdapterMonitorOut,
        {
            "items": [batch],
            "total": 1,
            "page": 1,
            "page_size": 50,
            "profiles": [],
            "execution_enabled": False,
        },
    )
    # stage / reconcile / approve liefern unterschiedliche Teilmengen.
    _assert_kein_feldverlust(
        la.AdapterBatchActionOut,
        {"id": "b1", "status": "staged", "staged_count": 9, "mismatch_count": 1,
         "execution_enabled": False},
        "Aktion(stage)",
    )
    _assert_kein_feldverlust(
        la.AdapterBatchActionOut,
        {"id": "b1", "status": "reconciled", "record_count": 10, "staged_count": 9,
         "mismatch_count": 1, "execution_enabled": False},
        "Aktion(reconcile)",
    )
    dumped = _assert_kein_feldverlust(
        la.AdapterBatchActionOut,
        {"id": "b1", "status": "approved", "execution_enabled": False,
         "next_gate": "customer_format_and_target_adapter_activation"},
        "Aktion(approve)",
    )
    assert dumped["next_gate"].startswith("customer_format")


# ── Rations-Schnittstellen ──────────────────────────────────────────────────


def test_rations_import_traegt_den_duplikatpfad():
    eintrag = {
        "id": "i1",
        "adapter": "agrirouter",
        "external_id": "EXT-1",
        "source_version": "1.0",
        "target_model": "feeding_log",
        "result": {"target": {"tierzahl": 120}},
        "imported_at": datetime(2026, 8, 1),
        "duplicate": False,
    }
    dumped = _assert_kein_feldverlust(ri.RationsImportOut, eintrag)
    assert dumped["result"]["target"]["tierzahl"] == 120


def test_herd_data_verbindung_gibt_kein_geheimnis_preis():
    verbindung = {
        "id": "c1",
        "provider": "herde",
        "herd_id": "H-1",
        "base_url": "https://example.invalid",
        "endpoint_templates": {"cows": "/cows"},
        "query_parameters": {"since": "{cursor}"},
        "credential_env_key": "HERD_API_TOKEN",
        "contract_ref": "V-2026-1",
        "consent_ref": "E-2026-1",
        "enabled": True,
        "live_enabled": False,
        "created_at": datetime(2026, 8, 1),
        "updated_at": datetime(2026, 8, 2),
    }
    dumped = _assert_kein_feldverlust(ri.HerdDataConnectionOut, verbindung)
    # Nur der Name der Umgebungsvariablen, nie das Geheimnis selbst.
    assert dumped["credential_env_key"] == "HERD_API_TOKEN"
    assert "credential" not in {k for k in dumped if k.endswith("_secret")}


def test_herd_data_sync_mock_und_beobachtungen():
    _assert_kein_feldverlust(
        ri.HerdDataSyncOut,
        {
            "run_id": "r1",
            "status": "success",
            "cursor_from": "2026-08-01T00:00:00",
            "cursor_to": "2026-08-02T00:00:00",
            "imported_count": 42,
        },
    )
    _assert_kein_feldverlust(
        ri.HerdDataMockImportOut,
        {
            "kind": "milk_yield",
            "normalized_count": 2,
            "imported_count": 0,
            "observations": [{"entity_id": "cow-1"}],
        },
    )
    _assert_kein_feldverlust(
        ri.HerdDataObservationOut,
        {
            "id": "o1",
            "provider": "herde",
            "herd_id": "H-1",
            "kind": "milk_yield",
            "entity_id": "cow-1",
            "effective_at": datetime(2026, 8, 1),
            "provider_updated_at": datetime(2026, 8, 1),
            "group_id": "g1",
            "previous_group_id": None,
            "is_deleted": False,
            "payload": {"kg": 38.5},
            "imported_at": datetime(2026, 8, 2),
        },
    )
